"""Steps Lexer - Tokenization Module.

The lexer converts Steps source code into a stream of tokens. It handles:
- Significant whitespace (indentation tracking with INDENT/DEDENT tokens)
- Multi-word keywords (matched longest-first)
- String literals with escape sequences
- Numbers (integers and decimals)
- Comments (note: and note block:)
- All Steps keywords and operators
"""

from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import List, Optional, Tuple

from .errors import LexerError, SourceLocation, ErrorCode, make_error


class TokenType(Enum):
    """All token types in the Steps language."""
    
    # Structure
    BUILDING = auto()          # "building:"
    FLOOR = auto()             # "floor:"
    FLOORS = auto()            # "floors:"
    STEP = auto()              # "step:"
    RISER = auto()             # "riser:"
    BELONGS_TO = auto()        # "belongs to:"
    EXPECTS = auto()           # "expects:"
    RETURNS = auto()           # "returns:"
    DECLARE = auto()           # "declare:"
    DO = auto()                # "do:"
    EXIT = auto()              # "exit"
    
    # Variables
    AS = auto()                # "as"
    FIXED = auto()             # "fixed"
    SET = auto()               # "set"
    TO = auto()                # "to"
    
    # Invocation
    CALL = auto()              # "call"
    WITH = auto()              # "with"
    STORING_RESULT_IN = auto() # "storing result in"
    RETURN = auto()            # "return"
    DISPLAY = auto()           # "display"
    INDICATE = auto()          # "indicate"
    INPUT = auto()             # "input"
    CLEAR = auto()             # "clear"
    CONSOLE = auto()           # "console"
    ITERATION = auto()         # "iteration"
    LIMIT = auto()             # "limit"
    
    # Control Flow
    IF = auto()                # "if"
    OTHERWISE_IF = auto()      # "otherwise if"
    OTHERWISE = auto()         # "otherwise"
    REPEAT = auto()            # "repeat"
    TIMES = auto()             # "times"
    FOR_EACH = auto()          # "for each"
    IN = auto()                # "in"
    WHILE = auto()             # "while"
    
    # Error Handling
    ATTEMPT = auto()           # "attempt:"
    IF_UNSUCCESSFUL = auto()   # "if unsuccessful:"
    THEN_CONTINUE = auto()     # "then continue:"
    
    # Comments
    NOTE = auto()              # "note:"
    NOTE_BLOCK = auto()        # "note block:"
    END_NOTE = auto()          # "end note"
    
    # Operators - Comparison
    IS_EQUAL_TO = auto()       # "is equal to"
    EQUALS = auto()            # "equals"
    IS_NOT_EQUAL_TO = auto()   # "is not equal to"
    IS_LESS_THAN = auto()      # "is less than"
    IS_GREATER_THAN = auto()   # "is greater than"
    IS_LESS_THAN_OR_EQUAL_TO = auto()     # "is less than or equal to"
    IS_GREATER_THAN_OR_EQUAL_TO = auto()  # "is greater than or equal to"
    
    # Operators - Boolean
    AND = auto()               # "and"
    OR = auto()                # "or"
    NOT = auto()               # "not"
    
    # Operators - Text
    ADDED_TO = auto()          # "added to"
    SPLIT_BY = auto()          # "split by"
    CHARACTER_AT = auto()      # "character at"
    LENGTH_OF = auto()         # "length of"
    CONTAINS = auto()          # "contains"
    STARTS_WITH = auto()       # "starts with"
    ENDS_WITH = auto()         # "ends with"
    OF = auto()                # "of"
    
    # Operators - List
    ADD = auto()               # "add"
    REMOVE = auto()            # "remove"
    FROM = auto()              # "from"
    IS_IN = auto()             # "is in"
    
    # Type checking
    TYPE_OF = auto()           # "type of"
    IS_A_NUMBER = auto()       # "is a number"
    IS_A_TEXT = auto()         # "is a text"
    IS_A_BOOLEAN = auto()      # "is a boolean"
    IS_A_LIST = auto()         # "is a list"
    IS_A_TABLE = auto()        # "is a table"
    
    # Operators - Math
    PLUS = auto()              # "+"
    MINUS = auto()             # "-"
    MULTIPLY = auto()          # "*"
    DIVIDE = auto()            # "/"
    MODULO = auto()            # "modulo" or "%"
    
    # Punctuation
    COLON = auto()             # ":"
    COMMA = auto()             # ","
    LBRACKET = auto()          # "["
    RBRACKET = auto()          # "]"
    LPAREN = auto()            # "("
    RPAREN = auto()            # ")"
    
    # Literals
    NUMBER = auto()            # 42, 3.14
    TEXT = auto()              # "hello"
    TRUE = auto()              # "true"
    FALSE = auto()             # "false"
    NOTHING = auto()           # "nothing"
    
    # Types
    TYPE_NUMBER = auto()       # "number"
    TYPE_TEXT = auto()         # "text"
    TYPE_BOOLEAN = auto()      # "boolean"
    TYPE_LIST = auto()         # "list"
    TYPE_TABLE = auto()        # "table"
    
    # Whitespace and Structure
    IDENTIFIER = auto()        # variable/step names
    NEWLINE = auto()           # end of line
    INDENT = auto()            # increase in indentation
    DEDENT = auto()            # decrease in indentation
    EOF = auto()               # end of file


