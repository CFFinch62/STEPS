"""
Steps Language Syntax Highlighter for PyQt6
Provides syntax highlighting for the Steps programming language
"""

from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from typing import Dict, List, Tuple

from steps_ide.app.themes import Theme, SyntaxColors


# Steps Language structure keywords
STEPS_STRUCTURE_KEYWORDS = [
    'building:', 'floor:', 'floors:', 'step:', 'riser:'
]

# Steps clause keywords
STEPS_CLAUSE_KEYWORDS = [
    'belongs to:', 'expects:', 'returns:', 'declare:', 'do:',
    'attempt:', 'if unsuccessful:', 'then continue:'
]

# Steps control flow keywords
STEPS_CONTROL_KEYWORDS = [
    'if', 'otherwise if', 'otherwise', 'while', 'repeat', 'times',
    'for each', 'exit', 'in'
]

# Steps variable/assignment keywords
STEPS_VAR_KEYWORDS = [
    'set', 'to', 'as', 'fixed', 'from', 'iteration', 'limit'
]

# Steps function keywords
STEPS_FUNCTION_KEYWORDS = [
    'call', 'with', 'return', 'storing result in'
]

# Steps builtin functions (multi-word entries must come before single-word)
STEPS_BUILTINS = [
    'clear console',
    'display', 'indicate', 'input', 'console'
]

# Steps list operations
STEPS_LIST_KEYWORDS = [
    'add', 'remove'
]

# Steps types
STEPS_TYPES = [
    'number', 'text', 'boolean', 'list', 'table', 'decimal'
]

# Steps boolean constants
STEPS_BOOLEANS = [
    'true', 'false', 'nothing'
]

# Steps boolean operators
STEPS_BOOL_OPERATORS = [
    'and', 'or', 'not'
]

# Steps multi-word comparison / expression operators
STEPS_COMPARISON_OPERATORS = [
    'is greater than or equal to',
    'is less than or equal to',
    'is not equal to',
    'is greater than',
    'is less than',
    'is a boolean',
    'is a number',
    'is a table',
    'is a list',
    'is a text',
    'is equal to',
    'type of',
    'length of',
    'added to',
    'starts with',
    'ends with',
    'split by',
    'character at',
    'is in',
    'contains',
    'equals',
    'modulo'
]


class StepsHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for the Steps programming language"""
    
    def __init__(self, parent=None, theme: Theme = None):
        super().__init__(parent)
        self.theme = theme
        self._formats: Dict[str, QTextCharFormat] = {}
        self._rules: List[Tuple[QRegularExpression, str]] = []
        
        self._setup_formats()
        self._setup_rules()
    
    def set_theme(self, theme: Theme):
        """Update the theme and recreate formats"""
        self.theme = theme
        self._setup_formats()
        self.rehighlight()
    
    def _setup_formats(self):
        """Set up text formats based on theme colors"""
        if self.theme is None:
            from steps_ide.app.themes import DARK_THEME
            self.theme = DARK_THEME
        
        colors = self.theme.syntax
        
        # Structure keyword format (building:, floor:, etc.)
        structure_fmt = QTextCharFormat()
        structure_fmt.setForeground(QColor(colors.keyword))
        structure_fmt.setFontWeight(QFont.Weight.Bold)
        self._formats['structure'] = structure_fmt
        
        # Clause format
        clause_fmt = QTextCharFormat()
        clause_fmt.setForeground(QColor(colors.keyword))
        self._formats['clause'] = clause_fmt
        
        # Control flow format
        control_fmt = QTextCharFormat()
        control_fmt.setForeground(QColor(colors.keyword))
        control_fmt.setFontWeight(QFont.Weight.Bold)
        self._formats['control'] = control_fmt
        
        # Keyword format (regular keywords)
        keyword_fmt = QTextCharFormat()
        keyword_fmt.setForeground(QColor(colors.keyword))
        self._formats['keyword'] = keyword_fmt
        
        # Function keyword format
        func_kw_fmt = QTextCharFormat()
        func_kw_fmt.setForeground(QColor(colors.function))
        self._formats['function_keyword'] = func_kw_fmt
        
        # Built-in function format
        builtin_fmt = QTextCharFormat()
        builtin_fmt.setForeground(QColor(colors.builtin))
        self._formats['builtin'] = builtin_fmt
        
        # Type format
        type_fmt = QTextCharFormat()
        type_fmt.setForeground(QColor(colors.type))
        self._formats['type'] = type_fmt
        
        # String format
        string_fmt = QTextCharFormat()
        string_fmt.setForeground(QColor(colors.string))
        self._formats['string'] = string_fmt
        
        # Number format
        number_fmt = QTextCharFormat()
        number_fmt.setForeground(QColor(colors.number))
        self._formats['number'] = number_fmt
        
        # Boolean/constant format
        bool_fmt = QTextCharFormat()
        bool_fmt.setForeground(QColor(colors.constant))
        self._formats['boolean'] = bool_fmt
        
        # Comment format
        comment_fmt = QTextCharFormat()
        comment_fmt.setForeground(QColor(colors.comment))
        comment_fmt.setFontItalic(True)
        self._formats['comment'] = comment_fmt
        
        # Operator format
        operator_fmt = QTextCharFormat()
        operator_fmt.setForeground(QColor(colors.operator))
        self._formats['operator'] = operator_fmt
        
        # Word operator format (is equal to, etc.)
        word_op_fmt = QTextCharFormat()
        word_op_fmt.setForeground(QColor(colors.keyword))
        self._formats['word_operator'] = word_op_fmt
        
        # Variable format
        variable_fmt = QTextCharFormat()
        variable_fmt.setForeground(QColor(colors.variable))
        self._formats['variable'] = variable_fmt
        
        # Identifier format (default)
        identifier_fmt = QTextCharFormat()
        identifier_fmt.setForeground(QColor(colors.identifier))
        self._formats['identifier'] = identifier_fmt
    
    def _setup_rules(self):
        """Set up highlighting rules - order matters, more specific first"""
        self._rules = []
        
        # Line comments (note: ...)
        self._rules.append((QRegularExpression(r'note:.*$'), 'comment'))
        
        # Strings
        self._rules.append((QRegularExpression(r'"(?:[^"\\]|\\.)*"'), 'string'))
        
        # Structure keywords with colons
        for kw in STEPS_STRUCTURE_KEYWORDS:
            pattern = r'\b' + kw.replace(':', r':')
            self._rules.append((QRegularExpression(pattern), 'structure'))
        
        # Clause keywords
        for kw in STEPS_CLAUSE_KEYWORDS:
            pattern = r'\b' + kw.replace(':', r':').replace(' ', r'\s+')
            self._rules.append((QRegularExpression(pattern), 'clause'))
        
        # Multi-word comparison operators (before single words)
        for op in STEPS_COMPARISON_OPERATORS:
            pattern = r'\b' + op.replace(' ', r'\s+') + r'\b'
            self._rules.append((QRegularExpression(pattern), 'word_operator'))
        
        # Multi-word control keywords
        self._rules.append((QRegularExpression(r'\botherwise if\b'), 'control'))
        self._rules.append((QRegularExpression(r'\bfor each\b'), 'control'))
        
        # Single-word control keywords
        for kw in STEPS_CONTROL_KEYWORDS:
            if ' ' not in kw:  # Skip multi-word ones already handled
                self._rules.append((QRegularExpression(r'\b' + kw + r'\b'), 'control'))
        
        # Boolean operators
        for op in STEPS_BOOL_OPERATORS:
            self._rules.append((QRegularExpression(r'\b' + op + r'\b'), 'word_operator'))
        
        # Function keywords
        for kw in STEPS_FUNCTION_KEYWORDS:
            pattern = r'\b' + kw.replace(' ', r'\s+') + r'\b'
            self._rules.append((QRegularExpression(pattern), 'function_keyword'))
        
        # Variable/assignment keywords
        for kw in STEPS_VAR_KEYWORDS:
            self._rules.append((QRegularExpression(r'\b' + kw + r'\b'), 'keyword'))
        
        # List operation keywords
        for kw in STEPS_LIST_KEYWORDS:
            self._rules.append((QRegularExpression(r'\b' + kw + r'\b'), 'keyword'))
        
        # Built-in functions (multi-word entries use \s+ so they match before single words)
        for fn in STEPS_BUILTINS:
            pattern = r'\b' + fn.replace(' ', r'\s+') + r'\b'
            self._rules.append((QRegularExpression(pattern), 'builtin'))
        
        # Types
        for t in STEPS_TYPES:
            self._rules.append((QRegularExpression(r'\b' + t + r'\b'), 'type'))
        
        # Boolean literals and nothing
        for b in STEPS_BOOLEANS:
            self._rules.append((QRegularExpression(r'\b' + b + r'\b'), 'boolean'))
        
        # Numbers (integers and floats)
        self._rules.append((QRegularExpression(r'-?\b\d+\.?\d*\b'), 'number'))
        
        # Math operators
        self._rules.append((QRegularExpression(r'[+\-*/]'), 'operator'))
        
        # end note for block comments
        self._rules.append((QRegularExpression(r'\bend note\b'), 'comment'))
    
    def highlightBlock(self, text: str):
        """Highlight a single block of text"""
        # First pass: find all string and comment regions (these are "protected")
        protected_ranges = []
        
        # Collect string spans
        string_pattern = QRegularExpression(r'"(?:[^"\\]|\\.)*"')
        iterator = string_pattern.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            protected_ranges.append((match.capturedStart(), match.capturedEnd()))
        
        # Collect line comment spans
        comment_pattern = QRegularExpression(r'note:.*$')
        iterator = comment_pattern.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            protected_ranges.append((match.capturedStart(), match.capturedEnd()))
        
        # Apply all rules, but skip keyword matches that fall inside protected regions
        for pattern, format_name in self._rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                start = match.capturedStart()
                length = match.capturedLength()
                
                # String and comment rules always apply (they define the protected regions)
                if format_name in ('string', 'comment'):
                    self.setFormat(start, length, self._formats[format_name])
                else:
                    # Skip if this match starts inside a protected region
                    inside_protected = False
                    for pstart, pend in protected_ranges:
                        if pstart <= start < pend:
                            inside_protected = True
                            break
                    if not inside_protected:
                        self.setFormat(start, length, self._formats[format_name])
        
        # Handle multi-line block comments (note block: ... end note)
        self._handle_multiline_comments(text)
    
    def _handle_multiline_comments(self, text: str):
        """Handle multi-line block comments"""
        comment_start = QRegularExpression(r'note block:')
        comment_end = QRegularExpression(r'end note')
        
        self.setCurrentBlockState(0)
        
        start_index = 0
        if self.previousBlockState() != 1:
            match = comment_start.match(text)
            if match.hasMatch():
                start_index = match.capturedStart()
            else:
                start_index = -1
        
        while start_index >= 0:
            end_match = comment_end.match(text, start_index)
            if end_match.hasMatch():
                end_index = end_match.capturedStart()
                comment_length = end_index - start_index + end_match.capturedLength()
                self.setCurrentBlockState(0)
            else:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            
            self.setFormat(start_index, comment_length, self._formats['comment'])
            
            start_match = comment_start.match(text, start_index + comment_length)
            if start_match.hasMatch():
                start_index = start_match.capturedStart()
            else:
                start_index = -1


class GenericHighlighter(QSyntaxHighlighter):
    """Generic syntax highlighter for common file types"""
    
    def __init__(self, parent=None, theme: Theme = None, language: str = ""):
        super().__init__(parent)
        self.theme = theme
        self.language = language.lower()
        self._formats: Dict[str, QTextCharFormat] = {}
        self._rules: List[Tuple[QRegularExpression, str]] = []
        
        self._setup_formats()
        self._setup_rules()
    
    def set_theme(self, theme: Theme):
        """Update the theme and recreate formats"""
        self.theme = theme
        self._setup_formats()
        self.rehighlight()
    
    def _setup_formats(self):
        """Set up text formats based on theme colors"""
        if self.theme is None:
            from steps_ide.app.themes import DARK_THEME
            self.theme = DARK_THEME
        
        colors = self.theme.syntax
        
        keyword_fmt = QTextCharFormat()
        keyword_fmt.setForeground(QColor(colors.keyword))
        keyword_fmt.setFontWeight(QFont.Weight.Bold)
        self._formats['keyword'] = keyword_fmt
        
        string_fmt = QTextCharFormat()
        string_fmt.setForeground(QColor(colors.string))
        self._formats['string'] = string_fmt
        
        number_fmt = QTextCharFormat()
        number_fmt.setForeground(QColor(colors.number))
        self._formats['number'] = number_fmt
        
        comment_fmt = QTextCharFormat()
        comment_fmt.setForeground(QColor(colors.comment))
        comment_fmt.setFontItalic(True)
        self._formats['comment'] = comment_fmt
        
        function_fmt = QTextCharFormat()
        function_fmt.setForeground(QColor(colors.function))
        self._formats['function'] = function_fmt
    
    def _setup_rules(self):
        """Set up basic highlighting rules"""
        self._rules = []
        
        # Common programming constructs
        # Numbers
        self._rules.append((QRegularExpression(r'\b[0-9]+\.?[0-9]*\b'), 'number'))
        
        # Strings
        self._rules.append((QRegularExpression(r'"[^"]*"'), 'string'))
        self._rules.append((QRegularExpression(r"'[^']*'"), 'string'))
        
        # Comments (common styles)  
        self._rules.append((QRegularExpression(r'//[^\n]*'), 'comment'))
        self._rules.append((QRegularExpression(r'#[^\n]*'), 'comment'))
    
    def highlightBlock(self, text: str):
        """Highlight a single block of text"""
        for pattern, format_name in self._rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), 
                             self._formats[format_name])
