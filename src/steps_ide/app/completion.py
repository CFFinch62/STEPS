"""
Steps IDE Code Completion Engine

Provides context-aware autocomplete for the Steps programming language.
Supports comparison operators, statement shortcuts, structure snippets,
and project step-name completion.
"""

import re
from dataclasses import dataclass, field
from typing import Optional, List, Dict

from PyQt6.QtWidgets import (
    QWidget, QListWidget, QListWidgetItem, QVBoxLayout, QLabel, QApplication
)
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal, QPoint
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QIcon, QPalette


# ─── Completion Item ────────────────────────────────────────────────────────

@dataclass
class CompletionItem:
    """A single completion suggestion."""
    display_text: str       # Shown in popup (e.g., "is equal to")
    insert_text: str        # What gets inserted (may contain $CURSOR)
    category: str           # "comparison", "statement", "snippet", "step", "call_clause"
    description: str = ""   # Short description for tooltip


# ─── Category Icons ─────────────────────────────────────────────────────────

CATEGORY_ICONS = {
    "comparison": "⚖️",
    "statement":  "📝",
    "snippet":    "📦",
    "step":       "🔷",
    "call_clause": "🔗",
}


# ─── Static Completion Data ─────────────────────────────────────────────────

COMPARISON_ITEMS = [
    CompletionItem("equal to",                      "equal to ",                      "comparison", "Equality check"),
    CompletionItem("not equal to",                   "not equal to ",                   "comparison", "Inequality check"),
    CompletionItem("less than",                      "less than ",                      "comparison", "Less than"),
    CompletionItem("greater than",                   "greater than ",                   "comparison", "Greater than"),
    CompletionItem("less than or equal to",          "less than or equal to ",          "comparison", "Less than or equal"),
    CompletionItem("greater than or equal to",       "greater than or equal to ",       "comparison", "Greater than or equal"),
    CompletionItem("in",                             "in ",                             "comparison", "Membership check"),
    CompletionItem("a number",                       "a number",                        "comparison", "Type check: number"),
    CompletionItem("a text",                         "a text",                          "comparison", "Type check: text"),
    CompletionItem("a boolean",                      "a boolean",                       "comparison", "Type check: boolean"),
    CompletionItem("a list",                         "a list",                          "comparison", "Type check: list"),
    CompletionItem("a table",                        "a table",                         "comparison", "Type check: table"),
]

STATEMENT_ITEMS = [
    # Control flow
    CompletionItem("if",                "if $CURSOR",                                    "statement", "Conditional branch"),
    CompletionItem("otherwise if",      "otherwise if $CURSOR",                          "statement", "Else-if branch"),
    CompletionItem("otherwise",         "otherwise",                                     "statement", "Else branch"),
    # Loops
    CompletionItem("repeat … times",    "repeat $CURSOR times",                          "statement", "Count-based loop"),
    CompletionItem("repeat while",      "repeat while $CURSOR",                          "statement", "While loop"),
    CompletionItem("repeat for each",   "repeat for each $CURSOR in ",                   "statement", "For-each loop"),
    # I/O
    CompletionItem("display",           "display $CURSOR",                               "statement", "Print output"),
    CompletionItem("input",             "input",                                         "statement", "Read user input"),
    # Variables
    CompletionItem("set … to",          "set $CURSOR to ",                               "statement", "Assign variable"),
    # Functions
    CompletionItem("call",              "call $CURSOR",                                  "statement", "Call a step"),
    CompletionItem("return",            "return $CURSOR",                                "statement", "Return value"),
    # Error handling
    CompletionItem("attempt:",          "attempt:\n    $CURSOR\nif unsuccessful:\n    ",  "statement", "Try/catch block"),
    # Other
    CompletionItem("exit",              "exit",                                          "statement", "End program"),
    CompletionItem("clear console",     "clear console",                                 "statement", "Clear terminal"),
]

# Map abbreviated prefixes to statement items for fast lookup
# These are the "shortcut" prefixes that trigger expansion
STATEMENT_PREFIX_MAP: Dict[str, List[CompletionItem]] = {}

