from __future__ import annotations

from contextlib import contextmanager
from multiprocessing import Process, Queue
from pathlib import Path
from queue import Empty
from tempfile import TemporaryDirectory
from typing import Literal

from steps import builtins
from steps.errors import StepsRuntimeError
from steps.interpreter import run_building
from steps.loader import load_project

from .contracts import PlaygroundDiagnostic, PlaygroundRequest, PlaygroundResponse
from .wrapper import PLAYGROUND_NAME, PLAYGROUND_STEP_NAME, build_wrapper_files, write_wrapper_files


PLAYGROUND_RUN_TIMEOUT_SECONDS = 2.0
DISABLED_PLAYGROUND_BUILTINS = {
    "read_file",
    "write_file",
    "append_file",
    "file_exists",
    "read_csv",
    "write_csv",
}


def _make_input_handler(input_lines: list[str]):
    remaining = list(input_lines)

    def _read_input() -> str:
        return remaining.pop(0) if remaining else ""

    return _read_input


def _playground_diagnostic(message: str, code: str) -> PlaygroundDiagnostic:
    return PlaygroundDiagnostic(
        code=code,
        message=message,
        file="editor",
        line=1,
        column=1,
        hint="Start with `step: main` and keep all code inside that step.",
    )


def _has_explicit_belongs(step_source: str) -> bool:
    lines = step_source.replace("\r\n", "\n").split("\n")
    for line in lines[1:]:
        stripped = line.strip().lower()
        if line.startswith("    ") and not line.startswith("        ") and stripped.startswith("belongs to:"):
            return True
    return False


def _map_diagnostic_to_editor(
    diagnostic: PlaygroundDiagnostic,
    step_source: str,
) -> PlaygroundDiagnostic:
    if not diagnostic.file or diagnostic.file == "editor":
        return diagnostic

    normalized_file = diagnostic.file.replace("\\", "/")
    explicit_belongs = _has_explicit_belongs(step_source)

    if normalized_file.endswith(f"/{PLAYGROUND_STEP_NAME}.step"):
        mapped_line = diagnostic.line
        if mapped_line is not None and not explicit_belongs and mapped_line >= 2:
            mapped_line -= 1

        return PlaygroundDiagnostic(
            code=diagnostic.code,
            message=diagnostic.message,
            file="editor",
            line=max(mapped_line or 1, 1),
            column=diagnostic.column,
            hint=diagnostic.hint,
        )

    if normalized_file.endswith(".building") or normalized_file.endswith(".floor"):
        return PlaygroundDiagnostic(
            code=diagnostic.code,
            message=diagnostic.message,
            file="editor",
            line=1,
            column=1,
            hint=diagnostic.hint,
        )

    return diagnostic


def _map_diagnostics_to_editor(
    diagnostics: list[PlaygroundDiagnostic],
    step_source: str,
) -> list[PlaygroundDiagnostic]:
    return [_map_diagnostic_to_editor(diagnostic, step_source) for diagnostic in diagnostics]


def _meta() -> dict[str, str]:
    return {
        "building_name": PLAYGROUND_NAME,
        "floor_name": PLAYGROUND_NAME,
        "step_name": PLAYGROUND_STEP_NAME,
    }


def _timeout_diagnostic() -> PlaygroundDiagnostic:
    return PlaygroundDiagnostic(
        code="PLAY003",
        message=(
            f"Playground run exceeded the {PLAYGROUND_RUN_TIMEOUT_SECONDS:g}-second execution limit."
        ),
        file="editor",
        line=1,
        column=1,
        hint="Check for an infinite loop or long-running recursion, then try again.",
    )


def _unexpected_execution_diagnostic() -> PlaygroundDiagnostic:
    return PlaygroundDiagnostic(
        code="PLAY004",
        message="Playground execution ended unexpectedly.",
        file="editor",
        line=1,
        column=1,
        hint="Try running again. If the problem continues, the playground runner may need attention.",
    )


def _disabled_builtin(name: str):
    def _raise_disabled(*_arguments, location=None):
        raise StepsRuntimeError(
            code="PLAY005",
            message=f"The '{name}' built-in is not available in the playground.",
            file=location.file if location else Path("<unknown>"),
            line=location.line if location else 0,
            column=location.column if location else 0,
            hint=(
                "Use input/output and in-memory values in the playground. "
                "File and CSV access belong in the full Steps product."
            ),
        )

    return _raise_disabled


