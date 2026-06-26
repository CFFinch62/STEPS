"""
Settings Manager for Steps IDE
Handles loading and saving configuration from JSON files
"""

import json
import os
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, asdict, field


def get_config_dir() -> Path:
    """Get the configuration directory for Steps IDE"""
    if os.name == 'nt':  # Windows
        config_dir = Path(os.environ.get('APPDATA', '')) / 'Steps-IDE'
    else:  # Linux/macOS
        config_dir = Path.home() / '.config' / 'steps-ide'
    
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


@dataclass
class EditorSettings:
    """Editor-specific settings"""
    font_family: str = "JetBrains Mono"
    font_size: int = 12
    tab_width: int = 4
    use_spaces: bool = True
    show_line_numbers: bool = True
    word_wrap: bool = False
    auto_indent: bool = True
    highlight_current_line: bool = True
    show_whitespace: bool = False
    bracket_matching: bool = True
    autocomplete_mode: str = "automatic"  # "automatic" or "manual"
    autocomplete_delay_ms: int = 300      # Delay before showing suggestions


@dataclass
class FileBrowserSettings:
    """File browser settings"""
    show_hidden_files: bool = False
    show_file_icons: bool = True
    bookmarks: list = field(default_factory=list)
    last_directory: str = ""


@dataclass
class TerminalSettings:
    """Terminal settings"""
    shell: str = ""  # Empty means use system default
    font_family: str = "JetBrains Mono"
    font_size: int = 14
    background_color: str = "#1e1e1e"
    foreground_color: str = "#d4d4d4"
    position: str = "bottom"  # "bottom" or "right"
    visible: bool = True


@dataclass
class WindowSettings:
    """Window layout settings"""
    width: int = 1400
    height: int = 900
    maximized: bool = False
    file_browser_width: int = 190
    file_browser_visible: bool = True
    terminal_height: int = 200
    terminal_width: int = 400
    toolbar_visible: bool = True


@dataclass
class ThemeSettings:
    """Theme settings"""
    current_theme: str = "dark"


@dataclass
class StepsSettings:
    """Steps interpreter settings"""
    interpreter_path: str = ""  # Empty = use built-in interpreter


@dataclass
class IDESettings:
    """Main IDE settings container"""
    editor: EditorSettings = field(default_factory=EditorSettings)
    file_browser: FileBrowserSettings = field(default_factory=FileBrowserSettings)
    terminal: TerminalSettings = field(default_factory=TerminalSettings)
    window: WindowSettings = field(default_factory=WindowSettings)
    theme: ThemeSettings = field(default_factory=ThemeSettings)
    steps: StepsSettings = field(default_factory=StepsSettings)
    recent_files: list = field(default_factory=list)
    recent_projects: list = field(default_factory=list)


