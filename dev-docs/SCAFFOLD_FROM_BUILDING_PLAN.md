# Scaffold from Building — Implementation Plan

**Status: IMPLEMENTED — 2026-06-27**

## Overview

Add a **"Scaffold from Building..."** menu item and toolbar button to the Steps IDE that reads the `floors:` section of the currently open `.building` file and automatically creates the corresponding floor folders and step files with boilerplate code.

## Design Decisions

1. **Non-Destructive**: Never overwrites existing files. If a floor folder or step file already exists, it is silently skipped. Safe to run repeatedly as the user adds new floors/steps to the `floors:` section.

2. **Include all sections in scaffold**: Step templates include `expects:`, `returns:`, `declare:`, and `do:` sections even when empty/minimal. Better to have them and not need them than need them and not have them.

3. **Both menu item and toolbar button**: Add to File menu after "New Project..." AND add a 🏗️ Scaffold toolbar button.

## File to Modify

**`src/steps_ide/app/main_window.py`**

### 1. Add Menu Item

Insert after line 565 (the existing "New Project..." entry, around line 563-565):

```python
scaffold_action = file_menu.addAction("&Scaffold from Building...")
scaffold_action.setShortcut("Ctrl+Shift+G")
scaffold_action.triggered.connect(self._scaffold_from_building)
```

### 2. Add Toolbar Button

Insert in `_setup_toolbar()` method (around line 825), after the New/Open/Save group:

```python
scaffold_btn = self.toolbar.addAction("🏗️ Scaffold")
scaffold_btn.setToolTip("Scaffold from Building (Ctrl+Shift+G)")
scaffold_btn.triggered.connect(self._scaffold_from_building)
```

### 3. Add `_scaffold_from_building()` Method

Insert after the existing `_new_project()` method (ends around line 1035).

**Logic flow:**

1. Get the current file path from `self.editor_tabs.get_current_filepath()`
2. Check if it's a `.building` file — if not, show error via `QMessageBox.warning()`
3. Save the file first via `self.editor_tabs.save_current()`
4. Parse the building file using the existing pipeline:
   ```python
   from pathlib import Path
   from steps.lexer import Lexer
   from steps.parser import Parser

   source = Path(filepath).read_text(encoding='utf-8')
   lexer = Lexer(source, Path(filepath))
   tokens = lexer.tokenize()
   parser = Parser(tokens, Path(filepath))
   result = parser.parse_building()
   ```
5. Check `result.success` and `result.ast.floors` — if no floors, show info message
6. Read `building_node.floors` — a `List[FloorNode]`, each with:
   - `.name` (str) — the floor name
   - `.steps` (List[str]) — list of step names
7. Determine `project_dir` from the building file's parent: `Path(filepath).parent`
8. For each floor, create `project_dir / floor_name /` if it doesn't exist
9. For each step in each floor, create `project_dir / floor_name / step_name.step` if it doesn't exist, using the scaffold template below
10. Refresh the file browser via `self.file_browser.navigate_to(str(project_dir))`
11. Show terminal if hidden, report results: "Created X folders, Y step files. Skipped Z existing."

### Step Scaffold Template

```python
STEP_TEMPLATE = (
    "step: {step_name}\n"
    "    belongs to: {floor_name}\n"
    "    expects: nothing\n"
    "    returns: nothing\n"
    "\n"
    "    declare:\n"
    "        note: Add variable declarations here\n"
    "\n"
    "    do:\n"
    '        note: TODO - implement {step_name}\n'
    '        display "{step_name} called"\n'
)
```

## Key AST Types (Reference)

From `src/steps/ast_nodes.py`:

- `BuildingNode.floors: List[FloorNode]` — inline floor declarations
- `FloorNode.name: str` — floor name
- `FloorNode.steps: List[str]` — step names in this floor

From `src/steps/parser.py`:

- `Parser.parse_building()` returns `ParseResult` with `.success`, `.ast` (BuildingNode), `.errors`

## Existing Patterns to Follow

The `_new_project()` method (line 930-1035) already:
- Creates directories with `Path.mkdir(parents=True)`
- Writes step files with `Path.write_text(content)`
- Navigates the file browser with `self.file_browser.navigate_to()`
- Reports via `self.statusbar.showMessage()`

The `_check_project_syntax()` method (line 1618-1686) already:
- Checks if current file is `.building` or `.step`
- Parses via the `Lexer → Parser` pipeline
- Writes output to terminal via `self.terminal.write_output()`
- Shows terminal if hidden

## User Workflow

```
1. File → New Project...           → Creates project folder + building file + main/ + first_step.step
2. User edits the floors: section to add floors and steps
3. File → Scaffold from Building   → Creates all missing floor folders and step files
4. User fills in the step implementations
5. (User adds more steps to floors: section → re-runs Scaffold → only new ones created)
```

## Verification

1. Create a new project via "New Project..."
2. Edit the building file to add 2 floors with 3 steps each
3. Click "Scaffold from Building" — verify 2 folders + 6 step files created
4. Click "Scaffold from Building" again — verify 0 created, 6 skipped
5. Verify all generated `.step` files load without parse errors (F6 check)