def _build_prefix_map():
    """Build the prefix lookup map for statement triggers."""
    # Explicit abbreviations
    abbrevs = {
        "oi":   ["otherwise if"],
        "ow":   ["otherwise"],
        "rep":  ["repeat … times", "repeat while", "repeat for each"],
        "rw":   ["repeat while"],
        "rfe":  ["repeat for each"],
        "dis":  ["display"],
        "ret":  ["return"],
        "att":  ["attempt:"],
        "cal":  ["call"],
        "inp":  ["input"],
        "cl":   ["clear console"],
    }
    
    name_map = {item.display_text: item for item in STATEMENT_ITEMS}
    
    for prefix, names in abbrevs.items():
        STATEMENT_PREFIX_MAP[prefix] = [name_map[n] for n in names if n in name_map]
    
    # Also match by natural prefix of each item's first word
    for item in STATEMENT_ITEMS:
        first_word = item.display_text.split()[0].split("…")[0].strip()
        for length in range(2, len(first_word) + 1):
            pfx = first_word[:length].lower()
            if pfx not in STATEMENT_PREFIX_MAP:
                STATEMENT_PREFIX_MAP[pfx] = []
            if item not in STATEMENT_PREFIX_MAP[pfx]:
                STATEMENT_PREFIX_MAP[pfx].append(item)

_build_prefix_map()


SNIPPET_ITEMS = [
    CompletionItem("newstep", (
        "step: $CURSOR\n"
        "    belongs to: \n"
        "    expects: nothing\n"
        "    returns: nothing\n"
        "\n"
        "    do:\n"
        "        "
    ), "snippet", "New step template"),
    
    CompletionItem("newbuild", (
        "building: $CURSOR\n"
        "    note: \n"
        "\n"
        "    floors:\n"
        "        floor: input\n"
        "            step: get_input\n"
        "        floor: output\n"
        "            step: show_output\n"
        "        floor: actions\n"
        "            step: main_action\n"
        "        floor: data\n"
        "            step: manage_data\n"
        "\n"
        "    exit\n"
    ), "snippet", "New building template"),
    
    CompletionItem("newriser", (
        "riser: $CURSOR\n"
        "    expects: nothing\n"
        "    returns: nothing\n"
        "\n"
        "    do:\n"
        "        "
    ), "snippet", "New riser template"),
]

CALL_CLAUSE_ITEMS = [
    CompletionItem("with",              "with $CURSOR",              "call_clause", "Pass arguments"),
    CompletionItem("storing result in", "storing result in $CURSOR", "call_clause", "Capture return value"),
]


# ─── Completion Engine ──────────────────────────────────────────────────────