class SettingsManager:
    """Manages loading and saving of IDE settings"""
    
    def __init__(self):
        self.config_dir = get_config_dir()
        self.settings_file = self.config_dir / "settings.json"
        self.keybindings_file = self.config_dir / "keybindings.json"
        self.settings = IDESettings()
        self.keybindings = self._get_default_keybindings()
        
        self.load()
    
    def _get_default_keybindings(self) -> dict:
        """Get default keybindings"""
        return {
            "file": {
                "new_file": "Ctrl+N",
                "open_file": "Ctrl+O",
                "save_file": "Ctrl+S",
                "save_as": "Ctrl+Shift+S",
                "close_tab": "Ctrl+W",
                "close_all": "Ctrl+Shift+W",
            },
            "edit": {
                "undo": "Ctrl+Z",
                "redo": "Ctrl+Shift+Z",
                "cut": "Ctrl+X",
                "copy": "Ctrl+C",
                "paste": "Ctrl+V",
                "select_all": "Ctrl+A",
                "find": "Ctrl+F",
                "replace": "Ctrl+H",
                "goto_line": "Ctrl+G",
            },
            "view": {
                "toggle_file_browser": "Ctrl+B",
                "toggle_terminal": "Ctrl+`",
                "zoom_in": "Ctrl+=",
                "zoom_out": "Ctrl+-",
                "reset_zoom": "Ctrl+0",
            },
            "run": {
                "run_project": "F5",
                "check_syntax": "F6",
            }
        }
    
    def load(self):
        """Load settings from JSON files"""
        # Load main settings
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._apply_settings(data)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load settings: {e}")
        
        # Load keybindings
        if self.keybindings_file.exists():
            try:
                with open(self.keybindings_file, 'r', encoding='utf-8') as f:
                    self.keybindings = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load keybindings: {e}")
    
    def _apply_settings(self, data: dict):
        """Apply loaded settings data to settings objects"""
        if 'editor' in data:
            for key, value in data['editor'].items():
                if hasattr(self.settings.editor, key):
                    setattr(self.settings.editor, key, value)
        
        if 'file_browser' in data:
            for key, value in data['file_browser'].items():
                if hasattr(self.settings.file_browser, key):
                    setattr(self.settings.file_browser, key, value)
        
        if 'terminal' in data:
            for key, value in data['terminal'].items():
                if hasattr(self.settings.terminal, key):
                    setattr(self.settings.terminal, key, value)
        
        if 'window' in data:
            for key, value in data['window'].items():
                if hasattr(self.settings.window, key):
                    setattr(self.settings.window, key, value)
        
        if 'theme' in data:
            for key, value in data['theme'].items():
                if hasattr(self.settings.theme, key):
                    setattr(self.settings.theme, key, value)
        
        if 'steps' in data:
            for key, value in data['steps'].items():
                if hasattr(self.settings.steps, key):
                    setattr(self.settings.steps, key, value)
        
        if 'recent_files' in data:
            self.settings.recent_files = data['recent_files']
        
        if 'recent_projects' in data:
            self.settings.recent_projects = data['recent_projects']
    
    def save(self):
        """Save all settings to JSON files"""
        # Save main settings
        settings_data = {
            'editor': asdict(self.settings.editor),
            'file_browser': asdict(self.settings.file_browser),
            'terminal': asdict(self.settings.terminal),
            'window': asdict(self.settings.window),
            'theme': asdict(self.settings.theme),
            'steps': asdict(self.settings.steps),
            'recent_files': self.settings.recent_files,
            'recent_projects': self.settings.recent_projects,
        }
        
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=2)
        except IOError as e:
            print(f"Error saving settings: {e}")
        
        # Save keybindings
        try:
            with open(self.keybindings_file, 'w', encoding='utf-8') as f:
                json.dump(self.keybindings, f, indent=2)
        except IOError as e:
            print(f"Error saving keybindings: {e}")
    
    def get_keybinding(self, category: str, action: str) -> str:
        """Get a specific keybinding"""
        return self.keybindings.get(category, {}).get(action, "")
    
    def set_keybinding(self, category: str, action: str, shortcut: str):
        """Set a specific keybinding"""
        if category not in self.keybindings:
            self.keybindings[category] = {}
        self.keybindings[category][action] = shortcut
    
    def add_recent_file(self, filepath: str):
        """Add a file to recent files list"""
        if filepath in self.settings.recent_files:
            self.settings.recent_files.remove(filepath)
        self.settings.recent_files.insert(0, filepath)
        # Keep only last 20 files
        self.settings.recent_files = self.settings.recent_files[:20]
        self.save()
    
    def add_bookmark(self, path: str):
        """Add a folder bookmark"""
        if path not in self.settings.file_browser.bookmarks:
            self.settings.file_browser.bookmarks.append(path)
            self.save()
    
    def remove_bookmark(self, path: str):
        """Remove a folder bookmark"""
        if path in self.settings.file_browser.bookmarks:
            self.settings.file_browser.bookmarks.remove(path)
            self.save()
