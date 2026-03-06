# Steps Web

This folder contains planning and implementation materials for the browser-based
Steps playground / mini-IDE subproject.

## Purpose

The goal of `steps-web` is to create a lightweight, browser-based Steps learning
environment modeled after the PLAIN playground:

- examples
- tutorials
- browser editor
- run/check output
- low-friction exposure to the language

This subproject is intentionally **not** a full browser port of the desktop
Steps product in v1.

## Chosen v1 stack

- **Backend:** FastAPI
- **Frontend:** plain static HTML/CSS/JavaScript
- **Deployment shape:** one Python web app serving both the API and the static UI

This keeps deployment simple by avoiding a separate SPA build pipeline.

## Primary document

- `IMPLEMENTATION_PLAN.md` - product spec, architecture, phased roadmap, and
  multi-session progress checklists

## Starter structure

- `backend/steps_web_backend/` - backend scaffold and playground runner
- `frontend/` - static browser UI scaffold
- `content/` - examples and tutorial starter content
- `tests/` - targeted tests for wrapper/execution helpers

## Dependency note

FastAPI + Uvicorn have been added for the web layer.

Useful local verification commands:

- `python3 -m uv run python -c "import fastapi, uvicorn; print(fastapi.__version__, uvicorn.__version__)"`
- `PYTHONPATH=src:steps-web/backend python3 -m uv run python -m uvicorn steps_web_backend.app:app --reload`

## Initial deployment target

The current deployment target is **Render**.

- repo config: `render.yaml`
- deployment overview: `DEPLOYMENT.md`
- Render step-by-step guide: `RENDER_DEPLOYMENT.md`
- health endpoint: `/api/health`
- deploy start command uses `PYTHONPATH=src:steps-web/backend`

This avoids installing the full desktop-oriented package on the server while the
web backend still lives outside `src/`.
