# Steps IDE - Implementation from Only Code

## Overview

This document provides a concrete roadmap for transforming Only Code into the Steps IDE. It maps each Only Code file to its Steps equivalent and describes exactly what changes are needed.

## Source Material

Only Code repository structure:
```
Only_Code/
├── onlycode/
│   ├── __init__.py
│   ├── main.py
│   ├── app/
│   │   ├── application.py
│   │   └── screens/
│   │       ├── main_screen.py
│   │       └── file_dialogs.py
│   │   └── widgets/
│   │       ├── file_browser.py
│   │       ├── terminal_panel.py
│   │       ├── tab_bar.py
│   │       └── status_bar.py
│   ├── editor/
│   │   ├── editor_widget.py
│   │   └── buffer_manager.py
│   └── shared/
│       └── config/
│           ├── loader.py
│           ├── session.py
│           └── settings.py
├── pyproject.toml
├── requirements.txt
└── run_onlycode.py
```

## File-by-File Transformation

### 1. Project Root

| Only Code | Steps IDE | Action |
|-----------|-----------|--------|
| `onlycode/` | `steps_ide/` | Rename folder |
| `run_onlycode.py` | `run_steps_ide.py` | Rename, update imports |
| `pyproject.toml` | `pyproject.toml` | Update name, add interpreter deps |
| `requirements.txt` | `requirements.txt` | Same dependencies |

### 2. Main Entry Point

**`onlycode/main.py` → `steps_ide/main.py`**

```python
# ORIGINAL (Only Code)
from onlycode.app.application import OnlyCodeApp

def main():
    app = OnlyCodeApp()
    app.run()

# TRANSFORMED (Steps IDE)
from steps_ide.app.application import StepsIDEApp

def main():
    app = StepsIDEApp()
    app.run()
```

Changes:
- Rename import
- Rename class reference

### 3. Application Class

**`onlycode/app/application.py` → `steps_ide/app/application.py`**

```python
# ORIGINAL (Only Code) - Key sections
class OnlyCodeApp(App):
    TITLE = "Only Code"
    
    def on_mount(self) -> None:
        self.push_screen(MainScreen())

# TRANSFORMED (Steps IDE)
class StepsIDEApp(App):
    TITLE = "Steps IDE"
    
    BINDINGS = [
        # Inherited from Only Code
        ("ctrl+b", "toggle_project_browser", "Browser"),
        ("ctrl+j", "toggle_terminal", "Terminal"),
        # NEW: Steps-specific
        ("f5", "run_project", "Run"),
        ("f6", "check_project", "Check"),
        ("f7", "show_diagram", "Diagram"),
        ("ctrl+shift+n", "new_floor", "New Floor"),
    ]
    
    def __init__(self):
        super().__init__()
        self.current_project = None  # NEW: Track open project
    
    def on_mount(self) -> None:
        self.push_screen(MainScreen())
    
    # NEW METHODS
    def action_run_project(self):
        """Run the current Steps project."""
        if self.current_project:
            terminal = self.screen.query_one(TerminalPanel)
            terminal.execute_command(f"steps run {self.current_project}")
    
    def action_check_project(self):
        """Validate the current Steps project."""
        if self.current_project:
            terminal = self.screen.query_one(TerminalPanel)
            terminal.execute_command(f"steps check {self.current_project}")
    
    def action_show_diagram(self):
        """Show flow diagram for current project."""
        # Toggle diagram panel or open diagram screen
        pass
    
    def action_new_floor(self):
        """Create a new floor in the current project."""
        self.push_screen(NewFloorDialog())
```

Changes needed:
- Rename class `OnlyCodeApp` → `StepsIDEApp`
- Update TITLE
- Add Steps-specific keybindings (F5, F6, F7)
- Add `current_project` tracking
- Add action methods for run/check/diagram
- Add action methods for new floor/step
- Keep all existing Only Code functionality

### 4. Main Screen

**`onlycode/app/screens/main_screen.py` → `steps_ide/app/screens/main_screen.py`**

Key changes in `compose()`:

