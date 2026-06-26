# Steps Testing Strategy

## Overview

Testing for Steps follows a pyramid approach:
1. **Unit tests** - Test individual functions and classes
2. **Integration tests** - Test components working together
3. **End-to-end tests** - Test complete programs

## Test Organization

```
tests/
├── conftest.py              # Shared fixtures
├── unit/
│   ├── test_lexer.py
│   ├── test_parser.py
│   ├── test_interpreter.py
│   ├── test_types.py
│   ├── test_environment.py
│   └── test_builtins.py
├── integration/
│   ├── test_lexer_parser.py
│   ├── test_full_pipeline.py
│   └── test_error_reporting.py
├── e2e/
│   ├── test_examples.py
│   └── test_repl.py
└── fixtures/
    ├── valid_programs/
    ├── invalid_programs/
    └── expected_outputs/
```

## Shared Fixtures

```python
# conftest.py
import pytest
from pathlib import Path
from steps.lexer import Lexer
from steps.parser import Parser
from steps.interpreter import Interpreter
from steps.environment import Environment

@pytest.fixture
def lexer():
    """Create a lexer for a test file."""
    def _lexer(source: str, filename: str = "test.step"):
        return Lexer(source, Path(filename))
    return _lexer

@pytest.fixture
def parser():
    """Create a parser from source."""
    def _parser(source: str, file_type: str = "step"):
        lex = Lexer(source, Path(f"test.{file_type}"))
        tokens = lex.tokenize()
        return Parser(tokens, file_type)
    return _parser

@pytest.fixture
def interpreter():
    """Create an interpreter with fresh environment."""
    return Interpreter(Environment())

@pytest.fixture
def tmp_project(tmp_path):
    """Create a temporary project directory."""
    def _project(name: str, files: dict):
        project_dir = tmp_path / name
        project_dir.mkdir()
        for filepath, content in files.items():
            full_path = project_dir / filepath
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
        return project_dir
    return _project
```

## Unit Tests

### Lexer Tests

```python
# tests/unit/test_lexer.py

class TestTokenizeBasics:
    def test_empty_source(self, lexer):
        lex = lexer("")
        tokens = lex.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF
    
    def test_single_number(self, lexer):
        lex = lexer("42")
        tokens = lex.tokenize()
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == "42"
    
    def test_negative_number(self, lexer):
        lex = lexer("-3.14")
        tokens = lex.tokenize()
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == "-3.14"
    
    def test_string_literal(self, lexer):
        lex = lexer('"hello world"')
        tokens = lex.tokenize()
        assert tokens[0].type == TokenType.TEXT
        assert tokens[0].value == "hello world"
    
    def test_string_escapes(self, lexer):
        lex = lexer(r'"hello\nworld"')
        tokens = lex.tokenize()
        assert tokens[0].value == "hello\nworld"


class TestTokenizeKeywords:
    @pytest.mark.parametrize("keyword,token_type", [
        ("building:", TokenType.BUILDING),
        ("floor:", TokenType.FLOOR),
        ("step:", TokenType.STEP),
        ("display", TokenType.DISPLAY),
        ("set", TokenType.SET),
        ("to", TokenType.TO),
    ])
    def test_single_keywords(self, lexer, keyword, token_type):
        lex = lexer(keyword)
        tokens = lex.tokenize()
        assert tokens[0].type == token_type
    
    @pytest.mark.parametrize("keyword,token_type", [
        ("belongs to:", TokenType.BELONGS_TO),
        ("storing result in", TokenType.STORING_RESULT_IN),
        ("is equal to", TokenType.IS_EQUAL_TO),
        ("is greater than or equal to", TokenType.IS_GREATER_THAN_OR_EQUAL_TO),
    ])
    def test_multi_word_keywords(self, lexer, keyword, token_type):
        lex = lexer(keyword)
        tokens = lex.tokenize()
        assert tokens[0].type == token_type


class TestTokenizeIndentation:
    def test_single_indent(self, lexer):
        source = "building: test\n    display 1"
        lex = lexer(source)
        tokens = lex.tokenize()
        # Find INDENT token
        indent_tokens = [t for t in tokens if t.type == TokenType.INDENT]
        assert len(indent_tokens) == 1
    
    def test_multiple_indent_levels(self, lexer):
        source = "if true\n    if true\n        display 1"
        lex = lexer(source)
        tokens = lex.tokenize()
        indent_tokens = [t for t in tokens if t.type == TokenType.INDENT]
        assert len(indent_tokens) == 2
    
    def test_dedent(self, lexer):
        source = "if true\n    display 1\ndisplay 2"
        lex = lexer(source)
        tokens = lex.tokenize()
        dedent_tokens = [t for t in tokens if t.type == TokenType.DEDENT]
        assert len(dedent_tokens) == 1
    
    def test_bad_indentation_error(self, lexer):
        source = "building: test\n   display 1"  # 3 spaces, not 4
        lex = lexer(source)
        with pytest.raises(LexerError) as exc:
            lex.tokenize()
        assert "4 spaces" in str(exc.value)


class TestTokenizeSourceLocation:
    def test_line_numbers(self, lexer):
        source = "line1\nline2\nline3"
        lex = lexer(source)
        tokens = lex.tokenize()
        assert tokens[0].line == 1
        assert tokens[2].line == 2
        assert tokens[4].line == 3
    
    def test_column_numbers(self, lexer):
        source = "set x to 42"
        lex = lexer(source)
        tokens = lex.tokenize()
        assert tokens[0].column == 1   # set
        assert tokens[1].column == 5   # x
        assert tokens[2].column == 7   # to
        assert tokens[3].column == 10  # 42
```

