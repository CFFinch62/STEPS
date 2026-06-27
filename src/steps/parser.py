"""Steps Parser - Recursive Descent Parser.

The parser transforms a stream of tokens into an Abstract Syntax Tree (AST).
It implements a recursive descent parser with the following capabilities:

- Parses building, floor, and step files
- Handles all statement types
- Parses expressions with correct operator precedence
- Collects multiple errors during a single parse
- Provides educational error messages
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional, Tuple, Union

from .ast_nodes import (
    # Top-level nodes
    ASTNode, BuildingNode, FloorNode, StepNode, RiserNode,
    # Declaration nodes
    ParameterNode, ReturnDeclaration, DeclarationNode,
    # Statement nodes
    StatementNode, DisplayStatement, SetStatement, SetIndexStatement, CallStatement,
    ReturnStatement, ExitStatement, IfStatement, IfBranch,
    RepeatTimesStatement, RepeatForEachStatement, RepeatWhileStatement,
    AttemptStatement, NoteStatement, AddToListStatement, RemoveFromListStatement,
    # Expression nodes
    ExpressionNode, NumberLiteral, TextLiteral, BooleanLiteral, NothingLiteral,
    ListLiteral, TableLiteral, IdentifierNode, InputNode,
    BinaryOpNode, UnaryOpNode, TypeConversionNode, TypeOfNode, TypeCheckNode, TableAccessNode,
    AddedToNode, SplitByNode, CharacterAtNode, LengthOfNode,
    ContainsNode, StartsWithNode, EndsWithNode, IsInNode,
    FormatNumberNode,
)
from .errors import ParseError, StepsError, SourceLocation, ErrorCode
from .lexer import Token, TokenType, Lexer


@dataclass
class ParseResult:
    """Result of parsing, containing AST and any errors."""
    ast: Optional[ASTNode]
    errors: List[StepsError] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0 and self.ast is not None


class Parser:
    """Recursive descent parser for Steps language.
    
    Transforms a list of tokens into an AST, collecting errors
    along the way for educational error reporting.
    """
    
    def __init__(self, tokens: List[Token], file_path: Path):
        """Initialize the parser.
        
        Args:
            tokens: List of tokens from the lexer
            file_path: Path to source file for error messages
        """
        self.tokens = tokens
        self.file = file_path
        self.pos = 0
        self.errors: List[StepsError] = []
    
    # =========================================================================
    # Token Navigation
    # =========================================================================
    
    @property
    def current(self) -> Token:
        """Get the current token."""
        if self.pos >= len(self.tokens):
            return self.tokens[-1]  # Return EOF
        return self.tokens[self.pos]
    
    @property
    def previous(self) -> Token:
        """Get the previous token."""
        if self.pos > 0:
            return self.tokens[self.pos - 1]
        return self.tokens[0]
    
    def peek(self, offset: int = 1) -> Token:
        """Look ahead without consuming."""
        pos = self.pos + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[pos]
    
    def advance(self) -> Token:
        """Consume and return current token."""
        token = self.current
        if not self.is_at_end():
            self.pos += 1
        return token
    
    def is_at_end(self) -> bool:
        """Check if we've reached the end of tokens."""
        return self.current.type == TokenType.EOF
    
    def check(self, *types: TokenType) -> bool:
        """Check if current token matches any of the given types."""
        return self.current.type in types
    
    def match(self, *types: TokenType) -> bool:
        """If current token matches, consume it and return True."""
        if self.check(*types):
            self.advance()
            return True
        return False
    
    def expect(self, token_type: TokenType, message: str) -> Token:
        """Expect a specific token type, or report an error."""
        if self.check(token_type):
            return self.advance()
        
        self.error(message)
        # Return a dummy token to continue parsing
        return Token(token_type, "", self.current.line, self.current.column, self.file)
    
    def skip_newlines(self) -> None:
        """Skip any newline tokens."""
        while self.match(TokenType.NEWLINE):
            pass
    
    def location(self) -> SourceLocation:
        """Get source location from current token."""
        token = self.current
        return SourceLocation(
            file=self.file,
            line=token.line,
            column=token.column
        )
    
    def location_from(self, token: Token) -> SourceLocation:
        """Get source location from a specific token."""
        return SourceLocation(
            file=self.file,
            line=token.line,
            column=token.column
        )
    
    # =========================================================================
    # Error Handling
    # =========================================================================
    
    def error(self, message: str, hint: str = "") -> None:
        """Record a parse error at the current position."""
        err = ParseError(
            code=ErrorCode.E207,
            message=message,
            file=self.file,
            line=self.current.line,
            column=self.current.column,
            hint=hint
        )
        self.errors.append(err)
    
    def synchronize(self) -> None:
        """Recover from error by skipping to next statement."""
        self.advance()
        
        while not self.is_at_end():
            # Stop at statement boundaries
            if self.previous.type == TokenType.NEWLINE:
                # Check if next token starts a statement
                if self.check(
                    TokenType.DISPLAY, TokenType.SET, TokenType.CALL,
                    TokenType.RETURN, TokenType.EXIT, TokenType.IF,
                    TokenType.REPEAT, TokenType.ATTEMPT, TokenType.ADD,
                    TokenType.REMOVE, TokenType.NOTE, TokenType.DEDENT
                ):
                    return
            
            # Skip to structure boundaries
            if self.check(
                TokenType.BUILDING, TokenType.FLOOR, TokenType.STEP,
                TokenType.RISER, TokenType.DO, TokenType.DECLARE
            ):
                return
            
            self.advance()
    
    # =========================================================================
    # Top-Level Parsing
    # =========================================================================
    
    def parse_building(self) -> ParseResult:
        """Parse a .building file.
        
        Supports an optional 'floors:' section before the body:
        
            building: name
                [notes]
                floors:
                    floor: name1
                        step: step_a
                    floor: name2
                        step: step_b
                do:
                    ...body...
        """
        self.skip_newlines()
        
        # building: name
        start = self.current
        if not self.match(TokenType.BUILDING):
            self.error("Expected 'building:' at the start of a building file.")
            return ParseResult(None, self.errors)
        
        name_token = self.expect(TokenType.IDENTIFIER, "Expected building name after 'building:'")
        name = name_token.value
        
        self.expect(TokenType.NEWLINE, "Expected newline after building name")
        self.skip_newlines()
        
        # Expect indented body
        if not self.match(TokenType.INDENT):
            self.error("Expected indented code block after 'building:'")
            return ParseResult(None, self.errors)
        
        # Parse optional note statements before floors:/do:
        floors: List[FloorNode] = []
        pre_notes: List[StatementNode] = []
        
        while self.check(TokenType.NOTE) and not self.check(TokenType.DEDENT, TokenType.EOF):
            note_token = self.current
            self.advance()  # consume NOTE
            pre_notes.append(NoteStatement(
                location=SourceLocation(file=note_token.file, line=note_token.line, column=note_token.column),
                text=note_token.value
            ))
            self.match(TokenType.NEWLINE)
            self.skip_newlines()
        
        # Check for optional 'floors:' section
        if self.check(TokenType.FLOORS):
            self.advance()  # consume 'floors:'
            self.match(TokenType.NEWLINE)
            self.skip_newlines()
            
            # Expect indented block of floor declarations
            if self.match(TokenType.INDENT):
                floors = self._parse_floors_section()
                self.match(TokenType.DEDENT)
            
            self.skip_newlines()
        
        # Parse remaining body (may start with 'do:' or just statements)
        body: List[StatementNode] = list(pre_notes)
        
        if self.check(TokenType.DEDENT, TokenType.EOF):
            # Building with only floors and no body
            self.match(TokenType.DEDENT)
        elif self.check(TokenType.DO):
            # Optional 'do:' section header (borrowed from step file syntax)
            self.advance()  # consume 'do:'
            self.match(TokenType.NEWLINE)
            self.skip_newlines()
            if self.match(TokenType.INDENT):
                body.extend(self._parse_statements_until_dedent())
            # Consume the outer DEDENT for the building block
            self.match(TokenType.DEDENT)
        else:
            # Parse body statements until DEDENT
            body.extend(self._parse_statements_until_dedent())
        
        node = BuildingNode(
            location=self.location_from(start),
            name=name,
            floors=floors,
            body=body
        )
        
        return ParseResult(node, self.errors)
    
    def parse_floor(self) -> ParseResult:
        """Parse a floor declaration (used for standalone floor parsing)."""
        self.skip_newlines()
        
        # floor: name
        start = self.current
        if not self.match(TokenType.FLOOR):
            self.error("Expected 'floor:' at the start of a floor file.")
            return ParseResult(None, self.errors)
        
        name_token = self.expect(TokenType.IDENTIFIER, "Expected floor name after 'floor:'")
        name = name_token.value
        
        self.expect(TokenType.NEWLINE, "Expected newline after floor name")
        self.skip_newlines()
        
        # Expect indented list of steps
        if not self.match(TokenType.INDENT):
            self.error("Expected indented step list after 'floor:'")
            return ParseResult(None, self.errors)
        
        # Parse step declarations
        steps: List[str] = []
        while not self.check(TokenType.DEDENT, TokenType.EOF):
            self.skip_newlines()
            if self.check(TokenType.DEDENT, TokenType.EOF):
                break
            
            # step: step_name
            if self.match(TokenType.STEP):
                step_name = self.expect(TokenType.IDENTIFIER, "Expected step name after 'step:'")
                steps.append(step_name.value)
                self.match(TokenType.NEWLINE)
            else:
                self.error(f"Expected 'step:' declaration, found '{self.current.value}'")
                self.advance()
        
        self.match(TokenType.DEDENT)
        
        node = FloorNode(
            location=self.location_from(start),
            name=name,
            steps=steps
        )
        
        return ParseResult(node, self.errors)
    
    def _parse_floors_section(self) -> List[FloorNode]:
        """Parse the contents of a 'floors:' section inside a building file.
        
        Expects to be called after the INDENT following 'floors:' has been consumed.
        Parses one or more 'floor:' declarations, each with indented 'step:' lists.
        
        Returns:
            List of FloorNode objects
        """
        floors: List[FloorNode] = []
        
        while not self.check(TokenType.DEDENT, TokenType.EOF):
            self.skip_newlines()
            if self.check(TokenType.DEDENT, TokenType.EOF):
                break
            
            if not self.check(TokenType.FLOOR):
                self.error(f"Expected 'floor:' declaration in floors section, found '{self.current.value}'")
                self.advance()
                continue
            
            # floor: name
            floor_start = self.current
            self.advance()  # consume FLOOR token
            
            floor_name_token = self.expect(TokenType.IDENTIFIER, "Expected floor name after 'floor:'")
            floor_name = floor_name_token.value
            
            self.match(TokenType.NEWLINE)
            self.skip_newlines()
            
            # Parse indented step declarations
            steps: List[str] = []
            if self.match(TokenType.INDENT):
                while not self.check(TokenType.DEDENT, TokenType.EOF):
                    self.skip_newlines()
                    if self.check(TokenType.DEDENT, TokenType.EOF):
                        break
                    
                    if self.match(TokenType.STEP):
                        step_name = self.expect(TokenType.IDENTIFIER, "Expected step name after 'step:'")
                        steps.append(step_name.value)
                        self.match(TokenType.NEWLINE)
                    else:
                        self.error(f"Expected 'step:' declaration, found '{self.current.value}'")
                        self.advance()
                
                self.match(TokenType.DEDENT)
            
            floor_node = FloorNode(
                location=self.location_from(floor_start),
                name=floor_name,
                steps=steps
            )
            floors.append(floor_node)
            
            self.skip_newlines()
        
        return floors
    
    def parse_step(self) -> ParseResult:
        """Parse a .step file."""
        self.skip_newlines()
        
        # step: name
        start = self.current
        if not self.match(TokenType.STEP):
            self.error("Expected 'step:' at the start of a step file.")
            return ParseResult(None, self.errors)
        
        name_token = self.expect(TokenType.IDENTIFIER, "Expected step name after 'step:'")
        name = name_token.value
        
        self.expect(TokenType.NEWLINE, "Expected newline after step name")
        self.skip_newlines()
        
        # Expect indented body
        if not self.match(TokenType.INDENT):
            self.error("Expected indented block after 'step:'")
            return ParseResult(None, self.errors)
        
        # Parse step sections
        belongs_to = ""
        expects: List[ParameterNode] = []
        returns: Optional[ReturnDeclaration] = None
        risers: List[RiserNode] = []
        declarations: List[DeclarationNode] = []
        body: List[StatementNode] = []
        
        while not self.check(TokenType.DEDENT, TokenType.EOF):
            self.skip_newlines()
            if self.check(TokenType.DEDENT, TokenType.EOF):
                break
            
            # belongs to: floor_name
            if self.match(TokenType.BELONGS_TO):
                belongs_token = self.expect(TokenType.IDENTIFIER, "Expected floor name after 'belongs to:'")
                belongs_to = belongs_token.value
                self.match(TokenType.NEWLINE)
            
            # expects: parameters
            elif self.match(TokenType.EXPECTS):
                expects = self.parse_parameters()
                self.match(TokenType.NEWLINE)
            
            # returns: name [as type]
            elif self.match(TokenType.RETURNS):
                returns = self.parse_return_declaration()
                self.match(TokenType.NEWLINE)
            
            # declare: block
            elif self.match(TokenType.DECLARE):
                self.match(TokenType.NEWLINE)
                declarations = self.parse_declarations()
            
            # riser: name
            elif self.match(TokenType.RISER):
                riser = self.parse_riser()
                risers.append(riser)
            
            # do: block
            elif self.match(TokenType.DO):
                self.match(TokenType.NEWLINE)
                body = self.parse_do_block()

            # note: comment (skip notes in step header)
            elif self.match(TokenType.NOTE):
                self.match(TokenType.NEWLINE)

            else:
                self.error(f"Unexpected '{self.current.value}' in step definition")
                self.advance()
        
        self.match(TokenType.DEDENT)
        
        node = StepNode(
            location=self.location_from(start),
            name=name,
            belongs_to=belongs_to,
            expects=expects,
            returns=returns,
            risers=risers,
            declarations=declarations,
            body=body
        )
        
        return ParseResult(node, self.errors)
    
    # =========================================================================
    # Step Components
    # =========================================================================
    
    def parse_parameters(self) -> List[ParameterNode]:
        """Parse parameter list (expects: a, b as number, c)."""
        params: List[ParameterNode] = []
        
        # Check for 'nothing'
        if self.match(TokenType.NOTHING):
            return params
        
        while True:
            if self.check(TokenType.NEWLINE, TokenType.EOF):
                break
            
            name_token = self.expect(TokenType.IDENTIFIER, "Expected parameter name")
            name = name_token.value
            type_annotation: Optional[str] = None
            
            # Optional type annotation: as type
            if self.match(TokenType.AS):
                type_token = self.advance()
                type_annotation = type_token.value
            
            params.append(ParameterNode(
                location=self.location_from(name_token),
                name=name,
                type_annotation=type_annotation
            ))
            
            if not self.match(TokenType.COMMA):
                break
        
        return params
    
    def parse_return_declaration(self) -> Optional[ReturnDeclaration]:
        """Parse return declaration (returns: name as type)."""
        # Check for 'nothing'
        if self.match(TokenType.NOTHING):
            return None
        
        name_token = self.expect(TokenType.IDENTIFIER, "Expected return value name")
        type_annotation: Optional[str] = None
        
        if self.match(TokenType.AS):
            type_token = self.advance()
            type_annotation = type_token.value
        
        return ReturnDeclaration(
            location=self.location_from(name_token),
            name=name_token.value,
            type_annotation=type_annotation
        )
    
    def parse_declarations(self) -> List[DeclarationNode]:
        """Parse declaration block."""
        declarations: List[DeclarationNode] = []
        
        if not self.match(TokenType.INDENT):
            return declarations
        
        while not self.check(TokenType.DEDENT, TokenType.EOF):
            self.skip_newlines()
            if self.check(TokenType.DEDENT, TokenType.EOF):
                break
            
            # Skip notes (comments) in declaration block
            if self.match(TokenType.NOTE):
                self.match(TokenType.NEWLINE)
                continue
            
            # name as type [fixed]
            name_token = self.expect(TokenType.IDENTIFIER, "Expected variable name in declaration")
            self.expect(TokenType.AS, "Expected 'as' after variable name")
            
            type_token = self.advance()
            type_name = type_token.value
            
            is_fixed = self.match(TokenType.FIXED)
            
            declarations.append(DeclarationNode(
                location=self.location_from(name_token),
                name=name_token.value,
                type_name=type_name,
                is_fixed=is_fixed
            ))
            
            self.match(TokenType.NEWLINE)
        
        self.match(TokenType.DEDENT)
        return declarations
    
    def parse_do_block(self) -> List[StatementNode]:
        """Parse the do: block of a step."""
        return self.parse_statement_block()
    
    def parse_riser(self) -> RiserNode:
        """Parse a riser definition."""
        start = self.previous  # Already consumed RISER
        
        name_token = self.expect(TokenType.IDENTIFIER, "Expected riser name")
        name = name_token.value
        
        self.expect(TokenType.NEWLINE, "Expected newline after riser name")
        self.skip_newlines()
        
        if not self.match(TokenType.INDENT):
            self.error("Expected indented block after riser declaration")
            return RiserNode(location=self.location_from(start), name=name)
        
        expects: List[ParameterNode] = []
        returns: Optional[ReturnDeclaration] = None
        declarations: List[DeclarationNode] = []
        body: List[StatementNode] = []
        
        while not self.check(TokenType.DEDENT, TokenType.EOF):
            self.skip_newlines()
            if self.check(TokenType.DEDENT, TokenType.EOF):
                break
            
            if self.match(TokenType.EXPECTS):
                expects = self.parse_parameters()
                self.match(TokenType.NEWLINE)
            elif self.match(TokenType.RETURNS):
                returns = self.parse_return_declaration()
                self.match(TokenType.NEWLINE)
            elif self.match(TokenType.DECLARE):
                self.match(TokenType.NEWLINE)
                declarations = self.parse_declarations()
            elif self.match(TokenType.DO):
                self.match(TokenType.NEWLINE)
                body = self.parse_statement_block()
            elif self.match(TokenType.NOTE):
                # Skip notes in riser header
                self.match(TokenType.NEWLINE)
            else:
                self.error(f"Unexpected '{self.current.value}' in riser definition")
                self.advance()
        
        self.match(TokenType.DEDENT)
        
        return RiserNode(
            location=self.location_from(start),
            name=name,
            expects=expects,
            returns=returns,
            declarations=declarations,
            body=body
        )
    
    # =========================================================================
    # Statement Parsing
    # =========================================================================
    
    def parse_repl_statements(self) -> List[StatementNode]:
        """Parse REPL input as a list of statements.

        Unlike parsing a full step/building, this:
        - Doesn't expect step/floor/building declarations
        - Parses raw statements directly
        - Handles multiline blocks (if/repeat)
        """
        statements: List[StatementNode] = []

        while not self.match(TokenType.EOF):
            self.skip_newlines()
            if self.check(TokenType.EOF):
                break

            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)

        return statements

    def parse_statement_block(self) -> List[StatementNode]:
        """Parse an indented block of statements (expects INDENT token)."""
        statements: List[StatementNode] = []

        if not self.match(TokenType.INDENT):
            # Block may not be indented if it's empty
            return statements

        return self._parse_statements_until_dedent()

    def _parse_statements_until_dedent(self) -> List[StatementNode]:
        """Parse statements until we hit DEDENT (already inside indented block)."""
        statements: List[StatementNode] = []
        
        while not self.check(TokenType.DEDENT, TokenType.EOF):
            self.skip_newlines()
            if self.check(TokenType.DEDENT, TokenType.EOF):
                break
            
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        
        self.match(TokenType.DEDENT)
        return statements
    
    def parse_statement(self) -> Optional[StatementNode]:
        """Parse a single statement."""
        # Skip blank lines
        self.skip_newlines()
        
        if self.check(TokenType.DEDENT, TokenType.EOF):
            return None
        
        # display expression
        if self.match(TokenType.DISPLAY):
            return self.parse_display()

        # indicate expression (display without newline)
        if self.match(TokenType.INDICATE):
            return self.parse_indicate()

        # clear console
        if self.match(TokenType.CLEAR):
            return self.parse_clear()

        # set target to value OR set iteration limit to value
        if self.match(TokenType.SET):
            return self.parse_set()
        
        # call step_name [with args] [storing result in var]
        if self.match(TokenType.CALL):
            return self.parse_call()
        
        # return [value]
        if self.match(TokenType.RETURN):
            return self.parse_return()
        
        # exit
        if self.match(TokenType.EXIT):
            return self.parse_exit()
        
        # if condition
        if self.match(TokenType.IF):
            return self.parse_if()
        
        # repeat ...
        if self.match(TokenType.REPEAT):
            return self.parse_repeat()
        
        # attempt:
        if self.match(TokenType.ATTEMPT):
            return self.parse_attempt()
        
        # add item to list
        if self.match(TokenType.ADD):
            return self.parse_add_to_list()
        
        # remove item from list
        if self.match(TokenType.REMOVE):
            return self.parse_remove_from_list()
        
        # note: comment
        if self.match(TokenType.NOTE):
            return self.parse_note()
        
        # note block: ... end note (multi-line comment)
        if self.match(TokenType.NOTE_BLOCK):
            return self.parse_note_block()
        
        # Unknown statement
        self.error(f"Expected statement, found '{self.current.value}'")
        self.synchronize()
        return None
    
    def parse_display(self) -> DisplayStatement:
        """Parse: display expression"""
        start = self.previous
        expr = self.parse_expression()
        self.match(TokenType.NEWLINE)

        return DisplayStatement(
            location=self.location_from(start),
            expression=expr
        )

    def parse_indicate(self) -> "IndicateStatement":
        """Parse: indicate expression"""
        from .ast_nodes import IndicateStatement
        start = self.previous
        expr = self.parse_expression()
        self.match(TokenType.NEWLINE)

        return IndicateStatement(
            location=self.location_from(start),
            expression=expr
        )

    def parse_clear(self) -> "ClearConsoleStatement":
        """Parse: clear console"""
        from .ast_nodes import ClearConsoleStatement
        start = self.previous
        self.expect(TokenType.CONSOLE, "Expected 'console' after 'clear'")
        self.match(TokenType.NEWLINE)

        return ClearConsoleStatement(
            location=self.location_from(start)
        )

    def parse_set(self) -> Union[SetStatement, "SetIterationLimitStatement", SetIndexStatement]:
        """Parse: set target to value OR set target[index] to value OR set iteration limit to value"""
        from .ast_nodes import SetIterationLimitStatement
        start = self.previous

        # Check for "set iteration limit to value"
        if self.check(TokenType.ITERATION):
            self.advance()  # consume 'iteration'
            self.expect(TokenType.LIMIT, "Expected 'limit' after 'iteration'")
            self.expect(TokenType.TO, "Expected 'to' after 'limit'")
            limit_expr = self.parse_expression()
            self.match(TokenType.NEWLINE)

            return SetIterationLimitStatement(
                location=self.location_from(start),
                limit=limit_expr
            )

        target_token = self.expect(TokenType.IDENTIFIER, "Expected variable name after 'set'")

        # Check for bracket notation: set target[index] to value
        if self.match(TokenType.LBRACKET):
            index_expr = self.parse_expression()
            self.expect(TokenType.RBRACKET, "Expected ']' after index")

            self.expect(TokenType.TO, "Expected 'to' after ']'")
            value = self.parse_expression()
            self.match(TokenType.NEWLINE)

            return SetIndexStatement(
                location=self.location_from(start),
                target=target_token.value,
                index=index_expr,
                value=value
            )

        # Normal assignment: set target to value
        self.expect(TokenType.TO, "Expected 'to' after variable name")
        value = self.parse_expression()
        self.match(TokenType.NEWLINE)

        return SetStatement(
            location=self.location_from(start),
            target=target_token.value,
            value=value
        )
    
    def parse_call(self) -> CallStatement:
        """Parse: call step_name [with args] [storing result in var]"""
        start = self.previous
        
        step_token = self.expect(TokenType.IDENTIFIER, "Expected step name after 'call'")
        step_name = step_token.value
        
        arguments: List[ExpressionNode] = []
        result_target: Optional[str] = None
        
        # with arg1, arg2, ...
        if self.match(TokenType.WITH):
            arguments = self.parse_argument_list()
        
        # storing result in var
        if self.match(TokenType.STORING_RESULT_IN):
            result_token = self.expect(TokenType.IDENTIFIER, "Expected variable name after 'storing result in'")
            result_target = result_token.value
        
        self.match(TokenType.NEWLINE)
        
        return CallStatement(
            location=self.location_from(start),
            step_name=step_name,
            arguments=arguments,
            result_target=result_target
        )
    
    def parse_argument_list(self) -> List[ExpressionNode]:
        """Parse comma-separated argument expressions."""
        args: List[ExpressionNode] = []
        
        while True:
            # Stop at keywords that end the argument list
            if self.check(TokenType.STORING_RESULT_IN, TokenType.NEWLINE, TokenType.EOF):
                break
            
            arg = self.parse_expression()
            args.append(arg)
            
            if not self.match(TokenType.COMMA):
                break
        
        return args
    
    def parse_return(self) -> ReturnStatement:
        """Parse: return [value]"""
        start = self.previous
        
        value: Optional[ExpressionNode] = None
        if not self.check(TokenType.NEWLINE, TokenType.EOF, TokenType.DEDENT):
            value = self.parse_expression()
        
        self.match(TokenType.NEWLINE)
        
        return ReturnStatement(
            location=self.location_from(start),
            value=value
        )
    
    def parse_exit(self) -> ExitStatement:
        """Parse: exit"""
        start = self.previous
        self.match(TokenType.NEWLINE)
        
        return ExitStatement(location=self.location_from(start))
    
    def parse_if(self) -> IfStatement:
        """Parse: if condition ... otherwise if ... otherwise ..."""
        start = self.previous
        
        # Main if branch
        condition = self.parse_expression()
        self.match(TokenType.NEWLINE)
        body = self.parse_statement_block()
        
        if_branch = IfBranch(
            location=self.location_from(start),
            condition=condition,
            body=body
        )
        
        # Otherwise if branches
        otherwise_if_branches: List[IfBranch] = []
        while self.match(TokenType.OTHERWISE_IF):
            branch_start = self.previous
            branch_condition = self.parse_expression()
            self.match(TokenType.NEWLINE)
            branch_body = self.parse_statement_block()
            
            otherwise_if_branches.append(IfBranch(
                location=self.location_from(branch_start),
                condition=branch_condition,
                body=branch_body
            ))
        
        # Otherwise branch
        otherwise_branch: Optional[List[StatementNode]] = None
        if self.match(TokenType.OTHERWISE):
            self.match(TokenType.NEWLINE)
            otherwise_branch = self.parse_statement_block()
        
        return IfStatement(
            location=self.location_from(start),
            if_branch=if_branch,
            otherwise_if_branches=otherwise_if_branches,
            otherwise_branch=otherwise_branch
        )
    
    def parse_repeat(self) -> Union[RepeatTimesStatement, RepeatForEachStatement, RepeatWhileStatement]:
        """Parse: repeat N times | repeat for each item in list | repeat while condition"""
        start = self.previous
        
        # repeat for each item in collection
        if self.match(TokenType.FOR_EACH):
            item_token = self.expect(TokenType.IDENTIFIER, "Expected variable name after 'for each'")
            self.expect(TokenType.IN, "Expected 'in' after loop variable")
            collection = self.parse_expression()
            self.match(TokenType.NEWLINE)
            body = self.parse_statement_block()
            
            return RepeatForEachStatement(
                location=self.location_from(start),
                item_name=item_token.value,
                collection=collection,
                body=body
            )
        
        # repeat while condition
        if self.match(TokenType.WHILE):
            condition = self.parse_expression()
            self.match(TokenType.NEWLINE)
            body = self.parse_statement_block()
            
            return RepeatWhileStatement(
                location=self.location_from(start),
                condition=condition,
                body=body
            )
        
        # repeat N times
        count = self.parse_expression()
        self.expect(TokenType.TIMES, "Expected 'times' after count expression")
        self.match(TokenType.NEWLINE)
        body = self.parse_statement_block()
        
        return RepeatTimesStatement(
            location=self.location_from(start),
            count=count,
            body=body
        )
    
    def parse_attempt(self) -> AttemptStatement:
        """Parse: attempt: ... if unsuccessful: ... then continue: ..."""
        start = self.previous
        self.match(TokenType.NEWLINE)
        
        attempt_body = self.parse_statement_block()
        unsuccessful_body: Optional[List[StatementNode]] = None
        continue_body: Optional[List[StatementNode]] = None
        
        # if unsuccessful:
        if self.match(TokenType.IF_UNSUCCESSFUL):
            self.match(TokenType.NEWLINE)
            unsuccessful_body = self.parse_statement_block()
        
        # then continue:
        if self.match(TokenType.THEN_CONTINUE):
            self.match(TokenType.NEWLINE)
            continue_body = self.parse_statement_block()
        
        return AttemptStatement(
            location=self.location_from(start),
            attempt_body=attempt_body,
            unsuccessful_body=unsuccessful_body,
            continue_body=continue_body
        )
    
    def parse_add_to_list(self) -> AddToListStatement:
        """Parse: add item to list_name"""
        start = self.previous
        
        item = self.parse_expression()
        self.expect(TokenType.TO, "Expected 'to' after item in 'add' statement")
        list_token = self.expect(TokenType.IDENTIFIER, "Expected list name after 'to'")
        self.match(TokenType.NEWLINE)
        
        return AddToListStatement(
            location=self.location_from(start),
            item=item,
            list_name=list_token.value
        )
    
    def parse_remove_from_list(self) -> RemoveFromListStatement:
        """Parse: remove item from list_name"""
        start = self.previous
        
        item = self.parse_expression()
        self.expect(TokenType.FROM, "Expected 'from' after item in 'remove' statement")
        list_token = self.expect(TokenType.IDENTIFIER, "Expected list name after 'from'")
        self.match(TokenType.NEWLINE)
        
        return RemoveFromListStatement(
            location=self.location_from(start),
            item=item,
            list_name=list_token.value
        )
    
    def parse_note(self) -> NoteStatement:
        """Parse a note comment."""
        start = self.previous
        # The lexer already captured the comment text
        text = start.value
        self.match(TokenType.NEWLINE)
        
        return NoteStatement(
            location=self.location_from(start),
            text=text,
            is_block=False
        )
    
    def parse_note_block(self) -> NoteStatement:
        """Parse a multi-line note block: ... end note comment."""
        start = self.previous
        self.match(TokenType.NEWLINE)
        
        # Skip all tokens until we find END_NOTE or EOF
        while not self.check(TokenType.END_NOTE, TokenType.EOF):
            self.advance()
        
        # Consume the END_NOTE token
        if self.match(TokenType.END_NOTE):
            self.match(TokenType.NEWLINE)
        
        return NoteStatement(
            location=self.location_from(start),
            text="(block comment)",
            is_block=True
        )
    
    # =========================================================================
    # Expression Parsing (Precedence Climbing)
    # =========================================================================
    
    def parse_expression(self) -> ExpressionNode:
        """Parse an expression (entry point)."""
        return self.parse_or_expr()
    
    def parse_or_expr(self) -> ExpressionNode:
        """Parse: expr or expr"""
        left = self.parse_and_expr()
        
        while self.match(TokenType.OR):
            op = self.previous
            right = self.parse_and_expr()
            left = BinaryOpNode(
                location=self.location_from(op),
                left=left,
                operator="or",
                right=right
            )
        
        return left
    
    def parse_and_expr(self) -> ExpressionNode:
        """Parse: expr and expr"""
        left = self.parse_not_expr()
        
        while self.match(TokenType.AND):
            op = self.previous
            right = self.parse_not_expr()
            left = BinaryOpNode(
                location=self.location_from(op),
                left=left,
                operator="and",
                right=right
            )
        
        return left
    
    def parse_not_expr(self) -> ExpressionNode:
        """Parse: not expr"""
        if self.match(TokenType.NOT):
            op = self.previous
            operand = self.parse_not_expr()
            return UnaryOpNode(
                location=self.location_from(op),
                operator="not",
                operand=operand
            )
        
        return self.parse_comparison()
    
    def parse_comparison(self) -> ExpressionNode:
        """Parse comparison operators."""
        left = self.parse_addition()
        
        # Comparison operators
        comparison_ops = {
            TokenType.IS_EQUAL_TO: "is equal to",
            TokenType.IS_NOT_EQUAL_TO: "is not equal to",
            TokenType.EQUALS: "equals",
            TokenType.IS_LESS_THAN: "is less than",
            TokenType.IS_GREATER_THAN: "is greater than",
            TokenType.IS_LESS_THAN_OR_EQUAL_TO: "is less than or equal to",
            TokenType.IS_GREATER_THAN_OR_EQUAL_TO: "is greater than or equal to",
            TokenType.IS_IN: "is in",
            TokenType.CONTAINS: "contains",
            TokenType.STARTS_WITH: "starts with",
            TokenType.ENDS_WITH: "ends with",
        }
        
        for token_type, op_str in comparison_ops.items():
            if self.match(token_type):
                op = self.previous
                right = self.parse_addition()
                
                # Special handling for text operations
                if token_type == TokenType.IS_IN:
                    return IsInNode(
                        location=self.location_from(op),
                        item=left,
                        collection=right
                    )
                elif token_type == TokenType.CONTAINS:
                    return ContainsNode(
                        location=self.location_from(op),
                        text=left,
                        substring=right
                    )
                elif token_type == TokenType.STARTS_WITH:
                    return StartsWithNode(
                        location=self.location_from(op),
                        text=left,
                        prefix=right
                    )
                elif token_type == TokenType.ENDS_WITH:
                    return EndsWithNode(
                        location=self.location_from(op),
                        text=left,
                        suffix=right
                    )
                
                return BinaryOpNode(
                    location=self.location_from(op),
                    left=left,
                    operator=op_str,
                    right=right
                )
        # Type check operators (postfix): expr is a number, expr is a text, etc.
        type_check_ops = {
            TokenType.IS_A_NUMBER: "number",
            TokenType.IS_A_TEXT: "text",
            TokenType.IS_A_BOOLEAN: "boolean",
            TokenType.IS_A_LIST: "list",
            TokenType.IS_A_TABLE: "table",
        }
        
        for token_type, type_name in type_check_ops.items():
            if self.match(token_type):
                op = self.previous
                return TypeCheckNode(
                    location=self.location_from(op),
                    expression=left,
                    type_name=type_name
                )
        
        return left
    
    def parse_addition(self) -> ExpressionNode:
        """Parse: addition and subtraction, text operations."""
        left = self.parse_multiplication()
        
        while True:
            if self.match(TokenType.PLUS):
                op = self.previous
                right = self.parse_multiplication()
                left = BinaryOpNode(
                    location=self.location_from(op),
                    left=left,
                    operator="+",
                    right=right
                )
            elif self.match(TokenType.MINUS):
                op = self.previous
                right = self.parse_multiplication()
                left = BinaryOpNode(
                    location=self.location_from(op),
                    left=left,
                    operator="-",
                    right=right
                )
            elif self.match(TokenType.ADDED_TO):
                op = self.previous
                right = self.parse_multiplication()
                left = AddedToNode(
                    location=self.location_from(op),
                    left=left,
                    right=right
                )
            elif self.match(TokenType.SPLIT_BY):
                op = self.previous
                right = self.parse_multiplication()
                left = SplitByNode(
                    location=self.location_from(op),
                    text=left,
                    delimiter=right
                )
            else:
                break
        
        return left
    
    def parse_multiplication(self) -> ExpressionNode:
        """Parse: multiplication, division, and modulo."""
        left = self.parse_unary()
        
        while True:
            if self.match(TokenType.MULTIPLY):
                op = self.previous
                right = self.parse_unary()
                left = BinaryOpNode(
                    location=self.location_from(op),
                    left=left,
                    operator="*",
                    right=right
                )
            elif self.match(TokenType.DIVIDE):
                op = self.previous
                right = self.parse_unary()
                left = BinaryOpNode(
                    location=self.location_from(op),
                    left=left,
                    operator="/",
                    right=right
                )
            elif self.match(TokenType.MODULO):
                op = self.previous
                right = self.parse_unary()
                left = BinaryOpNode(
                    location=self.location_from(op),
                    left=left,
                    operator="modulo",
                    right=right
                )
            else:
                break
        
        return left
    
    def parse_unary(self) -> ExpressionNode:
        """Parse: unary minus, length of, character at."""
        # Unary minus
        if self.match(TokenType.MINUS):
            op = self.previous
            operand = self.parse_unary()
            return UnaryOpNode(
                location=self.location_from(op),
                operator="-",
                operand=operand
            )
        
        # length of expr
        if self.match(TokenType.LENGTH_OF):
            op = self.previous
            operand = self.parse_unary()
            return LengthOfNode(
                location=self.location_from(op),
                collection=operand
            )
        
        # character at index of text
        if self.match(TokenType.CHARACTER_AT):
            op = self.previous
            index = self.parse_primary()
            self.expect(TokenType.OF, "Expected 'of' after index in 'character at'")
            text = self.parse_unary()
            return CharacterAtNode(
                location=self.location_from(op),
                index=index,
                text=text
            )
        
        # type of expr
        if self.match(TokenType.TYPE_OF):
            op = self.previous
            operand = self.parse_unary()
            return TypeOfNode(
                location=self.location_from(op),
                expression=operand
            )
        
        return self.parse_postfix()
    
    def parse_postfix(self) -> ExpressionNode:
        """Parse: postfix operations ([], as type)."""
        expr = self.parse_primary()
        
        while True:
            # Table/list access: expr[key]
            if self.match(TokenType.LBRACKET):
                bracket = self.previous
                key = self.parse_expression()
                self.expect(TokenType.RBRACKET, "Expected ']' after index")
                expr = TableAccessNode(
                    location=self.location_from(bracket),
                    table=expr,
                    key=key
                )
            # Type conversion: expr as type or formatting: expr as decimal(N)
            elif self.match(TokenType.AS):
                as_token = self.previous
                
                # Check for "decimal" keyword which implies formatting
                # We need to check if the current token is "decimal" AND the next is "("
                if (self.check(TokenType.IDENTIFIER) and 
                    self.current.value == "decimal" and 
                    self.peek().type == TokenType.LPAREN):
                    
                    self.advance() # consume "decimal"
                    self.expect(TokenType.LPAREN, "Expected '(' after 'decimal'")
                    places = self.parse_expression()
                    self.expect(TokenType.RPAREN, "Expected ')' after decimal places")
                    
                    expr = FormatNumberNode(
                        location=self.location_from(as_token),
                        expression=expr,
                        decimal_places=places
                    )
                else:
                    # Standard type conversion
                    type_token = self.advance()
                    expr = TypeConversionNode(
                        location=self.location_from(as_token),
                        expression=expr,
                        target_type=type_token.value
                    )

            else:
                break
        
        return expr
    
    def parse_primary(self) -> ExpressionNode:
        """Parse: literals, identifiers, parentheses, collections."""
        # Number literal
        if self.match(TokenType.NUMBER):
            token = self.previous
            return NumberLiteral(
                location=self.location_from(token),
                value=float(token.value)
            )
        
        # Text literal
        if self.match(TokenType.TEXT):
            token = self.previous
            return TextLiteral(
                location=self.location_from(token),
                value=token.value
            )
        
        # Boolean literals
        if self.match(TokenType.TRUE):
            return BooleanLiteral(
                location=self.location_from(self.previous),
                value=True
            )
        
        if self.match(TokenType.FALSE):
            return BooleanLiteral(
                location=self.location_from(self.previous),
                value=False
            )
        
        # Nothing literal
        if self.match(TokenType.NOTHING):
            return NothingLiteral(
                location=self.location_from(self.previous)
            )
        
        # Input expression
        if self.match(TokenType.INPUT):
            return InputNode(
                location=self.location_from(self.previous)
            )
        
        # List or table literal: [...]
        if self.match(TokenType.LBRACKET):
            return self.parse_list_or_table()
        
        # Parenthesized expression
        if self.match(TokenType.LPAREN):
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN, "Expected ')' after expression")
            return expr
        
        # Identifier
        if self.match(TokenType.IDENTIFIER):
            token = self.previous
            return IdentifierNode(
                location=self.location_from(token),
                name=token.value
            )
        
        # Error case
        self.error(f"Expected expression, found '{self.current.value}'")
        # Return a placeholder
        return NothingLiteral(location=self.location())
    
    def parse_list_or_table(self) -> ExpressionNode:
        """Parse list literal [...] or table literal [key: value, ...]."""
        start = self.previous  # Already consumed [
        
        # Empty list
        if self.match(TokenType.RBRACKET):
            return ListLiteral(
                location=self.location_from(start),
                elements=[]
            )
        
        # Empty table: [ : ]
        if self.match(TokenType.COLON):
            self.expect(TokenType.RBRACKET, "Expected ']' after empty table")
            return TableLiteral(
                location=self.location_from(start),
                pairs=[]
            )
        
        # Parse first element
        first_expr = self.parse_expression()
        
        # Check if it's a table (key: value)
        if self.match(TokenType.COLON):
            # It's a table
            first_value = self.parse_expression()
            pairs: List[Tuple[ExpressionNode, ExpressionNode]] = [(first_expr, first_value)]
            
            while self.match(TokenType.COMMA):
                if self.check(TokenType.RBRACKET):
                    break
                key = self.parse_expression()
                self.expect(TokenType.COLON, "Expected ':' after table key")
                value = self.parse_expression()
                pairs.append((key, value))
            
            self.expect(TokenType.RBRACKET, "Expected ']' after table")
            return TableLiteral(
                location=self.location_from(start),
                pairs=pairs
            )
        
        # It's a list
        elements: List[ExpressionNode] = [first_expr]
        
        while self.match(TokenType.COMMA):
            if self.check(TokenType.RBRACKET):
                break
            elements.append(self.parse_expression())
        
        self.expect(TokenType.RBRACKET, "Expected ']' after list")
        return ListLiteral(
            location=self.location_from(start),
            elements=elements
        )


