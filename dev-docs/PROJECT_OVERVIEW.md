# Steps Programming Language - Development Overview

## What is Steps?

Steps is an educational programming language designed to make program structure visible and mandatory. It enforces decomposition through its core metaphor:

- **Building** - The complete program (entry point)
- **Floor** - A functional grouping of related steps
- **Step** - A single unit of work (one file per step)
- **Riser** - A private helper function within a step

## Core Philosophy

1. **Visible Structure** - Program architecture is explicit, not hidden
2. **Mandatory Decomposition** - One step per file prevents monolithic code
3. **Conscious Engagement** - English-readable syntax requires understanding
4. **Clear Data Flow** - Explicit expects/returns declarations
5. **Educational Error Messages** - Errors teach, not frustrate

## Target Audience

- Beginning programmers learning structure and decomposition
- Students who benefit from explicit, visible program architecture
- Teachers who want to enforce good habits from day one

## Version 1.0 Scope

- CLI applications only (no GUI)
- Python-based interpreter
- REPL for interactive learning
- Visual flow diagram generation (text-based initially)

## Project Structure

```
steps/
├── src/
│   └── steps/
│       ├── __init__.py
│       ├── main.py           # CLI entry point
│       ├── repl.py           # Interactive REPL
│       ├── lexer.py          # Tokenization
│       ├── parser.py         # AST construction
│       ├── ast_nodes.py      # AST node definitions
│       ├── interpreter.py    # Execution engine
│       ├── environment.py    # Scopes and registry
│       ├── types.py          # Steps type system
│       ├── builtins.py       # Built-in operations
│       ├── loader.py         # Project file discovery
│       ├── errors.py         # Educational error messages
│       └── diagram.py        # Flow diagram generator
├── tests/
│   ├── test_lexer.py
│   ├── test_parser.py
│   ├── test_interpreter.py
│   └── examples/             # Test projects
│       └── price_calculator/
├── docs/
│   └── ...
├── pyproject.toml
└── README.md
```

## Steps Project Structure (User's View)

```
my_program/                      # Building folder
├── my_program.building          # Entry point (includes floors: section)
├── floor_one/                   # Floor folder
│   ├── step_a.step
│   └── step_b.step
└── floor_two/
    └── step_c.step
```

## Key Documents

| Document | Purpose |
|----------|---------|
| PROJECT_OVERVIEW.md | This file - high-level orientation |
| LANGUAGE_SPEC.md | Complete syntax and semantics |
| ARCHITECTURE.md | Interpreter design and data flow |
| AST_SPECIFICATION.md | All AST node types and structures |
| LEXER_SPEC.md | Token types and lexing rules |
| PARSER_SPEC.md | Grammar and parsing strategy |
| ERROR_MESSAGES.md | Error catalog with educational text |
| DEVELOPMENT_GUIDE.md | How to work on this codebase |
| TESTING_STRATEGY.md | Test approach and examples |

## Development Approach

1. **Parse upfront** - Validate entire project before execution
2. **Rich AST** - Preserve source locations for error messages
3. **Clear separation** - Lexer → Parser → AST → Interpreter
4. **Test-driven** - Each component has comprehensive tests
5. **Incremental** - Build minimal working version, then extend

## Command Line Interface

```bash
# Run a Steps program
steps run path/to/project/

# Start REPL
steps repl

# Validate without running
steps check path/to/project/

# Generate flow diagram
steps diagram path/to/project/

# Show version
steps --version
```
