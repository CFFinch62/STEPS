# Steps Language Specification

Version 2.0

## 1. Overview

Steps is an educational programming language with:
- Significant whitespace (4-space indentation)
- English-readable keywords
- Mandatory file-per-step structure
- Dynamic typing with optional type locking

## 2. The Building Metaphor

| Construct | Purpose | File Extension |
|-----------|---------|----------------|
| Building | Complete program entry point | `.building` |
| Floor | Functional grouping of steps | (in `.building`) |
| Step | Single unit of work | `.step` |
| Riser | Private helper within a step | (inside `.step`) |

### 2.1 Hierarchy

```
Building (complete program)
    Floor (functional grouping)
        Step (single task)
            Riser (private helper)
```

## 3. Project File Structure

```
project_name/                    # Building folder (project root)
    project_name.building        # Main entry point (includes floor declarations)
    
    floor_name/                  # Floor folder
        step_one.step            # Step files
        step_two.step
    
    another_floor/
        another_step.step
```

## 4. Syntax Specification

### 4.1 Building Definition

```
building: program_name

    note: Optional description

    floors:
        floor: floor_name
            step: step_one
            step: step_two
    
    call step_name storing result in variable
    display variable
    
    exit
```

### 4.2 Floor Declaration

Floors are declared inline in the building file's `floors:` section (see 4.1 above).

### 4.3 Step Definition

```
step: step_name
    belongs to: floor_name
    expects: param1, param2
    returns: return_value

    declare:
        variable_name as type
        fixed_var as type fixed

    do:
        set variable_name to value
        return return_value
```

### 4.4 Riser Definition (inside Step)

```
step: parent_step
    expects: value
    returns: result

    riser: helper_name
        expects: input
        returns: output

        do:
            set output to input * 2
            return output

    declare:
        result as number

    do:
        call helper_name with value storing result in result
        return result
```

## 5. Keywords Reference

### 5.1 Structure Keywords

| Keyword | Purpose |
|---------|---------|
| `building:` | Declares main program container |
| `floors:` | Begins inline floor declarations section |
| `floor:` | Declares a floor (functional grouping) |
| `step:` | Declares a step (one per file) |
| `riser:` | Declares a private helper within a step |
| `belongs to:` | Associates step with a floor |
| `expects:` | Declares expected parameters |
| `returns:` | Declares return value |
| `declare:` | Begins variable declaration section |
| `do:` | Begins logic section |
| `exit` | Ends program execution |

### 5.2 Variable Keywords

| Keyword | Purpose |
|---------|---------|
| `as` | Type declaration: `variable as type` |
| `fixed` | Locks variable to declared type |
| `set` | Assignment: `set variable to value` |
| `to` | Assignment target |

### 5.3 Invocation Keywords

| Keyword | Purpose |
|---------|---------|
| `call` | Invokes a step or riser |
| `with` | Passes arguments: `call step with arg1, arg2` |
| `storing result in` | Captures return value |
| `return` | Returns value from step/riser |
| `display` | Outputs to console |
| `input` | Gets input from user |

### 5.4 Control Flow Keywords

| Keyword | Purpose |
|---------|---------|
| `if` | Conditional branch |
| `otherwise if` | Additional conditional branch |
| `otherwise` | Default branch |
| `repeat ... times` | Fixed iteration loop |
| `repeat for each ... in` | Collection iteration |
| `repeat while` | Conditional loop |

### 5.5 Error Handling Keywords

| Keyword | Purpose |
|---------|---------|
| `attempt:` | Begins error-handled block |
| `if unsuccessful:` | Error handling block |
| `then continue:` | Cleanup block (always runs) |
| `problem_message` | Built-in variable with error details |

## 6. Data Types

### 6.1 Built-in Types

| Type | Description | Example |
|------|-------------|---------|
| `number` | Integer or decimal | `42`, `3.14` |
| `text` | String values | `"hello"` |
| `boolean` | True or false | `true`, `false` |
| `list` | Ordered collection | `[1, 2, 3]` |
| `table` | Key-value pairs | `["key": value]` |

### 6.2 Type Conversion

```
set count to "42" as number
set label to 42 as text
set flag to 1 as boolean
```

### 6.3 Type Locking

```
declare:
    count as number fixed    # Cannot change type after assignment
    name as text             # Can be reassigned to any type
```

## 7. Operators

### 7.1 Math Operators

Standard symbols: `+  -  *  /`

### 7.2 Comparison Operators

| Operator | Meaning |
|----------|---------|
| `is equal to` / `equals` | Equality |
| `is not equal to` | Inequality |
| `is less than` | Less than |
| `is greater than` | Greater than |
| `is less than or equal to` | Less than or equal |
| `is greater than or equal to` | Greater than or equal |

### 7.3 Boolean Operators

| Operator | Meaning |
|----------|---------|
| `and` | Logical AND |
| `or` | Logical OR |
| `not` | Logical NOT |

### 7.4 Text Operators

| Operator | Purpose | Example |
|----------|---------|---------|
| `added to` | Concatenation | `"Hello, " added to name` |
| `split by` | Split into list | `text split by ","` |
| `character at` | Index access | `character at 0 of text` |
| `length of` | Get length | `length of text` |
| `contains` | Substring check | `text contains "hello"` |
| `starts with` | Prefix check | `text starts with "http"` |
| `ends with` | Suffix check | `text ends with ".txt"` |

### 7.5 List Operations

| Operation | Purpose | Example |
|-----------|---------|---------|
| `add ... to` | Add item | `add item to my_list` |
| `remove ... from` | Remove item | `remove item from my_list` |
| `length of` | Get length | `length of my_list` |
| `is in` | Membership | `item is in my_list` |

### 7.6 Table Operations

| Operation | Purpose | Example |
|-----------|---------|---------|
| `table["key"]` | Access value | `results["price"]` |
| `set table["key"] to` | Set value | `set results["price"] to 100` |

## 8. Control Flow

### 8.1 Conditionals

```
if condition
    do something
otherwise if other_condition
    do something else
otherwise
    do default thing
```

### 8.2 Loops

```
# Fixed count
repeat 10 times
    do something

# Collection iteration
repeat for each item in my_list
    call process with item

# Conditional
repeat while count is less than 100
    set count to count + 1
```

## 9. Error Handling

```
attempt:
    call risky_operation storing result in data
if unsuccessful:
    display "Error: " added to problem_message
then continue:
    call cleanup
```

## 10. Comments

### 10.1 Single-line

```
note: This is a comment
```

### 10.2 Multi-line

```
note block:
    This comment spans
    multiple lines
end note
```

## 11. Special Values

| Value | Meaning |
|-------|---------|
| `nothing` | No value (used in expects/returns) |
| `true` | Boolean true |
| `false` | Boolean false |
| `problem_message` | Error details (in unsuccessful block) |

## 12. Reserved Words

All keywords are reserved and cannot be used as identifiers:

```
building floor step riser belongs expects returns declare do exit
as fixed set to call with storing result in return display input
if otherwise repeat times for each while
attempt unsuccessful then continue
note block end
and or not is equal less greater than
true false nothing
number text boolean list table
add remove from length of contains starts ends split character at added
```
