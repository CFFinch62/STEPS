# Steps Web Playground - Implementation Plan

## 1. Project Summary

`steps-web` is a browser-based Steps playground intended for:

- language exposure
- guided learning
- low-friction experimentation
- funneling users toward the marketing site and full Steps product

It should mirror the spirit of the PLAIN playground: focused, approachable,
educational, and intentionally limited.

## 2. Product Positioning

### Primary purpose

Provide a safe, browser-based introduction to Steps without requiring local
installation or the full multi-file project structure.

### Secondary purpose

Act as a bridge between:

1. the Steps marketing website
2. the Steps playground
3. the full downloadable / GitHub-based Steps product

### Non-goal

This is **not** a full browser replacement for the desktop Steps IDE in v1.

## 3. Core Product Decision

The playground will support a **subset** of Steps centered on:

- one visible `step`
- optional `risers` inside that step
- normal statements and expressions inside the step body

The playground will **hide** project structure details from the learner.

Behind the scenes, the system will generate a virtual Steps project with:

- a hidden `.building`
- a hidden `.floor`
- one generated `.step` from the user's editor content

## 4. V1 Scope

### In scope

- browser editor
- output panel
- input panel for `input`
- examples list
- tutorial content
- Run action
- Check action
- clear/reset actions
- hidden wrapper generation for building/floor
- server-side execution using the current Python interpreter
- links to marketing website and full product GitHub

### Supported language subset in v1

- `step:`
- `riser:`
- `expects:`
- `returns:`
- `declare:`
- `do:`
- `set`
- `display` / `indicate`
- `call`
- `return`
- `if` / `otherwise if` / `otherwise`
- `repeat times`
- `repeat for each`
- `repeat while`
- `attempt` / `if unsuccessful` / `then continue`
- lists, tables, numbers, text, booleans, `nothing`
- selected safe built-ins

### Out of scope for v1

- visible floors/buildings editing
- multi-file project authoring
- full IDE/debugger parity
- unrestricted file I/O
- terminal/TUI-heavy features
- account system
- cloud save backend
- collaborative editing

## 5. UX Requirements

### Main page sections

- header / title
- examples menu
- tutorials menu
- editor
- output pane
- pre-supplied input pane
- action buttons
- about / limitations panel
- marketing and GitHub links

### Required actions

- Run
- Check
- Reset lesson
- Clear editor
- Clear output

### Keyboard shortcut

- `Ctrl+Enter` runs the current code

### Educational framing

The page should explicitly explain:

- what works in the playground
- what is intentionally unavailable
- that full Steps projects use buildings and floors
- that the full product is the next step after the playground

## 6. Editor Contract

### Visible contract for the learner

The learner edits a single public step.

Recommended v1 rule:

- the public step name is fixed to `main`

This simplifies:

- example authoring
- hidden wrapper generation
- tutorial instructions
- backend execution

### Exact visible editor requirement

The editor accepts a **full step definition**.

Required first line:

- `step: main`

Optional in the visible editor:

- `expects:`
- `returns:`
- `declare:`
- `riser:` blocks
- `do:` block

`belongs to:` is allowed in pasted examples but will be normalized to the hidden
playground floor name during wrapper generation.

### Hidden wrapper behavior

For each run/check request, the backend creates a temporary virtual project:

- `playground.building`
- `playground/playground.floor`
- `playground/main.step`

The hidden building will call `main` and exit.

### Exact generated files

#### `playground.building`

```steps
building: playground
    call main
    exit
```

#### `playground/playground.floor`

```steps
floor: playground
    step: main
```

#### `playground/main.step`

- starts from the editor contents
- first line must remain `step: main`
- top-level `belongs to:` is rewritten to `belongs to: playground`
- if `belongs to:` is omitted, it is inserted automatically

## 7. Backend Architecture

### Chosen stack

- **Backend framework:** FastAPI
- **Frontend stack:** plain static HTML/CSS/JavaScript
- **Serving model:** backend serves both `/api/*` and the static playground UI

### Why this stack

- simplest deployment story
- one service instead of separate frontend/backend deployments
- no JavaScript build tooling required for v1
- easy to host on a small Python-compatible platform

