from __future__ import annotations

from pathlib import Path
from typing import Any

try:  # pragma: no cover - exercised only when FastAPI is installed
    from fastapi import FastAPI
    from fastapi.responses import FileResponse
    from fastapi.staticfiles import StaticFiles
except ImportError:  # pragma: no cover
    FastAPI = None  # type: ignore[assignment]
    FileResponse = None  # type: ignore[assignment]
    StaticFiles = None  # type: ignore[assignment]

from .content import load_examples, load_tutorials
from .contracts import PlaygroundRequest
from .runner import execute_playground


FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
MARKETING_DIR = Path(__file__).resolve().parents[3] / "marketing-website"


def _request_from_payload(payload: dict[str, Any]) -> PlaygroundRequest:
    input_lines = payload.get("input_lines", [])
    return PlaygroundRequest(
        step_source=str(payload.get("step_source", "")),
        input_lines=[str(item) for item in input_lines],
        include_wrapper=bool(payload.get("include_wrapper", False)),
    )


def create_app():  # pragma: no cover - depends on optional FastAPI install
    if FastAPI is None:
        raise RuntimeError(
            "FastAPI is not installed yet. Add FastAPI/Uvicorn dependencies before starting the web app."
        )

    app = FastAPI(title="Steps Web Playground", version="0.1.0")

    @app.get("/api/health")
    async def health() -> dict[str, str]:
        return {"ok": "true", "service": "steps-web"}

    @app.get("/api/examples")
    async def examples() -> dict[str, Any]:
        return {"items": load_examples()}

    @app.get("/api/tutorials")
    async def tutorials() -> dict[str, Any]:
        return {"items": load_tutorials()}

    @app.post("/api/run")
    async def run_api(payload: dict[str, Any]) -> dict[str, Any]:
        return execute_playground(_request_from_payload(payload), mode="run").to_dict()

    @app.post("/api/check")
    async def check_api(payload: dict[str, Any]) -> dict[str, Any]:
        return execute_playground(_request_from_payload(payload), mode="check").to_dict()

    @app.get("/")
    async def index() -> Any:
        return FileResponse(FRONTEND_DIR / "index.html")

    app.mount("/marketing", StaticFiles(directory=MARKETING_DIR, html=True), name="marketing")
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
    return app


app = create_app() if FastAPI is not None else None