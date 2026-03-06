# Steps Web Deployment Overview

This document explains what the current `steps-web` deployment looks like and
what to verify before creating a public deployment.

## Current hosting shape

`steps-web` is currently designed to deploy as **one Python web service**:

- FastAPI serves the JSON API
- the same app serves the static playground frontend
- the same app also mounts the local marketing site under `/marketing`

This keeps the first deployment simple:

- no separate frontend hosting
- no JavaScript build pipeline
- no database
- no background workers

## Files involved in deployment

- `render.yaml` - Render blueprint for the first hosted service
- `steps-web/backend/steps_web_backend/app.py` - FastAPI app entry point
- `steps-web/frontend/` - static browser UI served by the backend
- `marketing-website/` - mounted at `/marketing`
- `src/` - Steps runtime used by the playground backend

## Current deploy commands

The current Render blueprint uses:

- build command: `python -m pip install "fastapi>=0.135.1" "uvicorn>=0.41.0"`
- start command: `PYTHONPATH=src:steps-web/backend python -m uvicorn steps_web_backend.app:app --host 0.0.0.0 --port $PORT`
- health check path: `/api/health`

## Why deployment runs from source

The repo root package currently includes desktop-oriented dependencies, while the
web backend lives outside `src/`.

For that reason, the first deployment intentionally runs from source using:

- `PYTHONPATH=src:steps-web/backend`

This avoids needing to package and install the full desktop app on the server.

## Local preflight before deploying

Recommended local checks:

1. Confirm the app imports:
   - `PYTHONPATH=src:steps-web/backend python3 -m uv run python -c "from steps_web_backend.app import app; print(type(app).__name__)"`
2. Run the web tests:
   - `PYTHONPATH=".venv/lib/python3.13/site-packages:src:steps-web/backend${PYTHONPATH:+:$PYTHONPATH}" python3 -m pytest steps-web/tests/test_playground_runner.py steps-web/tests/test_web_app.py`
3. Optional local smoke run:
   - `PYTHONPATH=src:steps-web/backend python3 -m uv run python -m uvicorn steps_web_backend.app:app --host 127.0.0.1 --port 8765`
4. Confirm the health endpoint:
   - `http://127.0.0.1:8765/api/health`

## What to verify after deploy

Once Render gives you a public URL, verify:

1. `/api/health` returns success
2. `/` loads the Steps playground
3. `/marketing/` loads the marketing site
4. `/api/examples` returns JSON
5. `/api/tutorials` returns JSON
6. `Run` works on the default example
7. `Check` works on the default example
8. GitHub and documentation links load correctly

## What to send back after you deploy

Once you have deployed it, send me:

- the public Render URL
- whether you used the Render blueprint or manual setup
- any build/start errors if Render reports them

Then I can run the post-deploy smoke test with you.