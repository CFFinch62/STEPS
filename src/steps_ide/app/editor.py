"""
Code Editor Widget for Steps IDE
Tabbed code editor with syntax highlighting, line numbers, and editing features
"""

import os
from pathlib import Path
from typing import Optional, Dict, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QTabWidget,
    QLabel, QFrame, QMessageBox, QFileDialog, QMenu, QTextEdit, QPushButton
)
from PyQt6.QtCore import (
    Qt, QRect, QSize, pyqtSignal, QTimer, QRegularExpression
)
from PyQt6.QtGui import (
    QColor, QPainter, QTextFormat, QFont, QFontMetrics, QTextCursor,
    QKeySequence, QAction, QPaintEvent, QTextCharFormat, QTextDocument,
    QKeyEvent, QWheelEvent, QFontInfo
)

from steps_ide.app.settings import SettingsManager
from steps_ide.app.themes import Theme, ThemeManager
from steps_ide.app.syntax import StepsHighlighter, GenericHighlighter


class LineNumberArea(QWidget):
    """Line number display widget"""
    
    def __init__(self, editor: 'CodeEditor'):
        super().__init__(editor)
        self.code_editor = editor
    
    def sizeHint(self) -> QSize:
        return QSize(self.code_editor.line_number_area_width(), 0)
    
    def paintEvent(self, event: QPaintEvent):
        self.code_editor.line_number_area_paint_event(event)
    
    def mousePressEvent(self, event):
        """Handle mouse click to toggle breakpoint."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Calculate which line was clicked
            y = event.position().y()
            block = self.code_editor.firstVisibleBlock()
            top = self.code_editor.blockBoundingGeometry(block).translated(
                self.code_editor.contentOffset()
            ).top()
            
            while block.isValid():
                block_top = top
                block_height = self.code_editor.blockBoundingRect(block).height()
                
                if block_top <= y < block_top + block_height:
                    line = block.blockNumber() + 1
                    self.code_editor.toggle_breakpoint(line)
                    break
                
                top += block_height
                block = block.next()
        
        super().mousePressEvent(event)


class CodeEditor(QPlainTextEdit):
    """Single file code editor with line numbers and syntax highlighting"""
    
    # Signal for breakpoint toggle
    # Signal for breakpoint toggle
    breakpoint_toggled = pyqtSignal(int)  # line number
    modified_changed = pyqtSignal(bool)
    cursor_position_changed = pyqtSignal(int, int)  # line, column

    def __init__(self, theme: Theme, settings: SettingsManager, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.settings_manager = settings
        self.file_path: Optional[str] = None
        self._highlighter: Optional[StepsHighlighter] = None
        
        # Debugger state
        self._current_debug_line = -1
        self._breakpoints: set[int] = set()
        
        self._setup_editor()
        self._setup_line_numbers()
        self._setup_connections()
        self._apply_theme()
    
    def _setup_editor(self):
        """Set up editor configuration"""
        settings = self.settings_manager.settings.editor
        
        # Font
        font = QFont(settings.font_family, settings.font_size)
        font.setFixedPitch(True)
        self.setFont(font)
        
        # Tab width
        metrics = QFontMetrics(font)
        self.setTabStopDistance(metrics.horizontalAdvance(' ') * settings.tab_width)
        
        # Word wrap
        if settings.word_wrap:
            self.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        else:
            self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        
        # Cursor width
        self.setCursorWidth(2)
    
    def _setup_line_numbers(self):
        """Set up line number area"""
        self.line_number_area = LineNumberArea(self)
        
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        
        self.update_line_number_area_width(0)
        self.highlight_current_line()
    
    def _setup_connections(self):
        """Set up signal connections"""
        self.modificationChanged.connect(self.modified_changed.emit)
        self.cursorPositionChanged.connect(self._emit_cursor_position)
    
    def _apply_theme(self):
        """Apply theme colors to editor"""
        settings = self.settings_manager.settings.editor
        self.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {self.theme.editor_background};
                color: {self.theme.editor_foreground};
                selection-background-color: {self.theme.editor_selection};
                border: none;
                font-family: "{settings.font_family}";
                font-size: {settings.font_size}pt;
            }}
        """)
        
        # Update line numbers
        self.line_number_area.update()
        self.highlight_current_line()
    
    def set_theme(self, theme: Theme):
        """Update the theme"""
        self.theme = theme
        self._apply_theme()
        if self._highlighter:
            self._highlighter.set_theme(theme)
    
    def refresh_settings(self):
        """Re-apply all settings from settings manager"""
        settings = self.settings_manager.settings.editor
        
        # Re-apply theme which now includes font settings in stylesheet
        self._apply_theme()
        
        # Also set font programmatically for line number area
        font = QFont(settings.font_family, settings.font_size)
        font.setFixedPitch(True)
        self.line_number_area.setFont(font)
        
        # Tab width
        self._update_tab_width()
        
        # Word wrap
        if settings.word_wrap:
            self.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        else:
            self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        
        # Line numbers - update width
        self.update_line_number_area_width(0)
        self.line_number_area.update()
        
        # Current line highlight
        self.highlight_current_line()
        
        # Force repaint
        self.viewport().update()
        self.update()
    
    def line_number_area_width(self) -> int:
        """Calculate width needed for line numbers"""
        if not self.settings_manager.settings.editor.show_line_numbers:
            return 0
        
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        
        # Minimum 4 digits width + padding + icon space
        digits = max(4, digits)
        space = 24 + self.fontMetrics().horizontalAdvance('9') * digits
        return space
    
    def update_line_number_area_width(self, _):
        """Update the viewport margin for line numbers"""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    
    def update_line_number_area(self, rect: QRect, dy: int):
        """Update line number area on scroll"""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), 
                                         self.line_number_area.width(), rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)
    
    def resizeEvent(self, event):
        """Handle resize to update line number area"""
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )
    
    def line_number_area_paint_event(self, event: QPaintEvent):
        """Paint line numbers and debug indicators"""
        if not self.settings_manager.settings.editor.show_line_numbers:
            return
        
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(self.theme.editor_gutter_bg))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())
        
        current_cursor_line = self.textCursor().blockNumber()
        height = self.fontMetrics().height()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                line_num = block_number + 1
                number_str = str(line_num)
                
                # Draw Breakpoint (Red Circle)
                if line_num in self._breakpoints:
                    painter.setBrush(QColor("#f44336"))  # Red
                    painter.setPen(Qt.PenStyle.NoPen)
                    circle_size = min(height, 12)
                    circle_rect = QRect(
                        4, 
                        top + (height - circle_size) // 2,
                        circle_size, 
                        circle_size
                    )
                    painter.drawEllipse(circle_rect)
                
                # Draw Debug Execution Arrow (Yellow Triangle)
                if line_num == self._current_debug_line:
                    painter.setBrush(QColor("#FFC107"))  # Amber/Yellow
                    painter.setPen(Qt.PenStyle.NoPen)
                    
                    # Draw a triangle pointing right
                    arrow_size = min(height, 12)
                    arrow_x = 4
                    arrow_y = top + (height - arrow_size) // 2
                    
                    from PyQt6.QtGui import QPolygon, QPolygonF
                    from PyQt6.QtCore import QPointF
                    
                    points = [
                         QPointF(arrow_x, arrow_y),
                         QPointF(arrow_x + arrow_size, arrow_y + arrow_size / 2),
                         QPointF(arrow_x, arrow_y + arrow_size)
                    ]
                    painter.drawPolygon(QPolygonF(points))
                
                # Draw Line Number
                if block_number == current_cursor_line:
                    painter.setPen(QColor(self.theme.editor_foreground))
                else:
                    painter.setPen(QColor(self.theme.editor_gutter_fg))
                
                painter.drawText(
                    0, top,
                    self.line_number_area.width() - 8, 
                    height,
                    Qt.AlignmentFlag.AlignRight, number_str
                )
            
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1
    
    def highlight_current_line(self):
        """Highlight the current line and debug execution line"""
        extra_selections = []
        
        # 1. Debug Execution Line (Yellow Highlight)
        if self._current_debug_line != -1:
            selection = QTextEdit.ExtraSelection()
            # Use a slightly transparent yellow/amber
            line_color = QColor("#FFC107") # Amber 500
            line_color.setAlpha(60)
            
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            
            # Find the block for the debug line (1-based to 0-based)
            block = self.document().findBlockByLineNumber(self._current_debug_line - 1)
            selection.cursor = QTextCursor(block)
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        # 2. Current Cursor Line (Standard Highlight)
        if (self.settings_manager.settings.editor.highlight_current_line and 
            not self.isReadOnly()):
            selection = QTextEdit.ExtraSelection()
            line_color = QColor(self.theme.editor_line_highlight)
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        
        self.setExtraSelections(extra_selections)

    def highlight_debug_line(self, line: int):
        """Highlight a specific line for debugging."""
        self._current_debug_line = line
        self.highlight_current_line()
        self.line_number_area.update()
        
        # Scroll to line
        block = self.document().findBlockByLineNumber(line - 1)
        cursor = QTextCursor(block)
        self.setTextCursor(cursor)
        self.centerCursor()

    def clear_debug_highlight(self):
        """Clear the debug line highlighting."""
        self._current_debug_line = -1
        self.highlight_current_line()
        self.line_number_area.update()
        
    def toggle_breakpoint(self, line: int):
        """Toggle a breakpoint at the given line."""
        if line in self._breakpoints:
            self._breakpoints.remove(line)
        else:
            self._breakpoints.add(line)
        self.line_number_area.update()
        self.breakpoint_toggled.emit(line)
        
    def get_breakpoints(self) -> set[int]:
        """Get the set of breakpoint line numbers."""
        return self._breakpoints.copy()
    
    def _emit_cursor_position(self):
        """Emit cursor position signal"""
        cursor = self.textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.columnNumber() + 1
        self.cursor_position_changed.emit(line, column)
    
    def set_file(self, filepath: str):
        """Load a file into the editor"""
        self.file_path = filepath
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            self.setPlainText(content)
            self.document().setModified(False)
            
            # Set up appropriate highlighter
            self._setup_highlighter(filepath)
            
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(filepath, 'r', encoding='latin-1') as f:
                    content = f.read()
                self.setPlainText(content)
                self.document().setModified(False)
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Could not read file: {e}")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Could not open file: {e}")
    
    def _setup_highlighter(self, filepath: str):
        """Set up syntax highlighter based on file extension"""
        ext = os.path.splitext(filepath)[1].lower()
        
        # Steps file types
        if ext in ('.building', '.step'):
            self._highlighter = StepsHighlighter(self.document(), self.theme)
        else:
            # Use generic highlighter for other files
            self._highlighter = GenericHighlighter(self.document(), self.theme, ext)
    
    def save_file(self, filepath: str = None) -> bool:
        """Save the file"""
        if filepath:
            self.file_path = filepath
        
        if not self.file_path:
            return False
        
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(self.toPlainText())
            self.document().setModified(False)
            return True
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Could not save file: {e}")
            return False
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events"""
        settings = self.settings_manager.settings.editor
        
        # Auto-indent on Enter
        if event.key() == Qt.Key.Key_Return and settings.auto_indent:
            cursor = self.textCursor()
            block = cursor.block()
            text = block.text()
            
            # Get leading whitespace
            indent = ""
            for char in text:
                if char in (' ', '\t'):
                    indent += char
                else:
                    break
            
            # Check if line ends with : to add extra indent (Steps uses colons)
            stripped = text.rstrip()
            if stripped.endswith(':'):
                if settings.use_spaces:
                    indent += ' ' * settings.tab_width
                else:
                    indent += '\t'
            
            super().keyPressEvent(event)
            self.insertPlainText(indent)
            return
        
        # Tab handling
        if event.key() == Qt.Key.Key_Tab:
            if settings.use_spaces:
                self.insertPlainText(' ' * settings.tab_width)
            else:
                self.insertPlainText('\t')
            return
        
        # Bracket matching - auto-close brackets
        if settings.bracket_matching:
            brackets = {'[': ']', '(': ')', '"': '"', "'": "'"}
            text = event.text()
            if text in brackets:
                cursor = self.textCursor()
                cursor.insertText(text + brackets[text])
                cursor.movePosition(QTextCursor.MoveOperation.Left)
                self.setTextCursor(cursor)
                return
        
        super().keyPressEvent(event)
    
    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel for zoom"""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            elif delta < 0:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)
    
    def zoom_in(self):
        """Increase font size"""
        font = self.font()
        size = font.pointSize()
        if size < 48:
            font.setPointSize(size + 1)
            self.setFont(font)
            self._update_tab_width()
    
    def zoom_out(self):
        """Decrease font size"""
        font = self.font()
        size = font.pointSize()
        if size > 6:
            font.setPointSize(size - 1)
            self.setFont(font)
            self._update_tab_width()
    
    def reset_zoom(self):
        """Reset to default font size"""
        size = self.settings_manager.settings.editor.font_size
        font = self.font()
        font.setPointSize(size)
        self.setFont(font)
        self._update_tab_width()
    
    def _update_tab_width(self):
        """Update tab stop distance after font change"""
        tab_width = self.settings_manager.settings.editor.tab_width
        metrics = QFontMetrics(self.font())
        self.setTabStopDistance(metrics.horizontalAdvance(' ') * tab_width)


