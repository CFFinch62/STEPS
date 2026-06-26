"""
Main Window for Steps IDE
The primary application window integrating all components
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QFrame, QLabel, QToolBar, QStatusBar, QMenuBar, QMenu,
    QFileDialog, QInputDialog, QMessageBox, QDockWidget,
    QDialog, QFormLayout, QLineEdit, QComboBox, QSpinBox,
    QCheckBox, QPushButton, QDialogButtonBox, QTabWidget,
    QApplication, QTextBrowser
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import (
    QAction, QKeySequence, QIcon, QCloseEvent, QFont, QFontDatabase, QTextCursor
)

from steps_ide.app.settings import SettingsManager
from steps_ide.app.themes import ThemeManager, Theme
from steps_ide.app.file_browser import FileBrowserWidget
from steps_ide.app.editor import EditorTabs
from steps_ide.app.terminal import TerminalWidget


class SettingsDialog(QDialog):
    """Settings dialog for configuring the IDE"""
    
    settings_applied = pyqtSignal()  # Emitted when settings are applied
    
    def __init__(self, settings: SettingsManager, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.theme_manager = theme_manager
        
        self.setWindowTitle("Settings")
        self.setMinimumSize(500, 400)
        
        self._setup_ui()
    
    def _get_monospace_fonts(self):
        """Get a list of available monospace fonts"""
        monospace_fonts = []
        
        # Common monospace fonts to always check/include
        common = ["Consolas", "Courier New", "Monaco", "Menlo", "Ubuntu Mono", "DejaVu Sans Mono", "Monospace", "Hack", "Fira Code", "JetBrains Mono"]
        
        try:
            # QFontDatabase methods are static in PyQt6
            families = QFontDatabase.families()
            
            for family in families:
                is_fixed = False
                try:
                    is_fixed = QFontDatabase.isFixedPitch(family)
                except:
                    pass
                    
                if is_fixed or family in common or "Mono" in family or "Code" in family or "Term" in family:
                    if family not in monospace_fonts:
                        monospace_fonts.append(family)
        except Exception:
            # Fallback if QFontDatabase fails completely
            pass
            
        # Ensure we have at least some defaults if detection failed or returned nothing
        if not monospace_fonts:
            monospace_fonts = ["Monospace", "Courier New"]
            
        monospace_fonts.sort()
        return monospace_fonts

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Tab widget for different settings categories
        tabs = QTabWidget()
        
        # Editor settings
        editor_tab = QWidget()
        editor_layout = QFormLayout(editor_tab)
        
        # Get available fonts
        fonts = self._get_monospace_fonts()
        
        self.font_family = QComboBox()
        self.font_family.setEditable(False)  # Standard non-editable dropdown
        self.font_family.addItems(fonts)
        
        # Set current font
        current_font = self.settings.settings.editor.font_family
        index = self.font_family.findText(current_font)
        if index >= 0:
            self.font_family.setCurrentIndex(index)
        else:
            # If current font not in detected list, add it and select it
            self.font_family.addItem(current_font)
            self.font_family.setCurrentIndex(self.font_family.count() - 1)
            
        editor_layout.addRow("Font Family:", self.font_family)
        
        self.font_size = QSpinBox()
        self.font_size.setRange(6, 48)
        self.font_size.setValue(self.settings.settings.editor.font_size)
        editor_layout.addRow("Font Size:", self.font_size)
        
        self.tab_width = QSpinBox()
        self.tab_width.setRange(1, 8)
        self.tab_width.setValue(self.settings.settings.editor.tab_width)
        editor_layout.addRow("Tab Width:", self.tab_width)
        
        self.use_spaces = QCheckBox("Use spaces instead of tabs")
        self.use_spaces.setChecked(self.settings.settings.editor.use_spaces)
        editor_layout.addRow("", self.use_spaces)
        
        self.show_line_numbers = QCheckBox("Show line numbers")
        self.show_line_numbers.setChecked(self.settings.settings.editor.show_line_numbers)
        editor_layout.addRow("", self.show_line_numbers)
        
        self.word_wrap = QCheckBox("Word wrap")
        self.word_wrap.setChecked(self.settings.settings.editor.word_wrap)
        editor_layout.addRow("", self.word_wrap)
        
        self.highlight_line = QCheckBox("Highlight current line")
        self.highlight_line.setChecked(self.settings.settings.editor.highlight_current_line)
        editor_layout.addRow("", self.highlight_line)
        
        self.bracket_matching = QCheckBox("Auto-close brackets")
        self.bracket_matching.setChecked(self.settings.settings.editor.bracket_matching)
        editor_layout.addRow("", self.bracket_matching)
        
        # Autocomplete settings
        editor_layout.addRow(QLabel(""))  # Spacer
        editor_layout.addRow(QLabel("Code Completion"))
        
        self.autocomplete_mode = QComboBox()
        self.autocomplete_mode.addItems(["Automatic", "Manual (Ctrl+Space)"])
        if self.settings.settings.editor.autocomplete_mode == "manual":
            self.autocomplete_mode.setCurrentIndex(1)
        editor_layout.addRow("Autocomplete Mode:", self.autocomplete_mode)
        
        self.autocomplete_delay = QSpinBox()
        self.autocomplete_delay.setRange(100, 1000)
        self.autocomplete_delay.setSingleStep(50)
        self.autocomplete_delay.setSuffix(" ms")
        self.autocomplete_delay.setValue(self.settings.settings.editor.autocomplete_delay_ms)
        editor_layout.addRow("Suggestion Delay:", self.autocomplete_delay)
        
        tabs.addTab(editor_tab, "Editor")
        
        # Theme settings
        theme_tab = QWidget()
        theme_layout = QFormLayout(theme_tab)
        
        self.theme_combo = QComboBox()
        themes = self.theme_manager.get_available_themes()
        self.theme_combo.addItems([t.title() for t in themes])
        current_theme = self.settings.settings.theme.current_theme
        for i, t in enumerate(themes):
            if t == current_theme:
                self.theme_combo.setCurrentIndex(i)
                break
        theme_layout.addRow("Theme:", self.theme_combo)
        
        tabs.addTab(theme_tab, "Appearance")
        
        # Terminal settings
        terminal_tab = QWidget()
        terminal_layout = QFormLayout(terminal_tab)
        
        self.terminal_font = QComboBox()
        self.terminal_font.setEditable(False)
        self.terminal_font.addItems(fonts)
        
        current_term_font = self.settings.settings.terminal.font_family
        term_index = self.terminal_font.findText(current_term_font)
        if term_index >= 0:
            self.terminal_font.setCurrentIndex(term_index)
        else:
            self.terminal_font.addItem(current_term_font)
            self.terminal_font.setCurrentIndex(self.terminal_font.count() - 1)
            
        terminal_layout.addRow("Font Family:", self.terminal_font)
        
        self.terminal_font_size = QSpinBox()
        self.terminal_font_size.setRange(6, 48)
        self.terminal_font_size.setValue(self.settings.settings.terminal.font_size)
        terminal_layout.addRow("Font Size:", self.terminal_font_size)
        
        self.terminal_position = QComboBox()
        self.terminal_position.addItems(["Bottom", "Right"])
        if self.settings.settings.terminal.position == "right":
            self.terminal_position.setCurrentIndex(1)
        terminal_layout.addRow("Position:", self.terminal_position)
        
        tabs.addTab(terminal_tab, "Terminal")
        
        layout.addWidget(tabs)
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply
        )
        buttons.accepted.connect(self._save_and_close)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self._apply)
        
        layout.addWidget(buttons)
    
    def _apply(self):
        """Apply settings without closing"""
        # Editor settings
        self.settings.settings.editor.font_family = self.font_family.currentText()
        self.settings.settings.editor.font_size = self.font_size.value()
        self.settings.settings.editor.tab_width = self.tab_width.value()
        self.settings.settings.editor.use_spaces = self.use_spaces.isChecked()
        self.settings.settings.editor.show_line_numbers = self.show_line_numbers.isChecked()
        self.settings.settings.editor.word_wrap = self.word_wrap.isChecked()
        self.settings.settings.editor.highlight_current_line = self.highlight_line.isChecked()
        self.settings.settings.editor.bracket_matching = self.bracket_matching.isChecked()
        
        # Autocomplete settings
        mode = "manual" if self.autocomplete_mode.currentIndex() == 1 else "automatic"
        self.settings.settings.editor.autocomplete_mode = mode
        self.settings.settings.editor.autocomplete_delay_ms = self.autocomplete_delay.value()
        
        # Theme
        themes = self.theme_manager.get_available_themes()
        theme_name = themes[self.theme_combo.currentIndex()]
        self.theme_manager.set_theme(theme_name)
        
        # Terminal settings
        self.settings.settings.terminal.font_family = self.terminal_font.currentText()
        self.settings.settings.terminal.font_size = self.terminal_font_size.value()
        self.settings.settings.terminal.position = self.terminal_position.currentText().lower()
        
        self.settings.save()
        
        # Notify parent to refresh UI
        self.settings_applied.emit()
    
    def _save_and_close(self):
        """Save settings and close dialog"""
        self._apply()
        self.accept()


class GotoLineDialog(QDialog):
    """Dialog for going to a specific line"""
    
    def __init__(self, max_line: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Go to Line")
        self.setFixedSize(250, 100)
        
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        self.line_input = QSpinBox()
        self.line_input.setRange(1, max_line)
        self.line_input.setValue(1)
        form.addRow("Line number:", self.line_input)
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_line(self) -> int:
        return self.line_input.value()


class QuickReferenceDialog(QDialog):
    """Dialog for displaying the language quick reference"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Steps Language Quick Reference")
        self.resize(900, 700)
        
        layout = QVBoxLayout(self)
        
        # Text browser for markdown display
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(False)
        
        # Set monospace font for code blocks
        font = QFont("Monospace", 10)
        font.setStyleHint(QFont.StyleHint.TypeWriter)
        self.browser.setFont(font)
        
        # Load the quick reference content
        self._load_content()
        
        layout.addWidget(self.browser)
        
        # Close button
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.close)
        layout.addWidget(buttons)
    
    def _load_content(self):
        """Load the quick reference markdown file"""
        try:
            # Resolve base path for both frozen (.app bundle) and development environments.
            # When frozen by PyInstaller, __file__-relative paths don't work because the
            # directory structure inside the bundle is different.  All --add-data files land
            # directly under sys._MEIPASS, so we must use that as the base.
            if getattr(sys, 'frozen', False):
                base_path = Path(sys._MEIPASS)   # type: ignore[attr-defined]
            else:
                base_path = Path(__file__).parent.parent.parent.parent

            quick_ref_path = base_path / "docs" / "QUICK-REFERENCE.md"

            if quick_ref_path.exists():
                content = quick_ref_path.read_text(encoding='utf-8')
                # Convert markdown to HTML for better rendering
                html_content = self._markdown_to_html(content)
                self.browser.setHtml(html_content)
            else:
                self.browser.setPlainText(f"Quick reference file not found at:\n{quick_ref_path}")
        except Exception as e:
            self.browser.setPlainText(f"Error loading quick reference: {e}")
    
    def _markdown_to_html(self, markdown_text: str) -> str:
        """Convert markdown to basic HTML for display"""
        html = ['<html><head><style>']
        # Explicitly set text color to black and background to white to ensure contrast
        # regardless of the system/app theme
        html.append('body { font-family: sans-serif; margin: 20px; color: #333333; background-color: #ffffff; }')
        html.append('h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }')
        html.append('h2 { color: #34495e; margin-top: 30px; border-bottom: 1px solid #bdc3c7; padding-bottom: 5px; }')
        html.append('h3 { color: #555; margin-top: 20px; }')
        html.append('code { background-color: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: monospace; }')
        html.append('pre { background-color: #f8f8f8; padding: 15px; border-radius: 5px; border-left: 4px solid #3498db; overflow-x: auto; }')
        html.append('pre code { background-color: transparent; padding: 0; }')
        html.append('ul, ol { line-height: 1.6; }')
        html.append('</style></head><body>')
        
        lines = markdown_text.split('\n')
        in_code_block = False
        code_block_lines = []
        
        for line in lines:
            # Handle code blocks
            if line.startswith('```'):
                if in_code_block:
                    # End code block
                    html.append('<pre><code>')
                    html.append('\n'.join(code_block_lines))
                    html.append('</code></pre>')
                    code_block_lines = []
                    in_code_block = False
                else:
                    # Start code block
                    in_code_block = True
                continue
            
            if in_code_block:
                code_block_lines.append(line.replace('<', '&lt;').replace('>', '&gt;'))
                continue
            
            # Handle headings
            if line.startswith('# '):
                html.append(f'<h1>{line[2:]}</h1>')
            elif line.startswith('## '):
                html.append(f'<h2>{line[3:]}</h2>')
            elif line.startswith('### '):
                html.append(f'<h3>{line[4:]}</h3>')
            # Handle inline code
            elif '`' in line:
                # Simple inline code replacement
                parts = line.split('`')
                result = []
                for i, part in enumerate(parts):
                    if i % 2 == 0:
                        result.append(part)
                    else:
                        result.append(f'<code>{part}</code>')
                html.append(''.join(result) + '<br/>')
            elif line.strip():
                html.append(line + '<br/>')
            else:
                html.append('<br/>')
        
        html.append('</body></html>')
        return '\n'.join(html)


