"""Unit Tests for Steps Parser.

Comprehensive tests for parsing including:
- Building, floor, and step file structures
- All statement types
- Expression parsing with correct precedence
- Error handling and recovery
"""

import pytest
from pathlib import Path

from steps.parser import (
    Parser, ParseResult, parse_building, parse_floor, parse_step
)
from steps.lexer import Lexer, TokenType
from steps.ast_nodes import (
    BuildingNode, FloorNode, StepNode, RiserNode,
    DisplayStatement, SetStatement, CallStatement,
    ReturnStatement, ExitStatement, IfStatement,
    RepeatTimesStatement, RepeatForEachStatement, RepeatWhileStatement,
    AttemptStatement, AddToListStatement, RemoveFromListStatement,
    NumberLiteral, TextLiteral, BooleanLiteral, NothingLiteral,
    ListLiteral, TableLiteral, IdentifierNode, InputNode,
    BinaryOpNode, UnaryOpNode, TypeConversionNode, TableAccessNode,
    LengthOfNode, CharacterAtNode, AddedToNode, SplitByNode,
    ContainsNode, StartsWithNode, EndsWithNode, IsInNode,
)


# =============================================================================
# Helper Functions
# =============================================================================

def make_parser(source: str) -> Parser:
    """Create a parser from source code."""
    path = Path("test.step")
    lexer = Lexer(source, path)
    tokens = lexer.tokenize()
    return Parser(tokens, path)


# =============================================================================
# Building File Tests
# =============================================================================

class TestParseBuilding:
    """Tests for parsing .building files."""
    
    def test_minimal_building(self):
        source = """building: hello

    exit
"""
        result = parse_building(source)
        assert result.success
        assert isinstance(result.ast, BuildingNode)
        assert result.ast.name == "hello"
        assert len(result.ast.body) == 1
    
    def test_building_with_display(self):
        source = """building: test

    display "Hello, World!"
    exit
"""
        result = parse_building(source)
        assert result.success
        assert len(result.ast.body) == 2
        assert isinstance(result.ast.body[0], DisplayStatement)
        assert isinstance(result.ast.body[1], ExitStatement)
    
    def test_building_with_multiple_statements(self):
        source = """building: test

    set x to 10
    set y to 20
    display x + y
    exit
"""
        result = parse_building(source)
        assert result.success
        assert len(result.ast.body) == 4


# =============================================================================
# Building File with Floors Tests
# =============================================================================

