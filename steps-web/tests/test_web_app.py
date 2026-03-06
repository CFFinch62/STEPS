from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "steps-web" / "backend"))

from steps_web_backend.app import create_app


def test_homepage_includes_learning_panels_and_links() -> None:
    client = TestClient(create_app())

    response = client.get("/")

    assert response.status_code == 200
    assert "What works here" in response.text
    assert "Not available here" in response.text
    assert "No diagnostics yet. Use Check or Run." in response.text
    assert "Ready." in response.text
    assert 'id="request-status"' in response.text
    assert 'id="diagnostics"' in response.text
    assert "/marketing/" in response.text
    assert "https://github.com/CFFinch62/Steps" in response.text


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