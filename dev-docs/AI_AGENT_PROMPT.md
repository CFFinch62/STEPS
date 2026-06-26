# Steps Language - AI Development Agent Prompt

## Context

You are helping develop **Steps**, an educational programming language designed to make program structure visible and mandatory. The project is in its initial implementation phase.

## Key Documents

Before making any changes, review the relevant documentation:

1. **PROJECT_OVERVIEW.md** - High-level project goals and structure
2. **LANGUAGE_SPEC.md** - Complete syntax and semantics specification
3. **ARCHITECTURE.md** - Interpreter design and component responsibilities
4. **AST_SPECIFICATION.md** - All AST node types
5. **LEXER_SPEC.md** - Token types and lexing rules
6. **PARSER_SPEC.md** - Grammar and parsing implementation
7. **ERROR_MESSAGES.md** - Error catalog with educational messages
8. **DEVELOPMENT_GUIDE.md** - Code style and development workflow
9. **TESTING_STRATEGY.md** - Testing approach and examples

## Design Principles

When implementing or modifying code, keep these principles in mind:

1. **Educational First** - This language is for teaching. Clarity beats cleverness.

2. **Helpful Errors** - Every error message should explain what went wrong, where, and how to fix it.

3. **Visible Structure** - The building/floor/step/riser metaphor is core. Maintain it.

4. **English-Readable** - Syntax uses words like "storing result in" deliberately. Don't abbreviate.

5. **Mandatory Decomposition** - One step per file. This is a feature, not a limitation.

6. **IDE Intellisense** - The IDE includes context-aware code completion (`completion.py`) that offers comparison operators, statement shortcuts, structure snippets, and project step names. It supports both automatic and manual (`Ctrl+Space`) modes.

## Project Structure

```
steps/
├── src/steps/
│   ├── __init__.py
│   ├── main.py           # CLI entry point
│   ├── repl.py           # Interactive REPL
│   ├── lexer.py          # Tokenization
│   ├── parser.py         # AST construction
│   ├── ast_nodes.py      # AST definitions
│   ├── interpreter.py    # Execution
│   ├── environment.py    # Scopes/registry
│   ├── types.py          # Type system
│   ├── builtins.py       # Built-in ops
│   ├── loader.py         # Project discovery
│   ├── errors.py         # Error handling
│   └── diagram.py        # Flow diagrams
├── tests/
└── examples/
```

## User's Steps Project Structure

```
project_name/
├── project_name.building        # includes floors: section
├── floor_name/
│   ├── step_one.step
│   └── step_two.step
└── another_floor/
    └── step_three.step
```

## Implementation Order

If starting fresh, implement in this order:

1. **ast_nodes.py** - Define all AST node dataclasses
2. **errors.py** - Define error types and formatting
3. **lexer.py** - Implement tokenizer
4. **parser.py** - Implement recursive descent parser
5. **types.py** - Implement Steps types (StepsNumber, StepsText, etc.)
6. **environment.py** - Implement scope chain and step registry
7. **builtins.py** - Implement built-in operations
8. **interpreter.py** - Implement tree-walking interpreter
9. **loader.py** - Implement project discovery
10. **main.py** - Wire up CLI
11. **repl.py** - Implement interactive mode

## Code Patterns

### Creating AST Nodes

```python
@dataclass
class StepNode(ASTNode):
    name: str
    belongs_to: str
    expects: List[ParameterNode]
    returns: Optional[ReturnDeclaration]
    risers: List[RiserNode]
    declarations: List[DeclarationNode]
    body: List[StatementNode]
```

### Error Creation

```python
def undefined_variable_error(name: str, location: SourceLocation) -> StepsError:
    return StepsError(
        code="E401",
        message=f"Variable '{name}' has not been defined yet.",
        hint=f"Define it first with: declare:\\n    {name} as text",
        file=location.file,
        line=location.line,
        column=location.column,
    )
```

### Lexer Pattern