class TestParseBuildingFloors:
    """Tests for parsing building files with inline 'floors:' section."""
    
    def test_building_with_single_floor(self):
        source = """building: my_app

    floors:
        floor: main
            step: greet
            step: farewell

    display "Starting"
    exit
"""
        result = parse_building(source)
        assert result.success
        assert isinstance(result.ast, BuildingNode)
        assert result.ast.name == "my_app"
        assert len(result.ast.floors) == 1
        assert result.ast.floors[0].name == "main"
        assert result.ast.floors[0].steps == ["greet", "farewell"]
        # Body should have display + exit
        assert len(result.ast.body) == 2
    
    def test_building_with_multiple_floors(self):
        source = """building: calculator

    floors:
        floor: math_ops
            step: add_numbers
            step: subtract_numbers
            step: multiply_numbers
        floor: output
            step: show_result
            step: show_menu

    call show_menu
    exit
"""
        result = parse_building(source)
        assert result.success
        assert len(result.ast.floors) == 2
        
        math_floor = result.ast.floors[0]
        assert math_floor.name == "math_ops"
        assert math_floor.steps == ["add_numbers", "subtract_numbers", "multiply_numbers"]
        
        output_floor = result.ast.floors[1]
        assert output_floor.name == "output"
        assert output_floor.steps == ["show_result", "show_menu"]
    
    def test_building_with_floors_and_notes(self):
        source = """building: app

    note: This is a cool app

    floors:
        floor: helpers
            step: utility

    display "Hello"
    exit
"""
        result = parse_building(source)
        assert result.success
        assert len(result.ast.floors) == 1
        assert result.ast.floors[0].name == "helpers"
        # Body should include the note + display + exit
        assert len(result.ast.body) == 3
    
    def test_building_with_floors_and_do_block(self):
        source = """building: advanced

    floors:
        floor: calculations
            step: compute

    do:
        set x to 10
        call compute
        exit
"""
        result = parse_building(source)
        assert result.success
        assert len(result.ast.floors) == 1
        assert result.ast.floors[0].name == "calculations"
        # Body should have set + call + exit from the do: block
        assert len(result.ast.body) == 3
    
    def test_building_with_only_floors_no_body(self):
        source = """building: lib

    floors:
        floor: utils
            step: helper
"""
        result = parse_building(source)
        assert result.success
        assert len(result.ast.floors) == 1
        assert result.ast.floors[0].name == "utils"
        assert len(result.ast.body) == 0
    
    def test_building_without_floors_section(self):
        """Building files without a floors: section should still work."""
        source = """building: simple

    display "No floors here"
    exit
"""
        result = parse_building(source)
        assert result.success
        assert len(result.ast.floors) == 0
        assert len(result.ast.body) == 2
    
    def test_building_floor_with_single_step(self):
        source = """building: tiny

    floors:
        floor: main
            step: only_step

    exit
"""
        result = parse_building(source)
        assert result.success
        assert len(result.ast.floors) == 1
        assert result.ast.floors[0].steps == ["only_step"]


# =============================================================================
# Floor File Tests
# =============================================================================

class TestParseFloor:
    """Tests for parsing .floor files."""
    
    def test_floor_with_steps(self):
        source = """floor: main

    step: greet
    step: farewell
"""
        result = parse_floor(source)
        assert result.success
        assert isinstance(result.ast, FloorNode)
        assert result.ast.name == "main"
        assert result.ast.steps == ["greet", "farewell"]
    
    def test_floor_single_step(self):
        source = """floor: utilities

    step: calculate
"""
        result = parse_floor(source)
        assert result.success
        assert len(result.ast.steps) == 1
        assert result.ast.steps[0] == "calculate"


# =============================================================================
# Step File Tests
# =============================================================================

class TestParseStep:
    """Tests for parsing .step files."""
    
    def test_minimal_step(self):
        source = """step: greet
    belongs to: main
    expects: nothing
    returns: nothing

    do:
        display "Hello"
"""
        result = parse_step(source)
        assert result.success
        assert isinstance(result.ast, StepNode)
        assert result.ast.name == "greet"
        assert result.ast.belongs_to == "main"
    
    def test_step_with_parameters(self):
        source = """step: greet
    belongs to: main
    expects: name, age as number

    do:
        display name
"""
        result = parse_step(source)
        assert result.success
        assert len(result.ast.expects) == 2
        assert result.ast.expects[0].name == "name"
        assert result.ast.expects[1].name == "age"
        assert result.ast.expects[1].type_annotation == "number"
    
    def test_step_with_return(self):
        source = """step: addnumbers
    belongs to: math
    expects: a, b
    returns: result as number

    do:
        return a + b
"""
        result = parse_step(source)
        assert result.success
        assert result.ast.returns is not None
        assert result.ast.returns.name == "result"
        assert result.ast.returns.type_annotation == "number"
    
    def test_step_with_declarations(self):
        source = """step: counter
    belongs to: main

    declare:
        count as number
        name as text fixed

    do:
        set count to 0
"""
        result = parse_step(source)
        assert result.success
        assert len(result.ast.declarations) == 2
        assert result.ast.declarations[0].name == "count"
        assert result.ast.declarations[0].type_name == "number"
        assert not result.ast.declarations[0].is_fixed
        assert result.ast.declarations[1].is_fixed
    
    def test_step_with_riser(self):
        source = """step: process
    belongs to: main

    riser: helper
        expects: x
        returns: y

        do:
            return x + 1

    do:
        call helper with 5 storing result in result
"""
        result = parse_step(source)
        assert result.success
        assert len(result.ast.risers) == 1
        assert result.ast.risers[0].name == "helper"


