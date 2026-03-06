from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "steps-web" / "backend"))

from steps_web_backend.contracts import PlaygroundRequest
from steps_web_backend.runner import execute_playground
from steps_web_backend.wrapper import build_wrapper_files


def test_build_wrapper_files_injects_floor_membership() -> None:
    files = build_wrapper_files(
        "step: main\n"
        "    do:\n"
        "        display \"Hello\"\n"
    )

    assert set(files) == {
        "playground.building",
        "playground/playground.floor",
        "playground/main.step",
    }
    assert "belongs to: playground" in files["playground/main.step"]


def test_execute_playground_run_returns_output() -> None:
    request = PlaygroundRequest(
        step_source=(
            "step: main\n"
            "    do:\n"
            "        display \"Hello from test\"\n"
        ),
        include_wrapper=True,
    )

    response = execute_playground(request, mode="run")

    assert response.ok is True
    assert response.output == "Hello from test\n"
    assert response.wrapper_files["playground.building"].startswith("building: playground")


def test_execute_playground_rejects_non_main_step() -> None:
    request = PlaygroundRequest(step_source="step: greeting\n    do:\n        display \"Hi\"\n")

    response = execute_playground(request, mode="check")

    assert response.ok is False
    assert response.diagnostics[0].code == "PLAY002"


def test_execute_playground_times_out_infinite_loop() -> None:
    request = PlaygroundRequest(
        step_source=(
            "step: main\n"
            "    do:\n"
            "        repeat while true\n"
            "            set counter to 1\n"
        ),
        include_wrapper=True,
    )

    response = execute_playground(request, mode="run")

    assert response.ok is False
    assert response.diagnostics[0].code == "PLAY003"
    assert "execution limit" in response.diagnostics[0].message
    assert response.wrapper_files["playground.building"].startswith("building: playground")


def test_execute_playground_blocks_file_builtins() -> None:
    request = PlaygroundRequest(
        step_source=(
            "step: main\n"
            "    do:\n"
            "        call read_file with \"secret.txt\"\n"
        )
    )

    response = execute_playground(request, mode="run")

    assert response.ok is False
    assert response.diagnostics[0].code == "PLAY005"
    assert "read_file" in response.diagnostics[0].message
    assert response.diagnostics[0].file == "editor"
    assert response.diagnostics[0].line == 3


def test_execute_playground_maps_runtime_errors_to_editor_lines() -> None:
    request = PlaygroundRequest(
        step_source=(
            "step: main\n"
            "    do:\n"
            "        call missing_step\n"
        )
    )

    response = execute_playground(request, mode="run")

    assert response.ok is False
    assert response.diagnostics[0].code == "E402"
    assert response.diagnostics[0].file == "editor"
    assert response.diagnostics[0].line == 3