```python
def read_identifier_or_keyword(self) -> Token:
    # Check multi-word keywords first (longest first!)
    for keyword, token_type in self.multi_word_keywords:
        if self.match_ahead(keyword):
            # ... return token
    
    # Fall back to identifier
    value = self.read_while(lambda c: c.isalnum() or c == '_')
    token_type = self.keywords.get(value, TokenType.IDENTIFIER)
    return Token(token_type, value, self.line, self.column, self.file)
```

### Parser Pattern

```python
def parse_statement(self) -> StatementNode:
    if self.match(TokenType.DISPLAY):
        return self.parse_display()
    elif self.match(TokenType.SET):
        return self.parse_set()
    # ... etc
    else:
        self.error(f"Expected statement, got {self.current.value}")
```

### Interpreter Pattern

```python
class Interpreter(ASTVisitor):
    def visit_DisplayStatement(self, node: DisplayStatement) -> None:
        value = self.visit(node.expression)
        print(self.stringify(value))
    
    def visit_SetStatement(self, node: SetStatement) -> None:
        value = self.visit(node.value)
        self.environment.set(node.target, value)
```

## Testing Expectations

Every component should have tests. When adding a feature:

1. Write a test that fails
2. Implement the feature
3. Verify the test passes
4. Add edge case tests

```python
def test_tokenize_multi_word_keyword(lexer):
    tokens = lexer("storing result in").tokenize()
    assert tokens[0].type == TokenType.STORING_RESULT_IN

def test_undefined_variable_error_message():
    # Should produce helpful error with suggestion
    ...
```

## Common Tasks

### "Add a new keyword"

1. Add TokenType in lexer.py
2. Add to keywords or multi_word_keywords
3. Add AST node if needed
4. Add parser rule
5. Add interpreter visitor
6. Add tests
7. Update LANGUAGE_SPEC.md

### "Improve an error message"

1. Find error in ERROR_MESSAGES.md
2. Update the template in errors.py
3. Add test verifying new message
4. Update ERROR_MESSAGES.md

### "Add a built-in operation"

1. Implement in builtins.py
2. Register in BUILTINS dict
3. Add parser support if syntax is special
4. Add tests
5. Update LANGUAGE_SPEC.md

## Questions to Ask

When implementing something new, ask:

1. Is this consistent with the building/floor/step metaphor?
2. Will the error message help a beginner understand what went wrong?
3. Does the syntax read like English?
4. Is there a test for this?
5. Is the documentation updated?

## Response Format

When providing implementation code:

1. State which file(s) will be modified
2. Explain the approach briefly
3. Provide complete, working code
4. Include relevant tests
5. Note any documentation updates needed

## Example Interaction

**User**: "Implement the lexer's string tokenization"

**Assistant**: 
I'll implement string tokenization in `lexer.py`. Strings in Steps:
- Are delimited by double quotes
- Support escape sequences: \n, \t, \\, \"
- Cannot span multiple lines

```python
# In lexer.py

def read_string(self) -> Token:
    """Read a string literal, handling escape sequences."""
    start_line = self.line
    start_col = self.column
    self.advance()  # Skip opening quote
    
    value = []
    while self.current_char != '"':
        if self.current_char == '\n' or self.current_char == '\0':
            raise LexerError(
                message="String was never closed. Add a \" at the end.",
                file=self.file,
                line=start_line,
                column=start_col,
            )
        
        if self.current_char == '\\':
            self.advance()
            value.append(self.escape_sequence())
        else:
            value.append(self.current_char)
            self.advance()
    
    self.advance()  # Skip closing quote
    return Token(TokenType.TEXT, ''.join(value), start_line, start_col, self.file)

def escape_sequence(self) -> str:
    """Convert escape sequence to actual character."""
    escapes = {'n': '\n', 't': '\t', '\\': '\\', '"': '"'}
    char = self.current_char
    self.advance()
    if char in escapes:
        return escapes[char]
    raise LexerError(
        message=f"Unknown escape sequence: \\{char}",
        file=self.file,
        line=self.line,
        column=self.column - 1,
    )
```

Test:
```python
def test_string_escapes(lexer):
    tokens = lexer(r'"hello\nworld"').tokenize()
    assert tokens[0].value == "hello\nworld"
```