```python
# ORIGINAL (Only Code)
def compose(self):
    yield Header()
    start_path = os.getcwd()
    with Vertical(id="workspace"):
        with Horizontal(id="main-container"):
            yield FileBrowser(path=start_path, id="file-browser", classes="hidden")
            with Vertical(id="editor-container"):
                yield TabBar(id="tab-bar")
                yield OnlyCodeEditor(id="editor")
        yield TerminalPanel(id="terminal-panel", classes="hidden")
        yield StatusBar(id="status-bar")
    yield Footer()

# TRANSFORMED (Steps IDE)
def compose(self):
    yield Header()
    with Vertical(id="workspace"):
        with Horizontal(id="main-container"):
            # CHANGED: ProjectBrowser instead of FileBrowser
            yield ProjectBrowser(id="project-browser", classes="hidden")
            with Vertical(id="editor-container"):
                yield TabBar(id="tab-bar")
                # CHANGED: StepsEditor instead of OnlyCodeEditor
                yield StepsEditor(id="editor")
        # NEW: Output panel for interpreter messages
        yield OutputPanel(id="output-panel", classes="hidden")
        # KEPT: Terminal panel
        yield TerminalPanel(id="terminal-panel", classes="hidden")
        yield StatusBar(id="status-bar")
    yield Footer()
```

Handler changes:

```python
# ORIGINAL
def on_file_browser_file_selected(self, event: FileBrowser.FileSelected):
    """Handle file selection from file browser."""
    path = event.path
    # ... open file logic

# TRANSFORMED
def on_project_browser_step_selected(self, event: ProjectBrowser.StepSelected):
    """Handle step selection from project browser."""
    path = event.path
    floor = event.floor
    step = event.step
    # ... open step file, update context

def on_project_browser_floor_selected(self, event: ProjectBrowser.FloorSelected):
    """Handle floor selection - show floor definition."""
    pass

def on_project_browser_building_selected(self, event: ProjectBrowser.BuildingSelected):
    """Handle building selection - show main entry point."""
    pass
```

New methods needed:

```python
def load_project(self, project_path: str):
    """Load a Steps project."""
    self.app.current_project = project_path
    project_browser = self.query_one(ProjectBrowser)
    project_browser.load_project(project_path)
    # Load building file by default
    building_file = Path(project_path) / f"{Path(project_path).name}.building"
    if building_file.exists():
        self._open_file(str(building_file))

def action_toggle_project_browser(self):
    """Toggle the project browser panel."""
    # Same logic as action_toggle_file_browser, different widget
    project_browser = self.query_one(ProjectBrowser)
    # ... toggle logic
```

### 5. Project Browser (NEW - replaces FileBrowser)

**`onlycode/app/widgets/file_browser.py` → `steps_ide/app/widgets/project_browser.py`**

This is a significant rewrite. Start with FileBrowser as template:

```python
# steps_ide/app/widgets/project_browser.py

from textual.widgets import Tree, Static
from textual.containers import Vertical, ScrollableContainer
from textual.widget import Widget
from textual.message import Message
from pathlib import Path

# Import from Steps interpreter
from steps_ide.interpreter.loader import load_project_structure, ProjectStructure


class ProjectBrowser(Widget):
    """Steps project browser - shows building/floor/step structure."""

    DEFAULT_CSS = """
    ProjectBrowser {
        width: 35;
        height: 100%;
        border-right: solid $primary;
        background: $surface;
    }

    ProjectBrowser.hidden {
        display: none;
    }

    ProjectBrowser #browser-header {
        dock: top;
        height: 1;
        background: $primary;
        color: $text;
        padding: 0 1;
    }

    ProjectBrowser #project-tree {
        height: 1fr;
    }
    """

    class StepSelected(Message):
        """Sent when a step file is selected."""
        def __init__(self, path: str, floor: str, step: str):
            super().__init__()
            self.path = path
            self.floor = floor
            self.step = step

    class FloorSelected(Message):
        """Sent when a floor definition is selected."""
        def __init__(self, path: str, floor: str):
            super().__init__()
            self.path = path
            self.floor = floor

    class BuildingSelected(Message):
        """Sent when the building file is selected."""
        def __init__(self, path: str):
            super().__init__()
            self.path = path

    def __init__(self, project_path: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.project_path = project_path
        self.project_structure: ProjectStructure | None = None

    def compose(self):
        yield Static("🏢 Project", id="browser-header")
        with ScrollableContainer(id="tree-container"):
            yield Tree("No project loaded", id="project-tree")

    def load_project(self, path: str):
        """Load a Steps project and build the tree."""
        self.project_path = path
        self.project_structure = load_project_structure(path)
        self._build_tree()

    def _build_tree(self):
        """Build the tree widget from project structure."""
        tree = self.query_one("#project-tree", Tree)
        tree.clear()
        
        if not self.project_structure:
            tree.root.set_label("No project loaded")
            return
        
        # Set root to building name
        project_name = self.project_structure.name
        tree.root.set_label(f"🏢 {project_name}")
        tree.root.data = {"type": "building", "path": self.project_structure.building_path}
        
        # Add building file
        building_node = tree.root.add(
            f"📄 {project_name}.building",
            data={"type": "building_file", "path": self.project_structure.building_path}
        )
        
        # Add floors
        for floor in self.project_structure.floors:
            floor_node = tree.root.add(
                f"📁 {floor.name}",
                data={"type": "floor", "name": floor.name}
            )
            
            # Add steps directly (no .floor node)
            for step in floor.steps:
                floor_node.add(
                    f"📝 {step.name}.step",
                    data={"type": "step", "path": step.path, "floor": floor.name, "step": step.name}
                )
        
        tree.root.expand_all()

    def on_tree_node_selected(self, event: Tree.NodeSelected):
        """Handle tree node selection."""
        data = event.node.data
        if not data:
            return
        
        node_type = data.get("type")
        
        if node_type == "building_file":
            self.post_message(self.BuildingSelected(path=data["path"]))
        elif node_type == "floor_file":
            self.post_message(self.FloorSelected(path=data["path"], floor=data["floor"]))
        elif node_type == "step":
            self.post_message(self.StepSelected(
                path=data["path"],
                floor=data["floor"],
                step=data["step"]
            ))

    # Keep toggle/show/hide methods from FileBrowser
    def toggle(self):
        self.toggle_class("hidden")
        return not self.has_class("hidden")

    def show(self):
        self.remove_class("hidden")

    def hide(self):
        self.add_class("hidden")

    @property
    def is_visible(self) -> bool:
        return not self.has_class("hidden")

    def focus_tree(self):
        tree = self.query_one("#project-tree", Tree)
        tree.focus()
```

