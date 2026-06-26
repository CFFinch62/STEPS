# Steps Error Messages Catalog

## Design Philosophy

Error messages in Steps are **educational first**. Every error should:

1. **Explain what went wrong** in plain English
2. **Show where** it happened (file, line, column)
3. **Suggest how to fix it** when possible
4. **Show context** (surrounding code)

## Error Format

```
Error in [file] at line [line], column [column]:
    [The problematic line of code]
    [^^^^^ pointer to exact location]

[Clear explanation of the problem]

Hint: [Suggestion for fixing]
```

## Error Categories

### Structure Errors

#### MISSING_BUILDING_FILE
```
Error: No .building file found in project directory.

Every Steps project needs a .building file as its entry point.
Create a file named 'my_project.building' in the project root.

Example:
    building: my_project
    
        display "Hello, world!"
        exit
```

#### MISSING_STEP_FILE
```
Error in tip_calculator.building:
    Floor 'math' declares step 'calculate_tip' but file not found.

Create 'math/calculate_tip.step' or remove the step from the floors: section.
```

#### STEP_NOT_IN_FLOOR
```
Error in calculations/helper.step at line 2:
    belongs to: utilities
    ^^^^^^^^^^^^^^^^^^^^

This step says it belongs to 'utilities', but it's in the 'calculations' folder.

Either:
  - Move this file to a 'utilities' folder, or
  - Change 'belongs to: calculations'
```

#### FLOOR_STEP_MISMATCH
```
Error in project.building:
    Floor 'user_interaction' declares step 'display_menu' but 
    file 'user_interaction/display_menu.step' not found.

Either:
  - Create the file 'user_interaction/display_menu.step', or
  - Remove 'step: display_menu' from the floors: section
```

### Lexer Errors

#### INVALID_CHARACTER
```
Error in greet.step at line 5, column 12:
    set name to @input
               ^

Unexpected character '@'. Steps doesn't use this symbol.

Did you mean just 'input' without the @?
```

#### BAD_INDENTATION
```
Error in main.step at line 8:
       display "hello"
    ^^^

Indentation must use exactly 4 spaces per level.
This line has 3 spaces. Add 1 more space.
```

#### TAB_CHARACTER
```
Error in calc.step at line 4:
	set x to 5
^

Found a tab character. Steps uses 4 spaces for indentation, not tabs.

Most editors can convert tabs to spaces automatically.
In VS Code: "editor.insertSpaces": true
```

#### UNTERMINATED_STRING
```
Error in greet.step at line 7:
    display "Hello, world
                        ^

This string was never closed. Add a " at the end.

    display "Hello, world"
```

#### INCONSISTENT_INDENTATION
```
Error in loop.step at line 12:
      display item
    ^^

This line's indentation (6 spaces) doesn't match any previous level.
The current levels are: 0, 4, 8 spaces.

Did you mean to indent by 8 spaces?
```

### Parser Errors

#### EXPECTED_IDENTIFIER
```
Error in math.step at line 3:
    step: 123invalid
          ^^^

Expected a name here, but found a number.
Names must start with a letter or underscore.

Try: step: calculate_sum
```

#### EXPECTED_COLON
```
Error in main.step at line 1:
    step greet
            ^

Expected ':' after 'step'.

Try: step: greet
```

#### EXPECTED_NEWLINE
```
Error in calc.step at line 5:
    set x to 5 set y to 10
               ^^^

Expected end of line after 'set x to 5'.
Put each statement on its own line.

    set x to 5
    set y to 10
```

#### EXPECTED_INDENT
```
Error in main.step at line 3:
    do:
display "hello"
^

Expected indented code after 'do:'.
Indent the code that should run by 4 spaces.

    do:
        display "hello"
```

#### EXPECTED_EXPRESSION
```
Error in calc.step at line 8:
    set result to 
                  ^

Expected a value here (number, text, or variable name).

Examples:
    set result to 42
    set result to "hello"
    set result to other_variable
```

#### MISSING_DO_SECTION
```
Error in greet.step at line 10:
    declare:
        name as text
    
    return name
    ^^^^^^

Every step needs a 'do:' section with its logic.
Add 'do:' before your code:

    declare:
        name as text
    
    do:
        return name
```

#### UNEXPECTED_TOKEN
```
Error in loop.step at line 6:
    repeat 10 time
                 ^^^^

Expected 'times' (plural) after the number.

Try: repeat 10 times
```

#### ELSE_INSTEAD_OF_OTHERWISE
```
Error in check.step at line 8:
    else
    ^^^^

Steps uses 'otherwise' instead of 'else'.

Try: otherwise
```

### Type Errors

#### TYPE_MISMATCH_FIXED
```
Error in calc.step at line 12:
    set count to "hello"
                 ^^^^^^^

Cannot assign text to 'count' - it was declared as 'number fixed'.
Once a variable is declared with 'fixed', it can only hold that type.

Either:
  - Assign a number: set count to 42
  - Remove 'fixed' from the declaration if you need flexibility
```

#### INVALID_OPERATION
```
Error in math.step at line 8:
    set result to "hello" + 5
                          ^

Cannot add a number to text.

To combine text and numbers, convert the number first:
    set result to "hello" added to (5 as text)
```