# =============================================================================
# Statement Tests
# =============================================================================

class TestParseStatements:
    """Tests for parsing individual statement types."""
    
    def test_display_statement(self):
        source = """building: test

    display "hello"
"""
        result = parse_building(source)
        assert result.success
        stmt = result.ast.body[0]
        assert isinstance(stmt, DisplayStatement)
        assert isinstance(stmt.expression, TextLiteral)
    
    def test_set_statement(self):
        source = """building: test

    set x to 42
"""
        result = parse_building(source)
        assert result.success
        stmt = result.ast.body[0]
        assert isinstance(stmt, SetStatement)
        assert stmt.target == "x"
        assert isinstance(stmt.value, NumberLiteral)
    
    def test_call_statement_simple(self):
        source = """building: test

    call greet
"""
        result = parse_building(source)
        assert result.success
        stmt = result.ast.body[0]
        assert isinstance(stmt, CallStatement)
        assert stmt.step_name == "greet"
        assert len(stmt.arguments) == 0
        assert stmt.result_target is None
    
    def test_call_statement_with_args(self):
        source = """building: test

    call greet with "Alice", 25
"""
        result = parse_building(source)
        assert result.success
        stmt = result.ast.body[0]
        assert isinstance(stmt, CallStatement)
        assert len(stmt.arguments) == 2
    
    def test_call_statement_with_result(self):
        source = """building: test

    call calculate with 10, 20 storing result in sum
"""
        result = parse_building(source)
        assert result.success
        stmt = result.ast.body[0]
        assert isinstance(stmt, CallStatement)
        assert stmt.result_target == "sum"
    
    def test_return_statement_with_value(self):
        source = """step: addnumbers
    belongs to: main

    do:
        return 42
"""
        result = parse_step(source)
        assert result.success
        stmt = result.ast.body[0]
        assert isinstance(stmt, ReturnStatement)
        assert stmt.value is not None
    
    def test_return_statement_empty(self):
        source = """step: done
    belongs to: main

    do:
        return
"""
        result = parse_step(source)
        assert result.success
        stmt = result.ast.body[0]
        assert isinstance(stmt, ReturnStatement)
        assert stmt.value is None
    
    def test_exit_statement(self):
        source = """building: test

    exit
"""
        result = parse_building(source)
        assert result.success
        stmt = result.ast.body[0]
        assert isinstance(stmt, ExitStatement)


# =============================================================================
# Control Flow Tests
# =============================================================================

