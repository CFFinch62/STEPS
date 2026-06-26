"""Steps Abstract Syntax Tree Node Definitions.

This module defines all AST node types for the Steps language.
Every node includes source location information for accurate error reporting.

Node Categories:
- Top-Level: BuildingNode, FloorNode, StepNode, RiserNode
- Declarations: ParameterNode, ReturnDeclaration, DeclarationNode
- Statements: DisplayStatement, SetStatement, CallStatement, etc.
- Expressions: NumberLiteral, BinaryOpNode, IdentifierNode, etc.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional, Tuple, Union
from abc import ABC

from .errors import SourceLocation


# =============================================================================
# Base Classes
# =============================================================================

@dataclass
class ASTNode(ABC):
    """Base class for all AST nodes.
    
    Every node must have a source location for error reporting.
    """
    location: SourceLocation


class ExpressionNode(ASTNode):
    """Base class for expression nodes (nodes that produce values)."""
    pass


class StatementNode(ASTNode):
    """Base class for statement nodes (nodes that perform actions)."""
    pass


# =============================================================================
# Top-Level Nodes
# =============================================================================

@dataclass
class BuildingNode(ASTNode):
    """Represents a .building file (program entry point).
    
    Attributes:
        name: Building/program name
        floors: Inline floor declarations defining the project's floor/step structure
        body: Statements to execute
    """
    name: str
    floors: List["FloorNode"] = field(default_factory=list)
    body: List[StatementNode] = field(default_factory=list)


@dataclass
class FloorNode(ASTNode):
    """Represents an inline floor declaration within a building file.
    
    Attributes:
        name: Floor name
        steps: Step names declared in this floor
    """
    name: str
    steps: List[str] = field(default_factory=list)


@dataclass
class ParameterNode(ASTNode):
    """A parameter in an expects clause.
    
    Attributes:
        name: Parameter name
        type_annotation: Optional type hint (e.g., "number", "text")
    """
    name: str
    type_annotation: Optional[str] = None


@dataclass
class ReturnDeclaration(ASTNode):
    """The returns clause of a step/riser.
    
    Attributes:
        name: Name of return value
        type_annotation: Optional type hint
    """
    name: str
    type_annotation: Optional[str] = None


@dataclass
class DeclarationNode(ASTNode):
    """A variable declaration in the declare section.
    
    Attributes:
        name: Variable name
        type_name: Declared type (number, text, boolean, list, table)
        is_fixed: Whether type is locked (cannot be changed)
    """
    name: str
    type_name: str
    is_fixed: bool = False


@dataclass
class RiserNode(ASTNode):
    """Represents a private helper function within a step.
    
    Attributes:
        name: Riser name
        expects: Parameters (may be empty)
        returns: Return declaration or None
        declarations: Variable declarations (may be empty)
        body: Statements to execute
    """
    name: str
    expects: List[ParameterNode] = field(default_factory=list)
    returns: Optional[ReturnDeclaration] = None
    declarations: List[DeclarationNode] = field(default_factory=list)
    body: List[StatementNode] = field(default_factory=list)


@dataclass
class StepNode(ASTNode):
    """Represents a .step file (single unit of work).
    
    Attributes:
        name: Step name
        belongs_to: Floor name this step belongs to
        expects: Parameters (may be empty)
        returns: Return declaration or None
        risers: Private helper functions
        declarations: Variable declarations
        body: Statements to execute
    """
    name: str
    belongs_to: str
    expects: List[ParameterNode] = field(default_factory=list)
    returns: Optional[ReturnDeclaration] = None
    risers: List[RiserNode] = field(default_factory=list)
    declarations: List[DeclarationNode] = field(default_factory=list)
    body: List[StatementNode] = field(default_factory=list)


# =============================================================================
# Statement Nodes
# =============================================================================

@dataclass
class DisplayStatement(StatementNode):
    """Output to console.

    Example: display "Hello, world!"
    """
    expression: ExpressionNode


@dataclass
class IndicateStatement(StatementNode):
    """Output to console without newline.

    Example: indicate "Progress: "
    """
    expression: ExpressionNode


@dataclass
class ClearConsoleStatement(StatementNode):
    """Clear the console screen.

    Example: clear console
    """
    pass


@dataclass
class SetIterationLimitStatement(StatementNode):
    """Set the maximum iteration limit for loops.

    Example: set iteration limit to 100000
    """
    limit: ExpressionNode


@dataclass
class WriteStatement(StatementNode):
    """Output to console without newline.

    Example: write "Progress: "
    """
    expression: ExpressionNode


@dataclass
class ClearConsoleStatement(StatementNode):
    """Clear the console screen.

    Example: clear console
    """
    pass


@dataclass
class SetIterationLimitStatement(StatementNode):
    """Set the maximum iteration limit for loops.

    Example: set iteration limit to 100000
    """
    limit: ExpressionNode


@dataclass
class SetStatement(StatementNode):
    """Variable assignment.
    
    Example: set count to count + 1
    
    Attributes:
        target: Variable name to assign to
        value: Expression to evaluate and assign
    """
    target: str
    value: ExpressionNode


@dataclass
class SetIndexStatement(StatementNode):
    """Indexed assignment (table or list).
    
    Example: set my_table["key"] to value
    Example: set my_list[0] to value
    
    Attributes:
        target: Variable name of table or list
        index: Expression for key (table) or index (list)
        value: Expression to evaluate and assign
    """
    target: str
    index: ExpressionNode
    value: ExpressionNode


@dataclass
class CallStatement(StatementNode):
    """Step or riser invocation.
    
    Example: call greet_user with name storing result in greeting
    
    Attributes:
        step_name: Name of step/riser to call
        arguments: Expressions for arguments
        result_target: Variable to store result (None if not storing)
    """
    step_name: str
    arguments: List[ExpressionNode] = field(default_factory=list)
    result_target: Optional[str] = None


@dataclass
class ReturnStatement(StatementNode):
    """Return from step/riser.
    
    Example: return greeting
    
    Attributes:
        value: Expression to return (None for return without value)
    """
    value: Optional[ExpressionNode] = None


@dataclass
class ExitStatement(StatementNode):
    """End program execution.
    
    Example: exit
    """
    pass


@dataclass
class IfBranch(ASTNode):
    """A single branch in an if statement.
    
    Attributes:
        condition: Expression to evaluate
        body: Statements to execute if condition is true
    """
    condition: ExpressionNode
    body: List[StatementNode] = field(default_factory=list)


@dataclass
class IfStatement(StatementNode):
    """Conditional branching.
    
    Example:
        if age is less than 18
            display "Minor"
        otherwise if age is greater than 65
            display "Senior"
        otherwise
            display "Adult"
    
    Attributes:
        if_branch: The main if condition and body
        otherwise_if_branches: Zero or more 'otherwise if' branches
        otherwise_branch: Optional 'otherwise' body
    """
    if_branch: IfBranch
    otherwise_if_branches: List[IfBranch] = field(default_factory=list)
    otherwise_branch: Optional[List[StatementNode]] = None


@dataclass
class RepeatTimesStatement(StatementNode):
    """Fixed-count loop.
    
    Example: repeat 10 times
    
    Attributes:
        count: Expression for number of iterations
        body: Statements to execute each iteration
    """
    count: ExpressionNode
    body: List[StatementNode] = field(default_factory=list)


@dataclass
class RepeatForEachStatement(StatementNode):
    """Collection iteration loop.
    
    Example: repeat for each item in my_list
    
    Attributes:
        item_name: Variable name for current item
        collection: Expression evaluating to a list
        body: Statements to execute for each item
    """
    item_name: str
    collection: ExpressionNode
    body: List[StatementNode] = field(default_factory=list)


@dataclass
class RepeatWhileStatement(StatementNode):
    """Conditional loop.
    
    Example: repeat while count is less than 100
    
    Attributes:
        condition: Expression to check each iteration
        body: Statements to execute while condition is true
    """
    condition: ExpressionNode
    body: List[StatementNode] = field(default_factory=list)


@dataclass
class AttemptStatement(StatementNode):
    """Error handling block.
    
    Example:
        attempt:
            call risky_operation
        if unsuccessful:
            display problem_message
        then continue:
            call cleanup
    
    Attributes:
        attempt_body: Statements to attempt
        unsuccessful_body: Statements if error occurs (optional)
        continue_body: Cleanup statements that always run (optional)
    """
    attempt_body: List[StatementNode] = field(default_factory=list)
    unsuccessful_body: Optional[List[StatementNode]] = None
    continue_body: Optional[List[StatementNode]] = None


@dataclass
class NoteStatement(StatementNode):
    """Comment (preserved in AST for documentation tools).
    
    Example: note: This is a comment
    
    Attributes:
        text: Comment text
        is_block: True for multi-line note block
    """
    text: str
    is_block: bool = False


@dataclass
class AddToListStatement(StatementNode):
    """Add item to list.
    
    Example: add item to my_list
    
    Attributes:
        item: Expression for item to add
        list_name: Variable name of list
    """
    item: ExpressionNode
    list_name: str


@dataclass
class RemoveFromListStatement(StatementNode):
    """Remove item from list.
    
    Example: remove item from my_list
    
    Attributes:
        item: Expression for item to remove
        list_name: Variable name of list
    """
    item: ExpressionNode
    list_name: str


# =============================================================================
# Expression Nodes - Literals
# =============================================================================

@dataclass
class NumberLiteral(ExpressionNode):
    """Numeric literal.
    
    Example: 42, 3.14, -7
    """
    value: float


@dataclass
class TextLiteral(ExpressionNode):
    """String literal.
    
    Example: "Hello, world!"
    """
    value: str


@dataclass
class BooleanLiteral(ExpressionNode):
    """Boolean literal.
    
    Example: true, false
    """
    value: bool


@dataclass
class NothingLiteral(ExpressionNode):
    """The 'nothing' value.
    
    Example: nothing
    """
    pass


@dataclass
class ListLiteral(ExpressionNode):
    """List literal.
    
    Example: [1, 2, 3]
    """
    elements: List[ExpressionNode] = field(default_factory=list)


@dataclass
class TableLiteral(ExpressionNode):
    """Table literal (key-value pairs).
    
    Example: ["name": "Alice", "age": 30]
    
    Attributes:
        pairs: List of (key_expression, value_expression) tuples
    """
    pairs: List[Tuple[ExpressionNode, ExpressionNode]] = field(default_factory=list)


# =============================================================================
# Expression Nodes - References and Input
# =============================================================================

@dataclass
class IdentifierNode(ExpressionNode):
    """Variable reference.
    
    Example: my_variable
    """
    name: str


@dataclass
class InputNode(ExpressionNode):
    """User input expression.
    
    Example: set name to input
    """
    pass


# =============================================================================
# Expression Nodes - Operations
# =============================================================================

@dataclass
class BinaryOpNode(ExpressionNode):
    """Binary operation (math, comparison, boolean).
    
    Example: x + y, a is greater than b, flag and other_flag
    
    Attributes:
        left: Left operand
        operator: Operator string (+, -, is equal to, and, etc.)
        right: Right operand
    """
    left: ExpressionNode
    operator: str
    right: ExpressionNode


@dataclass
class UnaryOpNode(ExpressionNode):
    """Unary operation.
    
    Example: not flag, -value
    
    Attributes:
        operator: Operator string (not, -)
        operand: Expression to operate on
    """
    operator: str
    operand: ExpressionNode


@dataclass
class TypeConversionNode(ExpressionNode):
    """Type conversion expression.
    
    Example: input_text as number
    
    Attributes:
        expression: Expression to convert
        target_type: Target type name
    """
    expression: ExpressionNode
    target_type: str


@dataclass
class FormatNumberNode(ExpressionNode):
    """Number formatting expression.
    
    Example: pi as decimal(2)
    
    Attributes:
        expression: Expression to format
        decimal_places: Expression for number of decimal places
    """
    expression: ExpressionNode
    decimal_places: ExpressionNode



@dataclass
class TypeOfNode(ExpressionNode):
    """Get the type of an expression.
    
    Example: type of 42 → "number"
    
    Attributes:
        expression: Expression to get type of
    """
    expression: ExpressionNode


@dataclass
class TypeCheckNode(ExpressionNode):
    """Check if expression is of a specific type.
    
    Example: x is a number → true/false
    
    Attributes:
        expression: Expression to check
        type_name: Type to check for ("number", "text", "boolean", "list", "table")
    """
    expression: ExpressionNode
    type_name: str


@dataclass
class TableAccessNode(ExpressionNode):
    """Table/list index access.
    
    Example: results["price"], my_list[0]
    
    Attributes:
        table: Expression evaluating to table or list
        key: Expression for key or index
    """
    table: ExpressionNode
    key: ExpressionNode


# =============================================================================
# Expression Nodes - Text Operations
# =============================================================================

@dataclass
class AddedToNode(ExpressionNode):
    """Text concatenation.
    
    Example: "Hello, " added to name
    """
    left: ExpressionNode
    right: ExpressionNode


@dataclass
class SplitByNode(ExpressionNode):
    """Split text by delimiter.
    
    Example: text split by ","
    """
    text: ExpressionNode
    delimiter: ExpressionNode


@dataclass
class CharacterAtNode(ExpressionNode):
    """Get character at index.
    
    Example: character at 0 of text
    """
    index: ExpressionNode
    text: ExpressionNode


@dataclass
class LengthOfNode(ExpressionNode):
    """Get length of collection or text.
    
    Example: length of my_list
    """
    collection: ExpressionNode


@dataclass
class ContainsNode(ExpressionNode):
    """Check if text contains substring.
    
    Example: text contains "hello"
    """
    text: ExpressionNode
    substring: ExpressionNode


@dataclass
class StartsWithNode(ExpressionNode):
    """Check if text starts with prefix.
    
    Example: text starts with "http"
    """
    text: ExpressionNode
    prefix: ExpressionNode


@dataclass
class EndsWithNode(ExpressionNode):
    """Check if text ends with suffix.
    
    Example: text ends with ".txt"
    """
    text: ExpressionNode
    suffix: ExpressionNode


# =============================================================================
# Expression Nodes - List Operations
# =============================================================================

@dataclass
class IsInNode(ExpressionNode):
    """List membership check.
    
    Example: item is in my_list
    """
    item: ExpressionNode
    collection: ExpressionNode


# =============================================================================
# Visitor Pattern
# =============================================================================

class ASTVisitor:
    """Base class for AST visitors.
    
    Subclasses should implement visit_* methods for each node type
    they need to handle.
    """
    
    def visit(self, node: ASTNode) -> Any:
        """Visit a node by dispatching to the appropriate visitor method."""
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node: ASTNode) -> Any:
        """Called when no specific visitor exists for a node type."""
        raise NotImplementedError(f"No visitor for {type(node).__name__}")
    
    # Top-level nodes
    def visit_BuildingNode(self, node: BuildingNode) -> Any:
        raise NotImplementedError
    
    def visit_FloorNode(self, node: FloorNode) -> Any:
        raise NotImplementedError
    
    def visit_StepNode(self, node: StepNode) -> Any:
        raise NotImplementedError
    
    def visit_RiserNode(self, node: RiserNode) -> Any:
        raise NotImplementedError
    
    # Statement nodes
    def visit_DisplayStatement(self, node: DisplayStatement) -> Any:
        raise NotImplementedError
    
    def visit_SetStatement(self, node: SetStatement) -> Any:
        raise NotImplementedError
    
    def visit_SetIndexStatement(self, node: 'SetIndexStatement') -> Any:
        raise NotImplementedError
    
    def visit_CallStatement(self, node: CallStatement) -> Any:
        raise NotImplementedError

    
    def visit_ReturnStatement(self, node: ReturnStatement) -> Any:
        raise NotImplementedError
    
    def visit_ExitStatement(self, node: ExitStatement) -> Any:
        raise NotImplementedError
    
    def visit_IfStatement(self, node: IfStatement) -> Any:
        raise NotImplementedError
    
    def visit_RepeatTimesStatement(self, node: RepeatTimesStatement) -> Any:
        raise NotImplementedError
    
    def visit_RepeatForEachStatement(self, node: RepeatForEachStatement) -> Any:
        raise NotImplementedError
    
    def visit_RepeatWhileStatement(self, node: RepeatWhileStatement) -> Any:
        raise NotImplementedError
    
    def visit_AttemptStatement(self, node: AttemptStatement) -> Any:
        raise NotImplementedError
    
    def visit_NoteStatement(self, node: NoteStatement) -> Any:
        raise NotImplementedError
    
    def visit_AddToListStatement(self, node: AddToListStatement) -> Any:
        raise NotImplementedError
    
    def visit_RemoveFromListStatement(self, node: RemoveFromListStatement) -> Any:
        raise NotImplementedError
    
    # Expression nodes - Literals
    def visit_NumberLiteral(self, node: NumberLiteral) -> Any:
        raise NotImplementedError
    
    def visit_TextLiteral(self, node: TextLiteral) -> Any:
        raise NotImplementedError
    
    def visit_BooleanLiteral(self, node: BooleanLiteral) -> Any:
        raise NotImplementedError
    
    def visit_NothingLiteral(self, node: NothingLiteral) -> Any:
        raise NotImplementedError
    
    def visit_ListLiteral(self, node: ListLiteral) -> Any:
        raise NotImplementedError
    
    def visit_TableLiteral(self, node: TableLiteral) -> Any:
        raise NotImplementedError
    
    # Expression nodes - References
    def visit_IdentifierNode(self, node: IdentifierNode) -> Any:
        raise NotImplementedError
    
    def visit_InputNode(self, node: InputNode) -> Any:
        raise NotImplementedError
    
    # Expression nodes - Operations
    def visit_BinaryOpNode(self, node: BinaryOpNode) -> Any:
        raise NotImplementedError
    
    def visit_UnaryOpNode(self, node: UnaryOpNode) -> Any:
        raise NotImplementedError
    
    def visit_TypeConversionNode(self, node: TypeConversionNode) -> Any:
        raise NotImplementedError
    
    def visit_TypeOfNode(self, node: 'TypeOfNode') -> Any:
        raise NotImplementedError
    
    def visit_TypeCheckNode(self, node: 'TypeCheckNode') -> Any:
        raise NotImplementedError
    
    def visit_TableAccessNode(self, node: TableAccessNode) -> Any:
        raise NotImplementedError

    
    # Expression nodes - Text operations
    def visit_AddedToNode(self, node: AddedToNode) -> Any:
        raise NotImplementedError
    
    def visit_SplitByNode(self, node: SplitByNode) -> Any:
        raise NotImplementedError
    
    def visit_CharacterAtNode(self, node: CharacterAtNode) -> Any:
        raise NotImplementedError
    
    def visit_LengthOfNode(self, node: LengthOfNode) -> Any:
        raise NotImplementedError
    
    def visit_ContainsNode(self, node: ContainsNode) -> Any:
        raise NotImplementedError
    
    def visit_StartsWithNode(self, node: StartsWithNode) -> Any:
        raise NotImplementedError
    
    def visit_EndsWithNode(self, node: EndsWithNode) -> Any:
        raise NotImplementedError
    
    # Expression nodes - List operations
    def visit_IsInNode(self, node: IsInNode) -> Any:
        raise NotImplementedError


def pretty_print(node: ASTNode, indent: int = 0) -> str:
    """Generate a pretty-printed representation of an AST node.
    
    Useful for debugging and understanding program structure.
    """
    prefix = "  " * indent
    lines = [f"{prefix}{type(node).__name__}"]
    
    for field_name, field_value in node.__dict__.items():
        if field_name == "location":
            continue  # Skip location for cleaner output
        
        if isinstance(field_value, ASTNode):
            lines.append(f"{prefix}  {field_name}:")
            lines.append(pretty_print(field_value, indent + 2))
        elif isinstance(field_value, list):
            if field_value:
                lines.append(f"{prefix}  {field_name}: [")
                for item in field_value:
                    if isinstance(item, ASTNode):
                        lines.append(pretty_print(item, indent + 2))
                    else:
                        lines.append(f"{prefix}    {repr(item)}")
                lines.append(f"{prefix}  ]")
            else:
                lines.append(f"{prefix}  {field_name}: []")
        else:
            lines.append(f"{prefix}  {field_name}: {repr(field_value)}")
    
    return "\n".join(lines)