### Recommendation

Use the existing Python Steps interpreter as the execution backend for v1.

### Why

- fastest path to launch
- no interpreter rewrite
- no semantic drift
- uses existing parser/runtime/tests
- easier to maintain initially

### Backend responsibilities

- receive editor source and input lines
- validate the visible step format
- generate hidden building/floor files
- create temporary sandbox project
- execute `check` or `run`
- capture output and errors
- return structured JSON response

### Suggested API surface

- `GET /api/health`
- `POST /api/run`
- `POST /api/check`
- `GET /api/examples`
- `GET /api/tutorials`

## 8. API Contracts

### `POST /api/run`

#### Request JSON

```json
{
  "step_source": "step: main\n    do:\n        display \"Hello\"\n",
  "input_lines": ["Alice", "42"],
  "include_wrapper": false
}
```

#### Response JSON

```json
{
  "ok": true,
  "mode": "run",
  "output": "Hello\n",
  "output_lines": ["Hello\n"],
  "diagnostics": [],
  "wrapper_files": {},
  "meta": {
    "building_name": "playground",
    "floor_name": "playground",
    "step_name": "main"
  }
}
```

### `POST /api/check`

#### Request JSON

Same as `/api/run`.

#### Response JSON

```json
{
  "ok": true,
  "mode": "check",
  "output": "",
  "output_lines": [],
  "diagnostics": [],
  "wrapper_files": {},
  "meta": {
    "building_name": "playground",
    "floor_name": "playground",
    "step_name": "main"
  }
}
```

### Diagnostic object shape

```json
{
  "code": "E206",
  "message": "Every step needs a 'do:' section with its logic.",
  "file": "playground/main.step",
  "line": 4,
  "column": 5,
  "hint": "Add 'do:' before your code."
}
```

### Request field rules

- `step_source` is required
- `step_source` must begin with `step: main`
- `input_lines` is optional and defaults to an empty list
- if execution requests more input than supplied, the backend returns empty text
- `include_wrapper` is optional and returns generated hidden files when true

### Error handling rules

- parse/load/runtime errors return `ok: false`
- errors are returned in `diagnostics`
- runtime output already produced is still returned in `output`
- wrapper validation errors use a playground-specific code namespace (e.g. `PLAY001`)

## 9. Sandbox / Safety Requirements

### Mandatory protections

- temporary workspace per request
- execution timeout
- loop safety remains enabled
- cleanup temp files after execution
- request size limit
- rate limiting if deployed publicly

### Built-ins policy

#### Allowed in v1

- text utilities
- math utilities
- list utilities
- safe date/time utilities as needed

#### Restricted or disabled in v1

- `read_file`
- `write_file`
- `append_file`
- CSV file operations
- terminal cursor/control features if they degrade web UX

If restricted built-ins are encountered, return a clear playground-specific
error message.

## 10. Content Strategy

### Examples should cover

- first output
- variables and display
- if/otherwise
- loops
- lists
- tables
- input handling
- simple risers
- a small complete mini-program

### Tutorials should cover

1. What a Step is
2. Setting values with `set`
3. Showing results with `display`
4. Making decisions with `if`
5. Repeating with loops
6. Using a riser helper
7. Taking input
8. Next step: full Steps projects with buildings and floors

## 11. Site Integration Requirements

### Cross-linking

- marketing website should link to playground
- playground should link back to marketing website
- playground should link to full product GitHub / download path

### Suggested messaging

- learn what Steps is on the marketing site
- try it instantly in the playground
- move to the full product for real multi-file projects

## 12. Proposed Folder Direction for `steps-web`

Initial scaffold direction:

- planning docs
- `backend/steps_web_backend/`
- `frontend/`
- `content/`
- `tests/`

Suggested tree:

```text
steps-web/
├── backend/
│   └── steps_web_backend/
├── content/
├── frontend/
├── tests/
├── IMPLEMENTATION_PLAN.md
└── README.md
```

## 13. Delivery Phases

### Phase 0 - Planning and decisions