class DiagramViewer(QWidget):
    """Read-only viewer for ASCII project diagrams"""

    def __init__(self, diagram_content: str, project_name: str, theme: Theme, parent=None):
        super().__init__(parent)
        self.diagram_content = diagram_content
        self.project_name = project_name
        self.theme = theme

        self._setup_ui()

    def _setup_ui(self):
        """Set up the diagram viewer UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar with save button
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(5, 5, 5, 5)

        save_btn = QPushButton("💾 Save Diagram As...")
        save_btn.clicked.connect(self._save_diagram)
        toolbar.addWidget(save_btn)

        toolbar.addStretch()

        info_label = QLabel(f"Project: {self.project_name}")
        info_label.setStyleSheet("color: gray; font-size: 10pt;")
        toolbar.addWidget(info_label)

        layout.addLayout(toolbar)

        # Text viewer - use QTextEdit for better emoji rendering
        from PyQt6.QtWidgets import QTextEdit
        self.text_viewer = QTextEdit()
        self.text_viewer.setReadOnly(True)
        self.text_viewer.setPlainText(self.diagram_content)
        self.text_viewer.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        # Set monospace font - try multiple options
        # Use a larger font size for better emoji rendering
        font_families = ["Courier New", "Courier", "Consolas", "Monaco", "Monospace"]
        font = None
        for family in font_families:
            test_font = QFont(family, 11)
            if QFontInfo(test_font).fixedPitch():
                font = test_font
                break

        if font is None:
            # Last resort fallback
            font = QFont("Monospace", 11)
            font.setStyleHint(QFont.StyleHint.TypeWriter)

        font.setFixedPitch(True)
        self.text_viewer.setFont(font)

        # Apply theme colors
        self.text_viewer.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.theme.editor_background};
                color: {self.theme.editor_foreground};
                border: none;
                font-family: monospace;
            }}
        """)

        layout.addWidget(self.text_viewer)

    def _save_diagram(self):
        """Save the diagram to a file"""
        default_filename = f"{self.project_name}_diagram.txt"
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save Diagram As",
            default_filename,
            "Text Files (*.txt);;All Files (*)"
        )

        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(self.diagram_content)
                QMessageBox.information(self, "Success", f"Diagram saved to:\n{filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save diagram:\n{e}")

    def set_theme(self, theme: Theme):
        """Update the theme"""
        self.theme = theme
        self.text_viewer.setStyleSheet(f"""
            QTextEdit {{
                background-color: {theme.editor_background};
                color: {theme.editor_foreground};
                border: none;
                font-family: monospace;
            }}
        """)


