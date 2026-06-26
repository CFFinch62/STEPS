# Steps Programming Language - Testing Guide

> **Test your Steps code with confidence!**

This guide covers all the ways to test Steps code, from quick interactive checks to comprehensive automated test suites.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Testing with the REPL](#testing-with-the-repl)
3. [Testing with run-step](#testing-with-run-step)
4. [Programmatic Testing](#programmatic-testing)
5. [pytest Integration](#pytest-integration)
6. [Testing Best Practices](#testing-best-practices)

---

## Quick Start

Choose the right approach for your needs:

| Method | Best For |
|--------|----------|
| **REPL** | Quick experiments, learning syntax |
| **run-step** | Testing individual steps in isolation |
| **Programmatic** | Unit tests, automated testing |
| **pytest** | Full test suites, CI/CD integration |

---

## Testing with the REPL

The REPL (Read-Eval-Print Loop) is perfect for quick experiments and learning.

### Starting the REPL

```bash
python -m steps_repl.main
```

### Example Session

```
Steps REPL v0.1 - Educational Programming Environment
Type 'help' for available commands, 'exit' to quit.

>>> set x to 10
>>> set y to 20
>>> display x + y
30
>>> vars
Variables:
  x = 10
  y = 20
>>> reset
Environment reset.
```

### REPL Commands

| Command | Description |
|---------|-------------|
| `help` | Show available commands |
| `vars` | Display all current variables |
| `reset` | Clear all variables |
| `clear` | Clear the screen |
| `exit` | Exit the REPL |

### Multi-line Input

Enter complex statements across multiple lines:

```
>>> if x is greater than 5
...     display "Big number"
... otherwise
...     display "Small number"
...
Big number
```

> [!TIP]
> The REPL is great for testing expressions and small code snippets before adding them to your project.

---

## Testing with run-step

The `run-step` command lets you test individual `.step` files without creating a full project.

### Basic Usage

```bash
python -m steps.main run-step path/to/your.step
```

### Passing Arguments

If your step expects parameters, pass them with `--args`:

```bash
python -m steps.main run-step my_step.step --args 10 20 "hello"
```

### Example

Given this step file (`calculate_tip.step`):

```steps
step: calculate_tip
    belongs to: math
    expects: amount, percent
    returns: tip

    do:
        set tip to amount * (percent / 100)
        return tip
```

Test it like this:

```bash
python -m steps.main run-step calculate_tip.step --args 100 15
```

Output:
```
Running step: calculate_tip
  Expects: amount, percent
  Returns: tip

Result: 15.0
```

### What run-step Does

1. **Parses** the step file to extract its signature
2. **Displays** what the step expects and returns
3. **Validates** that you provided the required arguments
4. **Wraps** the step in a minimal test harness
5. **Executes** the step and displays the result

> [!NOTE]
> The `run-step` command automatically detects whether arguments are numbers or text and formats them appropriately.

---

## Programmatic Testing

For automated tests, use the `run_source()` function to execute Steps code from Python.

### Basic Usage

```python
from steps.interpreter import run_source

result = run_source("""building: test
    set x to 10
    set y to 20
    display x + y
""")

print(result.success)        # True
print(result.output_lines)   # ['30']
```

### The ExecutionResult Object

When you call `run_source()`, you get an `ExecutionResult` with these attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `success` | `bool` | Whether execution completed without error |
| `output_lines` | `list[str]` | All output from `display` statements |
| `return_value` | `StepsValue` | The final return value (if any) |
| `error` | `StepsError` | Error details if execution failed |

### Testing Error Conditions

```python
from steps.interpreter import run_source

result = run_source("""building: test
    display unknown_variable
""")

assert not result.success
assert "not been defined" in result.error.message
```

### Testing with Pre-registered Steps

```python
from steps.interpreter import run_building
from steps.parser import parse_building, parse_step
from steps.environment import Environment, StepDefinition

# Set up environment
env = Environment()
outputs = []
env.output_handler = lambda s: outputs.append(s)

# Parse and register a step
step_source = """step: greet
    belongs to: main
    expects: name

    do:
        display "Hello, " added to name
"""
step_result = parse_step(step_source)
step_node = step_result.ast

step_def = StepDefinition(
    name=step_node.name,
    belongs_to=step_node.belongs_to,
    parameters=[p.name for p in step_node.expects],
    returns=None,
    body=step_node.body
)
env.register_step(step_def)

# Call the step from a building
building_source = """building: test
    call greet with "World"
"""
build_result = parse_building(building_source)
exec_result = run_building(build_result.ast, env)

assert exec_result.success
assert outputs[0] == "Hello, World"
```

---

## pytest Integration

The Steps project uses pytest for its test suite. You can follow the same patterns for your own tests.

### Running the Test Suite

```bash
# Run all tests
python -m pytest tests/ -v

# Run a specific test file
python -m pytest tests/unit/test_interpreter.py -v

# Run tests matching a pattern
python -m pytest tests/ -k "test_if" -v
```

### Writing Your Own Tests

Create test files in a `tests/` directory following this pattern:

```python
# tests/test_my_steps.py

import pytest
from steps.interpreter import run_source

class TestCalculations:
    """Tests for calculation functionality."""
    
    def test_addition(self):
        result = run_source("""building: test
    display 10 + 20
""")
        assert result.success
        assert "30" in result.output_lines[0]
    
    def test_division_by_zero(self):
        result = run_source("""building: test
    display 10 / 0
""")
        assert not result.success
        assert "divide by zero" in result.error.message.lower()
```

### Test Organization

```
my_project/
├── src/
│   └── my_steps/
│       └── ...
├── tests/
│   ├── conftest.py          # Shared fixtures
│   ├── test_calculations.py
│   ├── test_text_ops.py
│   └── fixtures/
│       └── sample_data.txt
└── pyproject.toml
```

### Creating Fixtures

Use `conftest.py` for shared test utilities:

```python
# tests/conftest.py

import pytest
from steps.interpreter import run_source

@pytest.fixture
def run():
    """Convenience fixture for running Steps code."""
    def _run(source: str):
        return run_source(source)
    return _run

# Usage in tests:
def test_something(run):
    result = run("""building: test
    display "Hello"
""")
    assert result.success
```

---

## Testing Best Practices

### 1. Test Steps in Isolation

Use `run-step` to verify individual steps work correctly before integrating them:

```bash
# Test each step independently
python -m steps.main run-step math/add.step --args 5 3
python -m steps.main run-step math/multiply.step --args 4 7
```

### 2. Test Edge Cases

Always test boundary conditions:

```python
def test_empty_list():
    result = run_source("""building: test
    set items to []
    display length of items
""")
    assert result.success
    assert "0" in result.output_lines[0]

def test_negative_numbers():
    result = run_source("""building: test
    set x to -10
    set y to -5
    display x + y
""")
    assert result.success
    assert "-15" in result.output_lines[0]
```

### 3. Test Error Handling

Verify your code handles errors gracefully:

```python
def test_type_conversion_error():
    result = run_source("""building: test
    attempt:
        set x to "abc" as number
    if unsuccessful:
        display "Caught error"
""")
    assert result.success
    assert result.output_lines[0] == "Caught error"
```

### 4. Use Descriptive Test Names

Name tests to describe what they verify:

```python
# Good
def test_calculate_tip_returns_fifteen_percent()
def test_empty_input_displays_error_message()

# Bad
def test_1()
def test_tip()
```

### 5. Create a Test Workflow

For your standard library, consider this workflow:

1. **Write the step** with its expected behavior
2. **Test with run-step** to verify basic functionality
3. **Write a pytest test** to codify the expected behavior
4. **Add edge case tests** as you discover them

### Example: Building a Standard Library

```bash
# Structure for a standard library
stdlib/
├── stdlib.building
├── math/
│   ├── add.step
│   ├── subtract.step
│   ├── multiply.step
│   └── divide.step
├── text/
│   ├── uppercase.step
│   ├── lowercase.step
│   └── reverse.step
└── tests/
    ├── test_math.py
    └── test_text.py
```

```bash
# Quick test during development
python -m steps.main run-step stdlib/math/add.step --args 5 3

# Run full test suite
python -m pytest stdlib/tests/ -v
```

---

## Next Steps

1. **Start with the REPL** to experiment with language features
2. **Use run-step** when developing new steps for your standard library
3. **Write pytest tests** as you solidify your implementations
4. **Run tests regularly** to catch regressions early

Happy testing! 🧪
