# Steps Web Render Deployment Instructions

This guide is the step-by-step manual process for deploying `steps-web` to
Render.

## Recommended path

Use **Render Blueprint** deployment from the repo root because `render.yaml`
already defines the current service shape.

## Option A - Deploy with `render.yaml` (recommended)

1. Push your current branch/commit to the Git provider connected to Render.
2. Log in to Render.
3. Choose **New +**.
4. Choose **Blueprint**.
5. Select this repository.
6. Confirm Render detects `render.yaml` in the repo root.
7. Review the generated service named `steps-web`.
8. Start the deploy.

Render should use these settings from the blueprint:

- type: `web`
- runtime: `python`
- build command: `python -m pip install "fastapi>=0.135.1" "uvicorn>=0.41.0"`
- start command: `PYTHONPATH=src:steps-web/backend python -m uvicorn steps_web_backend.app:app --host 0.0.0.0 --port $PORT`
- health check path: `/api/health`

## Option B - Manual Render Web Service setup

If you prefer not to use Blueprint, create one web service manually with these
settings:

1. Choose **New +**.
2. Choose **Web Service**.
3. Connect the repository.
4. Set the root directory to the repo root.
5. Use the following service settings:
   - Runtime: `Python`
   - Build Command: `python -m pip install "fastapi>=0.135.1" "uvicorn>=0.41.0"`
   - Start Command: `PYTHONPATH=src:steps-web/backend python -m uvicorn steps_web_backend.app:app --host 0.0.0.0 --port $PORT`
   - Health Check Path: `/api/health`

## Environment variables

No required custom environment variables are currently needed for the first
deployment.

## What success looks like in Render

The deploy is in good shape if:

1. the build finishes successfully
2. the service starts without import errors
3. the health check passes at `/api/health`
4. Render assigns a public HTTPS URL

## First checks to run in the browser

Open the public URL and verify:

1. homepage loads
2. example and tutorial selectors populate
3. default example can run
4. default example can check
5. diagnostics panel renders cleanly
6. `/marketing/` works

## Quick URL checklist

Replace `<your-render-url>` with your actual deployed URL:

- `<your-render-url>/`
- `<your-render-url>/api/health`
- `<your-render-url>/api/examples`
- `<your-render-url>/api/tutorials`
- `<your-render-url>/marketing/`

## If Render fails during build or start

Capture and send back:

1. build log errors
2. startup log errors
3. whether the failure is during build, boot, or health check

Common places to look:

- missing import in startup logs
- wrong repo branch selected in Render
- service rooted in the wrong directory
- health check failing because the service never finished booting

## After deployment

Send me the public URL and I will do the next planned step:

- public smoke test of the deployed playground flow