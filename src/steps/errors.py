"""Steps Error Types and Educational Error Messages.

This module provides the error handling infrastructure for Steps,
with a focus on producing educational error messages that help
learners understand what went wrong and how to fix it.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class SourceLocation:
    """Represents a location in source code.
    
    Used to track where tokens, AST nodes, and errors originate
    for accurate error reporting.
    """
    file: Path
    line: int
    column: int
    end_line: Optional[int] = None
    end_column: Optional[int] = None
    
    def __str__(self) -> str:
        if self.end_line and self.end_line != self.line:
            return f"{self.file}:{self.line}:{self.column}-{self.end_line}:{self.end_column}"
        return f"{self.file}:{self.line}:{self.column}"


class ErrorCode:
    """Error code constants organized by category."""
    
    # Structure Errors (E001-E099)
    E001 = "E001"  # Missing building file
    E002 = "E002"  # Step declared in floor but file not found
    E003 = "E003"  # Step not in declared floor
    E004 = "E004"  # Floor lists missing step
    
    # Lexer Errors (E101-E199)
    E101 = "E101"  # Invalid character
    E102 = "E102"  # Bad indentation
    E103 = "E103"  # Tab character
    E104 = "E104"  # Unterminated string
    E105 = "E105"  # Inconsistent indentation
    
    # Parser Errors (E201-E299)
    E201 = "E201"  # Expected identifier
    E202 = "E202"  # Expected colon
    E203 = "E203"  # Expected newline
    E204 = "E204"  # Expected indent
    E205 = "E205"  # Expected expression
    E206 = "E206"  # Missing do section
    E207 = "E207"  # Unexpected token
    E208 = "E208"  # Wrong keyword (e.g., else instead of otherwise)
    
    # Type Errors (E301-E399)
    E301 = "E301"  # Type mismatch on fixed variable
    E302 = "E302"  # Invalid operation for types
    E303 = "E303"  # Cannot iterate non-list
    E304 = "E304"  # Invalid comparison
    
    # Runtime Errors (E401-E499)
    E401 = "E401"  # Undefined variable
    E402 = "E402"  # Undefined step
    E403 = "E403"  # Reassigning fixed variable
    E404 = "E404"  # Division by zero
    E405 = "E405"  # Index out of bounds
    E406 = "E406"  # Key not found
    E407 = "E407"  # Internal error
    E408 = "E408"  # Maximum recursion depth exceeded
    E409 = "E409"  # Wrong argument count
    E410 = "E410"  # Maximum loop iterations exceeded
    
    # Error Handling Errors (E501-E599)
    E501 = "E501"  # Unhandled conversion error


@dataclass
class ErrorTemplate:
    """Template for generating educational error messages."""
    code: str
    message: str
    hint: str = ""


# Error message templates with educational hints
ERROR_TEMPLATES = {
    # Structure Errors
    ErrorCode.E001: ErrorTemplate(
        code=ErrorCode.E001,
        message="No .building file found in project directory.",
        hint="Every Steps project needs a .building file as its entry point.\n"
             "Create a file named 'your_project.building' in the project root."
    ),
    ErrorCode.E002: ErrorTemplate(
        code=ErrorCode.E002,
        message="Floor '{floor_name}' declares step files not found on disk.",
        hint="Ensure each step listed in the floors: section has a matching\n"
             ".step file in the '{floor_name}/' directory."
    ),
    ErrorCode.E003: ErrorTemplate(
        code=ErrorCode.E003,
        message="This step says it belongs to '{expected_floor}', but it's in the '{actual_floor}' folder.",
        hint="Either:\n"
             "  - Move this file to a '{expected_floor}' folder, or\n"
             "  - Change 'belongs to: {actual_floor}'"
    ),
    ErrorCode.E004: ErrorTemplate(
        code=ErrorCode.E004,
        message="Step '{step_name}' is listed in floor but file '{step_name}.step' not found.",
        hint="Either:\n"
             "  - Create the file '{step_name}.step', or\n"
             "  - Remove 'step: {step_name}' from the floors: section"
    ),
    
    # Lexer Errors
    ErrorCode.E101: ErrorTemplate(
        code=ErrorCode.E101,
        message="Unexpected character '{char}'. Steps doesn't use this symbol.",
        hint="Check for typos or unsupported characters."
    ),
    ErrorCode.E102: ErrorTemplate(
        code=ErrorCode.E102,
        message="Indentation must use exactly 4 spaces per level. Found {spaces} spaces.",
        hint="Use 4 spaces for each level of indentation."
    ),
    ErrorCode.E103: ErrorTemplate(
        code=ErrorCode.E103,
        message="Found a tab character. Steps uses 4 spaces for indentation, not tabs.",
        hint="Configure your editor to insert spaces instead of tabs.\n"
             "In VS Code: \"editor.insertSpaces\": true"
    ),
    ErrorCode.E104: ErrorTemplate(
        code=ErrorCode.E104,
        message="String starting here was never closed.",
        hint="Add a closing \" at the end of your string."
    ),
    ErrorCode.E105: ErrorTemplate(
        code=ErrorCode.E105,
        message="This line's indentation ({spaces} spaces) doesn't match any previous level.",
        hint="The current indentation levels are: {levels}\n"
             "Adjust your indentation to match one of these levels."
    ),
    
    # Parser Errors
    ErrorCode.E201: ErrorTemplate(
        code=ErrorCode.E201,
        message="Expected a name here, but found '{found}'.",
        hint="Names must start with a letter or underscore."
    ),
    ErrorCode.E202: ErrorTemplate(
        code=ErrorCode.E202,
        message="Expected ':' after '{keyword}'.",
        hint="Add a colon: {keyword}:"
    ),
    ErrorCode.E203: ErrorTemplate(
        code=ErrorCode.E203,
        message="Expected end of line after '{statement}'.",
        hint="Put each statement on its own line."
    ),
    ErrorCode.E204: ErrorTemplate(
        code=ErrorCode.E204,
        message="Expected indented code after '{keyword}:'.",
        hint="Indent the code that should be inside this block by 4 spaces."
    ),
    ErrorCode.E205: ErrorTemplate(
        code=ErrorCode.E205,
        message="Expected a value here (number, text, or variable name).",
        hint="Examples:\n"
             "    42          (a number)\n"
             "    \"hello\"     (text)\n"
             "    my_variable (a variable)"
    ),
    ErrorCode.E206: ErrorTemplate(
        code=ErrorCode.E206,
        message="Every step needs a 'do:' section with its logic.",
        hint="Add 'do:' before your code:\n\n"
             "    do:\n"
             "        your code here"
    ),
    ErrorCode.E207: ErrorTemplate(
        code=ErrorCode.E207,
        message="Unexpected '{token}' here.",
        hint="Check the syntax of your statement."
    ),
    ErrorCode.E208: ErrorTemplate(
        code=ErrorCode.E208,
        message="Steps uses '{correct}' instead of '{found}'.",
        hint="Try: {correct}"
    ),
    
    # Type Errors
    ErrorCode.E301: ErrorTemplate(
        code=ErrorCode.E301,
        message="Cannot assign {new_type} to '{variable}' - it was declared as '{declared_type} fixed'.",
        hint="Once a variable is declared with 'fixed', it can only hold that type.\n\n"
             "Either:\n"
             "  - Assign a {declared_type} value, or\n"
             "  - Remove 'fixed' from the declaration if you need flexibility"
    ),
    ErrorCode.E302: ErrorTemplate(
        code=ErrorCode.E302,
        message="Cannot {operation} with {left_type} and {right_type}.",
        hint="Check that the types are compatible for this operation."
    ),
    ErrorCode.E303: ErrorTemplate(
        code=ErrorCode.E303,
        message="Cannot iterate over a {type_name}. 'repeat for each' needs a list.",
        hint="Example:\n"
             "    set numbers to [1, 2, 3]\n"
             "    repeat for each item in numbers"
    ),
    ErrorCode.E304: ErrorTemplate(
        code=ErrorCode.E304,
        message="Cannot compare a {type_name} with '{operator}'.",
        hint="This comparison only works with numbers."
    ),
    
    # Runtime Errors
    ErrorCode.E401: ErrorTemplate(
        code=ErrorCode.E401,
        message="Variable '{name}' has not been defined yet.",
        hint="Define it first:\n\n"
             "    declare:\n"
             "        {name} as text\n\n"
             "    do:\n"
             "        set {name} to \"value\""
    ),
    ErrorCode.E402: ErrorTemplate(
        code=ErrorCode.E402,
        message="Step '{name}' does not exist.",
        hint="Did you mean '{suggestion}'?\n\n"
             "Available steps: {available}"
    ),
    ErrorCode.E403: ErrorTemplate(
        code=ErrorCode.E403,
        message="Cannot change '{name}' because it was declared as 'fixed'.",
        hint="Fixed variables cannot be reassigned after their initial value is set."
    ),
    ErrorCode.E404: ErrorTemplate(
        code=ErrorCode.E404,
        message="Cannot divide by zero.",
        hint="Check that your divisor is not zero before dividing."
    ),
    ErrorCode.E405: ErrorTemplate(
        code=ErrorCode.E405,
        message="Index {index} is out of bounds for list of length {length}.",
        hint="Valid indices are 0 to {max_index}."
    ),
    ErrorCode.E406: ErrorTemplate(
        code=ErrorCode.E406,
        message="Key \"{key}\" not found in table.",
        hint="Available keys: {available}"
    ),
    ErrorCode.E407: ErrorTemplate(
        code=ErrorCode.E407,
        message="Internal error: {details}",
        hint="This is likely a bug in the Steps interpreter."
    ),
    ErrorCode.E408: ErrorTemplate(
        code=ErrorCode.E408,
        message="Maximum recursion depth exceeded when calling '{step_name}'.",
        hint="Your step is calling itself too many times. Check for infinite recursion."
    ),
    ErrorCode.E409: ErrorTemplate(
        code=ErrorCode.E409,
        message="Step '{name}' expects {expected} argument(s), got {actual}.",
        hint="Expected parameters: {params}"
    ),
    ErrorCode.E410: ErrorTemplate(
        code=ErrorCode.E410,
        message="Maximum loop iterations exceeded ({limit}).",
        hint="Your loop may be infinite. Check the condition."
    ),
    
    # Error Handling Errors
    ErrorCode.E501: ErrorTemplate(
        code=ErrorCode.E501,
        message="Could not convert \"{value}\" to {target_type}.",
        hint="Use 'attempt' to handle this gracefully:\n\n"
             "    attempt:\n"
             "        set number to user_input as number\n"
             "    if unsuccessful:\n"
             "        display \"Please enter a valid number\""
    ),
}


@dataclass
class StepsError(Exception):
    """Base error type for all Steps errors.
    
    Provides rich formatting for educational error messages.
    """
    code: str
    message: str
    file: Optional[Path] = None
    line: Optional[int] = None
    column: Optional[int] = None
    hint: str = ""
    context_lines: List[str] = field(default_factory=list)
    
    def __str__(self) -> str:
        return self.format()
    
    def format(self) -> str:
        """Format the error for display with educational context."""
        output = []
        
        # Header with location
        if self.file and self.line:
            location = f"{self.file}"
            if self.line:
                location += f" at line {self.line}"
                if self.column:
                    location += f", column {self.column}"
            output.append(f"Error {self.code} in {location}:")
        else:
            output.append(f"Error {self.code}:")
        
        output.append("")
        
        # Context lines with error pointer
        if self.context_lines:
            start_line = self.line - len(self.context_lines) // 2 if self.line else 1
            for i, ctx_line in enumerate(self.context_lines):
                line_num = start_line + i
                marker = ">>>" if self.line and line_num == self.line else "   "
                output.append(f"{marker} {line_num:4d} | {ctx_line}")
            
            # Add pointer
            if self.column and self.column > 0:
                pointer = " " * (11 + self.column) + "^"
                output.append(pointer)
            
            output.append("")
        
        # Main error message
        output.append(self.message)
        
        # Hint
        if self.hint:
            output.append("")
            output.append(f"Hint: {self.hint}")
        
        return "\n".join(output)
    
    @classmethod
    def from_location(
        cls,
        code: str,
        message: str,
        location: SourceLocation,
        hint: str = "",
        context_lines: Optional[List[str]] = None
    ) -> "StepsError":
        """Create an error from a SourceLocation."""
        return cls(
            code=code,
            message=message,
            file=location.file,
            line=location.line,
            column=location.column,
            hint=hint,
            context_lines=context_lines or []
        )


class LexerError(StepsError):
    """Error during tokenization."""
    pass


class ParseError(StepsError):
    """Error during parsing."""
    pass


class StepsRuntimeError(StepsError):
    """Error during interpretation."""
    pass


class StepsTypeError(StepsError):
    """Error related to type operations."""
    pass


class StructureError(StepsError):
    """Error in project structure."""
    pass


# Helper functions for creating errors with templates

def make_error(
    code: str,
    location: Optional[SourceLocation] = None,
    context_lines: Optional[List[str]] = None,
    **kwargs: str
) -> StepsError:
    """Create an error using the template system.
    
    Args:
        code: Error code (e.g., ErrorCode.E401)
        location: Optional source location
        context_lines: Source code context
        **kwargs: Values to substitute into message and hint templates
    
    Returns:
        Formatted StepsError
    """
    template = ERROR_TEMPLATES.get(code)
    if not template:
        return StepsError(
            code=code,
            message=f"Unknown error {code}",
            file=location.file if location else None,
            line=location.line if location else None,
            column=location.column if location else None,
        )
    
    # Format message and hint with provided values
    try:
        message = template.message.format(**kwargs)
    except KeyError:
        message = template.message
    
    try:
        hint = template.hint.format(**kwargs)
    except KeyError:
        hint = template.hint
    
    return StepsError(
        code=code,
        message=message,
        file=location.file if location else None,
        line=location.line if location else None,
        column=location.column if location else None,
        hint=hint,
        context_lines=context_lines or []
    )


def undefined_variable_error(name: str, location: SourceLocation) -> StepsError:
    """Create an undefined variable error."""
    return make_error(ErrorCode.E401, location, name=name)


def undefined_step_error(
    name: str,
    location: SourceLocation,
    suggestion: str = "",
    available: str = ""
) -> StepsError:
    """Create an undefined step error with suggestions."""
    return make_error(
        ErrorCode.E402, 
        location, 
        name=name, 
        suggestion=suggestion or name,
        available=available or "(none)"
    )


def division_by_zero_error(variable: str, location: SourceLocation) -> StepsError:
    """Create a division by zero error."""
    return make_error(ErrorCode.E404, location, variable=variable)


def type_mismatch_error(
    variable: str,
    declared_type: str,
    new_type: str,
    location: SourceLocation
) -> StepsError:
    """Create a type mismatch error for fixed variables."""
    return make_error(
        ErrorCode.E301,
        location,
        variable=variable,
        declared_type=declared_type,
        new_type=new_type
    )
