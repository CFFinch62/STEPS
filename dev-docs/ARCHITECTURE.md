# Steps Interpreter Architecture

## Overview

The Steps interpreter follows a classic pipeline architecture:

```
Source Files → Lexer → Tokens → Parser → AST → Interpreter → Output
                                           ↓
                                      Environment
```

## Component Responsibilities

### 1. Loader (`loader.py`)

**Purpose:** Discover and load all project files.

**Input:** Path to project directory (building folder)

**Output:** Dictionary of file contents keyed by type and name

**Responsibilities:**
- Validate project structure (building file exists)
- Read inline `floors:` declarations from the building AST
- Auto-discover floor directories and `.step` files (used for stdlib)
- Report missing or malformed project structure
- Return organized collection of source files

**Key Functions:**
```python
def load_project(project_path: Path) -> Project:
    """Load entire Steps project from directory."""
    
def validate_structure(project_path: Path) -> List[StructureError]:
    """Check project structure without loading content."""

def find_building_file(project_path: Path) -> Path:
    """Locate the .building file in project root."""

def find_floors(project_path: Path) -> Dict[str, FloorFiles]:
    """Discover all floor directories and their contents."""
```

### 2. Lexer (`lexer.py`)

**Purpose:** Convert source text into tokens.

**Input:** Source text string + file path (for error messages)

**Output:** List of Token objects

**Responsibilities:**
- Track line and column numbers for each token
- Handle significant whitespace (indentation)
- Recognize all keywords and operators
- Tokenize string literals, numbers, identifiers
- Generate INDENT/DEDENT tokens for scope changes
- Produce meaningful errors for invalid characters

**Key Classes:**
```python
@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int
    file: Path

class Lexer:
    def __init__(self, source: str, file_path: Path):
        ...
    
    def tokenize(self) -> List[Token]:
        ...
```

### 3. Parser (`parser.py`)

**Purpose:** Build Abstract Syntax Tree from tokens.

**Input:** List of tokens

**Output:** AST (BuildingNode, FloorNode, or StepNode depending on file type)