class CompletionEngine:
    """Core logic for determining when and what to suggest.
    
    Analyzes the current line text and cursor position to determine
    if a completion trigger has been activated.
    """
    
    def __init__(self):
        self._project_steps: List[str] = []
    
    def set_project_steps(self, step_names: List[str]):
        """Update the list of known step names from the current project."""
        self._project_steps = sorted(set(step_names))
    
    def check_trigger(
        self,
        line_text: str,
        cursor_col: int,
        file_ext: str = ".step"
    ) -> Optional[List[CompletionItem]]:
        """Check if the current context should trigger completion.
        
        Args:
            line_text: Full text of the current line
            cursor_col: 0-based cursor column position
            file_ext: File extension (.step, .building)
            
        Returns:
            List of CompletionItems if triggered, None otherwise
        """
        # Get text up to cursor
        text_before = line_text[:cursor_col]
        
        # Strip leading whitespace to get the "effective" text
        stripped = text_before.lstrip()
        indent = text_before[:len(text_before) - len(stripped)]
        
        if not stripped:
            return None
        
        # 1. Check for "is " trigger (comparison operators)
        #    Match: "variable_name is " at the end of text_before
        if re.search(r'\bis\s$', text_before):
            return list(COMPARISON_ITEMS)
        
        # Also filter comparisons if user is typing after "is "
        is_match = re.search(r'\bis\s(.+)$', text_before)
        if is_match:
            typed_after_is = is_match.group(1)
            filtered = self.filter_items(COMPARISON_ITEMS, typed_after_is)
            if filtered:
                return filtered
        
        # 2. Check for "call <name> " trigger (call clauses)
        call_match = re.match(r'^call\s+(\w+)\s+(.*)$', stripped)
        if call_match:
            typed_clause = call_match.group(2)
            if typed_clause:
                return self.filter_items(CALL_CLAUSE_ITEMS, typed_clause)
            else:
                return list(CALL_CLAUSE_ITEMS)
        
        # 3. Check for "call " trigger (step name completion)
        call_prefix_match = re.match(r'^call\s+(\w*)$', stripped)
        if call_prefix_match:
            typed_name = call_prefix_match.group(1)
            if self._project_steps:
                step_items = [
                    CompletionItem(name, name + " ", "step", f"Step: {name}")
                    for name in self._project_steps
                ]
                if typed_name:
                    return self.filter_items(step_items, typed_name)
                return step_items
        
        # 4. Check for snippet triggers (at line start, complete word)
        stripped_lower = stripped.lower()
        for snippet in SNIPPET_ITEMS:
            if snippet.display_text.startswith(stripped_lower) and len(stripped_lower) >= 3:
                return [snippet]
        
        # 5. Check for statement prefix triggers (at effective line start)
        #    Only trigger if the stripped text looks like a statement start
        #    (no spaces in the typed text — it's a single token)
        if ' ' not in stripped:
            stripped_lower = stripped.lower()
            # Check explicit abbreviation map first
            if stripped_lower in STATEMENT_PREFIX_MAP:
                return STATEMENT_PREFIX_MAP[stripped_lower]
            
            # Then check all statement items by prefix match
            if len(stripped_lower) >= 2:
                matches = self.filter_items(STATEMENT_ITEMS, stripped_lower)
                if matches:
                    return matches
        
        return None
    
    def get_all_suggestions(
        self,
        line_text: str,
        cursor_col: int,
        file_ext: str = ".step"
    ) -> List[CompletionItem]:
        """Get all applicable suggestions for Ctrl+Space manual trigger.
        
        Returns a broader set of suggestions than automatic mode.
        """
        text_before = line_text[:cursor_col]
        stripped = text_before.lstrip()
        
        # Start with trigger-based results
        triggered = self.check_trigger(line_text, cursor_col, file_ext)
        if triggered:
            return triggered
        
        # If no specific trigger, offer statements + snippets + steps
        all_items: List[CompletionItem] = []
        all_items.extend(STATEMENT_ITEMS)
        all_items.extend(SNIPPET_ITEMS)
        
        if self._project_steps:
            all_items.extend([
                CompletionItem(name, f"call {name} ", "step", f"Step: {name}")
                for name in self._project_steps
            ])
        
        # Filter by whatever is typed
        if stripped and ' ' not in stripped:
            return self.filter_items(all_items, stripped)
        
        return all_items
    
    @staticmethod
    def filter_items(
        items: List[CompletionItem],
        prefix: str
    ) -> List[CompletionItem]:
        """Filter items by prefix (case-insensitive)."""
        prefix_lower = prefix.lower().strip()
        if not prefix_lower:
            return list(items)
        
        results = []
        for item in items:
            display_lower = item.display_text.lower()
            # Match if display text starts with prefix
            if display_lower.startswith(prefix_lower):
                results.append(item)
            # Also match if any word in display starts with prefix
            elif any(w.startswith(prefix_lower) for w in display_lower.split()):
                results.append(item)
        
        return results


# ─── Completion Popup ───────────────────────────────────────────────────────