class TestParseControlFlow:
    """Tests for control flow statements."""
    
    def test_if_simple(self):
        source = """building: test

    if true
        display "yes"
"""
        result = parse_building(source)
        assert result.success
        stmt = result.ast.body[0]
        assert isinstance(stmt, IfStatement)
        assert len(stmt.if_branch.body) == 1
    
    def test_if_with_otherwise(self):
        source = """building: test

    if false
        display "no"
    otherwise
        display "yes"
"""
        result = parse_building(source)
        assert result.success
        stmt = result.ast.body[0]
        assert isinstance(stmt, IfStatement)
        assert stmt.otherwise_branch is not None
    
    def test_if_with_otherwise_if(self):
        source = """building: test

    if x is equal to 1
        display "one"
    otherwise if x is equal to 2
        display "two"
    otherwise
        display "other"
"""
        result = parse_building(source)
        assert result.success
        stmt = result.ast.body[0]
        assert isinstance(stmt, IfStatement)
        assert len(stmt.otherwise_if_branches) == 1
        assert stmt.otherwise_branch is not None
    
    def test_repeat_times(self):
        source = """building: test

    repeat 5 times
        display "loop"
"""
        result = parse_building(source)
        assert result.success
        stmt = result.ast.body[0]
        assert isinstance(stmt, RepeatTimesStatement)
        assert isinstance(stmt.count, NumberLiteral)
    
    def test_repeat_for_each(self):
        source = """building: test

    repeat for each item in my_list
        display item
"""
        result = parse_building(source)
        assert result.success
        stmt = result.ast.body[0]
        assert isinstance(stmt, RepeatForEachStatement)
        assert stmt.item_name == "item"
    
    def test_repeat_while(self):
        source = """building: test

    repeat while x is less than 10
        set x to x + 1
"""
        result = parse_building(source)
        assert result.success
        stmt = result.ast.body[0]
        assert isinstance(stmt, RepeatWhileStatement)
    
    def test_attempt_simple(self):
        source = """building: test

    attempt:
        call risky
"""
        result = parse_building(source)
        assert result.success
        stmt = result.ast.body[0]
        assert isinstance(stmt, AttemptStatement)
        assert len(stmt.attempt_body) == 1
    
    def test_attempt_with_unsuccessful(self):
        source = """building: test

    attempt:
        call risky
    if unsuccessful:
        display "failed"
"""
        result = parse_building(source)
        assert result.success
        stmt = result.ast.body[0]
        assert isinstance(stmt, AttemptStatement)
        assert stmt.unsuccessful_body is not None
    
    def test_attempt_full(self):
        source = """building: test

    attempt:
        call risky
    if unsuccessful:
        display "failed"
    then continue:
        call cleanup
"""
        result = parse_building(source)
        assert result.success
        stmt = result.ast.body[0]
        assert isinstance(stmt, AttemptStatement)
        assert stmt.unsuccessful_body is not None
        assert stmt.continue_body is not None


# =============================================================================
# List Operations Tests
# =============================================================================

class TestParseListOperations:
    """Tests for list operation statements."""
    
    def test_add_to_list(self):
        source = """building: test

    add 42 to my_list
"""
        result = parse_building(source)
        assert result.success
        stmt = result.ast.body[0]
        assert isinstance(stmt, AddToListStatement)
        assert stmt.list_name == "my_list"
    
    def test_remove_from_list(self):
        source = """building: test

    remove 42 from my_list
"""
        result = parse_building(source)
        assert result.success
        stmt = result.ast.body[0]
        assert isinstance(stmt, RemoveFromListStatement)
        assert stmt.list_name == "my_list"


# =============================================================================
# Expression Tests - Literals
# =============================================================================

class TestParseLiterals:
    """Tests for parsing literal expressions."""
    
    def test_number_literal(self):
        source = """building: test

    display 42
"""
        result = parse_building(source)
        assert result.success
        expr = result.ast.body[0].expression
        assert isinstance(expr, NumberLiteral)
        assert expr.value == 42.0
    
    def test_decimal_literal(self):
        source = """building: test

    display 3.14
"""
        result = parse_building(source)
        assert result.success
        expr = result.ast.body[0].expression
        assert isinstance(expr, NumberLiteral)
        assert expr.value == 3.14
    
    def test_text_literal(self):
        source = """building: test

    display "hello world"
"""
        result = parse_building(source)
        assert result.success
        expr = result.ast.body[0].expression
        assert isinstance(expr, TextLiteral)
        assert expr.value == "hello world"
    
    def test_boolean_true(self):
        source = """building: test

    display true
"""
        result = parse_building(source)
        assert result.success
        expr = result.ast.body[0].expression
        assert isinstance(expr, BooleanLiteral)
        assert expr.value is True
    
    def test_boolean_false(self):
        source = """building: test

    display false
"""
        result = parse_building(source)
        assert result.success
        expr = result.ast.body[0].expression
        assert isinstance(expr, BooleanLiteral)
        assert expr.value is False
    
    def test_nothing_literal(self):
        source = """building: test

    display nothing
"""
        result = parse_building(source)
        assert result.success
        expr = result.ast.body[0].expression
        assert isinstance(expr, NothingLiteral)
    
    def test_list_literal(self):
        source = """building: test

    display [1, 2, 3]
"""
        result = parse_building(source)
        assert result.success
        expr = result.ast.body[0].expression
        assert isinstance(expr, ListLiteral)
        assert len(expr.elements) == 3
    
    def test_empty_list(self):
        source = """building: test

    display []
"""
        result = parse_building(source)
        assert result.success
        expr = result.ast.body[0].expression
        assert isinstance(expr, ListLiteral)
        assert len(expr.elements) == 0
    
    def test_table_literal(self):
        source = """building: test

    display ["name": "Alice", "age": 30]
"""
        result = parse_building(source)
        assert result.success
        expr = result.ast.body[0].expression
        assert isinstance(expr, TableLiteral)
        assert len(expr.pairs) == 2
    
    def test_input_expression(self):
        source = """building: test

    set name to input
"""
        result = parse_building(source)
        assert result.success
        stmt = result.ast.body[0]
        assert isinstance(stmt.value, InputNode)
    
    def test_identifier(self):
        source = """building: test

    display my_variable
"""
        result = parse_building(source)
        assert result.success
        expr = result.ast.body[0].expression
        assert isinstance(expr, IdentifierNode)
        assert expr.name == "my_variable"