**Responsibilities:**
- Implement recursive descent parser
- Validate syntax according to grammar
- Build rich AST nodes with source locations
- Collect multiple errors when possible (don't stop at first error)
- Validate structural rules (e.g., step has belongs to)

**Key Functions:**
```python
def parse_building(tokens: List[Token]) -> BuildingNode:
    """Parse a .building file (including optional floors: section)."""

def parse_step(tokens: List[Token]) -> StepNode:
    """Parse a .step file."""
```

### 4. AST Nodes (`ast_nodes.py`)

**Purpose:** Define all node types in the abstract syntax tree.

See AST_SPECIFICATION.md for complete node definitions.

**Design Principles:**
- Every node stores source location (file, line, column)
- Nodes are immutable dataclasses
- Visitor pattern support for tree traversal
- Rich enough to reconstruct original source (for error messages)

### 5. Interpreter (`interpreter.py`)

**Purpose:** Execute the AST.

**Input:** Complete project AST + initial environment

**Output:** Program output (via display) and exit code

**Responsibilities:**
- Tree-walking interpreter (not bytecode)
- Manage call stack for step invocations
- Handle control flow (if/otherwise, loops)
- Implement error handling (attempt/unsuccessful)
- Enforce type constraints (fixed variables)
- Provide rich runtime errors with context

**Key Classes:**
```python
class Interpreter:
    def __init__(self, project: ProjectAST, environment: Environment):
        ...
    
    def run(self) -> int:
        """Execute the program, return exit code."""
    
    def visit(self, node: ASTNode) -> Any:
        """Visit and evaluate an AST node."""
```

### 6. Environment (`environment.py`)

**Purpose:** Manage variable scopes and step registry.

**Responsibilities:**
- Track variable bindings in nested scopes
- Register all floors and steps at startup
- Resolve step calls to their AST nodes
- Handle floor namespacing (calculations.calc_from_price_and_margin)
- Enforce scope rules (risers only visible within parent step)

**Key Classes:**
```python
class Environment:
    def __init__(self):
        self.scopes: List[Dict[str, Value]] = [{}]
        self.floors: Dict[str, FloorNode] = {}
        self.steps: Dict[str, StepNode] = {}
    
    def define(self, name: str, value: Value, fixed: bool = False):
        """Define variable in current scope."""
    
    def get(self, name: str) -> Value:
        """Look up variable, searching enclosing scopes."""
    
    def register_step(self, floor: str, step: StepNode):
        """Register a step for later invocation."""
    
    def resolve_step(self, name: str) -> StepNode:
        """Find step by name, checking all floors."""
```

### 7. Types (`types.py`)

**Purpose:** Implement Steps type system.

**Types:**
- `StepsNumber` - Wraps Python float/int
- `StepsText` - Wraps Python str
- `StepsBoolean` - Wraps Python bool
- `StepsList` - Wraps Python list with Steps semantics
- `StepsTable` - Wraps Python dict with Steps semantics
- `StepsNothing` - Represents `nothing`

**Responsibilities:**
- Type checking and conversion
- Operator implementation for each type
- Truthiness rules
- Equality semantics

### 8. Builtins (`builtins.py`)

**Purpose:** Implement built-in operations.

**Operations:**
- `display` - Output to console
- `input` - Read from console
- `length of` - Get collection/text length
- `add ... to` - Add to list
- `remove ... from` - Remove from list
- Text operations (split, contains, starts with, etc.)
- Type conversions

### 9. Errors (`errors.py`)

**Purpose:** Define error types with educational messages.

See ERROR_MESSAGES.md for complete error catalog.

**Key Classes:**
```python
@dataclass
class StepsError:
    message: str           # Human-readable explanation
    file: Path
    line: int
    column: int
    hint: str              # Suggestion for fixing
    context: List[str]     # Surrounding source lines

class LexerError(StepsError): ...
class ParseError(StepsError): ...
class RuntimeError(StepsError): ...
class TypeError(StepsError): ...
```

### 10. Diagram (`diagram.py`)

**Purpose:** Generate visual flow diagrams.

**Output:** Text-based diagram (ASCII art) or structured data for rendering

**Responsibilities:**
- Parse building to extract flow
- Represent conditionals as branches
- Show step calls as nodes
- Indicate floor groupings

### 11. REPL (`repl.py`)

**Purpose:** Interactive interpreter for learning.

**Features:**
- Execute single statements
- Define temporary steps
- Show variable state
- Step-by-step execution mode
- Help system

## Execution Flow

### Startup

1. `main.py` parses command line arguments
2. Loader discovers and reads all project files
3. Lexer tokenizes each file
4. Parser builds AST for each file
5. Environment registers all floors and steps
6. Interpreter validates all step references exist
7. If validation passes, execution begins

### Runtime

1. Interpreter starts at building's first statement
2. For each statement:
   - Evaluate expressions
   - Execute side effects (display, set)
   - Handle control flow
3. For step calls:
   - Push new scope
   - Bind parameters
   - Execute step body
   - Pop scope, return value
4. Continue until `exit` or error

### Error Handling

At any phase, errors are collected with full context:
- Source file and location
- What was expected vs. found
- Suggested fix
- Surrounding code context

Multiple errors are reported when possible (don't stop at first).

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User's Project                          │
│  project/                                                       │
│  ├── project.building          (includes floors: section)       │
│  ├── floor1/                                                   │
│  │   └── step1.step                                            │
│  └── floor2/                                                   │
│      └── step2.step                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          Loader                                 │
│  - Validates project structure                                  │
│  - Collects all source files                                   │
│  - Returns: Project { building, floors: [Floor { steps }] }    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          Lexer                                  │
│  - Tokenizes each source file                                  │
│  - Handles indentation → INDENT/DEDENT tokens                  │
│  - Returns: Dict[Path, List[Token]]                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          Parser                                 │
│  - Builds AST for each file                                    │
│  - Validates syntax                                            │
│  - Returns: ProjectAST { BuildingNode, FloorNodes, StepNodes } │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Environment                               │
│  - Registers all floors and steps                              │
│  - Validates all references resolve                            │
│  - Prepares scope chain                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Interpreter                               │
│  - Walks AST from building entry point                         │
│  - Evaluates expressions                                       │
│  - Manages call stack for step invocations                     │
│  - Outputs via display, reads via input                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                         Program Output
```