class CompletionPopup(QWidget):
    """Popup widget that displays completion suggestions below the cursor.
    
    Positioned relative to the parent editor widget, themed to match
    the IDE appearance. Handles keyboard navigation and selection.
    """
    
    completion_accepted = pyqtSignal(CompletionItem)
    completion_dismissed = pyqtSignal()
    
    # Maximum items to display before scrolling
    MAX_VISIBLE_ITEMS = 10
    
    def __init__(self, parent=None, theme=None):
        super().__init__(parent, Qt.WindowType.ToolTip)
        self.theme = theme
        self._items: List[CompletionItem] = []
        
        self._setup_ui()
        self._apply_theme()
        self.hide()
    
    def _setup_ui(self):
        """Set up the popup UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(0)
        
        self._list = QListWidget()
        self._list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._list.itemDoubleClicked.connect(self._on_item_double_clicked)
        
        layout.addWidget(self._list)
        
        # Description label at the bottom
        self._desc_label = QLabel()
        self._desc_label.setWordWrap(True)
        self._desc_label.setMaximumHeight(40)
        layout.addWidget(self._desc_label)
        
        self._list.currentRowChanged.connect(self._on_row_changed)
    
    def _apply_theme(self):
        """Apply theme colors to the popup."""
        if self.theme:
            bg = self.theme.editor_background
            fg = self.theme.editor_foreground
            sel_bg = self.theme.editor_selection
            border = self.theme.sidebar_border if hasattr(self.theme, 'sidebar_border') else "#3c3c3c"
        else:
            bg = "#1e1e1e"
            fg = "#d4d4d4"
            sel_bg = "#264f78"
            border = "#3c3c3c"
        
        self.setStyleSheet(f"""
            CompletionPopup {{
                background: {bg};
                border: 1px solid {border};
                border-radius: 4px;
            }}
            QListWidget {{
                background: {bg};
                color: {fg};
                border: none;
                outline: none;
                font-size: 11pt;
            }}
            QListWidget::item {{
                padding: 3px 8px;
                border: none;
            }}
            QListWidget::item:selected {{
                background: {sel_bg};
                color: {fg};
            }}
            QListWidget::item:hover {{
                background: {sel_bg};
            }}
            QLabel {{
                color: #888;
                font-size: 10pt;
                padding: 2px 8px;
                background: {bg};
                border-top: 1px solid {border};
            }}
        """)
    
    def set_theme(self, theme):
        """Update theme."""
        self.theme = theme
        self._apply_theme()
    
    def show_items(self, items: List[CompletionItem], pos: QPoint):
        """Show the popup with the given items at the given position.
        
        Args:
            items: List of completion items to display
            pos: Global position to show the popup at (below cursor)
        """
        if not items:
            self.hide()
            return
        
        self._items = items
        self._list.clear()
        
        for item in items:
            icon = CATEGORY_ICONS.get(item.category, "")
            list_item = QListWidgetItem(f"{icon} {item.display_text}")
            list_item.setData(Qt.ItemDataRole.UserRole, item)
            self._list.addItem(list_item)
        
        # Select first item
        self._list.setCurrentRow(0)
        
        # Size the popup
        visible_count = min(len(items), self.MAX_VISIBLE_ITEMS)
        item_height = 26
        desc_height = 40
        total_height = (visible_count * item_height) + desc_height + 4
        width = 350
        
        self.setFixedSize(width, total_height)
        
        # Position: avoid going off-screen
        screen = QApplication.primaryScreen()
        if screen:
            screen_rect = screen.availableGeometry()
            x = pos.x()
            y = pos.y()
            
            # Adjust horizontal
            if x + width > screen_rect.right():
                x = screen_rect.right() - width
            
            # Adjust vertical: show above cursor if no room below
            if y + total_height > screen_rect.bottom():
                y = pos.y() - total_height - 20  # 20px for line height
            
            self.move(x, y)
        else:
            self.move(pos)
        
        self.show()
        self.raise_()
    
    def select_next(self):
        """Move selection down."""
        row = self._list.currentRow()
        if row < self._list.count() - 1:
            self._list.setCurrentRow(row + 1)
    
    def select_previous(self):
        """Move selection up."""
        row = self._list.currentRow()
        if row > 0:
            self._list.setCurrentRow(row - 1)
    
    def accept_current(self):
        """Accept the currently selected item."""
        row = self._list.currentRow()
        if 0 <= row < len(self._items):
            self.completion_accepted.emit(self._items[row])
            self.hide()
    
    def dismiss(self):
        """Dismiss the popup."""
        self.hide()
        self.completion_dismissed.emit()
    
    def current_item(self) -> Optional[CompletionItem]:
        """Get the currently selected item."""
        row = self._list.currentRow()
        if 0 <= row < len(self._items):
            return self._items[row]
        return None
    
    def _on_row_changed(self, row: int):
        """Update description when selection changes."""
        if 0 <= row < len(self._items):
            item = self._items[row]
            self._desc_label.setText(item.description)
        else:
            self._desc_label.setText("")
    
    def _on_item_double_clicked(self, list_item: QListWidgetItem):
        """Handle double-click to accept."""
        self.accept_current()