#### CANNOT_ITERATE
```
Error in loop.step at line 5:
    repeat for each item in 42
                            ^^

Cannot iterate over a number. 'repeat for each' needs a list.

Example:
    set numbers to [1, 2, 3]
    repeat for each item in numbers
```

#### INVALID_COMPARISON
```
Error in check.step at line 6:
    if my_list is less than 10
       ^^^^^^^

Cannot compare a list with 'is less than'.
This comparison only works with numbers.

To check list length:
    if length of my_list is less than 10
```

### Runtime Errors

#### UNDEFINED_VARIABLE
```
Error in calc.step at line 8:
    set result to count + 1
                  ^^^^^

Variable 'count' has not been defined yet.

Define it first:
    declare:
        count as number
    
    do:
        set count to 0
        set result to count + 1
```

#### UNDEFINED_STEP
```
Error in main.building at line 5:
    call calculate_totl storing result in sum
         ^^^^^^^^^^^^^^

Step 'calculate_totl' does not exist.

Did you mean 'calculate_total'?

Available steps in this project:
  - calculate_total (in calculations)
  - display_result (in user_interaction)
```

#### DIVISION_BY_ZERO
```
Error in math.step at line 7:
    set result to 100 / count
                      ^

Cannot divide by zero. 'count' is currently 0.

Add a check before dividing:
    if count is not equal to 0
        set result to 100 / count
    otherwise
        display "Cannot divide by zero"
```

#### INDEX_OUT_OF_BOUNDS
```
Error in list.step at line 6:
    set item to my_list[10]
                       ^^^^

Index 10 is out of bounds. The list only has 5 items (indices 0-4).

Check the list length first:
    if 10 is less than length of my_list
        set item to my_list[10]
```

#### KEY_NOT_FOUND
```
Error in table.step at line 8:
    set value to results["pric"]
                         ^^^^^^

Key "pric" not found in table.

Did you mean "price"?

Keys in this table:
  - "price"
  - "cost"
  - "margin"
```

#### WRONG_ARGUMENT_COUNT
```
Error in main.building at line 6:
    call greet_user storing result in message
         ^^^^^^^^^^

Step 'greet_user' expects 1 argument (name) but got 0.

Try: call greet_user with user_name storing result in message
```

#### RISER_NOT_FOUND
```
Error in route.step at line 15:
    call validate_input with choice
         ^^^^^^^^^^^^^^

'validate_input' is a riser in step 'process_choice', not this step.
Risers are private - they can only be called from within their parent step.

Either:
  - Move this code into 'process_choice', or
  - Promote 'validate_input' to a full step if it needs to be shared
```

### Attempt/Error Handling

#### UNHANDLED_ERROR
```
Error in data.step at line 8:
    set number to user_input as number
                  ^^^^^^^^^^

Could not convert "abc" to a number.

Use 'attempt' to handle this gracefully:
    attempt:
        set number to user_input as number
    if unsuccessful:
        display "Please enter a valid number"
```

## Error Code Reference

| Code | Category | Brief Description |
|------|----------|-------------------|
| E001 | Structure | Missing building file |
| E002 | Structure | Step declared in floor but file not found |
| E003 | Structure | Step not in declared floor |
| E004 | Structure | Floor lists missing step |
| E101 | Lexer | Invalid character |
| E102 | Lexer | Bad indentation |
| E103 | Lexer | Tab character |
| E104 | Lexer | Unterminated string |
| E105 | Lexer | Inconsistent indentation |
| E201 | Parser | Expected identifier |
| E202 | Parser | Expected colon |
| E203 | Parser | Expected newline |
| E204 | Parser | Expected indent |
| E205 | Parser | Expected expression |
| E206 | Parser | Missing do section |
| E207 | Parser | Unexpected token |
| E301 | Type | Type mismatch on fixed variable |
| E302 | Type | Invalid operation for types |
| E303 | Type | Cannot iterate non-list |
| E304 | Type | Invalid comparison |
| E401 | Runtime | Undefined variable |
| E402 | Runtime | Undefined step |
| E403 | Runtime | Division by zero |
| E404 | Runtime | Index out of bounds |
| E405 | Runtime | Key not found |
| E406 | Runtime | Wrong argument count |
| E407 | Runtime | Riser not accessible |
| E501 | Error | Unhandled conversion error |

## Implementation

```python
@dataclass
class StepsError:
    code: str
    message: str
    file: Path
    line: int
    column: int
    hint: str
    context_lines: List[str]
    
    def format(self) -> str:
        output = []
        output.append(f"Error {self.code} in {self.file} at line {self.line}, column {self.column}:")
        output.append("")
        
        # Show context
        for i, ctx_line in enumerate(self.context_lines):
            line_num = self.line - len(self.context_lines) // 2 + i
            marker = ">>>" if line_num == self.line else "   "
            output.append(f"{marker} {line_num:4d} | {ctx_line}")
        
        # Show pointer
        if self.column > 0:
            pointer = " " * (11 + self.column) + "^"
            output.append(pointer)
        
        output.append("")
        output.append(self.message)
        
        if self.hint:
            output.append("")
            output.append(f"Hint: {self.hint}")
        
        return "\n".join(output)
```