### 6. Steps Editor (extends OnlyCodeEditor)

**`onlycode/editor/editor_widget.py` → `steps_ide/editor/steps_editor.py`**

```python
# steps_ide/editor/steps_editor.py

from steps_ide.editor.editor_widget import OnlyCodeEditor  # Keep original
from pathlib import Path

# Steps-specific language mapping
STEPS_EXTENSIONS = {
    ".building": "steps",
    ".step": "steps",
}


class StepsEditor(OnlyCodeEditor):
    """Editor with Steps language awareness."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Will be set when Steps syntax highlighting is registered
        self.language = None

    def detect_language(self, path: str) -> str | None:
        """Detect language - Steps files get Steps highlighting."""
        p = Path(path)
        ext = p.suffix.lower()
        
        # Check for Steps files first
        if ext in STEPS_EXTENSIONS:
            return "steps"
        
        # Fall back to parent implementation
        return super().detect_language(path)

    def validate_steps(self) -> list:
        """Validate current content as Steps code."""
        # Import here to avoid circular dependency
        from steps_ide.interpreter.lexer import Lexer
        from steps_ide.interpreter.parser import Parser
        from steps_ide.interpreter.errors import StepsError
        
        errors = []
        try:
            lexer = Lexer(self.text, Path("current.step"))
            tokens = lexer.tokenize()
            # Parser validation would go here
        except StepsError as e:
            errors.append(e)
        
        return errors
```

Keep `editor_widget.py` as-is (renamed import path) - StepsEditor extends it.

### 7. Terminal Panel

**`onlycode/app/widgets/terminal_panel.py` → `steps_ide/app/widgets/terminal_panel.py`**

Minimal changes - mostly works as-is. Add one helper method:

```python
# Add to TerminalPanel class

def execute_command(self, command: str):
    """Programmatically execute a command (for F5/F6 shortcuts)."""
    output = self.query_one("#terminal-output", Log)
    output.write_line(f"$ {command}")
    
    # Trigger execution
    asyncio.create_task(self._execute_command(command))
```

### 8. Buffer Manager

**`onlycode/editor/buffer_manager.py` → `steps_ide/editor/buffer_manager.py`**

Add project awareness:

```python
# Add to Buffer class
@staticmethod
def _detect_language(suffix: str) -> str:
    """Detect language from file extension."""
    # ADD Steps extensions at the top
    if suffix in [".building", ".step"]:
        return "steps"
    
    # Keep existing language_map...
```

### 9. New Files Needed

#### `steps_ide/app/screens/project_dialogs.py`

