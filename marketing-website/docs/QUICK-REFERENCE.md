# Steps Language Quick Reference

## Basic Syntax

### Variables
```steps
set name to "Alice"
set age to 25
set score to 98.5
set active to true
set items to [1, 2, 3]
set person to ["name": "Bob", "age": 30]
```

### Display & Input
```steps
display "Hello, World!"                      # Output with newline
indicate "Loading..."                        # Output without newline
display "Your score: " added to (score as text)
set name to input
set age to input as number
```

### Operators
```steps
# Arithmetic: +  -  *  /
set total to price * quantity

# Comparison
if age is greater than 18
if name equals "Alice"
if score is less than or equal to 100

# Boolean: and  or  not
if age is greater than 18 and has_license
```

## Control Flow

### If Statements
```steps
if condition
    statements

if condition
    statements
otherwise
    statements

if condition1
    statements
otherwise if condition2
    statements
otherwise
    statements
```

### Loops
```steps
# Repeat N times
repeat 10 times
    display "Hello"

# For each item
repeat for each item in my_list
    display item

# While loop
repeat while count is less than 10
    set count to count + 1

# Set iteration limit (default: 10,000,000)
set iteration limit to 100000
```

## Data Types

### Lists
```steps
set numbers to [1, 2, 3, 4, 5]
set first to numbers[0]
add 6 to numbers
remove 3 from numbers
set len to length of numbers
if 5 is in numbers
    display "Found it"

# Create a pre-filled list at C speed (native builtin)
call create_list with 1000, 0 storing result in counters   # 1000 zeros
call create_list with 500, true storing result in flags    # 500 trues
```

### Tables (Dictionaries)
```steps
set person to ["name": "Alice", "age": 25]
set name to person["name"]
set person["city"] to "Boston"
```

### Text Operations
```steps
set greeting to "Hello, " added to name
set len to length of "hello"
set first_char to character at 0 of "hello"
if "hello" contains "ell"
if "hello" starts with "he"
if "hello" ends with "lo"
set words to "a,b,c" split by ","
```

## Program Structure

### Building with Floors (Entry Point)
```steps
building: project_name
    note: Optional description

    floors:
        floor: my_floor
            step: step_one
            step: step_two

    statements
    exit
```

### Step Definition
```steps
step: calculate_total
    belongs to: my_floor
    expects: price, quantity
    returns: total
    
    declare:
        tax as number
    
    do:
        set tax to price * 0.1
        set total to (price * quantity) + tax
        return total
```

### Calling Steps
```steps
call my_step
call my_step with arg1, arg2
call my_step storing result in result_var
call my_step with arg1, arg2 storing result in result_var
```

### Risers (Helper Functions)
```steps
step: parent_step
    expects: value
    returns: result
    
    riser: helper
        expects: input
        returns: output
        do:
            set output to input * 2
            return output
    
    do:
        call helper with value storing result in doubled
        return doubled
```

## Error Handling

```steps
attempt:
    set num to input as number
    set result to 100 / num
if unsuccessful:
    display "Error: " added to problem_message
    set result to 0
then continue:
    display "Done"
```

## Console Control

```steps
# Clear the terminal screen
clear console

# Display without newline (for progress bars, etc.)
indicate "\r" added to "Progress: 50%"

# Update progress bar in place
set i to 0
repeat while i is less than or equal to 100
    call progress_bar with i, 100, 40 storing result in bar
    indicate "\r" added to "Loading: " added to bar
    set i to i + 10
display ""  # Final newline
```

## Type Conversion

```steps
set num to "42" as number
set text to 42 as text
set bool to 1 as boolean
set formatted to 3.14159 as decimal(2)  # "3.14"
```

## Type Checking

```steps
set t to type of value
if value is a number
if value is a text
if value is a boolean
if value is a list
if value is a table
```

## Comments

```steps
note: This is a single-line comment

note block:
    This is a multi-line comment.
    It can span multiple lines.
end note
```

## File Organization

```
my_project/
├── my_project.building    # Entry point (includes floors: section)
├── floor1/
│   ├── step1.step         # Step files
│   └── step2.step
└── floor2/
    └── step3.step
```

## Reserved Words

`add`, `added`, `and`, `as`, `attempt`, `belongs`, `boolean`, `building`, `call`, `character`, `clear`, `console`, `contains`, `continue`, `declare`, `display`, `do`, `each`, `else`, `end`, `ends`, `equals`, `exit`, `expects`, `false`, `fixed`, `floor`, `for`, `from`, `greater`, `if`, `in`, `indicate`, `input`, `is`, `iteration`, `less`, `limit`, `list`, `length`, `not`, `note`, `nothing`, `number`, `of`, `or`, `otherwise`, `problem_message`, `remove`, `repeat`, `result`, `return`, `returns`, `riser`, `set`, `split`, `starts`, `step`, `storing`, `table`, `than`, `then`, `times`, `to`, `true`, `type`, `unsuccessful`, `while`, `with`

## IDE Code Completion Shortcuts

| Abbreviation | Expands To |
|---|---|
| `dis` | `display` |
| `rep` | `repeat` (times/while/for each) |
| `oi` | `otherwise if` |
| `ow` | `otherwise` |
| `rw` | `repeat while` |
| `rfe` | `repeat for each` |
| `att` | `attempt:` scaffold |
| `ret` | `return` |
| `cal` | `call` |
| `set` | `set … to` |
| `newstep` | Full step template |
| `newbuild` | Full building template |
| `newriser` | Full riser template |
| `Ctrl+Space` | Force show completions |

See the [Code Completion Reference](CODE-COMPLETION.md) for the complete guide including all triggers, matching rules, and cursor placement.