### Parser Tests

```python
# tests/unit/test_parser.py

class TestParseBuilding:
    def test_minimal_building(self, parser):
        source = """building: test

    exit
"""
        p = parser(source, "building")
        ast = p.parse()
        assert isinstance(ast, BuildingNode)
        assert ast.name == "test"
    
    def test_building_with_display(self, parser):
        source = """building: test

    display "hello"
    exit
"""
        p = parser(source, "building")
        ast = p.parse()
        assert len(ast.body) == 2
        assert isinstance(ast.body[0], DisplayStatement)


class TestParseStep:
    def test_minimal_step(self, parser):
        source = """step: greet
    belongs to: main
    expects: nothing
    returns: nothing

    do:
        display "hi"
"""
        p = parser(source, "step")
        ast = p.parse()
        assert isinstance(ast, StepNode)
        assert ast.name == "greet"
        assert ast.belongs_to == "main"
    
    def test_step_with_parameters(self, parser):
        source = """step: greet
    belongs to: main
    expects: name, age
    returns: message

    declare:
        message as text

    do:
        set message to "Hello"
        return message
"""
        p = parser(source, "step")
        ast = p.parse()
        assert len(ast.expects) == 2
        assert ast.expects[0].name == "name"
        assert ast.expects[1].name == "age"


class TestParseExpressions:
    def test_number_literal(self, parser):
        source = """building: test

    display 42
    exit
"""
        p = parser(source, "building")
        ast = p.parse()
        display_stmt = ast.body[0]
        assert isinstance(display_stmt.expression, NumberLiteral)
        assert display_stmt.expression.value == 42
    
    def test_binary_operation(self, parser):
        source = """building: test

    display 1 + 2
    exit
"""
        p = parser(source, "building")
        ast = p.parse()
        expr = ast.body[0].expression
        assert isinstance(expr, BinaryOpNode)
        assert expr.operator == "+"
    
    def test_comparison(self, parser):
        source = """building: test

    if x is greater than 10
        display "big"
    exit
"""
        p = parser(source, "building")
        ast = p.parse()
        if_stmt = ast.body[0]
        assert isinstance(if_stmt.if_branch.condition, BinaryOpNode)
        assert if_stmt.if_branch.condition.operator == "is greater than"
```

### Interpreter Tests

```python
# tests/unit/test_interpreter.py

class TestInterpreterBasics:
    def test_display_number(self, interpreter, capsys):
        ast = DisplayStatement(
            location=mock_location(),
            expression=NumberLiteral(location=mock_location(), value=42)
        )
        interpreter.visit(ast)
        captured = capsys.readouterr()
        assert captured.out == "42\n"
    
    def test_set_and_get_variable(self, interpreter):
        # set x to 10
        interpreter.visit(SetStatement(
            location=mock_location(),
            target="x",
            value=NumberLiteral(location=mock_location(), value=10)
        ))
        
        # Check x is 10
        value = interpreter.environment.get("x")
        assert value.value == 10


class TestInterpreterControlFlow:
    def test_if_true_branch(self, interpreter, capsys):
        # if true
        #     display "yes"
        ast = IfStatement(
            location=mock_location(),
            if_branch=IfBranch(
                location=mock_location(),
                condition=BooleanLiteral(location=mock_location(), value=True),
                body=[DisplayStatement(
                    location=mock_location(),
                    expression=TextLiteral(location=mock_location(), value="yes")
                )]
            ),
            otherwise_if_branches=[],
            otherwise_branch=None
        )
        interpreter.visit(ast)
        assert capsys.readouterr().out == "yes\n"
    
    def test_if_false_otherwise(self, interpreter, capsys):
        # if false
        #     display "yes"
        # otherwise
        #     display "no"
        ast = IfStatement(
            location=mock_location(),
            if_branch=IfBranch(
                location=mock_location(),
                condition=BooleanLiteral(location=mock_location(), value=False),
                body=[DisplayStatement(
                    location=mock_location(),
                    expression=TextLiteral(location=mock_location(), value="yes")
                )]
            ),
            otherwise_if_branches=[],
            otherwise_branch=[DisplayStatement(
                location=mock_location(),
                expression=TextLiteral(location=mock_location(), value="no")
            )]
        )
        interpreter.visit(ast)
        assert capsys.readouterr().out == "no\n"
```