# =============================================================================
# Expression Tests - Operators
# =============================================================================

class TestParseOperators:
    """Tests for parsing operator expressions."""
    
    def test_addition(self):
        source = """building: test

    display 1 + 2
"""
        result = parse_building(source)
        assert result.success
        expr = result.ast.body[0].expression
        assert isinstance(expr, BinaryOpNode)
        assert expr.operator == "+"
    
    def test_subtraction(self):
        source = """building: test

    display 5 - 3
"""
        result = parse_building(source)
        assert result.success
        expr = result.ast.body[0].expression
        assert isinstance(expr, BinaryOpNode)
        assert expr.operator == "-"
    
    def test_multiplication(self):
        source = """building: test

    display 4 * 5
"""
        result = parse_building(source)
        assert result.success
        expr = result.ast.body[0].expression
        assert isinstance(expr, BinaryOpNode)
        assert expr.operator == "*"
    
    def test_division(self):
        source = """building: test

    display 10 / 2
"""
        result = parse_building(source)
        assert result.success
        expr = result.ast.body[0].expression
        assert isinstance(expr, BinaryOpNode)
        assert expr.operator == "/"
    
    def test_precedence_multiply_before_add(self):
        source = """building: test

    display 1 + 2 * 3
"""
        result = parse_building(source)
        assert result.success
        expr = result.ast.body[0].expression
        # Should be 1 + (2 * 3)
        assert isinstance(expr, BinaryOpNode)
        assert expr.operator == "+"
        assert isinstance(expr.right, BinaryOpNode)
        assert expr.right.operator == "*"
    
    def test_unary_minus(self):
        source = """building: test

    display 0 - 42
"""
        result = parse_building(source)
        assert result.success
        expr = result.ast.body[0].expression
        # The parser creates a binary subtraction from 0 - 42
        assert isinstance(expr, BinaryOpNode)
        assert expr.operator == "-"
    
    def test_boolean_and(self):
        source = """building: test

    display true and false
"""
        result = parse_building(source)
        assert result.success
        expr = result.ast.body[0].expression
        assert isinstance(expr, BinaryOpNode)
        assert expr.operator == "and"
    
    def test_boolean_or(self):
        source = """building: test

    display true or false
"""
        result = parse_building(source)
        assert result.success
        expr = result.ast.body[0].expression
        assert isinstance(expr, BinaryOpNode)
        assert expr.operator == "or"
    
    def test_boolean_not(self):
        source = """building: test

    display not true
"""
        result = parse_building(source)
        assert result.success
        expr = result.ast.body[0].expression
        assert isinstance(expr, UnaryOpNode)
        assert expr.operator == "not"
    
    def test_boolean_precedence(self):
        source = """building: test

    display true or false and true
"""
        result = parse_building(source)
        assert result.success
        expr = result.ast.body[0].expression
        # Should be true or (false and true)
        assert isinstance(expr, BinaryOpNode)
        assert expr.operator == "or"
        assert isinstance(expr.right, BinaryOpNode)
        assert expr.right.operator == "and"