@contextmanager
def _restricted_native_functions():
    original_registry = builtins.NATIVE_FUNCTIONS
    restricted_registry = original_registry.copy()
    for name in DISABLED_PLAYGROUND_BUILTINS:
        native_def = original_registry.get(name)
        if native_def is None:
            continue
        restricted_registry[name] = {
            **native_def,
            "function": _disabled_builtin(name),
        }

    builtins.NATIVE_FUNCTIONS = restricted_registry
    try:
        yield
    finally:
        builtins.NATIVE_FUNCTIONS = original_registry


def _run_project(project_dir: str, input_lines: list[str], result_queue: Queue) -> None:
    output_lines: list[str] = []

    try:
        building, environment, errors = load_project(Path(project_dir))
        if errors or building is None:
            result_queue.put(
                {
                    "ok": False,
                    "output_lines": [],
                    "diagnostics": [
                        PlaygroundDiagnostic.from_steps_error(error).__dict__ for error in errors
                    ],
                }
            )
            return

        environment.input_handler = _make_input_handler(input_lines)
        environment.output_handler = output_lines.append
        with _restricted_native_functions():
            result = run_building(building, environment)
        diagnostics = []
        if result.error:
            diagnostics.append(PlaygroundDiagnostic.from_steps_error(result.error).__dict__)

        result_queue.put(
            {
                "ok": result.success,
                "output_lines": output_lines.copy(),
                "diagnostics": diagnostics,
            }
        )
    except Exception:
        result_queue.put(
            {
                "ok": False,
                "output_lines": output_lines.copy(),
                "diagnostics": [_unexpected_execution_diagnostic().__dict__],
            }
        )


def _run_with_timeout(project_dir: Path, input_lines: list[str]) -> tuple[bool, list[str], list[PlaygroundDiagnostic]]:
    result_queue: Queue = Queue()
    process = Process(target=_run_project, args=(str(project_dir), input_lines, result_queue))
    process.start()

    try:
        process.join(timeout=PLAYGROUND_RUN_TIMEOUT_SECONDS)
        if process.is_alive():
            process.kill()
            process.join()
            return False, [], [_timeout_diagnostic()]

        try:
            payload = result_queue.get(timeout=1)
        except Empty:
            return False, [], [_unexpected_execution_diagnostic()]

        diagnostics = [PlaygroundDiagnostic(**item) for item in payload["diagnostics"]]
        return payload["ok"], payload["output_lines"], diagnostics
    finally:
        result_queue.close()
        result_queue.join_thread()


def execute_playground(
    request: PlaygroundRequest,
    mode: Literal["run", "check"],
) -> PlaygroundResponse:
    try:
        wrapper_files = build_wrapper_files(request.step_source)
    except ValueError as exc:
        text = str(exc)
        code, _, message = text.partition(": ")
        return PlaygroundResponse(
            ok=False,
            mode=mode,
            diagnostics=[_playground_diagnostic(message or text, code or "PLAY000")],
        )

    with TemporaryDirectory(prefix="steps-web-") as temp_dir:
        project_dir = Path(temp_dir)
        write_wrapper_files(project_dir, wrapper_files)
        building, environment, errors = load_project(project_dir)

        if errors or building is None:
            return PlaygroundResponse(
                ok=False,
                mode=mode,
                diagnostics=_map_diagnostics_to_editor(
                    [PlaygroundDiagnostic.from_steps_error(error) for error in errors],
                    request.step_source,
                ),
                wrapper_files=wrapper_files if request.include_wrapper else {},
                meta=_meta(),
            )

        if mode == "check":
            return PlaygroundResponse(
                ok=True,
                mode=mode,
                wrapper_files=wrapper_files if request.include_wrapper else {},
                meta=_meta(),
            )

        ok, output_lines, diagnostics = _run_with_timeout(project_dir, request.input_lines)
        diagnostics = _map_diagnostics_to_editor(diagnostics, request.step_source)

        return PlaygroundResponse(
            ok=ok,
            mode=mode,
            output="".join(output_lines),
            output_lines=output_lines,
            diagnostics=diagnostics,
            wrapper_files=wrapper_files if request.include_wrapper else {},
            meta=_meta(),
        )