class EditorTabs(QTabWidget):
    """Tabbed editor widget managing multiple code editors"""

    file_opened = pyqtSignal(str)
    file_saved = pyqtSignal(str)
    file_closed = pyqtSignal(str)
    current_file_changed = pyqtSignal(str)
    cursor_position_changed = pyqtSignal(int, int)
    
    def __init__(self, settings: SettingsManager, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.theme_manager = theme_manager
        self.editors: Dict[str, CodeEditor] = {}  # filepath -> editor
        
        self._setup_ui()
        self._setup_connections()
    
    def _setup_ui(self):
        """Set up the tab widget"""
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.setUsesScrollButtons(True)
        
        # Enable context menu on tabs
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    
    def _setup_connections(self):
        """Set up signal connections"""
        self.tabCloseRequested.connect(self.close_tab)
        self.currentChanged.connect(self._on_current_changed)
        self.customContextMenuRequested.connect(self._show_tab_context_menu)
    
    def open_file(self, filepath: str):
        """Open a file in a new or existing tab"""
        filepath = os.path.abspath(filepath)
        
        # Check if already open
        if filepath in self.editors:
            # Switch to existing tab
            for i in range(self.count()):
                if self.widget(i) == self.editors[filepath]:
                    self.setCurrentIndex(i)
                    return
        
        # Create new editor
        editor = CodeEditor(
            self.theme_manager.get_current_theme(),
            self.settings,
            self
        )
        editor.set_file(filepath)
        editor.modified_changed.connect(lambda m: self._on_modified_changed(filepath, m))
        editor.cursor_position_changed.connect(self.cursor_position_changed.emit)
        
        # Add tab
        self.editors[filepath] = editor
        filename = os.path.basename(filepath)
        index = self.addTab(editor, filename)
        self.setTabToolTip(index, filepath)
        self.setCurrentIndex(index)
        
        # Add to recent files
        self.settings.add_recent_file(filepath)
        
        self.file_opened.emit(filepath)
    
    def new_file(self, initial_content: str = ""):
        """Create a new untitled file"""
        # Find unique untitled name
        count = 1
        while True:
            name = f"Untitled-{count}"
            filepath = f"__untitled_{count}__"
            if filepath not in self.editors:
                break
            count += 1
        
        editor = CodeEditor(
            self.theme_manager.get_current_theme(),
            self.settings,
            self
        )
        editor.setPlainText(initial_content)
        editor.modified_changed.connect(lambda m: self._on_modified_changed(filepath, m))
        editor.cursor_position_changed.connect(self.cursor_position_changed.emit)
        
        # Set up Steps highlighter by default for new files
        editor._highlighter = StepsHighlighter(editor.document(), editor.theme)
        
        self.editors[filepath] = editor
        index = self.addTab(editor, name)
        self.setCurrentIndex(index)

    def show_diagram(self, diagram_content: str, project_name: str):
        """Show project diagram in a tab (reuse existing diagram tab if present)"""
        diagram_key = "__diagram__"

        # Check if diagram tab already exists
        if diagram_key in self.editors:
            # Find and update existing diagram tab
            for i in range(self.count()):
                widget = self.widget(i)
                if isinstance(widget, DiagramViewer):
                    # Update content
                    widget.diagram_content = diagram_content
                    widget.project_name = project_name
                    widget.text_viewer.setPlainText(diagram_content)
                    # Switch to this tab
                    self.setCurrentIndex(i)
                    return

        # Create new diagram viewer
        viewer = DiagramViewer(
            diagram_content,
            project_name,
            self.theme_manager.get_current_theme(),
            self
        )

        # Add to editors dict and create tab
        self.editors[diagram_key] = viewer
        index = self.addTab(viewer, f"📊 {project_name} Diagram")
        self.setTabToolTip(index, f"Project Diagram: {project_name}")
        self.setCurrentIndex(index)

    def save_current(self) -> bool:
        """Save the current file"""
        editor = self.currentWidget()
        if not isinstance(editor, CodeEditor):
            return False
        
        # Find filepath for this editor
        filepath = None
        for path, ed in self.editors.items():
            if ed == editor:
                filepath = path
                break
        
        if filepath and filepath.startswith("__untitled_"):
            # Need to save as
            return self.save_current_as()
        
        if editor.save_file():
            self.file_saved.emit(filepath)
            return True
        return False
    
    def save_current_as(self) -> bool:
        """Save current file with new name"""
        editor = self.currentWidget()
        if not isinstance(editor, CodeEditor):
            return False
        
        # Find old filepath
        old_filepath = None
        for path, ed in self.editors.items():
            if ed == editor:
                old_filepath = path
                break
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save As",
            str(Path.home()),
            "Steps Building (*.building);;Steps Step (*.step);;All Files (*)"
        )
        
        if filepath:
            # Update references
            if old_filepath in self.editors:
                del self.editors[old_filepath]
            self.editors[filepath] = editor
            
            # Update tab
            index = self.currentIndex()
            self.setTabText(index, os.path.basename(filepath))
            self.setTabToolTip(index, filepath)
            
            if editor.save_file(filepath):
                self.file_saved.emit(filepath)
                self.settings.add_recent_file(filepath)
                return True
        
        return False
    
    def save_all(self):
        """Save all open files"""
        for filepath, editor in self.editors.items():
            if not filepath.startswith("__untitled_"):
                if editor.document().isModified():
                    editor.save_file()
                    self.file_saved.emit(filepath)
    
    def close_tab(self, index: int) -> bool:
        """Close a tab, prompting to save if modified"""
        editor = self.widget(index)
        if not isinstance(editor, CodeEditor):
            self.removeTab(index)
            return True
        
        # Find filepath
        filepath = None
        for path, ed in self.editors.items():
            if ed == editor:
                filepath = path
                break
        
        # Check if modified
        if editor.document().isModified():
            name = os.path.basename(filepath) if filepath else "Untitled"
            reply = QMessageBox.question(
                self, "Save Changes",
                f"'{name}' has unsaved changes. Save before closing?",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Cancel:
                return False
            elif reply == QMessageBox.StandardButton.Save:
                if filepath and filepath.startswith("__untitled_"):
                    if not self.save_current_as():
                        return False
                else:
                    if not editor.save_file():
                        return False
        
        # Remove from editors dict
        if filepath in self.editors:
            del self.editors[filepath]
        
        self.removeTab(index)
        self.file_closed.emit(filepath or "")
        return True
    
    def close_all_tabs(self) -> bool:
        """Close all tabs"""
        while self.count() > 0:
            if not self.close_tab(0):
                return False
        return True
    
    def _on_current_changed(self, index: int):
        """Handle current tab change"""
        if index < 0:
            self.current_file_changed.emit("")
            return
        
        editor = self.widget(index)
        if isinstance(editor, CodeEditor):
            for filepath, ed in self.editors.items():
                if ed == editor:
                    self.current_file_changed.emit(filepath)
                    return
    
    def _on_modified_changed(self, filepath: str, modified: bool):
        """Update tab title when modified state changes"""
        if filepath not in self.editors:
            return
        
        editor = self.editors[filepath]
        for i in range(self.count()):
            if self.widget(i) == editor:
                name = os.path.basename(filepath)
                if filepath.startswith("__untitled_"):
                    name = f"Untitled-{filepath.split('_')[2]}"
                if modified:
                    name = "• " + name
                self.setTabText(i, name)
                break
    
    def _show_tab_context_menu(self, pos):
        """Show context menu for tabs"""
        index = self.tabBar().tabAt(pos)
        if index < 0:
            return
        
        menu = QMenu(self)
        
        close_action = menu.addAction("Close")
        close_action.triggered.connect(lambda: self.close_tab(index))
        
        close_others = menu.addAction("Close Others")
        close_others.triggered.connect(lambda: self._close_other_tabs(index))
        
        close_all = menu.addAction("Close All")
        close_all.triggered.connect(self.close_all_tabs)
        
        menu.addSeparator()
        
        copy_path = menu.addAction("Copy Path")
        copy_path.triggered.connect(lambda: self._copy_tab_path(index))
        
        menu.exec(self.tabBar().mapToGlobal(pos))
    
    def _close_other_tabs(self, keep_index: int):
        """Close all tabs except the specified one"""
        # Close tabs after keep_index first (in reverse)
        for i in range(self.count() - 1, keep_index, -1):
            if not self.close_tab(i):
                return
        # Close tabs before keep_index (always removing index 0)
        for i in range(keep_index):
            if not self.close_tab(0):
                return
    
    def _copy_tab_path(self, index: int):
        """Copy the file path of a tab to clipboard"""
        editor = self.widget(index)
        for filepath, ed in self.editors.items():
            if ed == editor and not filepath.startswith("__untitled_"):
                from PyQt6.QtWidgets import QApplication
                QApplication.clipboard().setText(filepath)
                return
    
    def get_current_editor(self) -> Optional[CodeEditor]:
        """Get the current editor widget"""
        widget = self.currentWidget()
        if isinstance(widget, CodeEditor):
            return widget
        return None
    
    def get_current_filepath(self) -> Optional[str]:
        """Get filepath of current tab"""
        editor = self.currentWidget()
        for filepath, ed in self.editors.items():
            if ed == editor:
                return filepath if not filepath.startswith("__untitled_") else None
        return None
    
    def get_editor_for_file(self, filepath: str) -> Optional[CodeEditor]:
        """Get the editor for a specific filepath"""
        filepath = os.path.abspath(filepath)
        return self.editors.get(filepath)
    
    def set_theme(self, theme: Theme):
        """Update theme for all editors and diagram viewers"""
        for widget in self.editors.values():
            if hasattr(widget, 'set_theme'):
                widget.set_theme(theme)
    
    def refresh_settings(self):
        """Refresh settings for all editors"""
        for widget in self.editors.values():
            if hasattr(widget, 'refresh_settings'):
                widget.refresh_settings()
    
    
    def goto_line(self, line: int):
        """Go to a specific line in the current editor"""
        editor = self.get_current_editor()
        if editor:
            block = editor.document().findBlockByLineNumber(line - 1)
            if block.isValid():
                cursor = QTextCursor(block)
                editor.setTextCursor(cursor)
                editor.centerCursor()

    def highlight_debug_line(self, filepath: str, line: int):
        """Highlight execution line in the appropriate editor."""
        from pathlib import Path
        
        # Robust path matching
        target_path = Path(filepath).resolve()
        target_editor = None
        
        # Try to find matching open editor
        for open_path, editor in self.editors.items():
            if Path(open_path).resolve() == target_path:
                target_editor = editor
                break
        
        # If file not open, open it
        if not target_editor:
            self.open_file(str(target_path))
            # Try to find it again (using the key format open_file used)
            for open_path, editor in self.editors.items():
                if Path(open_path).resolve() == target_path:
                    target_editor = editor
                    break
            
        # Switch to tab and highlight
        if target_editor:
            # Find index
            for i in range(self.count()):
                if self.widget(i) == target_editor:
                    self.setCurrentIndex(i)
                    break
            
            target_editor.highlight_debug_line(line)

    def clear_debug_highlight(self):
        """Clear debug highlight in all editors."""
        for editor in self.editors.values():
            editor.clear_debug_highlight()

    def get_all_breakpoints(self) -> Dict[str, set[int]]:
        """Get all breakpoints from all open editors.
        
        Returns:
            Dict mapping absolute filepath to set of line numbers
        """
        all_breakpoints = {}
        for filepath, editor in self.editors.items():
            bps = editor.get_breakpoints()
            if bps:
                all_breakpoints[filepath] = bps
        return all_breakpoints

    def handle_item_deleted(self, path: str, is_directory: bool):
        """Handle a file or folder being deleted - close affected tabs.
        
        For files: close the tab if that exact file was open.
        For directories: close all tabs for files within that directory.
        """
        path = os.path.abspath(path)
        tabs_to_close = []
        
        for filepath in list(self.editors.keys()):
            if is_directory:
                # Close all files within the deleted directory
                if filepath.startswith(path + os.sep):
                    tabs_to_close.append(filepath)
            else:
                # Close the exact file
                if filepath == path:
                    tabs_to_close.append(filepath)
        
        # Close tabs in reverse order to avoid index shifting issues
        for filepath in tabs_to_close:
            if filepath in self.editors:
                editor = self.editors[filepath]
                # Find the tab index
                for i in range(self.count()):
                    if self.widget(i) == editor:
                        # Force close without save prompt (file is already deleted)
                        del self.editors[filepath]
                        self.removeTab(i)
                        self.file_closed.emit(filepath)
                        break

    def handle_item_renamed(self, old_path: str, new_path: str):
        """Handle a file or folder being renamed - update affected tabs.
        
        For files: update the tab's filepath reference.
        For directories: update all tabs for files within that directory.
        """
        old_path = os.path.abspath(old_path)
        new_path = os.path.abspath(new_path)
        
        paths_to_update = []
        
        for filepath in list(self.editors.keys()):
            if filepath == old_path:
                # Exact file renamed
                paths_to_update.append((filepath, new_path))
            elif filepath.startswith(old_path + os.sep):
                # File inside renamed directory
                relative = filepath[len(old_path):]
                new_filepath = new_path + relative
                paths_to_update.append((filepath, new_filepath))
        
        # Update editor references and tab titles
        for old_filepath, new_filepath in paths_to_update:
            if old_filepath in self.editors:
                editor = self.editors[old_filepath]
                # Update the editors dict
                del self.editors[old_filepath]
                self.editors[new_filepath] = editor
                
                # Update the editor's file_path attribute
                editor.file_path = new_filepath
                
                # Update tab title and tooltip
                for i in range(self.count()):
                    if self.widget(i) == editor:
                        self.setTabText(i, os.path.basename(new_filepath))
                        self.setTabToolTip(i, new_filepath)
                        break


def validate_diagram_font(font: QFont) -> tuple[bool, str]:
    """Validate if a font is suitable for displaying ASCII diagrams.

    Args:
        font: The font to validate

    Returns:
        Tuple of (is_valid, warning_message)
        - is_valid: True if font is suitable, False otherwise
        - warning_message: Empty string if valid, warning message otherwise
    """
    font_info = QFontInfo(font)
    warnings = []

    # Check if monospace
    if not font_info.fixedPitch():
        warnings.append("Font is not monospace - diagram may not align properly")

    # Check Unicode support for box-drawing characters
    metrics = QFontMetrics(font)
    # Test single-byte box-drawing characters (emojis are multi-byte and harder to test)
    test_chars = ['┌', '─', '│']
    missing_chars = []

    for char in test_chars:
        try:
            if not metrics.inFont(char):
                missing_chars.append(char)
        except ValueError:
            # Character is multi-byte, skip it
            pass

    if missing_chars:
        warnings.append(f"Font may not support some Unicode box-drawing characters: {', '.join(missing_chars)}")

    if warnings:
        return False, "\n".join(warnings)

    return True, ""