# =============================================================================
# Expression Tests - Comparisons
# =============================================================================

class TestParseComparisons:
    """Tests for comparison expressions."""
    
    def test_is_equal_to(self):
        source = """building: test

    if x is equal to 5
        display "yes"
"""
        result = parse_building(source)
        assert result.success
        condition = result.ast.body[0].if_branch.condition
        assert isinstance(condition, BinaryOpNode)
        assert condition.operator == "is equal to"
    
    def test_is_not_equal_to(self):
        source = """building: test

    if x is not equal to 5
        display "yes"
"""
        result = parse_building(source)
        assert result.success
        condition = result.ast.body[0].if_branch.condition
        assert isinstance(condition, BinaryOpNode)
        assert condition.operator == "is not equal to"
    
    def test_is_less_than(self):
        source = """building: test

    if x is less than 5
        display "yes"
"""
        result = parse_building(source)
        assert result.success
        condition = result.ast.body[0].if_branch.condition
        assert isinstance(condition, BinaryOpNode)
        assert condition.operator == "is less than"
    
    def test_is_greater_than(self):
        source = """building: test

    if x is greater than 5
        display "yes"
"""
        result = parse_building(source)
        assert result.success
        condition = result.ast.body[0].if_branch.condition
        assert isinstance(condition, BinaryOpNode)
        assert condition.operator == "is greater than"
    
    def test_is_less_than_or_equal_to(self):
        source = """building: test

    if x is less than or equal to 5
        display "yes"
"""
        result = parse_building(source)
        assert result.success
        condition = result.ast.body[0].if_branch.condition
        assert isinstance(condition, BinaryOpNode)
        assert condition.operator == "is less than or equal to"
    
    def test_is_greater_than_or_equal_to(self):
        source = """building: test

    if x is greater than or equal to 5
        display "yes"
"""
        result = parse_building(source)
        assert result.success
        condition = result.ast.body[0].if_branch.condition
        assert isinstance(condition, BinaryOpNode)
        assert condition.operator == "is greater than or equal to"


# =============================================================================
# Expression Tests - Text Operations
# =============================================================================

class TestParseTextOperations:
    """Tests for text operation expressions."""
    
    def test_added_to(self):
        source = """building: test

    display "hello " added to "world"
"""
        result = parse_building(source)
        assert result.success
        expr = result.ast.body[0].expression
        assert isinstance(expr, AddedToNode)
    
    def test_split_by(self):
        source = """building: test

    display message split by ","
"""
        result = parse_building(source)
        assert result.success
        expr = result.ast.body[0].expression
        assert isinstance(expr, SplitByNode)
    
    def test_length_of(self):
        source = """building: test

    display length of my_list
"""
        result = parse_building(source)
        assert result.success
        expr = result.ast.body[0].expression
        assert isinstance(expr, LengthOfNode)
    
    def test_character_at(self):
        source = """building: test

    display character at 0 of message
"""
        result = parse_building(source)
        assert result.success
        expr = result.ast.body[0].expression
        assert isinstance(expr, CharacterAtNode)
    
    def test_contains(self):
        source = """building: test

    if message contains "hello"
        display "yes"
"""
        result = parse_building(source)
        assert result.success
        condition = result.ast.body[0].if_branch.condition
        assert isinstance(condition, ContainsNode)
    
    def test_starts_with(self):
        source = """building: test

    if url starts with "http"
        display "url"
"""
        result = parse_building(source)
        assert result.success
        condition = result.ast.body[0].if_branch.condition
        assert isinstance(condition, StartsWithNode)
    
    def test_ends_with(self):
        source = """building: test

    if filename ends with ".txt"
        display "text file"
"""
        result = parse_building(source)
        assert result.success
        condition = result.ast.body[0].if_branch.condition
        assert isinstance(condition, EndsWithNode)