@dataclass
class Token:
    """A single token from the source code.
    
    Attributes:
        type: The type of token
        value: The original text (or processed value for strings)
        line: 1-indexed line number
        column: 1-indexed column number
        file: Source file path
    """
    type: TokenType
    value: str
    line: int
    column: int
    file: Path
    
    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, L{self.line}:C{self.column})"


# Multi-word keywords - MUST be sorted by length (longest first) for correct matching
MULTI_WORD_KEYWORDS: List[Tuple[str, TokenType]] = [
    # Length 8+ words
    ("is greater than or equal to", TokenType.IS_GREATER_THAN_OR_EQUAL_TO),
    ("is less than or equal to", TokenType.IS_LESS_THAN_OR_EQUAL_TO),
    ("storing result in", TokenType.STORING_RESULT_IN),
    ("if unsuccessful:", TokenType.IF_UNSUCCESSFUL),
    ("is not equal to", TokenType.IS_NOT_EQUAL_TO),
    ("then continue:", TokenType.THEN_CONTINUE),
    ("is greater than", TokenType.IS_GREATER_THAN),
    ("is less than", TokenType.IS_LESS_THAN),
    ("is a boolean", TokenType.IS_A_BOOLEAN),
    ("is a number", TokenType.IS_A_NUMBER),
    ("is a table", TokenType.IS_A_TABLE),
    ("is a list", TokenType.IS_A_LIST),
    ("is a text", TokenType.IS_A_TEXT),
    ("is equal to", TokenType.IS_EQUAL_TO),
    ("character at", TokenType.CHARACTER_AT),
    ("otherwise if", TokenType.OTHERWISE_IF),
    ("note block:", TokenType.NOTE_BLOCK),
    ("belongs to:", TokenType.BELONGS_TO),
    ("starts with", TokenType.STARTS_WITH),
    ("ends with", TokenType.ENDS_WITH),
    ("length of", TokenType.LENGTH_OF),
    ("type of", TokenType.TYPE_OF),
    ("for each", TokenType.FOR_EACH),
    ("added to", TokenType.ADDED_TO),
    ("split by", TokenType.SPLIT_BY),
    ("end note", TokenType.END_NOTE),
    ("is in", TokenType.IS_IN),
]