# =============================================================================
# Convenience Functions
# =============================================================================

def parse_building(source: str, file_path: Optional[Path] = None) -> ParseResult:
    """Parse a building file from source code."""
    if file_path is None:
        file_path = Path("<string>")
    
    lexer = Lexer(source, file_path)
    tokens = lexer.tokenize()
    parser = Parser(tokens, file_path)
    return parser.parse_building()


def parse_floor(source: str, file_path: Optional[Path] = None) -> ParseResult:
    """Parse a floor file from source code."""
    if file_path is None:
        file_path = Path("<string>")
    
    lexer = Lexer(source, file_path)
    tokens = lexer.tokenize()
    parser = Parser(tokens, file_path)
    return parser.parse_floor()


def parse_step(source: str, file_path: Optional[Path] = None) -> ParseResult:
    """Parse a step file from source code."""
    if file_path is None:
        file_path = Path("<string>")

    lexer = Lexer(source, file_path)
    tokens = lexer.tokenize()
    parser = Parser(tokens, file_path)
    return parser.parse_step()


def parse_repl_input(source: str) -> List[StatementNode]:
    """Parse REPL input as a list of statements.

    Args:
        source: REPL input string

    Returns:
        List of statement nodes

    Raises:
        StepsParseError: If parsing fails
    """
    file_path = Path("<repl>")
    lexer = Lexer(source, file_path)
    tokens = lexer.tokenize()
    parser = Parser(tokens, file_path)
    return parser.parse_repl_statements()