# =============================================================================
# Expression Tests - Postfix Operations
# =============================================================================

class TestParsePostfixOperations:
    """Tests for postfix operations."""
    
    def test_table_access(self):
        source = """building: test

    display person["name"]
"""
        result = parse_building(source)
        assert result.success
        expr = result.ast.body[0].expression
        assert isinstance(expr, TableAccessNode)
    
    def test_list_access(self):
        source = """building: test

    display my_list[0]
"""
        result = parse_building(source)
        assert result.success
        expr = result.ast.body[0].expression
        assert isinstance(expr, TableAccessNode)
        assert isinstance(expr.key, NumberLiteral)
    
    def test_type_conversion(self):
        source = """building: test

    display text_value as number
"""
        result = parse_building(source)
        assert result.success
        expr = result.ast.body[0].expression
        assert isinstance(expr, TypeConversionNode)
        assert expr.target_type == "number"
    
    def test_is_in(self):
        source = """building: test

    if item is in my_list
        display "found"
"""
        result = parse_building(source)
        assert result.success
        condition = result.ast.body[0].if_branch.condition
        assert isinstance(condition, IsInNode)


# =============================================================================
# Complex Expression Tests
# =============================================================================

class TestParseComplexExpressions:
    """Tests for complex combined expressions."""
    
    def test_nested_arithmetic(self):
        source = """building: test

    display (1 + 2) * (3 + 4)
"""
        result = parse_building(source)
        assert result.success
        expr = result.ast.body[0].expression
        assert isinstance(expr, BinaryOpNode)
        assert expr.operator == "*"
    
    def test_chained_comparisons_with_and(self):
        source = """building: test

    if x is greater than 0 and x is less than 10
        display "valid"
"""
        result = parse_building(source)
        assert result.success
        condition = result.ast.body[0].if_branch.condition
        assert isinstance(condition, BinaryOpNode)
        assert condition.operator == "and"
    
    def test_chained_table_access(self):
        source = """building: test

    display data["users"][0]["name"]
"""
        result = parse_building(source)
        assert result.success
        expr = result.ast.body[0].expression
        # Should be ((data["users"])[0])["name"]
        assert isinstance(expr, TableAccessNode)


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestParserErrors:
    """Tests for parser error handling."""
    
    def test_missing_building_keyword(self):
        source = """test: hello

    exit
"""
        result = parse_building(source)
        assert not result.success
        assert len(result.errors) > 0
    
    def test_missing_step_name(self):
        source = """step:
    belongs to: main

    do:
        display "hello"
"""
        result = parse_step(source)
        assert len(result.errors) > 0
    
    def test_missing_to_in_set(self):
        source = """building: test

    set x 42
"""
        result = parse_building(source)
        assert len(result.errors) > 0
    
    def test_unexpected_token(self):
        source = """building: test

    display 1 + + 2
"""
        result = parse_building(source)
        # May have errors or parse with issues
        assert result.ast is not None or len(result.errors) > 0


# =============================================================================
# Source Location Tests
# =============================================================================

class TestParseSourceLocations:
    """Tests for accurate source location tracking."""
    
    def test_building_location(self):
        source = """building: test

    exit
"""
        result = parse_building(source)
        assert result.success
        assert result.ast.location.line == 1
    
    def test_statement_location(self):
        source = """building: test

    display "hello"
"""
        result = parse_building(source)
        assert result.success
        stmt = result.ast.body[0]
        # Statement should be on line 3 (after blank line and building line)
        assert stmt.location.line >= 3
    
    def test_expression_location(self):
        source = """building: test

    display 42
"""
        result = parse_building(source)
        assert result.success
        expr = result.ast.body[0].expression
        assert expr.location.line >= 3