## Integration Tests

```python
# tests/integration/test_full_pipeline.py

class TestFullPipeline:
    def test_hello_world(self, tmp_project):
        project = tmp_project("hello", {
            "hello.building": """building: hello

    display "Hello, World!"
    exit
"""
        })
        
        result = run_project(project)
        assert result.exit_code == 0
        assert result.output == "Hello, World!\n"
    
    def test_step_call(self, tmp_project):
        project = tmp_project("greet", {
            "greet.building": """building: greet

    floors:
        floor: main
            step: say_hello

    call say_hello
    exit
""",
            "main/say_hello.step": """step: say_hello
    belongs to: main
    expects: nothing
    returns: nothing

    do:
        display "Hello from step!"
"""
        })
        
        result = run_project(project)
        assert result.exit_code == 0
        assert result.output == "Hello from step!\n"
    
    def test_step_with_return(self, tmp_project):
        project = tmp_project("calc", {
            "calc.building": """building: calc

    floors:
        floor: math
            step: double

    call double with 21 storing result in answer
    display answer
    exit
""",
            "math/double.step": """step: double
    belongs to: math
    expects: n
    returns: result

    declare:
        result as number

    do:
        set result to n * 2
        return result
"""
        })
        
        result = run_project(project)
        assert result.exit_code == 0
        assert result.output == "42\n"
```

## End-to-End Tests

```python
# tests/e2e/test_examples.py
import subprocess
from pathlib import Path

EXAMPLES_DIR = Path(__file__).parent.parent.parent / "examples"

class TestExamplePrograms:
    @pytest.mark.parametrize("example,expected_output", [
        ("hello_world", "Hello, World!\n"),
    ])
    def test_example_output(self, example, expected_output):
        project_path = EXAMPLES_DIR / example
        result = subprocess.run(
            ["steps", "run", str(project_path)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert result.stdout == expected_output
    
    @pytest.mark.parametrize("example", [
        "price_calculator",
        "guessing_game",
    ])
    def test_example_runs(self, example):
        """Just verify these examples run without error."""
        project_path = EXAMPLES_DIR / example
        result = subprocess.run(
            ["steps", "check", str(project_path)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
```

## Error Message Tests

```python
# tests/integration/test_error_reporting.py

class TestLexerErrors:
    def test_tab_error_message(self, lexer):
        source = "\tdisplay 1"
        lex = lexer(source)
        with pytest.raises(LexerError) as exc:
            lex.tokenize()
        
        error = exc.value
        assert "tab" in error.message.lower()
        assert "4 spaces" in error.message
        assert error.line == 1
    
    def test_unterminated_string_error(self, lexer):
        source = 'display "hello'
        lex = lexer(source)
        with pytest.raises(LexerError) as exc:
            lex.tokenize()
        
        error = exc.value
        assert "unterminated" in error.message.lower() or "closed" in error.message.lower()


class TestRuntimeErrors:
    def test_undefined_variable_error(self, tmp_project):
        project = tmp_project("bad", {
            "bad.building": """building: bad

    display undefined_var
    exit
"""
        })
        
        result = run_project(project)
        assert result.exit_code != 0
        assert "undefined_var" in result.stderr
        assert "not been defined" in result.stderr or "does not exist" in result.stderr
    
    def test_undefined_step_suggests_similar(self, tmp_project):
        project = tmp_project("typo", {
            "typo.building": """building: typo

    floors:
        floor: main
            step: say_hello

    call say_helo
    exit
""",
            "main/say_hello.step": """step: say_hello
    belongs to: main
    expects: nothing
    returns: nothing

    do:
        display "hi"
"""
        })
        
        result = run_project(project)
        assert result.exit_code != 0
        assert "say_helo" in result.stderr
        assert "say_hello" in result.stderr  # Suggests correct name
```

## Test Data Fixtures

```python
# tests/fixtures/valid_programs/minimal.building
building: minimal

    exit

# tests/fixtures/valid_programs/hello.building
building: hello

    display "Hello, World!"
    exit

# tests/fixtures/invalid_programs/bad_indent.step
step: bad
    belongs to: main
   expects: nothing    # Wrong indentation
    returns: nothing

    do:
        display "hi"

# tests/fixtures/expected_outputs/hello.txt
Hello, World!
```

## Coverage Goals

- **Lexer**: 95%+ coverage
- **Parser**: 95%+ coverage  
- **Interpreter**: 90%+ coverage
- **Error messages**: Every error code has at least one test
- **Integration**: All example programs run successfully

## Running Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# End-to-end tests only
pytest tests/e2e/

# Tests for a specific component
pytest -k "lexer"
pytest -k "parser"
pytest -k "interpreter"

# Error message tests
pytest -k "error"
```