- [x] Decide playground is a subset experience, not full IDE parity
- [x] Decide to hide floors/buildings behind wrapper generation
- [x] Decide to start with server-side Python execution
- [x] Choose frontend stack
- [x] Choose backend web framework
- [x] Define deployment target

### Phase 1 - Backend MVP

- [x] Create web backend skeleton
- [x] Add `/api/run`
- [x] Add `/api/check`
- [x] Generate hidden project wrapper
- [x] Capture output/errors as JSON
- [x] Add temp cleanup
- [x] Add timeout enforcement
- [x] Disable/restrict unsafe built-ins
- [x] Add backend tests for run/check wrapper flow

### Phase 2 - Frontend MVP

- [x] Create playground page shell
- [x] Add browser editor
- [x] Add output pane
- [x] Add input pane
- [x] Add Run button
- [x] Add Check button
- [x] Add clear/reset actions
- [x] Add Ctrl+Enter shortcut
- [x] Connect frontend to backend API

### Phase 3 - Content

- [x] Add starter examples
- [x] Add tutorial lessons
- [x] Add “What works here” panel
- [x] Add “Not available here” panel
- [x] Add marketing site link
- [x] Add GitHub/full product links

### Phase 4 - Polish and launch prep

- [x] Improve error display formatting
- [x] Add loading and disabled-button states
- [x] Save editor contents locally in browser
- [x] Add mobile/compact layout review
- [x] Add deployment configuration
- [ ] Smoke test public flow end-to-end

## 14. Multi-Session Progress Tracking

Use this section as the running project status area for future sessions.

### Current status snapshot

- [x] Product direction agreed
- [x] Subproject folder created
- [x] Initial implementation plan written
- [x] Tech stack selected
- [x] MVP scaffold created
- [x] Backend MVP working
- [x] Frontend MVP working
- [x] Initial examples loaded
- [x] Initial tutorials loaded
- [x] First deploy completed

### Latest completed work

- [x] Added a wall-clock timeout for playground `run` requests
- [x] Added a regression test for an infinite `repeat while true` loop
- [x] Disabled file/CSV built-ins for playground execution
- [x] Added a regression test for blocked `read_file` usage
- [x] Remapped generated-file diagnostics back to editor-visible locations
- [x] Added regression coverage for editor-line mapping on runtime/playground errors
- [x] Expanded examples/tutorial metadata for the playground UI
- [x] Added “What works here” / “Not available here” guidance panels
- [x] Mounted the marketing site at `/marketing` and linked full-product resources
- [x] Added regression coverage for homepage links and enriched content APIs
- [x] Chose Render as the initial deployment platform for the single-service app
- [x] Added a Render blueprint with a health check and source-based start command
- [x] Documented the deployment/runtime path strategy for `src/` + `steps-web/backend`
- [x] Reworked playground diagnostics into structured cards with code/message/location display
- [x] Added a clearer empty diagnostics state and homepage coverage for the new diagnostics panel
- [x] Added live request status messaging for loading/running/checking states in the playground UI
- [x] Disabled action controls during in-flight requests and added homepage coverage for the new status panel
- [x] Added browser localStorage persistence for the editor source so refreshes keep in-progress code
- [x] Preserved saved editor text during initial starter-content loading without breaking example/tutorial hydration
- [x] Added a responsive CSS pass for compact/mobile layouts across controls, links, and output panels
- [x] Reduced editor/output panel heights and tightened spacing for narrower screens
- [x] Added Markdown deployment instructions for the current source-based hosting shape
- [x] Added a Render-specific manual deployment guide for handoff and post-deploy testing
- [x] Completed the first Render deployment of the playground service
- [x] Simplified the homepage to a single Examples/Tutorials mode toggle with one lesson selector and one notes panel
- [x] Replaced the separate output/diagnostics presentation with one shared console and moved input beneath it
- [x] Enlarged the editor, disabled code wrapping, and removed homepage full-product/tutorial upsell clutter
- [x] Updated homepage regression coverage for the simplified single-selector, single-console layout
- [x] Compressed the desktop layout into three columns so Learn, Editor, Console, and Input fit on one page without vertical scrolling
- [x] Replaced the large header card with a compact top bar to keep the playground near the page edges
- [x] Added an About Steps Playground dialog and an About Steps Language link in the top bar
- [x] Corrected the About Steps Language URL and refined the About Steps Playground dialog copy/spacing
- [x] Rebalanced the desktop column widths so the editor is narrower and the console/input column is wider