# Single-word keywords
KEYWORDS = {
    # Structure (with colon)
    "building": TokenType.BUILDING,
    "floor": TokenType.FLOOR,
    "floors": TokenType.FLOORS,
    "step": TokenType.STEP,
    "riser": TokenType.RISER,
    "expects": TokenType.EXPECTS,
    "returns": TokenType.RETURNS,
    "declare": TokenType.DECLARE,
    "do": TokenType.DO,
    "exit": TokenType.EXIT,
    "attempt": TokenType.ATTEMPT,
    "note": TokenType.NOTE,
    
    # Variables
    "as": TokenType.AS,
    "fixed": TokenType.FIXED,
    "set": TokenType.SET,
    "to": TokenType.TO,
    
    # Invocation
    "call": TokenType.CALL,
    "with": TokenType.WITH,
    "return": TokenType.RETURN,
    "display": TokenType.DISPLAY,
    "indicate": TokenType.INDICATE,
    "input": TokenType.INPUT,
    "clear": TokenType.CLEAR,
    "console": TokenType.CONSOLE,
    "iteration": TokenType.ITERATION,
    "limit": TokenType.LIMIT,
    
    # Control Flow
    "if": TokenType.IF,
    "otherwise": TokenType.OTHERWISE,
    "repeat": TokenType.REPEAT,
    "times": TokenType.TIMES,
    "in": TokenType.IN,
    "while": TokenType.WHILE,
    
    # Boolean Operators
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
    
    # Text Operators
    "contains": TokenType.CONTAINS,
    "of": TokenType.OF,
    
    # List Operators
    "add": TokenType.ADD,
    "remove": TokenType.REMOVE,
    "from": TokenType.FROM,
    
    # Comparison
    "equals": TokenType.EQUALS,
    
    # Math operators (word-based)
    "modulo": TokenType.MODULO,
    
    # Literals
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "nothing": TokenType.NOTHING,
    
    # Types
    "number": TokenType.TYPE_NUMBER,
    "text": TokenType.TYPE_TEXT,
    "boolean": TokenType.TYPE_BOOLEAN,
    "list": TokenType.TYPE_LIST,
    "table": TokenType.TYPE_TABLE,
}

# Keywords that expect a colon immediately after
COLON_KEYWORDS = {
    "building", "floor", "floors", "step", "riser", "expects", "returns",
    "declare", "do", "attempt", "note"
}


