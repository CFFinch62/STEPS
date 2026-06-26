# STEPS Programming Language

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-437%20passing-green.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

![STEPS IDE Screenshot](images/STEPSIDE.png)

> **An educational programming language that makes program structure visible and mandatory.**

STEPS teaches programming through an architectural metaphor, enforcing decomposition and clear structure from day one. STEPS is the first of 3 teaching labugaes crreated by Fragillidae Software. The others are PLAIN (general purpose scripting lanauge like a mix if Python and Go) and FORGE(statically types system programming language with easier beginer entry than C).



---

## 🏗️ The Building Metaphor

STEPS uses architecture to make program structure explicit and visible:

| Construct    | Purpose                                 | File Extension   |
| ------------ | --------------------------------------- | ---------------- |
| **Building** | Complete program (entry point)          | `.building`      |
| **Floor**    | Functional grouping of related STEPS    | (in `.building`) |
| **Step**     | Single unit of work (one file per step) | `.step`          |
| **Riser**    | Private helper function within a step   | (inside `.step`) |

This hierarchy enforces decomposition - you can't write monolithic code in STEPS!

---

## 📦 Installation

### From Source

```bash
# Clone the repository
git clone <repository-url>
cd STEPS

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install in development mode
pip install -e ".[dev]"

# Install IDE dependencies
pip install textual watchfiles
```

---

## 🚀 Quick Start

### 1. Create a Simple Program

Create a project folder with a `.building` file:

```
hello_world/
└── hello_world.building
```

In `hello_world.building`:
```STEPS
building: hello_world
    display "Hello, World!"
    exit
```

### 2. Run Your Program

```bash
python -m STEPS.main run hello_world/
```

### 3. Or Use the Interactive REPL

```bash
python -m STEPS_repl.main
```

```
STEPS REPL v0.1 - Educational Programming Environment
Type 'help' for available commands, 'exit' to quit.

>>> set greeting to "Hello, STEPS!"
>>> display greeting
Hello, STEPS!
>>> vars
Variables:
  greeting = "Hello, STEPS!"
```

### 4. Launch the STEPS IDE

```bash
python -m STEPS_ide.main
```

The IDE provides a full development environment with:
- Project browser (Ctrl+Shift+P)
- Syntax-aware editor
- Run (F5) and Check (F6) commands
- Terminal output panel (Ctrl+J)
- Project diagram viewer (Ctrl+D)
- Integrated debugger with breakpoints

---

## 📚 A Complete Example

Here's a more complete program with floors and STEPS:

```
price_calculator/
├── price_calculator.building
└── calculations/
    ├── calculate_subtotal.step
    └── apply_discount.step
```

**price_calculator.building:**
```STEPS
building: price_calculator
    note: Calculate the final price with discount

    floors:
        floor: calculations
            step: calculate_subtotal
            step: apply_discount

    display "Enter price: "
    set price to input as number

    display "Enter quantity: "
    set quantity to input as number

    call calculate_subtotal with price, quantity storing result in subtotal
    call apply_discount with subtotal, 10 storing result in final_price

    display "Final price: $" added to (final_price as text)
    exit
```

**calculations/calculate_subtotal.step:**
```STEPS
step: calculate_subtotal
    belongs to: calculations
    expects: price, quantity
    returns: total

    do:
        set total to price * quantity
        return total
```

**calculations/apply_discount.step:**
```STEPS
step: apply_discount
    belongs to: calculations
    expects: amount, percent
    returns: discounted

    declare:
        discount as number

    do:
        set discount to amount * (percent / 100)
        set discounted to amount - discount
        return discounted
```

---

## 🛠️ CLI Commands

| Command                               | Description                                                     |
| ------------------------------------- | --------------------------------------------------------------- |
| `python -m STEPS.main run <path>`     | Run a STEPS project                                             |
| `python -m STEPS.main check <path>`   | Validate syntax without running                                 |
| `python -m STEPS.main repl`           | Start the interactive REPL                                      |
| `python -m STEPS.main diagram <path>` | Generate ASCII flow diagram (also available in IDE with Ctrl+D) |
| `python -m STEPS_repl.main`           | Start REPL directly                                             |
| `python -m STEPS_ide.main`            | Launch the STEPS IDE                                            |

---

## 📖 Documentation

| Document                                       | Description                     |
| ---------------------------------------------- | ------------------------------- |
| [USER-GUIDE.md](USER-GUIDE.md)                 | Getting started guide for users |
| [LANGUAGE-REFERENCE.md](LANGUAGE-REFERENCE.md) | Complete language reference     |
| [dev-docs/](dev-docs/)                         | Developer documentation         |

### Developer Documentation (dev-docs/)

- `PROJECT_OVERVIEW.md` - High-level project orientation
- `LANGUAGE_SPEC.md` - Complete syntax and semantics
- `ARCHITECTURE.md` - Interpreter design
- `DEVELOPMENT_GUIDE.md` - Development workflow

---

## 🧪 Development

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_lexer.py
```

### With Coverage

```bash
pytest --cov=STEPS --cov-report=html
```

### Type Checking

```bash
mypy src/STEPS src/STEPS_repl --ignore-missing-imports
```

### Project Structure

```
STEPS/
├── src/
│   ├── STEPS/           # Core interpreter
│   │   ├── lexer.py     # Tokenization
│   │   ├── parser.py    # AST construction
│   │   ├── interpreter.py  # Execution engine
│   │   ├── environment.py  # Scopes and registry
│   │   └── ...
│   ├── STEPS_repl/      # Interactive REPL
│   └── STEPS_ide/       # TUI-based IDE
├── tests/
│   ├── unit/            # Unit tests
│   └── integration/     # Integration tests
├── dev-docs/            # Developer documentation
└── README.md
```

---

## 🎯 Design Philosophy

1. **Visible Structure** - Program architecture is explicit, not hidden
2. **Mandatory Decomposition** - One step per file prevents monolithic code
3. **Conscious Engagement** - English-readable syntax requires understanding
4. **Clear Data Flow** - Explicit `expects`/`returns` declarations
5. **Educational Error Messages** - Errors teach, not frustrate
6. **Attractive Console Output** - Built-in TUI functions for boxes, banners, menus, and dynamic progress bars

---

## 📄 License

MIT License

---

## 🤝 Contributing

Contributions are welcome! Please see `dev-docs/DEVELOPMENT_GUIDE.md` for guidelines.
