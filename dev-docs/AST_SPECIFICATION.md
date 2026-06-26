# Steps AST Specification

## Overview

The Abstract Syntax Tree (AST) represents the structure of a Steps program after parsing. Every node includes source location information for error reporting.

## Base Node

All nodes inherit from `ASTNode`:

```python
@dataclass
class SourceLocation:
    file: Path
    line: int
    column: int
    end_line: int
    end_column: int

@dataclass
class ASTNode:
    location: SourceLocation
```

## Top-Level Nodes

### BuildingNode

Represents a `.building` file (program entry point).

```python
@dataclass
class BuildingNode(ASTNode):
    name: str                      # Building/program name
    floors: List[FloorNode]        # Inline floor declarations (from floors: section)
    body: List[StatementNode]      # Statements to execute
```

**Example Source:**
```
building: price_calculator

    floors:
        floor: calculations
            step: calc_from_price_and_margin
            step: calc_from_price_and_cost

    display "Hello"
    call main_menu
    exit
```

### FloorNode

Represents a floor declaration (inline in the building's `floors:` section).

```python
@dataclass
class FloorNode(ASTNode):
    name: str                      # Floor name
    steps: List[str]               # Step names declared in this floor
```

**Example Source (within a building):**
```
floors:
    floor: calculations
        step: calc_from_price_and_margin
        step: calc_from_price_and_cost
```

### StepNode

Represents a `.step` file (single unit of work).

```python
@dataclass
class StepNode(ASTNode):
    name: str                      # Step name
    belongs_to: str                # Floor name
    expects: List[ParameterNode]   # Parameters (may be empty)
    returns: Optional[ReturnDeclaration]  # Return declaration or None
    risers: List[RiserNode]        # Private helper functions
    declarations: List[DeclarationNode]   # Variable declarations
    body: List[StatementNode]      # Logic to execute
```

**Example Source:**
```
step: greet_user
    belongs to: user_interaction
    expects: user_name
    returns: greeting

    declare:
        greeting as text

    do:
        set greeting to "Hello, " added to user_name
        return greeting
```

### RiserNode

Represents a private helper within a step.

```python
@dataclass
class RiserNode(ASTNode):
    name: str
    expects: List[ParameterNode]
    returns: Optional[ReturnDeclaration]
    body: List[StatementNode]
```

## Declaration Nodes

### ParameterNode

A parameter in expects clause.

```python
@dataclass
class ParameterNode(ASTNode):
    name: str
    type_annotation: Optional[str]  # Optional type hint
```

### ReturnDeclaration

The returns clause of a step/riser.

```python
@dataclass
class ReturnDeclaration(ASTNode):
    name: str                      # Name of return value
    type_annotation: Optional[str]  # Optional type hint
```

### DeclarationNode

A variable declaration in declare section.

```python
@dataclass
class DeclarationNode(ASTNode):
    name: str
    type_name: str                 # number, text, boolean, list, table
    is_fixed: bool                 # Whether type is locked
```

**Example Source:**
```
declare:
    count as number fixed
    name as text
```

## Statement Nodes

### DisplayStatement

Output to console.

```python
@dataclass
class DisplayStatement(ASTNode):
    expression: ExpressionNode
```

**Example:** `display "Hello, " added to name`

### SetStatement

Variable assignment.

```python
@dataclass
class SetStatement(ASTNode):
    target: str                    # Variable name
    value: ExpressionNode
```

**Example:** `set count to count + 1`

### CallStatement

Step or riser invocation.

```python
@dataclass
class CallStatement(ASTNode):
    step_name: str
    arguments: List[ExpressionNode]
    result_target: Optional[str]   # Variable to store result
```

**Example:** `call greet_user with name storing result in greeting`

### ReturnStatement

Return from step/riser.

```python
@dataclass
class ReturnStatement(ASTNode):
    value: Optional[ExpressionNode]
```

**Example:** `return greeting`

### ExitStatement

End program execution.

```python
@dataclass
class ExitStatement(ASTNode):
    pass
```

### IfStatement

Conditional branching.

```python
@dataclass
class IfBranch(ASTNode):
    condition: ExpressionNode
    body: List[StatementNode]

@dataclass
class IfStatement(ASTNode):
    if_branch: IfBranch
    otherwise_if_branches: List[IfBranch]
    otherwise_branch: Optional[List[StatementNode]]
```

**Example:**
```
if age is less than 18
    display "Minor"
otherwise if age is greater than 65
    display "Senior"
otherwise
    display "Adult"
```

### RepeatTimesStatement

Fixed-count loop.

```python
@dataclass
class RepeatTimesStatement(ASTNode):
    count: ExpressionNode
    body: List[StatementNode]
```

**Example:** `repeat 10 times`

### RepeatForEachStatement

Collection iteration.

```python
@dataclass
class RepeatForEachStatement(ASTNode):
    item_name: str
    collection: ExpressionNode
    body: List[StatementNode]
```

**Example:** `repeat for each item in my_list`

### RepeatWhileStatement

Conditional loop.

```python
@dataclass
class RepeatWhileStatement(ASTNode):
    condition: ExpressionNode
    body: List[StatementNode]
```

**Example:** `repeat while count is less than 100`

### AttemptStatement

Error handling.

```python
@dataclass
class AttemptStatement(ASTNode):
    attempt_body: List[StatementNode]
    unsuccessful_body: Optional[List[StatementNode]]
    continue_body: Optional[List[StatementNode]]
```

**Example:**
```
attempt:
    call risky_operation
if unsuccessful:
    display problem_message
then continue:
    call cleanup
```

### NoteStatement

Comment (preserved in AST for documentation tools).

```python
@dataclass
class NoteStatement(ASTNode):
    text: str
    is_block: bool                 # Single line vs block comment
```

### AddToListStatement

Add item to list.

```python
@dataclass
class AddToListStatement(ASTNode):
    item: ExpressionNode
    list_name: str
```

**Example:** `add item to my_list`

### RemoveFromListStatement

Remove item from list.

```python
@dataclass
class RemoveFromListStatement(ASTNode):
    item: ExpressionNode
    list_name: str
```

**Example:** `remove item from my_list`

## Expression Nodes

### LiteralNode

Literal values.

```python
@dataclass
class NumberLiteral(ASTNode):
    value: float

@dataclass
class TextLiteral(ASTNode):
    value: str

@dataclass
class BooleanLiteral(ASTNode):
    value: bool

@dataclass
class NothingLiteral(ASTNode):
    pass

@dataclass
class ListLiteral(ASTNode):
    elements: List[ExpressionNode]

@dataclass
class TableLiteral(ASTNode):
    pairs: List[Tuple[ExpressionNode, ExpressionNode]]
```

### IdentifierNode

Variable reference.

```python
@dataclass
class IdentifierNode(ASTNode):
    name: str
```

### InputNode

User input expression.

```python
@dataclass
class InputNode(ASTNode):
    pass  # Represents the `input` keyword
```

### BinaryOpNode

Binary operations (math, comparison, boolean).

```python
@dataclass
class BinaryOpNode(ASTNode):
    left: ExpressionNode
    operator: str                  # "+", "-", "is less than", "and", etc.
    right: ExpressionNode
```

### UnaryOpNode

Unary operations.

```python
@dataclass
class UnaryOpNode(ASTNode):
    operator: str                  # "not", "-"
    operand: ExpressionNode
```

### TypeConversionNode

Type conversion expression.

```python
@dataclass
class TypeConversionNode(ASTNode):
    expression: ExpressionNode
    target_type: str               # "number", "text", "boolean"
```

**Example:** `input_text as number`

### TableAccessNode

Table/list index access.

```python
@dataclass
class TableAccessNode(ASTNode):
    table: ExpressionNode
    key: ExpressionNode
```

**Example:** `results["price"]` or `my_list[0]`

### TextOperationNode

Text-specific operations.

```python
@dataclass
class AddedToNode(ASTNode):
    left: ExpressionNode
    right: ExpressionNode

@dataclass  
class SplitByNode(ASTNode):
    text: ExpressionNode
    delimiter: ExpressionNode

@dataclass
class CharacterAtNode(ASTNode):
    index: ExpressionNode
    text: ExpressionNode

@dataclass
class LengthOfNode(ASTNode):
    collection: ExpressionNode

@dataclass
class ContainsNode(ASTNode):
    text: ExpressionNode
    substring: ExpressionNode

@dataclass
class StartsWithNode(ASTNode):
    text: ExpressionNode
    prefix: ExpressionNode

@dataclass
class EndsWithNode(ASTNode):
    text: ExpressionNode
    suffix: ExpressionNode
```

### IsInNode

List membership check.

```python
@dataclass
class IsInNode(ASTNode):
    item: ExpressionNode
    collection: ExpressionNode
```

**Example:** `item is in my_list`

### CallExpression

Step call used as expression (when step returns a value).

```python
@dataclass
class CallExpression(ASTNode):
    step_name: str
    arguments: List[ExpressionNode]
```

Note: Most calls use CallStatement with `storing result in`. CallExpression is for inline usage.

## AST Example

For this source:

```
step: greet
    belongs to: ui
    expects: name
    returns: message

    declare:
        message as text

    do:
        set message to "Hello, " added to name
        return message
```

The AST would be:

```python
StepNode(
    location=SourceLocation(file="greet.step", line=1, ...),
    name="greet",
    belongs_to="ui",
    expects=[
        ParameterNode(name="name", type_annotation=None)
    ],
    returns=ReturnDeclaration(name="message", type_annotation=None),
    risers=[],
    declarations=[
        DeclarationNode(name="message", type_name="text", is_fixed=False)
    ],
    body=[
        SetStatement(
            target="message",
            value=AddedToNode(
                left=TextLiteral(value="Hello, "),
                right=IdentifierNode(name="name")
            )
        ),
        ReturnStatement(
            value=IdentifierNode(name="message")
        )
    ]
)
```

## Visitor Pattern

For tree traversal, implement a visitor:

```python
class ASTVisitor:
    def visit(self, node: ASTNode) -> Any:
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node: ASTNode) -> Any:
        raise NotImplementedError(f"No visitor for {type(node).__name__}")
    
    def visit_BuildingNode(self, node: BuildingNode) -> Any:
        ...
    
    def visit_StepNode(self, node: StepNode) -> Any:
        ...
    
    # ... etc for all node types
```
