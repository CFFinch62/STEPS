from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "steps-web" / "backend"))

from steps_web_backend.app import create_app


def test_homepage_uses_a_single_mode_playground_layout() -> None:
    client = TestClient(create_app())

    response = client.get("/")

    assert response.status_code == 200
    assert "Examples" in response.text
    assert "Tutorials" in response.text
    assert "Console" in response.text
    assert "Input" in response.text
    assert "About Steps Playground" in response.text
    assert "About Steps Language" in response.text
    assert "https://fragillidaesoftware.com/apps/steps/" in response.text
    assert 'id="about-playground-dialog"' in response.text
    assert "Ready. Use Run or Check to try the current code." in response.text
    assert 'id="request-status"' in response.text
    assert 'id="lesson-select"' in response.text
    assert 'id="learning-notes"' in response.text
    assert 'id="mode-examples"' in response.text
    assert 'id="mode-tutorials"' in response.text
    assert 'id="editor"' in response.text
    assert 'aria-label="Steps editor"' in response.text
    assert "/steps-lang.js" in response.text
    assert "monaco-editor@0.44.0/min/vs/loader.js" in response.text
    assert 'wrap="off"' not in response.text
    assert "https://github.com/CFFinch62/Steps" in response.text
    assert 'See "About Steps Language" for full language details.' in response.text
    assert "watching what happens" in response.text
    assert "make something happen yourself" in response.text
    assert "What works here" not in response.text
    assert "Not available here" not in response.text
    assert "Continue with full Steps" not in response.text
    assert 'id="diagnostics"' not in response.text
    assert 'id="example-select"' not in response.text
    assert 'id="tutorial-select"' not in response.text
    assert "/marketing/" not in response.text


def test_marketing_site_is_served_from_the_playground_app() -> None:
    client = TestClient(create_app())

    response = client.get("/marketing/")

    assert response.status_code == 200
    assert "Steps Programming Language" in response.text


def test_examples_and_tutorials_api_return_enriched_content() -> None:
    client = TestClient(create_app())

    examples = client.get("/api/examples").json()["items"]
    tutorials = client.get("/api/tutorials").json()["items"]

    hello_world = next(item for item in examples if item["id"] == "hello-world")
    first_tutorial = next(item for item in tutorials if item["id"] == "what-is-a-step")

    assert hello_world["focus_points"]
    assert first_tutorial["checklist"]
    assert first_tutorial["learn_more"]["href"].startswith("/marketing/")