class Lexer:
    """Tokenizer for Steps source code.
    
    Converts source text into a list of tokens, handling:
    - Significant whitespace (indentation)
    - Multi-word keywords
    - String literals
    - Numbers
    - All operators and punctuation
    """
    
    def __init__(self, source: str, file_path: Path):
        """Initialize the lexer.
        
        Args:
            source: The source code to tokenize
            file_path: Path to the source file (for error messages)
        """
        self.source = source
        self.file = file_path
        self.pos = 0
        self.line = 1
        self.column = 1
        self.indent_stack: List[int] = [0]
        self.at_line_start = True
        self.tokens: List[Token] = []
    
    @property
    def current_char(self) -> str:
        """Get the current character, or null if at end."""
        if self.pos >= len(self.source):
            return '\0'
        return self.source[self.pos]
    
    def peek(self, offset: int = 1) -> str:
        """Look ahead in the source without advancing."""
        pos = self.pos + offset
        if pos >= len(self.source):
            return '\0'
        return self.source[pos]
    
    def advance(self) -> str:
        """Consume and return the current character."""
        char = self.current_char
        self.pos += 1
        if char == '\n':
            self.line += 1
            self.column = 1
            self.at_line_start = True
        else:
            self.column += 1
        return char
    
    def match_ahead(self, text: str) -> bool:
        """Check if the upcoming text matches (case-sensitive)."""
        end = self.pos + len(text)
        if end > len(self.source):
            return False
        
        # Match the text
        if self.source[self.pos:end] != text:
            return False
        
        # Ensure it's not a partial word match (for keywords)
        if end < len(self.source):
            next_char = self.source[end]
            # If the pattern ends with a letter and next char is alphanumeric, 
            # it's a partial match (e.g., "in" matching "input")
            if text[-1].isalpha() and (next_char.isalnum() or next_char == '_'):
                return False
        
        return True
    
    def skip_whitespace(self) -> None:
        """Skip spaces (not newlines or tabs)."""
        while self.current_char == ' ':
            self.advance()
    
    def make_token(self, token_type: TokenType, value: str = "") -> Token:
        """Create a token at the current position."""
        return Token(
            type=token_type,
            value=value,
            line=self.line,
            column=self.column,
            file=self.file
        )
    
    def error(self, message: str, hint: str = "") -> LexerError:
        """Create a lexer error at the current position."""
        return LexerError(
            code=ErrorCode.E101,
            message=message,
            file=self.file,
            line=self.line,
            column=self.column,
            hint=hint
        )
    
    def tokenize(self) -> List[Token]:
        """Tokenize the entire source and return list of tokens."""
        self.tokens = []
        
        while self.pos < len(self.source):
            # Handle indentation at start of line
            if self.at_line_start:
                self._handle_line_start()
            
            # Skip if we're at end after handling line start
            if self.current_char == '\0':
                break
            
            # Newline
            if self.current_char == '\n':
                self.tokens.append(Token(
                    TokenType.NEWLINE, "\n", self.line, self.column, self.file
                ))
                self.advance()
                continue
            
            # Tab error
            if self.current_char == '\t':
                raise self.error(
                    "Found a tab character. Steps uses 4 spaces for indentation, not tabs.",
                    "Configure your editor to insert spaces instead of tabs."
                )
            
            # Skip spaces (not at line start)
            if self.current_char == ' ':
                self.skip_whitespace()
                continue
            
            # String literal
            if self.current_char == '"':
                self.tokens.append(self._read_string())
                continue
            
            # Number (including negative numbers)
            if self.current_char.isdigit() or (
                self.current_char == '-' and self.peek().isdigit()
            ):
                self.tokens.append(self._read_number())
                continue
            
            # Identifier or keyword
            if self.current_char.isalpha() or self.current_char == '_':
                self.tokens.append(self._read_identifier_or_keyword())
                continue
            
            # Operators and punctuation
            if self.current_char in '+-*/%':
                self.tokens.append(self._read_operator())
                continue
            
            if self.current_char in ':,[]()':
                self.tokens.append(self._read_punctuation())
                continue
            
            # Unknown character
            raise self.error(
                f"Unexpected character '{self.current_char}'. Steps doesn't use this symbol.",
                "Check for typos or unsupported characters."
            )
        
        # Emit final DEDENTs
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token(
                TokenType.DEDENT, "", self.line, 1, self.file
            ))
        
        # Add EOF
        self.tokens.append(Token(
            TokenType.EOF, "", self.line, self.column, self.file
        ))
        
        return self.tokens
    
    def _handle_line_start(self) -> None:
        """Handle indentation at the start of a line."""
        self.at_line_start = False
        
        # Skip blank lines
        if self.current_char == '\n':
            return
        
        # Count leading spaces
        spaces = 0
        start_pos = self.pos
        while self.current_char == ' ':
            spaces += 1
            self.advance()
        
        # Skip blank lines (line with only spaces)
        if self.current_char == '\n':
            return

        # Check if this is a comment line (note: or note block:)
        # Comments should still be part of the indent structure, but we
        # don't enforce indent validation as strictly
        is_comment_line = self.match_ahead("note:") or self.match_ahead("note block:")

        # Check for tabs
        if self.current_char == '\t':
            raise self.error(
                "Found a tab character. Steps uses 4 spaces for indentation, not tabs.",
                "Configure your editor to insert spaces instead of tabs."
            )
        
        # Validate indentation is multiple of 4
        if spaces % 4 != 0:
            raise LexerError(
                code=ErrorCode.E102,
                message=f"Indentation must use exactly 4 spaces per level. Found {spaces} spaces.",
                file=self.file,
                line=self.line,
                column=1,
                hint="Use 4 spaces for each level of indentation."
            )
        
        current_indent = self.indent_stack[-1]
        
        # Indent increased
        if spaces > current_indent:
            if spaces != current_indent + 4:
                raise LexerError(
                    code=ErrorCode.E102,
                    message=f"Indentation increased by more than one level.",
                    file=self.file,
                    line=self.line,
                    column=1,
                    hint=f"Expected {current_indent + 4} spaces, found {spaces}."
                )
            self.indent_stack.append(spaces)
            self.tokens.append(Token(
                TokenType.INDENT, "", self.line, 1, self.file
            ))
        
        # Indent decreased
        elif spaces < current_indent:
            while spaces < self.indent_stack[-1]:
                self.indent_stack.pop()
                self.tokens.append(Token(
                    TokenType.DEDENT, "", self.line, 1, self.file
                ))
            
            # Check that we landed on a valid level
            if spaces != self.indent_stack[-1]:
                levels = ", ".join(str(s) for s in self.indent_stack)
                raise LexerError(
                    code=ErrorCode.E105,
                    message=f"This line's indentation ({spaces} spaces) doesn't match any previous level.",
                    file=self.file,
                    line=self.line,
                    column=1,
                    hint=f"The current indentation levels are: {levels} spaces."
                )
    
    def _read_string(self) -> Token:
        """Read a string literal, handling escape sequences."""
        start_line = self.line
        start_col = self.column
        self.advance()  # Skip opening quote
        
        value_chars: List[str] = []
        
        while self.current_char != '"':
            if self.current_char == '\n' or self.current_char == '\0':
                raise LexerError(
                    code=ErrorCode.E104,
                    message="String starting here was never closed.",
                    file=self.file,
                    line=start_line,
                    column=start_col,
                    hint='Add a closing " at the end of your string.'
                )
            
            if self.current_char == '\\':
                self.advance()  # Skip backslash
                value_chars.append(self._escape_sequence())
            else:
                value_chars.append(self.current_char)
                self.advance()
        
        self.advance()  # Skip closing quote
        return Token(TokenType.TEXT, ''.join(value_chars), start_line, start_col, self.file)
    
    def _escape_sequence(self) -> str:
        """Convert an escape sequence to its character."""
        escapes = {
            'n': '\n',
            't': '\t',
            '\\': '\\',
            '"': '"',
            'r': '\r',
        }
        
        char = self.current_char
        self.advance()
        
        if char in escapes:
            return escapes[char]
        
        raise self.error(
            f"Unknown escape sequence: \\{char}",
            f"Valid escapes are: \\n, \\t, \\\\, \\\""
        )
    
    def _read_number(self) -> Token:
        """Read a number literal (integer or decimal)."""
        start_col = self.column
        value_chars: List[str] = []
        
        # Handle negative sign
        if self.current_char == '-':
            value_chars.append('-')
            self.advance()
        
        # Read integer part
        while self.current_char.isdigit():
            value_chars.append(self.current_char)
            self.advance()
        
        # Read decimal part
        if self.current_char == '.' and self.peek().isdigit():
            value_chars.append('.')
            self.advance()
            while self.current_char.isdigit():
                value_chars.append(self.current_char)
                self.advance()
        
        return Token(TokenType.NUMBER, ''.join(value_chars), self.line, start_col, self.file)
    
    def _read_identifier_or_keyword(self) -> Token:
        """Read an identifier or keyword, checking multi-word keywords first."""
        start_col = self.column
        
        # Check multi-word keywords first (longest match)
        for keyword, token_type in MULTI_WORD_KEYWORDS:
            if self.match_ahead(keyword):
                # Consume the keyword
                for _ in range(len(keyword)):
                    self.advance()
                return Token(token_type, keyword, self.line, start_col, self.file)
        
        # Read single identifier
        value_chars: List[str] = []
        while self.current_char.isalnum() or self.current_char == '_':
            value_chars.append(self.current_char)
            self.advance()
        
        value = ''.join(value_chars)
        
        # Check if we need a colon for structure keywords
        if value in COLON_KEYWORDS:
            # Skip any spaces before colon
            while self.current_char == ' ':
                self.advance()
            if self.current_char == ':':
                self.advance()  # Consume the colon
                # Return the appropriate token type
                if value == "building":
                    return Token(TokenType.BUILDING, value + ":", self.line, start_col, self.file)
                elif value == "floor":
                    return Token(TokenType.FLOOR, value + ":", self.line, start_col, self.file)
                elif value == "floors":
                    return Token(TokenType.FLOORS, value + ":", self.line, start_col, self.file)
                elif value == "step":
                    return Token(TokenType.STEP, value + ":", self.line, start_col, self.file)
                elif value == "riser":
                    return Token(TokenType.RISER, value + ":", self.line, start_col, self.file)
                elif value == "expects":
                    return Token(TokenType.EXPECTS, value + ":", self.line, start_col, self.file)
                elif value == "returns":
                    return Token(TokenType.RETURNS, value + ":", self.line, start_col, self.file)
                elif value == "declare":
                    return Token(TokenType.DECLARE, value + ":", self.line, start_col, self.file)
                elif value == "do":
                    return Token(TokenType.DO, value + ":", self.line, start_col, self.file)
                elif value == "attempt":
                    return Token(TokenType.ATTEMPT, value + ":", self.line, start_col, self.file)
                elif value == "note":
                    # Read the rest of the line as comment content
                    return self._read_note_content(start_col)
        
        # Check single-word keywords
        token_type = KEYWORDS.get(value, TokenType.IDENTIFIER)
        return Token(token_type, value, self.line, start_col, self.file)
    
    def _read_note_content(self, start_col: int) -> Token:
        """Read a note comment to end of line."""
        self.skip_whitespace()
        
        content_chars: List[str] = []
        while self.current_char != '\n' and self.current_char != '\0':
            content_chars.append(self.current_char)
            self.advance()
        
        return Token(TokenType.NOTE, ''.join(content_chars).strip(), self.line, start_col, self.file)
    
    def _read_operator(self) -> Token:
        """Read a math operator."""
        start_col = self.column
        char = self.current_char
        self.advance()
        
        if char == '+':
            return Token(TokenType.PLUS, '+', self.line, start_col, self.file)
        elif char == '-':
            return Token(TokenType.MINUS, '-', self.line, start_col, self.file)
        elif char == '*':
            return Token(TokenType.MULTIPLY, '*', self.line, start_col, self.file)
        elif char == '/':
            return Token(TokenType.DIVIDE, '/', self.line, start_col, self.file)
        elif char == '%':
            return Token(TokenType.MODULO, '%', self.line, start_col, self.file)

        # Should not reach here
        raise self.error(f"Unknown operator: {char}")
    
    def _read_punctuation(self) -> Token:
        """Read punctuation."""
        start_col = self.column
        char = self.current_char
        self.advance()
        
        if char == ':':
            return Token(TokenType.COLON, ':', self.line, start_col, self.file)
        elif char == ',':
            return Token(TokenType.COMMA, ',', self.line, start_col, self.file)
        elif char == '[':
            return Token(TokenType.LBRACKET, '[', self.line, start_col, self.file)
        elif char == ']':
            return Token(TokenType.RBRACKET, ']', self.line, start_col, self.file)
        elif char == '(':
            return Token(TokenType.LPAREN, '(', self.line, start_col, self.file)
        elif char == ')':
            return Token(TokenType.RPAREN, ')', self.line, start_col, self.file)
        
        # Should not reach here
        raise self.error(f"Unknown punctuation: {char}")


def tokenize(source: str, file_path: Optional[Path] = None) -> List[Token]:
    """Convenience function to tokenize source code.
    
    Args:
        source: The source code to tokenize
        file_path: Optional path for error messages
    
    Returns:
        List of tokens
    """
    if file_path is None:
        file_path = Path("<string>")
    
    lexer = Lexer(source, file_path)
    return lexer.tokenize()


def tokenize_for_debug(source: str) -> None:
    """Tokenize and print tokens for debugging."""
    tokens = tokenize(source)
    for token in tokens:
        print(f"{token.type.name:30} | {token.value!r:20} | L{token.line}:C{token.column}")