### Next-session checklist

Before ending a dev session:

- [ ] Update completed checklist items in this file
- [ ] Add any new decisions to the decision log
- [ ] Record blockers and open questions
- [ ] Record the next 1-3 concrete tasks
- [ ] Confirm whether scope changed

At the start of a new dev session:

- [ ] Read Sections 12-15 of this file
- [ ] Review the current status snapshot
- [ ] Review blockers/open questions
- [ ] Pick the next unchecked tasks from the active phase

## 15. Decision Log

### Confirmed decisions

- [x] Playground is for exposure and basic learning
- [x] Playground mirrors the PLAIN playground model
- [x] V1 supports steps and risers, not full visible project structure
- [x] Hidden building/floor wrapper will be generated automatically
- [x] Marketing site and playground should cross-link
- [x] Playground should link to the full product/repo
- [x] Go/WASM is deferred unless later justified
- [x] Backend framework is FastAPI
- [x] Frontend stack is plain static HTML/CSS/JavaScript
- [x] One Python service will serve both API and static frontend
- [x] Playground disables file/CSV built-ins (`read_file`, `write_file`, `append_file`, `file_exists`, `read_csv`, `write_csv`)
- [x] Initial deployment target is Render
- [x] Initial deployment will run from source with `PYTHONPATH=src:steps-web/backend` to avoid installing desktop IDE dependencies on the server
- [x] Playground homepage should default to Examples mode
- [x] Playground homepage should use a single Examples/Tutorials toggle, one shared notes panel, and one console for both output and errors
- [x] Playground homepage should keep only the GitHub link and avoid full-product/tutorial upsell clutter
- [x] Desktop layout should place Learn/Notes on the left, Editor in the center, and Console/Input on the right without page scrolling on a normal desktop screen
- [x] Top bar should include an About Steps Playground dialog and an external About Steps Language link to `https://fragillidaesoftware.com/apps/steps/`

### Open decisions

- [ ] Whether to also restrict TUI-oriented built-ins for cleaner browser UX
- [ ] Whether tutorials are static JSON/Markdown or hardcoded UI content
- [ ] Whether to later package `steps_web_backend` more formally instead of using a deploy-time `PYTHONPATH`

## 16. Blockers / Risks / Open Questions

### Risks

- hidden wrapper behavior may produce confusing errors unless locations are
  mapped clearly back to the visible editor
- some built-ins may not fit browser-playground expectations cleanly
- example/tutorial quality will strongly affect perceived usefulness

### Open questions

- Should the visible editor require a full `step: main` definition, or should
  the UI provide a skeleton automatically?
- Should the playground offer both `Run` and `Check`, or `Run` only at first?
- Should examples/tutorials live in this repo or the marketing site repo?
- Should the web backend later move under `src/` or a separate web package for cleaner install/deploy workflows?

## 17. Recommended Immediate Next Steps

1. Review the compact three-column layout locally in the browser and confirm it fits on one desktop page without vertical scrolling.
2. If the compact layout looks right locally, push it and smoke test the public Render flow end-to-end.
3. Revisit whether additional browser-unfriendly built-ins should be restricted.
4. Decide whether the web backend should later move under `src/` for cleaner packaging.
5. Decide whether example/tutorial selection should also persist locally, or only the editor source.

## 18. Current Scaffold Status

The repository now has a first-pass scaffold for:

- wrapper generation
- API endpoint skeletons
- timeout-enforced playground execution
- playground-only file/CSV builtin restrictions
- editor-visible diagnostic remapping from hidden wrapper files
- static browser UI
- richer examples/tutorial content and tutorial-path notes
- mounted marketing-site integration at `/marketing`
- initial Render deployment blueprint/configuration
- targeted wrapper/web-app tests

This is a **starter implementation**, not a production-ready deployed playground.