class StepsIDEMainWindow(QMainWindow):
    """Main IDE window"""
    
    def __init__(self, settings: SettingsManager, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.settings = settings
        self.theme_manager = theme_manager
        
        self.debug_panel = None
        self._debug_thread = None
        self.debug_dock = None
        
        self.setWindowTitle("Steps IDE")
        self._restore_window_state()
        
        self._setup_ui()
        self._setup_menus()
        self._setup_toolbar()
        self._setup_statusbar()
        self._setup_shortcuts()
        self._setup_connections()
    
    def _restore_window_state(self):
        """Restore window size and state"""
        ws = self.settings.settings.window
        self.resize(ws.width, ws.height)
        if ws.maximized:
            self.showMaximized()

    def _setup_ui(self):
        """Set up the main UI"""
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Main horizontal splitter
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # File browser - added directly to splitter
        self.file_browser = FileBrowserWidget(self.settings)
        self.file_browser.setMinimumWidth(150)
        self.file_browser.setMaximumWidth(500)
        
        self.main_splitter.addWidget(self.file_browser)
        
        # Editor and terminal area
        self.editor_terminal_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Editor tabs
        self.editor_tabs = EditorTabs(self.settings, self.theme_manager)
        self.editor_terminal_splitter.addWidget(self.editor_tabs)
        
        # Terminal
        self.terminal = TerminalWidget(
            self.settings, 
            self.theme_manager.get_current_theme()
        )
        self.terminal.setMinimumHeight(100)
        
        # Terminal container
        self.terminal_container = QFrame()
        terminal_layout = QVBoxLayout(self.terminal_container)
        terminal_layout.setContentsMargins(0, 0, 0, 0)
        terminal_layout.addWidget(self.terminal)
        
        self.editor_terminal_splitter.addWidget(self.terminal_container)
        
        # Set initial splitter sizes
        self.editor_terminal_splitter.setSizes([600, 200])
        
        self.main_splitter.addWidget(self.editor_terminal_splitter)

        # File browser keeps its saved width when the window is resized or
        # maximised; the editor panel absorbs all extra space.
        self.main_splitter.setStretchFactor(0, 0)
        self.main_splitter.setStretchFactor(1, 1)

        # Apply visibility settings
        ws = self.settings.settings.window
        if not ws.file_browser_visible:
            self.file_browser.hide()
        if not self.settings.settings.terminal.visible:
            self.terminal_container.hide()

        main_layout.addWidget(self.main_splitter)

        # Handle terminal position (bottom vs right)
        self._update_terminal_position()

        # Restore the saved file-browser width.  This is done AFTER
        # _update_terminal_position() because that method re-parents the
        # terminal container, which would otherwise cause Qt to recalculate
        # and discard any sizes we set earlier.  The setStretchFactor(0, 0)
        # call above ensures this width is preserved when the window is later
        # resized or maximised.
        self.main_splitter.setSizes([ws.file_browser_width, 1000])
        
        # Setup Debug Dock
        from steps_ide.app.debug_panel import DebugPanel
        self.debug_panel = DebugPanel()
        self.debug_dock = QDockWidget("Debug", self)
        self.debug_dock.setWidget(self.debug_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.debug_dock)
        self.debug_dock.hide()
        
        # Connect debug panel signals
        self.debug_panel.step_into_clicked.connect(self._step_into)
        self.debug_panel.step_over_clicked.connect(self._step_over)
        self.debug_panel.step_out_clicked.connect(self._step_out)
        self.debug_panel.continue_clicked.connect(self._continue_debug)
        self.debug_panel.stop_clicked.connect(self._stop_debug)
        self.debug_panel.frame_selected.connect(self._on_frame_selected)
    
    def _update_terminal_position(self):
        """Update terminal position based on settings"""
        pos = self.settings.settings.terminal.position
        
        # Remove terminal from current parent
        self.terminal_container.setParent(None)
        
        if pos == "right":
            # Add terminal to main horizontal splitter
            self.editor_terminal_splitter.setOrientation(Qt.Orientation.Horizontal)
        else:
            # Keep terminal below editor (vertical)
            self.editor_terminal_splitter.setOrientation(Qt.Orientation.Vertical)
        
        self.editor_terminal_splitter.addWidget(self.terminal_container)
        
        # Tell terminal to adjust its layout for the position
        self.terminal.set_position(pos)
        
        # Update sizes
        if pos == "right":
            self.editor_terminal_splitter.setSizes([
                800, 
                self.settings.settings.window.terminal_width
            ])
        else:
            self.editor_terminal_splitter.setSizes([
                600, 
                self.settings.settings.window.terminal_height
            ])
    
    def _setup_menus(self):
        """Set up the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = file_menu.addAction("&New File")
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._new_file)
        
        new_project_action = file_menu.addAction("New &Project...")
        new_project_action.setShortcut("Ctrl+Shift+N")
        new_project_action.triggered.connect(self._new_project)

        new_folder_action = file_menu.addAction("New Fo&lder in Browser...")
        new_folder_action.triggered.connect(self._new_folder_in_browser)

        file_menu.addSeparator()
        
        open_action = file_menu.addAction("&Open...")
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._open_file)
        
        open_folder_action = file_menu.addAction("Open &Folder...")
        open_folder_action.setShortcut("Ctrl+Shift+O")
        open_folder_action.triggered.connect(self._open_folder)
        
        file_menu.addSeparator()
        
        save_action = file_menu.addAction("&Save")
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._save_file)
        
        save_as_action = file_menu.addAction("Save &As...")
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self._save_file_as)
        
        save_all_action = file_menu.addAction("Save A&ll")
        save_all_action.setShortcut("Ctrl+Shift+S")
        save_all_action.triggered.connect(self.editor_tabs.save_all)
        
        file_menu.addSeparator()
        
        close_action = file_menu.addAction("&Close")
        close_action.setShortcut(QKeySequence.StandardKey.Close)
        close_action.triggered.connect(self._close_current_tab)
        
        close_all_action = file_menu.addAction("Close All")
        close_all_action.setShortcut("Ctrl+Shift+W")
        close_all_action.triggered.connect(self.editor_tabs.close_all_tabs)
        
        file_menu.addSeparator()
        
        # Recent files submenu
        self.recent_menu = file_menu.addMenu("Recent Files")
        self._update_recent_files_menu()
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("E&xit")
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        undo_action = edit_menu.addAction("&Undo")
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self._undo)
        
        redo_action = edit_menu.addAction("&Redo")
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self._redo)
        
        edit_menu.addSeparator()
        
        cut_action = edit_menu.addAction("Cu&t")
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(self._cut)
        
        copy_action = edit_menu.addAction("&Copy")
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self._copy)
        
        paste_action = edit_menu.addAction("&Paste")
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self._paste)
        
        edit_menu.addSeparator()
        
        select_all_action = edit_menu.addAction("Select &All")
        select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all_action.triggered.connect(self._select_all)

        edit_menu.addSeparator()

        indent_action = edit_menu.addAction("&Indent")
        indent_action.setShortcut("Ctrl+]")
        indent_action.triggered.connect(self._indent_selection)

        dedent_action = edit_menu.addAction("&Dedent")
        dedent_action.setShortcut("Ctrl+[")
        dedent_action.triggered.connect(self._dedent_selection)

        edit_menu.addSeparator()

        find_action = edit_menu.addAction("&Find...")
        find_action.setShortcut(QKeySequence.StandardKey.Find)
        find_action.triggered.connect(self._find)
        
        replace_action = edit_menu.addAction("&Replace...")
        replace_action.setShortcut("Ctrl+H")
        replace_action.triggered.connect(self._replace)
        
        goto_action = edit_menu.addAction("&Go to Line...")
        goto_action.setShortcut("Ctrl+G")
        goto_action.triggered.connect(self._goto_line)
        
        edit_menu.addSeparator()
        
        settings_action = edit_menu.addAction("&Settings...")
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self._show_settings)
        
        # View menu
        view_menu = menubar.addMenu("&View")

        self.toggle_toolbar_action = view_menu.addAction("Toggle &Toolbar")
        self.toggle_toolbar_action.setShortcut("Ctrl+Shift+B")
        self.toggle_toolbar_action.setCheckable(True)
        self.toggle_toolbar_action.setChecked(self.settings.settings.window.toolbar_visible)
        self.toggle_toolbar_action.triggered.connect(self._toggle_toolbar)

        view_menu.addSeparator()

        self.toggle_browser_action = view_menu.addAction("Toggle &File Browser")
        self.toggle_browser_action.setShortcut("Ctrl+B")
        self.toggle_browser_action.setCheckable(True)
        self.toggle_browser_action.setChecked(self.settings.settings.window.file_browser_visible)
        self.toggle_browser_action.triggered.connect(self._toggle_file_browser)
        
        self.toggle_terminal_action = view_menu.addAction("Toggle &Terminal")
        self.toggle_terminal_action.setShortcut("Ctrl+`")
        self.toggle_terminal_action.setCheckable(True)
        self.toggle_terminal_action.setChecked(self.settings.settings.terminal.visible)
        self.toggle_terminal_action.triggered.connect(self._toggle_terminal)
        
        open_external_term_action = view_menu.addAction("Open &External Terminal")
        open_external_term_action.setShortcut("Ctrl+Shift+T")
        open_external_term_action.triggered.connect(self._open_external_terminal)
        
        view_menu.addSeparator()
        
        terminal_position_menu = view_menu.addMenu("Terminal Position")
        
        terminal_bottom = terminal_position_menu.addAction("Bottom")
        terminal_bottom.setCheckable(True)
        terminal_bottom.setChecked(self.settings.settings.terminal.position == "bottom")
        terminal_bottom.triggered.connect(lambda: self._set_terminal_position("bottom"))
        
        terminal_right = terminal_position_menu.addAction("Right")
        terminal_right.setCheckable(True)
        terminal_right.setChecked(self.settings.settings.terminal.position == "right")
        terminal_right.triggered.connect(lambda: self._set_terminal_position("right"))
        
        self.terminal_position_actions = [terminal_bottom, terminal_right]
        
        view_menu.addSeparator()
        
        zoom_in_action = view_menu.addAction("Zoom &In")
        zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        zoom_in_action.triggered.connect(self._zoom_in)
        
        zoom_out_action = view_menu.addAction("Zoom &Out")
        zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        zoom_out_action.triggered.connect(self._zoom_out)
        
        zoom_reset_action = view_menu.addAction("Reset Zoom")
        zoom_reset_action.setShortcut("Ctrl+0")
        zoom_reset_action.triggered.connect(self._zoom_reset)
        
        view_menu.addSeparator()

        # Project diagram
        diagram_action = view_menu.addAction("Show Project &Diagram")
        diagram_action.setShortcut("Ctrl+D")
        diagram_action.triggered.connect(self._show_diagram)

        view_menu.addSeparator()

        # Theme submenu
        theme_menu = view_menu.addMenu("&Theme")
        self.theme_actions = []
        for theme_name in self.theme_manager.get_available_themes():
            action = theme_menu.addAction(theme_name.title())
            action.setCheckable(True)
            action.setChecked(theme_name == self.settings.settings.theme.current_theme)
            action.triggered.connect(lambda checked, t=theme_name: self._set_theme(t))
            self.theme_actions.append((theme_name, action))
        
        # Debug menu
        debug_menu = menubar.addMenu("&Debug")
        
        debug_menu.addAction("Start Debugging", "F5", self._start_debug)
        debug_menu.addSeparator()
        debug_menu.addAction("Step Into", "F11", self._step_into)
        debug_menu.addAction("Step Over", "F10", self._step_over)
        debug_menu.addAction("Step Out", "Shift+F11", self._step_out)
        debug_menu.addSeparator()
        debug_menu.addAction("Toggle Breakpoint", "F9", self._toggle_breakpoint)
        debug_menu.addSeparator()
        debug_menu.addAction("Stop Debugging", "Shift+F5", self._stop_debug)
        debug_menu.addSeparator()
        self.toggle_debug_panel_action = debug_menu.addAction("Toggle Debug Panel", "Ctrl+Shift+D", self._toggle_debug_panel)
        self.toggle_debug_panel_action.setCheckable(True)
        self.toggle_debug_panel_action.setChecked(False)  # Hidden by default
        
        # Run menu
        run_menu = menubar.addMenu("&Run")
        
        check_file_action = run_menu.addAction("Check &File")
        check_file_action.setShortcut("Shift+F6")
        check_file_action.triggered.connect(self._check_file_syntax)
        
        check_project_action = run_menu.addAction("Check &Project")
        check_project_action.setShortcut("F6")
        check_project_action.triggered.connect(self._check_project_syntax)
        
        run_menu.addSeparator()
        
        run_project_action = run_menu.addAction("&Run Steps Project")
        run_project_action.setShortcut("Ctrl+F5")  # F5 is for debugging
        run_project_action.triggered.connect(self._run_current_project)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        quick_ref_action = help_menu.addAction("Language &Quick Reference")
        quick_ref_action.setShortcut("F1")
        quick_ref_action.triggered.connect(self._show_quick_reference)
        
        help_menu.addSeparator()
        
        about_action = help_menu.addAction("&About Steps IDE")
        about_action.triggered.connect(self._show_about)
    
    def _setup_toolbar(self):
        """Set up the toolbar"""
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(self.toolbar)

        # Set font with emoji support
        toolbar_font = QFont()
        toolbar_font.setFamilies(["Sans", "Noto Color Emoji", "Segoe UI Emoji", "Apple Color Emoji"])
        self.toolbar.setFont(toolbar_font)

        # New file
        new_btn = self.toolbar.addAction("📄 New")
        new_btn.setToolTip("New File (Ctrl+N)")
        new_btn.triggered.connect(self._new_file)

        # Open file
        open_btn = self.toolbar.addAction("📂 Open")
        open_btn.setToolTip("Open File (Ctrl+O)")
        open_btn.triggered.connect(self._open_file)

        # Save
        save_btn = self.toolbar.addAction("💾 Save")
        save_btn.setToolTip("Save (Ctrl+S)")
        save_btn.triggered.connect(self._save_file)

        self.toolbar.addSeparator()

        # Run
        run_btn = self.toolbar.addAction("▶️ Run")
        run_btn.setToolTip("Run Steps Project (Ctrl+F5)")
        run_btn.triggered.connect(self._run_current_project)

        self.toolbar.addSeparator()

        # Toggle browser
        browser_btn = self.toolbar.addAction("📁 Browser")
        browser_btn.setToolTip("Toggle File Browser (Ctrl+B)")
        browser_btn.setCheckable(True)
        browser_btn.setChecked(self.settings.settings.window.file_browser_visible)
        browser_btn.triggered.connect(self._toggle_file_browser)
        self.browser_toolbar_btn = browser_btn

        # Toggle terminal
        terminal_btn = self.toolbar.addAction("💻 Terminal")
        terminal_btn.setToolTip("Toggle Terminal (Ctrl+`)")
        terminal_btn.setCheckable(True)
        terminal_btn.setChecked(self.settings.settings.terminal.visible)
        terminal_btn.triggered.connect(self._toggle_terminal)
        self.terminal_toolbar_btn = terminal_btn

        # External Terminal
        ext_term_btn = self.toolbar.addAction("📟 Ext. Term")
        ext_term_btn.setToolTip("Open External Terminal (Ctrl+Shift+T)")
        ext_term_btn.triggered.connect(self._open_external_terminal)

        # Apply saved visibility
        if not self.settings.settings.window.toolbar_visible:
            self.toolbar.hide()
    
    def _setup_statusbar(self):
        """Set up the status bar"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # File info label
        self.file_info_label = QLabel("Ready")
        self.statusbar.addWidget(self.file_info_label)
        
        self.statusbar.addPermanentWidget(QLabel(""))  # Spacer
        
        # Cursor position
        self.cursor_label = QLabel("Ln 1, Col 1")
        self.statusbar.addPermanentWidget(self.cursor_label)
        
        # Encoding
        self.encoding_label = QLabel("UTF-8")
        self.statusbar.addPermanentWidget(self.encoding_label)
    
    def _setup_shortcuts(self):
        """Set up additional keyboard shortcuts"""
        pass  # Most shortcuts are set through menu actions
    
    def _setup_connections(self):
        """Set up signal connections"""
        # File browser
        self.file_browser.file_opened.connect(self.editor_tabs.open_file)
        self.file_browser.item_deleted.connect(self.editor_tabs.handle_item_deleted)
        self.file_browser.item_renamed.connect(self.editor_tabs.handle_item_renamed)
        
        # Editor tabs
        self.editor_tabs.current_file_changed.connect(self._on_current_file_changed)
        self.editor_tabs.cursor_position_changed.connect(self._on_cursor_position_changed)
        self.editor_tabs.file_saved.connect(lambda f: self.statusbar.showMessage(f"Saved: {f}", 3000))
        
        # Update step names for completion when a file is opened or saved
        self.editor_tabs.file_opened.connect(self._update_completion_step_names)
        self.editor_tabs.file_saved.connect(self._update_completion_step_names)
    
    def _update_recent_files_menu(self):
        """Update the recent files submenu"""
        self.recent_menu.clear()
        
        for filepath in self.settings.settings.recent_files[:10]:
            if os.path.exists(filepath):
                action = self.recent_menu.addAction(os.path.basename(filepath))
                action.setToolTip(filepath)
                action.triggered.connect(lambda checked, f=filepath: self.editor_tabs.open_file(f))
        
        if self.recent_menu.isEmpty():
            self.recent_menu.addAction("No recent files").setEnabled(False)
        else:
            self.recent_menu.addSeparator()
            clear_action = self.recent_menu.addAction("Clear Recent Files")
            clear_action.triggered.connect(self._clear_recent_files)
    
    def _clear_recent_files(self):
        """Clear recent files list"""
        self.settings.settings.recent_files = []
        self.settings.save()
        self._update_recent_files_menu()
    
    # File operations
    def _new_file(self):
        self.editor_tabs.new_file()

    def _new_folder_in_browser(self):
        """Create a new folder in the file browser's current directory."""
        self.file_browser._create_new_folder()
    
    def _new_project(self):
        """Create a new Steps project with skeleton structure."""
        # Get project name from user
        project_name, ok = QInputDialog.getText(
            self, "New Project",
            "Enter project name:",
            QLineEdit.EchoMode.Normal
        )
        
        if not ok or not project_name.strip():
            return
        
        project_name = project_name.strip()
        
        # Sanitize name for filesystem (remove/replace problematic characters)
        safe_name = "".join(c if c.isalnum() or c in "_-" else "_" for c in project_name)
        if not safe_name:
            QMessageBox.critical(self, "Error", "Invalid project name.")
            return
        
        # Determine the projects directory (relative to the running IDE)
        # Try to find the projects folder in the Steps workspace
        projects_dir = None
        
        # Check if file browser is currently in a Steps workspace with a projects folder
        if self.file_browser.current_root:
            current_root = Path(self.file_browser.current_root)
            # Look for projects folder in current root or parent directories
            for parent in [current_root] + list(current_root.parents):
                potential_projects = parent / "projects"
                if potential_projects.is_dir():
                    projects_dir = potential_projects
                    break
        
        # If not found, try the default Steps location
        if not projects_dir:
            default_projects = Path(__file__).parent.parent.parent.parent.parent / "projects"
            if default_projects.is_dir():
                projects_dir = default_projects
        
        # Last resort: ask user to choose location
        if not projects_dir or not projects_dir.is_dir():
            folder = QFileDialog.getExistingDirectory(
                self, "Select Projects Folder",
                str(Path.home())
            )
            if not folder:
                return
            projects_dir = Path(folder)
        
        # Create project structure
        project_path = projects_dir / safe_name
        
        if project_path.exists():
            QMessageBox.critical(
                self, "Error",
                f"A project named '{safe_name}' already exists."
            )
            return
        
        try:
            # Create project folder
            project_path.mkdir(parents=True)
            
            # Create the .building file with inline floor declaration
            building_file = project_path / f"{safe_name}.building"
            building_content = (
                f"building: {safe_name}\n"
                f"    note: New Steps project\n"
                f"\n"
                f"    floors:\n"
                f"        floor: main\n"
                f"            step: first_step\n"
                f"\n"
                f"    call first_step\n"
                f"    exit\n"
            )
            building_file.write_text(building_content)
            
            # Create main floor folder
            main_path = project_path / "main"
            main_path.mkdir()
            
            # Create first_step.step file
            step_file = main_path / "first_step.step"
            step_content = (
                "step: first_step\n"
                "    belongs to: main\n"
                "    expects: nothing\n"
                "    returns: nothing\n"
                "\n"
                "    do:\n"
                "        display \"Hello from Steps!\"\n"
            )
            step_file.write_text(step_content)
            
            # Navigate file browser to the new project
            self.file_browser.navigate_to(str(project_path))
            
            # Open the building file in editor
            self.editor_tabs.open_file(str(building_file))
            
            self.statusbar.showMessage(f"Created new project: {safe_name}", 5000)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create project: {e}")
    
    def _open_file(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open File",
            self.file_browser.current_root or str(Path.home()),
            "Steps Files (*.building *.step);;All Files (*)"
        )
        if filepath:
            self.editor_tabs.open_file(filepath)
    
    def _open_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Open Folder",
            str(Path.home())
        )
        if folder:
            self.file_browser.navigate_to(folder)
    
    def _save_file(self):
        self.editor_tabs.save_current()
    
    def _save_file_as(self):
        self.editor_tabs.save_current_as()
    
    def _close_current_tab(self):
        index = self.editor_tabs.currentIndex()
        if index >= 0:
            self.editor_tabs.close_tab(index)
    
    # Edit operations
    def _undo(self):
        editor = self.editor_tabs.get_current_editor()
        if editor:
            editor.undo()
    
    def _redo(self):
        editor = self.editor_tabs.get_current_editor()
        if editor:
            editor.redo()
    
    def _cut(self):
        editor = self.editor_tabs.get_current_editor()
        if editor:
            editor.cut()
    
    def _copy(self):
        editor = self.editor_tabs.get_current_editor()
        if editor:
            editor.copy()
    
    def _paste(self):
        editor = self.editor_tabs.get_current_editor()
        if editor:
            editor.paste()
    
    def _select_all(self):
        editor = self.editor_tabs.get_current_editor()
        if editor:
            editor.selectAll()

    def _indent_selection(self):
        """Add 4 spaces to the beginning of each selected line."""
        editor = self.editor_tabs.get_current_editor()
        if not editor:
            return

        cursor = editor.textCursor()
        doc = editor.document()

        if cursor.hasSelection():
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            cursor.setPosition(start)
            start_block = cursor.blockNumber()
            cursor.setPosition(end)
            end_block = cursor.blockNumber()
            # If selection ends exactly at the start of a line, exclude that line
            if cursor.positionInBlock() == 0 and end > start:
                end_block -= 1
        else:
            start_block = cursor.blockNumber()
            end_block = start_block

        cursor.beginEditBlock()
        for block_num in range(start_block, end_block + 1):
            block = doc.findBlockByNumber(block_num)
            cursor.setPosition(block.position())
            cursor.insertText("    ")
        cursor.endEditBlock()

    def _dedent_selection(self):
        """Remove up to 4 spaces from the beginning of each selected line."""
        editor = self.editor_tabs.get_current_editor()
        if not editor:
            return

        cursor = editor.textCursor()
        doc = editor.document()

        if cursor.hasSelection():
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            cursor.setPosition(start)
            start_block = cursor.blockNumber()
            cursor.setPosition(end)
            end_block = cursor.blockNumber()
            # If selection ends exactly at the start of a line, exclude that line
            if cursor.positionInBlock() == 0 and end > start:
                end_block -= 1
        else:
            start_block = cursor.blockNumber()
            end_block = start_block

        cursor.beginEditBlock()
        for block_num in range(start_block, end_block + 1):
            block = doc.findBlockByNumber(block_num)
            text = block.text()
            spaces_to_remove = 0
            for ch in text[:4]:
                if ch == ' ':
                    spaces_to_remove += 1
                else:
                    break
            if spaces_to_remove > 0:
                cursor.setPosition(block.position())
                cursor.movePosition(
                    QTextCursor.MoveOperation.Right,
                    QTextCursor.MoveMode.KeepAnchor,
                    spaces_to_remove
                )
                cursor.removeSelectedText()
        cursor.endEditBlock()

    def _find(self):
        # Simple find implementation
        editor = self.editor_tabs.get_current_editor()
        if not editor:
            return
        
        text, ok = QInputDialog.getText(self, "Find", "Search for:")
        if ok and text:
            cursor = editor.textCursor()
            doc = editor.document()
            found = doc.find(text, cursor)
            if not found.isNull():
                editor.setTextCursor(found)
            else:
                # Try from beginning
                found = doc.find(text)
                if not found.isNull():
                    editor.setTextCursor(found)
                else:
                    self.statusbar.showMessage(f"'{text}' not found", 3000)
    
    def _replace(self):
        """Find and replace all instances of a string in the current file."""
        editor = self.editor_tabs.get_current_editor()
        if not editor:
            self.statusbar.showMessage("No file open", 3000)
            return
        
        # Create a custom dialog for find/replace
        dialog = QDialog(self)
        dialog.setWindowTitle("Replace")
        dialog.setFixedSize(400, 150)
        
        layout = QVBoxLayout(dialog)
        
        form = QFormLayout()
        find_input = QLineEdit()
        find_input.setPlaceholderText("Text to find")
        form.addRow("Find:", find_input)
        
        replace_input = QLineEdit()
        replace_input.setPlaceholderText("Replace with")
        form.addRow("Replace with:", replace_input)
        
        layout.addLayout(form)
        
        buttons = QDialogButtonBox()
        replace_all_btn = buttons.addButton("Replace All", QDialogButtonBox.ButtonRole.AcceptRole)
        cancel_btn = buttons.addButton(QDialogButtonBox.StandardButton.Cancel)
        
        layout.addWidget(buttons)
        
        replace_all_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        find_input.setFocus()
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            find_text = find_input.text()
            replace_text = replace_input.text()
            
            if not find_text:
                self.statusbar.showMessage("Nothing to find", 3000)
                return
            
            # Get the entire document text
            doc = editor.document()
            full_text = doc.toPlainText()
            
            # Count occurrences
            count = full_text.count(find_text)
            
            if count == 0:
                self.statusbar.showMessage(f"'{find_text}' not found", 3000)
                return
            
            # Replace all occurrences
            new_text = full_text.replace(find_text, replace_text)
            
            # Preserve cursor position as best as possible
            cursor = editor.textCursor()
            pos = cursor.position()
            
            # Update document
            editor.setPlainText(new_text)
            
            # Try to restore cursor position (adjusted if text length changed)
            new_pos = min(pos, len(new_text))
            cursor = editor.textCursor()
            cursor.setPosition(new_pos)
            editor.setTextCursor(cursor)
            
            self.statusbar.showMessage(f"Replaced {count} occurrence(s)", 3000)
    
    def _goto_line(self):
        editor = self.editor_tabs.get_current_editor()
        if not editor:
            return
        
        max_line = editor.blockCount()
        dialog = GotoLineDialog(max_line, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.editor_tabs.goto_line(dialog.get_line())
    
    def _show_settings(self):
        dialog = SettingsDialog(self.settings, self.theme_manager, self)
        dialog.settings_applied.connect(self._apply_settings)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Also refresh on OK
            self._apply_settings()
    
    def _apply_settings(self):
        """Apply settings changes to UI"""
        theme = self.theme_manager.get_current_theme()
        
        # Update stylesheet
        QApplication.instance().setStyleSheet(
            self.theme_manager.get_current_stylesheet()
        )
        
        # Update editor themes and settings
        self.editor_tabs.set_theme(theme)
        self.editor_tabs.refresh_settings()
        
        # Update terminal theme and settings
        self.terminal.set_theme(theme)
        self.terminal._apply_theme()  # Refresh terminal with new font settings
        
        # Update terminal position
        self._update_terminal_position()
        
        # Update theme menu checkmarks
        current = self.settings.settings.theme.current_theme
        for name, action in self.theme_actions:
            action.setChecked(name == current)
    
    # View operations
    def _toggle_toolbar(self):
        visible = self.toolbar.isVisible()
        self.toolbar.setVisible(not visible)
        self.settings.settings.window.toolbar_visible = not visible
        self.settings.save()
        self.toggle_toolbar_action.setChecked(not visible)

    def _toggle_file_browser(self):
        visible = self.file_browser.isVisible()
        self.file_browser.setVisible(not visible)
        self.settings.settings.window.file_browser_visible = not visible
        self.settings.save()
        
        self.toggle_browser_action.setChecked(not visible)
        self.browser_toolbar_btn.setChecked(not visible)
    
    def _toggle_terminal(self):
        visible = self.terminal_container.isVisible()
        self.terminal_container.setVisible(not visible)
        self.settings.settings.terminal.visible = not visible
        self.settings.save()
        
        self.toggle_terminal_action.setChecked(not visible)
        self.terminal_toolbar_btn.setChecked(not visible)
        
        if not visible:
            self.terminal.focus_input()
    
    def _toggle_debug_panel(self):
        """Toggle visibility of the debug panel."""
        visible = self.debug_dock.isVisible()
        self.debug_dock.setVisible(not visible)
        self.toggle_debug_panel_action.setChecked(not visible)
    
    def _set_terminal_position(self, position: str):
        self.settings.settings.terminal.position = position
        self.settings.save()
        self._update_terminal_position()
        
        # Update menu checkmarks
        for action in self.terminal_position_actions:
            action.setChecked(action.text().lower() == position)

    def _open_external_terminal(self):
        """Open an external terminal window in the current directory"""
        # Determine working directory
        cwd = self.file_browser.current_root
        if not cwd or not os.path.isdir(cwd):
            cwd = str(Path.home())
            
        try:
            if sys.platform == 'win32':
                # Windows
                subprocess.Popen(f'start cmd /K "cd /d {cwd}"', shell=True)
                
            elif sys.platform == 'darwin':
                # macOS
                subprocess.Popen(['open', '-a', 'Terminal', cwd])
                
            else:
                # Linux / Unix
                self._open_linux_terminal(cwd)
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to launch terminal:\n{str(e)}"
            )

    def _open_linux_terminal(self, cwd):
        """Helper to open Linux terminal"""
        # Detect available terminal emulator
        terminals = [
            'gnome-terminal',
            'konsole', 
            'xfce4-terminal',
            'mate-terminal',
            'terminator',
            'xterm',
            'urxvt',
            'rxvt',
            'x-terminal-emulator'
        ]
        
        terminal_cmd = None
        for term in terminals:
            if shutil.which(term):
                terminal_cmd = term
                break
        
        if not terminal_cmd:
            QMessageBox.warning(
                self, 
                "Terminal Not Found", 
                "Could not detect a supported external terminal emulator.\n"
                "Please install gnome-terminal, konsole, xterm, or ensure 'x-terminal-emulator' is configured."
            )
            return
            
        # Construct command based on terminal type
        if terminal_cmd == 'gnome-terminal':
            subprocess.Popen([terminal_cmd, '--working-directory', cwd])
        elif terminal_cmd == 'konsole':
                subprocess.Popen([terminal_cmd, '--workdir', cwd])
        elif terminal_cmd == 'xfce4-terminal':
            subprocess.Popen([terminal_cmd, '--working-directory', cwd])
        elif terminal_cmd == 'mate-terminal':
            subprocess.Popen([terminal_cmd, '--working-directory', cwd])
        else:
            # Fallback for xterm and others
            subprocess.Popen([terminal_cmd], cwd=cwd)
    
    def _zoom_in(self):
        editor = self.editor_tabs.get_current_editor()
        if editor:
            editor.zoom_in()
    
    def _zoom_out(self):
        editor = self.editor_tabs.get_current_editor()
        if editor:
            editor.zoom_out()
    
    def _zoom_reset(self):
        editor = self.editor_tabs.get_current_editor()
        if editor:
            editor.reset_zoom()
    
    def _set_theme(self, theme_name: str):
        self.theme_manager.set_theme(theme_name)
        self._apply_settings()

    def _show_diagram(self):
        """Show project diagram for the current project"""
        from pathlib import Path
        from steps.loader import load_project
        from steps.diagram import generate_flow_diagram
        from steps_ide.app.editor import validate_diagram_font

        # Determine project path
        project_path = None

        # Try to get from currently open file
        current_file = self.editor_tabs.get_current_filepath()
        if current_file:
            file_path = Path(current_file)
            # Find project root (directory containing .building file)
            search_path = file_path.parent
            while search_path != search_path.parent:
                if list(search_path.glob('*.building')):
                    project_path = search_path
                    break
                search_path = search_path.parent

        # If no file open or no project found, ask user to select
        if not project_path:
            from PyQt6.QtWidgets import QFileDialog
            folder = QFileDialog.getExistingDirectory(
                self,
                "Select Steps Project Folder",
                self.file_browser.current_root or str(Path.home())
            )
            if not folder:
                return  # User cancelled

            project_path = Path(folder)

            # Verify it's a Steps project
            if not list(project_path.glob('*.building')):
                QMessageBox.warning(
                    self,
                    "Not a Steps Project",
                    f"The selected folder does not contain a .building file.\n\n"
                    f"Please select a valid Steps project directory."
                )
                return

        # Validate font before generating diagram
        current_font = self.settings.settings.editor.font_family
        from PyQt6.QtGui import QFont
        test_font = QFont(current_font, 10)
        is_valid, warning_msg = validate_diagram_font(test_font)

        if not is_valid:
            reply = QMessageBox.question(
                self,
                "Font Warning",
                f"The current editor font may not display the diagram correctly:\n\n"
                f"{warning_msg}\n\n"
                f"Recommended fonts: JetBrains Mono, Consolas, Courier New\n\n"
                f"Do you want to continue anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return

        # Load project and generate diagram
        try:
            building, environment, errors = load_project(project_path)

            if errors or building is None:
                error_msg = "Failed to load project:\n\n"
                for error in errors[:5]:  # Show first 5 errors
                    error_msg += f"• {error}\n"
                if len(errors) > 5:
                    error_msg += f"\n... and {len(errors) - 5} more errors"

                QMessageBox.critical(self, "Project Load Error", error_msg)
                return

            # Generate diagram
            diagram = generate_flow_diagram(building, environment, project_path)

            # Show in diagram tab
            project_name = project_path.name
            self.editor_tabs.show_diagram(diagram, project_name)

            self.statusbar.showMessage(f"Generated diagram for project: {project_name}", 3000)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to generate diagram:\n\n{str(e)}"
            )
            import traceback
            traceback.print_exc()

    # Run operations
    def _run_current_project(self):
        """Run the current Steps file or project"""
        filepath = self.editor_tabs.get_current_filepath()
        
        if not filepath:
            self.statusbar.showMessage("No file open to run", 3000)
            return
        
        # Check if it's a Steps file
        if not any(filepath.endswith(ext) for ext in ['.building', '.step']):
            self.statusbar.showMessage("Not a Steps file (.building or .step)", 3000)
            return
        
        # Save first
        self.editor_tabs.save_current()
        
        # Show terminal if hidden
        if not self.terminal_container.isVisible():
            self._toggle_terminal()
        
        # Run in terminal
        self.terminal.run_steps_file(filepath)
    
    def _check_file_syntax(self):
        """Check only the current file for syntax errors (Shift+F6)."""
        filepath = self.editor_tabs.get_current_filepath()
        
        if not filepath:
            self.statusbar.showMessage("No file open to check", 3000)
            return
        
        # Check if it's a Steps file
        if not any(filepath.endswith(ext) for ext in ['.building', '.step']):
            self.statusbar.showMessage("Not a Steps file (.building or .step)", 3000)
            return
        
        # Save first
        self.editor_tabs.save_current()
        
        # Show terminal if hidden
        if not self.terminal_container.isVisible():
            self._toggle_terminal()
        
        try:
            from pathlib import Path
            from steps.parser import parse_building, parse_step
            
            file_path = Path(filepath)
            
            # Read the file content
            source = file_path.read_text(encoding='utf-8')
            
            # Clear terminal and show what we're checking
            self.terminal.clear_output()
            self.terminal.write_output(f"Checking file: {file_path.name}\n")
            self.terminal.write_output("-" * 40 + "\n")
            
            # Parse based on file extension
            if filepath.endswith('.building'):
                result = parse_building(source, file_path)
            elif filepath.endswith('.step'):
                result = parse_step(source, file_path)
            else:
                self.terminal.write_output("Unknown file type.\n")
                return
            
            # Check for errors
            if result.errors:
                for error in result.errors:
                    self.terminal.write_output(error.format() + "\n")
                self.statusbar.showMessage(f"Found {len(result.errors)} error(s)", 3000)
            else:
                self.terminal.write_output("✓ No syntax errors found in this file.\n")
                self.statusbar.showMessage("No syntax errors found", 3000)
                
        except ImportError as e:
            self.terminal.write_output(f"Error: Steps interpreter not available: {e}\n")
        except Exception as e:
            self.terminal.write_output(f"Unexpected error: {str(e)}\n")
            import traceback
            self.terminal.write_output(traceback.format_exc())
    
    def _check_project_syntax(self):
        """Check the entire Steps project for syntax errors (F6)."""
        filepath = self.editor_tabs.get_current_filepath()
        
        if not filepath:
            self.statusbar.showMessage("No file open to check", 3000)
            return
        
        # Check if it's a Steps file
        if not any(filepath.endswith(ext) for ext in ['.building', '.step']):
            self.statusbar.showMessage("Not a Steps file (.building or .step)", 3000)
            return
        
        # Save first
        self.editor_tabs.save_current()
        
        # Show terminal if hidden
        if not self.terminal_container.isVisible():
            self._toggle_terminal()
        
        # Load and check the project
        try:
            from pathlib import Path
            from steps.loader import load_project
            
            file_path = Path(filepath)
            
            # Determine the project directory
            # For .building files, the project is the parent directory
            # For .step files, we need to find the project root
            if filepath.endswith('.building'):
                project_path = file_path.parent
            else:
                # For .step files, find the project root (directory containing .building)
                project_path = file_path.parent
                while project_path != project_path.parent:
                    if list(project_path.glob('*.building')):
                        break
                    project_path = project_path.parent
                else:
                    self.terminal.write_output("Error: Could not find project root (no .building file found).\n")
                    return
            
            # Clear terminal and show what we're checking
            self.terminal.clear_output()
            self.terminal.write_output(f"Checking project: {project_path.name}\n")
            self.terminal.write_output("-" * 40 + "\n")
            
            # Load the project to check for errors
            building, env, errors = load_project(project_path)
            
            if errors:
                # Show loading/syntax errors
                for error in errors:
                    self.terminal.write_output(error.format() + "\n")
                self.statusbar.showMessage(f"Found {len(errors)} error(s)", 3000)
            elif building is None:
                self.terminal.write_output("Error: No building found in project.\n")
                self.statusbar.showMessage("No building found", 3000)
            else:
                self.terminal.write_output("✓ No syntax errors found in project.\n")
                self.statusbar.showMessage("No syntax errors found", 3000)
                
        except ImportError as e:
            self.terminal.write_output(f"Error: Steps interpreter not available: {e}\n")
        except Exception as e:
            self.terminal.write_output(f"Unexpected error: {str(e)}\n")
            import traceback
            self.terminal.write_output(traceback.format_exc())
    
    # Status updates
    def _on_current_file_changed(self, filepath: str):
        if filepath and not filepath.startswith("__untitled_"):
            self.file_info_label.setText(filepath)
        else:
            self.file_info_label.setText("Untitled")
        
        self._update_recent_files_menu()
    
    def _on_cursor_position_changed(self, line: int, column: int):
        self.cursor_label.setText(f"Ln {line}, Col {column}")
    
    def _update_completion_step_names(self, filepath: str):
        """Detect project root from a filepath and update step name completions."""
        if not filepath or filepath.startswith("__untitled_"):
            return
        
        file_path = Path(filepath)
        
        # Walk up to find the project root (directory containing .building file)
        search_path = file_path.parent if file_path.is_file() else file_path
        project_root = None
        
        for _ in range(10):  # Max depth guard
            if list(search_path.glob("*.building")):
                project_root = search_path
                break
            parent = search_path.parent
            if parent == search_path:
                break
            search_path = parent
        
        if project_root:
            self.editor_tabs.update_project_steps(str(project_root))
    
    # Help
    def _show_quick_reference(self):
        """Show the language quick reference dialog"""
        dialog = QuickReferenceDialog(self)
        dialog.exec()
    
    def _show_about(self):
        QMessageBox.about(
            self, "About Steps IDE",
            "<h2>Steps IDE</h2>"
            "<p>Version 1.0.0</p>"
            "<p>A modern IDE for the Steps programming language.</p>"
            "<p>(c) 2026 Chuck Finch - Fragillidae Software</p>"
        )
    
    # Window events
    def closeEvent(self, event: QCloseEvent):
        """Handle window close"""
        # Ask to save unsaved files
        if not self.editor_tabs.close_all_tabs():
            event.ignore()
            return
        
        # Stop debug thread if running
        if hasattr(self, '_debug_thread') and self._debug_thread and self._debug_thread.isRunning():
            self._debug_thread.stop()
            self._debug_thread.wait()

        # Stop terminal before closing to prevent thread crash
        self.terminal.stop_shell()
        
        # Save window state
        ws = self.settings.settings.window
        ws.maximized = self.isMaximized()
        if not ws.maximized:
            ws.width = self.width()
            ws.height = self.height()
        
        # Save splitter sizes
        sizes = self.main_splitter.sizes()
        if len(sizes) >= 2:
            ws.file_browser_width = sizes[0]
        
        sizes = self.editor_terminal_splitter.sizes()
        if len(sizes) >= 2:
            if self.settings.settings.terminal.position == "right":
                ws.terminal_width = sizes[1]
            else:
                ws.terminal_height = sizes[1]
        
        self.settings.save()
        event.accept()

    # Debugging Methods
    
    def _start_debug(self):
        """Start debugging the current file/project."""
        filepath = self.editor_tabs.get_current_filepath()
        if not filepath:
            self.statusbar.showMessage("No file to debug", 3000)
            return

        # Set debug panel state (but don't force show/hide)
        self.debug_panel.set_debugging_active(True)
        self.debug_panel.set_paused(True, "Start") # Initial state

        from steps_ide.app.debug_thread import DebugThread
        
        # Collect breakpoints from all open editors
        breakpoints = self.editor_tabs.get_all_breakpoints()
        
        self._debug_thread = DebugThread(filepath, breakpoints, self)
        self._debug_thread.debug_event.connect(self._on_debug_event)
        self._debug_thread.finished_signal.connect(self._on_debug_finished)
        self._debug_thread.output_signal.connect(self._on_debug_output)
        self._debug_thread.input_request_signal.connect(self._on_input_request)
        self._debug_thread.start()
        
        self.statusbar.showMessage("Debugging started...", 3000)

    def _stop_debug(self):
        """Stop the debug session."""
        if self._debug_thread:
            self._debug_thread.stop()
            self._debug_thread = None # Thread will clean itself up
        
        self.debug_panel.set_debugging_active(False)
        self.editor_tabs.clear_debug_highlight()
        self.statusbar.showMessage("Debugging stopped", 3000)

    def _step_into(self):
        if self._debug_thread:
            self._debug_thread.step_into()

    def _step_over(self):
        if self._debug_thread:
            self._debug_thread.step_over()

    def _step_out(self):
        if self._debug_thread:
            self._debug_thread.step_out()

    def _continue_debug(self):
        if self._debug_thread:
            # Clear paused state in UI immediately to feel responsive
            self.debug_panel.set_paused(False)
            self._debug_thread.continue_run()

    def _toggle_breakpoint(self):
        """Toggle breakpoint on current line."""
        editor = self.editor_tabs.get_current_editor()
        if editor:
            cursor = editor.textCursor()
            line = cursor.blockNumber() + 1
            editor.toggle_breakpoint(line)
            
            # If debugging, update thread
            if self._debug_thread:
                filepath = self.editor_tabs.get_current_filepath()
                if filepath:
                    if line in editor.get_breakpoints():
                        self._debug_thread.add_breakpoint(filepath, line)
                    else:
                        self._debug_thread.remove_breakpoint(filepath, line)

    def _on_debug_event(self, event):
        """Handle event from debug thread."""
        if event.event_type in ('paused', 'breakpoint', 'call', 'return'):
            # Paused or stepping
            # Paused or stepping
            # For call/return we might optionally update stack without stealing focus, 
            # but usually we only get events when paused.
            
            # Convert Path to str explicitly for editor lookup
            filepath = str(event.snapshot.current_file)
            line = event.snapshot.current_line
            
            self.debug_panel.set_paused(True, f"{event.snapshot.current_file.name}:{line}")
            self.debug_panel.update_from_snapshot(event.snapshot)
            self.editor_tabs.highlight_debug_line(filepath, line)
            self.activateWindow() # Bring window to front

    def _on_debug_finished(self, success: bool, message: str):
        """Handle debug session finish."""
        self._stop_debug()
        if not success and message:
             QMessageBox.warning(self, "Debug Error", message)
        else:
             self.statusbar.showMessage("Debugging finished", 3000)

    def _on_debug_output(self, text: str):
        """Handle output from debug session."""
        if self.terminal:
             self.terminal.write_output(text)

    def _on_input_request(self, prompt: str):
        """Handle input request from debugger."""
        if self.terminal:
            # Ensure terminal is visible so user can type
            if not self.terminal_container.isVisible():
                self.terminal_container.setVisible(True)
                self.settings.settings.terminal.visible = True
                self.toggle_terminal_action.setChecked(True)
                self.terminal_toolbar_btn.setChecked(True)
            
            # Focus terminal for input
            self.terminal.focus_input()
            self.terminal.request_input(prompt, self._on_input_received)

    def _on_input_received(self, text: str):
        """Handle input received from terminal."""
        if self._debug_thread:
            self._debug_thread.provide_input(text)

    def _on_frame_selected(self, filepath: str, line: int):
        """Handle click on call stack frame."""
        self.editor_tabs.highlight_debug_line(filepath, line)