```python
"""Dialogs for project operations."""

from textual.screen import ModalScreen
from textual.widgets import Input, Button, Static
from textual.containers import Vertical, Horizontal
from pathlib import Path


class NewProjectDialog(ModalScreen):
    """Dialog to create a new Steps project."""
    
    def compose(self):
        with Vertical(id="dialog"):
            yield Static("Create New Project", id="title")
            yield Input(placeholder="Project name", id="project-name")
            yield Input(placeholder="Location", id="location")
            with Horizontal(id="buttons"):
                yield Button("Create", variant="primary", id="create")
                yield Button("Cancel", id="cancel")
    
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "create":
            name = self.query_one("#project-name", Input).value
            location = self.query_one("#location", Input).value
            self._create_project(name, location)
            self.dismiss(True)
        else:
            self.dismiss(False)
    
    def _create_project(self, name: str, location: str):
        """Create the project folder structure."""
        project_path = Path(location) / name
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Create building file with inline floors
        building_file = project_path / f"{name}.building"
        building_file.write_text(f'''building: {name}

    note: Your program starts here

    floors:
        floor: main
            note: Add your steps here
    
    exit
''')


class NewFloorDialog(ModalScreen):
    """Dialog to create a new floor."""
    # Similar pattern...


class NewStepDialog(ModalScreen):
    """Dialog to create a new step."""
    # Similar pattern...
```

#### `steps_ide/app/widgets/output_panel.py`

```python
"""Output panel for interpreter messages."""

from textual.widgets import Static, Log
from textual.containers import Vertical
from textual.widget import Widget


class OutputPanel(Widget):
    """Panel for displaying interpreter output and errors."""

    DEFAULT_CSS = """
    OutputPanel {
        height: 8;
        dock: bottom;
        border-top: solid $primary;
        background: $surface-darken-1;
    }

    OutputPanel.hidden {
        display: none;
    }

    OutputPanel #output-header {
        dock: top;
        height: 1;
        background: $primary;
        color: $text;
        padding: 0 1;
    }

    OutputPanel #output-log {
        height: 1fr;
    }
    """

    def compose(self):
        yield Static("📋 Output", id="output-header")
        yield Log(id="output-log", highlight=True, auto_scroll=True)

    def write(self, text: str):
        """Write text to output."""
        log = self.query_one("#output-log", Log)
        log.write_line(text)

    def write_error(self, error):
        """Write a Steps error with formatting."""
        log = self.query_one("#output-log", Log)
        log.write_line(f"[red]Error[/red] at line {error.line}: {error.message}")
        if error.hint:
            log.write_line(f"  Hint: {error.hint}")

    def clear(self):
        """Clear the output."""
        log = self.query_one("#output-log", Log)
        log.clear()

    def toggle(self):
        self.toggle_class("hidden")

    def show(self):
        self.remove_class("hidden")

    def hide(self):
        self.add_class("hidden")

    @property
    def is_visible(self) -> bool:
        return not self.has_class("hidden")
```

## Implementation Order

### Phase 1: Basic Transformation (Copy & Rename)

1. Copy Only Code to new `steps_ide/` folder
2. Rename all `onlycode` → `steps_ide` in imports
3. Rename `OnlyCodeApp` → `StepsIDEApp`
4. Rename `OnlyCodeEditor` → keep as base, create `StepsEditor` subclass
5. Verify it still runs

### Phase 2: Project Browser

1. Create `ProjectBrowser` widget (based on `FileBrowser`)
2. Replace `FileBrowser` with `ProjectBrowser` in `main_screen.py`
3. Update message handlers
4. Add `load_project()` method to main screen
5. Test with example price_calculator project

### Phase 3: Steps Editor

1. Create `StepsEditor` class extending `OnlyCodeEditor`
2. Add Steps extension detection
3. Update buffer manager for Steps extensions
4. Replace editor in main screen

### Phase 4: Interpreter Integration

1. Copy interpreter modules into `steps_ide/interpreter/`
2. Add `load_project_structure()` for project browser
3. Add validation calls on save
4. Wire up F5 (run) and F6 (check) commands

### Phase 5: Project Operations

1. Create project dialog screens
2. Add New Project command
3. Add New Floor command
4. Add New Step command
5. Update project browser after operations

### Phase 6: Output Panel & Polish

1. Add output panel for errors
2. Show validation errors in output
3. Add flow diagram panel (Phase 2 feature)

## Testing Strategy

After each phase:

1. Verify the IDE launches
2. Verify existing Only Code features still work
3. Test new Steps-specific features
4. Test with price_calculator example project

## Files to Keep Unchanged

These Only Code files work as-is:

- `tab_bar.py` - Tab management
- `status_bar.py` - Status display
- `session.py` - Session persistence
- `settings.py` - Settings management
- `loader.py` (config) - Config file loading
- `terminal_panel.py` - Minor additions only
