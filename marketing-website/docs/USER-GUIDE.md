# Steps Programming Language - User Guide

> **Learn programming through architecture!**

This guide will help you get started with Steps, an educational programming language that makes program structure visible and mandatory.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Your First Program](#your-first-program)
4. [The Building Metaphor](#the-building-metaphor)
5. [Using the REPL](#using-the-repl)
6. [Using the IDE](#using-the-ide)
7. [Language Basics](#language-basics)
8. [Control Flow](#control-flow)
9. [Working with Data](#working-with-data)
10. [Creating Steps and Floors](#creating-steps-and-floors)
11. [Error Handling](#error-handling)
12. [Best Practices](#best-practices)

---

## Introduction

Steps is designed to teach programming concepts through an architectural metaphor. Just like a building has floors with different purposes, a Steps program has **floors** containing **steps** that perform specific tasks.

### Why Steps?

- **Visible Structure**: See your program's architecture at a glance
- **Forced Decomposition**: One step per file prevents "spaghetti code"
- **English-Readable**: Code reads like instructions, not cryptic symbols
- **Educational Errors**: Error messages explain what went wrong and how to fix it

---

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Quick Install

```bash
# Clone the repository
git clone https://github.com/CFFinch62/Steps
cd Steps

# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install Steps
pip install -e .

# Install IDE dependencies (optional)
pip install textual watchfiles
```

---

## Your First Program

### Step 1: Create a Project Folder

```bash
mkdir hello_world
cd hello_world
```

### Step 2: Create the Building File

Create `hello_world.building`:

```steps
building: hello_world
    display "Hello, World!"
    exit
```

### Step 3: Run Your Program

```bash
python -m steps.main run .
```

Output:
```
Hello, World!
```

Congratulations! You've written your first Steps program!

---

## The Building Metaphor

Steps uses an architectural metaphor to organize code:

### The Hierarchy

```
Building (your complete program)
    └── Floor (a group of related steps)
        └── Step (a single task)
            └── Riser (a private helper)
```

### File Structure

```
my_project/
├── my_project.building    # Entry point (required)
├── floor_one/             # A floor folder
│   ├── floor_one.floor    # Floor definition
│   ├── step_a.step        # A step
│   └── step_b.step        # Another step
└── floor_two/
    ├── floor_two.floor
    └── step_c.step
```

### Why This Structure?

1. **Buildings** are the entry point - where your program starts
2. **Floors** group related functionality (like departments in a building)
3. **Steps** are single tasks (one per file forces you to break down problems)
4. **Risers** are helpers that only their parent step can use

---

## Using the REPL

The REPL (Read-Eval-Print Loop) is perfect for learning Steps interactively.

### Starting the REPL

```bash
python -m steps_repl.main
```

### REPL Commands

| Command | Description |
|---------|-------------|
| `help` | Show available commands |
| `vars` | Display all variables |
| `reset` | Clear all variables |
| `clear` | Clear the screen |
| `exit` | Exit the REPL |

### Example Session

```
Steps REPL v0.1 - Educational Programming Environment
Type 'help' for available commands, 'exit' to quit.

>>> set name to "Alice"
>>> set age to 25
>>> display "Hello, " added to name
Hello, Alice
>>> display name added to " is " added to (age as text) added to " years old"
Alice is 25 years old
>>> vars
Variables:
  name = "Alice"
  age = 25
>>> reset
Environment reset.
>>> exit
Goodbye!
```

### Multi-line Input

Use `...` for multi-line statements:

```
>>> if age is greater than 18
...     display "Adult"
... otherwise
...     display "Minor"
...
Adult
```

---

## Using the IDE

The Steps IDE provides a full development environment.

### Launching the IDE

```bash
python -m steps_ide.main
```

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Ctrl+O | Open file |
| Ctrl+S | Save file |
| Ctrl+B | Toggle file browser |
| Ctrl+Shift+P | Toggle project browser |
| Ctrl+J | Toggle terminal |
| F5 | Run Steps project |
| F6 | Check syntax |
| Ctrl+P | Command palette |
| Ctrl+Q | Quit |

### IDE Features

1. **Project Browser**: View your project's building/floor/step structure
2. **Syntax-Aware Editor**: Recognizes `.building`, `.floor`, and `.step` files
3. **Run/Check Integration**: Press F5 to run, F6 to check syntax
4. **Terminal Panel**: See output and error messages
5. **Command Palette**: Access all commands with Ctrl+P

---

## Language Basics

### Variables and Assignment

Use `set` to create or update variables:

```steps
set name to "Alice"
set age to 25
set is_student to true
set balance to 1234.56
```

### Naming Rules

All names in Steps (variables, steps, floors, buildings, risers, parameters) must follow these rules:

| Rule | Example |
|------|---------|
| Start with a letter or underscore | `my_var`, `_private` |
| Contain only letters, digits, underscores | `count2`, `user_name` |
| No spaces | ✗ `my variable` |
| No hyphens | ✗ `my-variable` |
| No reserved words | ✗ `set`, `if`, `display` |

> **Case-sensitive:** `myAge` and `myage` are different variables.

```steps
# Good names
user_name
calculateTotal
item_count_2

# Bad names (will cause errors)
user-name     # hyphen not allowed
2nd_item      # can't start with digit
my variable   # spaces not allowed
```

### Declaring Variables with Types

In steps, use the `declare:` section for explicit declarations:

```steps
step: example
    declare:
        count as number
        message as text
        items as list
        settings as table

    do:
        set count to 0
        set message to "Hello"
```

### Type Locking with `fixed`

Prevent a variable from changing type:

```steps
declare:
    score as number fixed    # Can only hold numbers
    name as text            # Can be reassigned to any type
```

### Display Output

```steps
display "Hello, World!"
display "Your score is: " added to (score as text)
```

### Getting Input

```steps
display "Enter your name: "
set name to input

display "Enter your age: "
set age to input as number
```

---

## Control Flow

### Conditionals

```steps
if temperature is greater than 30
    display "It's hot!"
otherwise if temperature is greater than 20
    display "It's warm"
otherwise if temperature is greater than 10
    display "It's cool"
otherwise
    display "It's cold!"
```

### Comparison Operators

| Operator | Meaning |
|----------|---------|
| `is equal to` or `equals` | Equal |
| `is not equal to` | Not equal |
| `is less than` | Less than |
| `is greater than` | Greater than |
| `is less than or equal to` | ≤ |
| `is greater than or equal to` | ≥ |

### Boolean Operators

```steps
if age is greater than 18 and has_license
    display "Can drive"

if is_weekend or is_holiday
    display "Day off!"

if not is_busy
    display "Available"
```

### Loops

**Fixed count:**
```steps
repeat 5 times
    display "Hello!"
```

**Over a collection:**
```steps
set fruits to ["apple", "banana", "cherry"]
repeat for each fruit in fruits
    display fruit
```

**Conditional:**
```steps
set count to 0
repeat while count is less than 10
    display count
    set count to count + 1
```

---

## Working with Data

### Numbers

```steps
set price to 19.99
set quantity to 3
set total to price * quantity
set discount to total * 0.1
set final to total - discount
```

### Text (Strings)

```steps
set greeting to "Hello"
set name to "World"
set message to greeting added to ", " added to name added to "!"
display message    # Hello, World!

# Text operations
set length to length of message
set first_char to character at 0 of message
set has_hello to message contains "Hello"
set words to message split by " "
```

### Lists

```steps
set colors to ["red", "green", "blue"]

# Access by index
set first to colors[0]

# Add items
add "yellow" to colors

# Remove items
remove "green" from colors

# Check membership
if "red" is in colors
    display "Has red!"

# Get length
set count to length of colors
```

### Tables (Dictionaries)

```steps
set person to ["name": "Alice", "age": 25]

# Access values
set name to person["name"]

# Set values
set person["city"] to "Boston"

# Display
display person["name"] added to " is " added to (person["age"] as text)
```

---

## Creating Steps and Floors

### Step Definition

A step is a single unit of work in its own file:

**calculate_tax.step:**
```steps
step: calculate_tax
    belongs to: calculations
    expects: amount, rate
    returns: tax

    do:
        set tax to amount * (rate / 100)
        return tax
```

### Calling Steps

```steps
call calculate_tax with 100, 8.5 storing result in tax_amount
display "Tax: $" added to (tax_amount as text)
```

### Floor Definition

A floor groups related steps:

**calculations/calculations.floor:**
```steps
floor: calculations
    step: calculate_tax
    step: calculate_total
    step: apply_discount
```

### Private Helpers (Risers)

Risers are helpers that only their parent step can use:

```steps
step: format_currency
    expects: amount
    returns: formatted

    riser: add_commas
        expects: num_text
        returns: with_commas

        do:
            note: Add commas to number text (simplified)
            return num_text

    do:
        set text to amount as text
        call add_commas with text storing result in with_commas
        set formatted to "$" added to with_commas
        return formatted
```

---

## Error Handling

Use `attempt` blocks to handle errors gracefully:

```steps
attempt:
    set value to "abc" as number    # This will fail
if unsuccessful:
    display "Could not convert: " added to problem_message
then continue:
    display "Cleanup complete"
```

### The `problem_message` Variable

Inside an `if unsuccessful:` block, `problem_message` contains the error description.

---

## Best Practices

### 1. One Task Per Step

Each step should do ONE thing well:

```steps
# Good: Single responsibility
step: validate_email
step: send_notification
step: log_activity

# Bad: Step trying to do everything
step: validate_and_send_and_log
```

### 2. Meaningful Names

Use descriptive names that explain what the code does:

```steps
# Good
step: calculate_shipping_cost
set customer_age to input as number

# Bad
step: calc
set x to input as number
```

### 3. Use Floors to Organize

Group related steps into floors:

```
my_app/
├── my_app.building
├── user_management/        # User-related steps
│   ├── user_management.floor
│   ├── create_user.step
│   └── validate_user.step
├── payments/               # Payment-related steps
│   ├── payments.floor
│   ├── process_payment.step
│   └── issue_refund.step
└── notifications/          # Notification-related steps
    ├── notifications.floor
    └── send_email.step
```

### 4. Document with Notes

Use `note:` to explain complex logic:

```steps
step: calculate_discount
    expects: total, customer_type
    returns: discount

    note: Premium customers get 20%, regular get 10%, new get 5%

    do:
        if customer_type equals "premium"
            set discount to total * 0.20
        otherwise if customer_type equals "regular"
            set discount to total * 0.10
        otherwise
            set discount to total * 0.05
        return discount
```

### 5. Handle Errors Gracefully

Always handle potential errors:

```steps
attempt:
    set age to input as number
if unsuccessful:
    display "Please enter a valid number"
    set age to 0
```

---

## Next Steps

1. **Practice with the REPL**: Try out language features interactively
2. **Build a small project**: Start with a simple calculator or greeting program
3. **Read the Language Reference**: See [LANGUAGE-REFERENCE.md](LANGUAGE-REFERENCE.md) for complete details
4. **Explore the examples**: Check `dev-docs/examples/` for sample projects

Happy coding with Steps! 🏗️

