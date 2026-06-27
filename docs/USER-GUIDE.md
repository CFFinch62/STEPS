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
7. [Debugging](#debugging)
8. [Diagram Tool](#diagram-tool)
9. [Language Basics](#language-basics)
10. [Control Flow](#control-flow)
11. [Working with Data](#working-with-data)
12. [Creating Steps and Floors](#creating-steps-and-floors)
13. [Error Handling](#error-handling)
14. [Best Practices](#best-practices)

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
git clone <repository-url>
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
├── my_project.building    # Entry point (includes floor declarations)
├── floor_one/             # A floor folder
│   ├── step_a.step        # A step
│   └── step_b.step        # Another step
└── floor_two/
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
| Ctrl+D | Show project diagram |
| Ctrl+Shift+G | Scaffold from Building |
| Ctrl+F5 | Run Steps project |
| F5 | Start debugging |
| Shift+F5 | Stop debugging |
| F6 | Check syntax |
| Ctrl+P | Command palette |
| Ctrl+Space | Trigger code completion |

### IDE Features

1. **Project Browser**: View your project's building/floor/step structure
2. **Syntax-Aware Editor**: Recognizes `.building` and `.step` files
3. **Run/Check Integration**: Press Ctrl+F5 to run, F6 to check syntax
4. **Terminal Panel**: See output and error messages
5. **Command Palette**: Access all commands with Ctrl+P
6. **Integrated Debugger**: Step through code, inspect variables, set breakpoints
7. **Project Diagram Viewer**: Visualize program architecture with Ctrl+D
8. **Code Completion**: Context-aware suggestions as you type (see below)
9. **Scaffold from Building**: Auto-create floor folders and step files from your building's `floors:` section (Ctrl+Shift+G)

### Code Completion

The Steps IDE includes intelligent code completion that helps you write Steps code faster. It works in two modes:

- **Automatic** (default): Suggestions appear as you type after a short delay
- **Manual**: Press `Ctrl+Space` to trigger suggestions

**What gets completed:**

| Context | What You Type | What's Suggested |
|---------|---------------|------------------|
| After `is ` | `is ` | Comparison operators: `equal to`, `less than`, etc. |
| Line start | `dis` | Statement: `display` |
| Line start | `rep` | `repeat … times`, `repeat while`, `repeat for each` |
| Line start | `oi` | `otherwise if` |
| Line start | `att` | `attempt:` (with scaffold) |
| After `call ` | `call calc` | Step names from your project |
| After `call name ` | `call my_step ` | `with`, `storing result in` |
| Line start | `newstep` | Full step file template |
| Line start | `newbuild` | Full building file template |

You can switch between Automatic and Manual modes in **Settings → Editor → Autocomplete Mode**.

For the complete reference including all shortcuts, abbreviations, snippet templates, matching rules, and cursor placement behavior, see the [Code Completion Reference](CODE-COMPLETION.md).

---

## Debugging

The Steps IDE includes a full-featured debugger to help you understand how your programs run.

### Debug Keyboard Shortcuts

| Key | Action |
|-----|--------|
| F5 | Start debugging |
| Shift+F5 | Stop debugging |
| F9 | Toggle breakpoint |
| F11 | Step Into (enter steps/risers) |
| F10 | Step Over (skip into steps) |
| Shift+F11 | Step Out (exit current step) |
| Ctrl+Shift+D | Toggle debug panel |

### Starting the Debugger

1. Open a `.building` or `.step` file
2. Press **F5** or use **Debug → Start Debugging**
3. The debug panel will appear on the right side

### Setting Breakpoints

Click in the line number area (left margin) or press **F9** to toggle a breakpoint on the current line. A red circle indicates a breakpoint.

When the program runs, it will pause at breakpoints, allowing you to:
- Inspect variable values
- Step through code line by line
- Understand program flow

### The Debug Panel

The debug panel shows two tabs:

**Variables Tab:**
- **🌐 Globals**: Variables defined in the main building
- **📦 Step/Riser Name**: Local variables when inside a step or riser
- Values are color-coded by type (green = number, orange = text, etc.)
- Newly changed variables are highlighted in green

**Call Stack Tab:**
- Shows the chain of step/riser calls
- Empty when in the main building
- Shows nested levels when inside steps and risers
- Click a frame to jump to that location

### Stepping Through Code

- **Step Into (F11)**: Execute the next line. If it's a step call, enter the step.
- **Step Over (F10)**: Execute the next line. If it's a step call, run it completely without stopping inside.
- **Step Out (Shift+F11)**: Run until the current step returns, then pause.
- **Continue**: Resume running until the next breakpoint.

### Debugging Tips

1. **Start Small**: Set a breakpoint at the beginning of your program and step through
2. **Watch Variables**: Check that variables have the values you expect
3. **Use Step Over**: When you trust a step works correctly, use Step Over to skip into it
4. **Check the Call Stack**: When inside nested steps, the call stack shows how you got there

---

## Diagram Tool

The diagram tool generates ASCII art flow diagrams showing the structure of your Steps programs. You can use it from the command line or directly in the IDE.

### Using Diagrams in the IDE

The IDE includes an integrated diagram viewer for visualizing your project structure.

**To view a diagram:**

1. **With a file open**: Press **Ctrl+D** or go to **View → Show Project Diagram**
   - The IDE automatically detects the project from your currently open file

2. **Without a file open**: Press **Ctrl+D** and select your project folder
   - The IDE will prompt you to choose a folder containing a `.building` file

**Diagram Tab Features:**

- **Read-only viewer**: Displays the diagram with proper monospace formatting
- **Save button**: Click "💾 Save Diagram As..." to export the diagram to a `.txt` file
- **Single tab**: Only one diagram tab exists at a time - opening a new diagram updates the existing tab
- **Theme-aware**: The diagram viewer respects your IDE theme settings

**Font Recommendations:**

For best diagram display, use a monospace font that supports Unicode box-drawing characters:
- Courier New (recommended)
- Courier
- Consolas
- Monaco

The IDE will warn you if your current font may not display diagrams correctly.

### Using Diagrams from the Command Line

```bash
python -m steps.main diagram <path_to_project>

# Example
python -m steps.main diagram projects/tip_calculator
```

### What It Shows

The diagram displays your program's architecture:
- **Building**: The main program (🏢)
- **Floors**: Grouped functionality (📂)
- **Steps**: Individual tasks (🔷) with their parameters and return types
- **Flow arrows**: Relationships between components

### Example Output

```
┌──────────────────────────────────────────────────┐
│ 🏢 BUILDING: tip_calculator                      │
├──────────────────────────────────────────────────┤
│                                                  │
│  ┌────────────────────────────────────────────┐  │
│  │ 📂 FLOOR: calculations                     │  │
│  ├────────────────────────────────────────────┤  │
│  │                                            │  │
│  │    ┌────────────────────────────────────┐  │  │
│  │    │ 🔷 calculate_tip                   │  │  │
│  │    │   needs: bill, rate                │  │  │
│  │    │   returns: number                  │  │  │
│  │    └────────────────────────────────────┘  │  │
│  │                                            │  │
│  └────────────────────────────────────────────┘  │
│                                                  │
└──────────────────────────────────────────────────┘
```

### When to Use It

- **Understanding projects**: Quickly see how a project is organized
- **Documentation**: Generate architecture diagrams for your README
- **Teaching**: Show students how to structure their code
- **Planning**: Visualize your project before building it
- **Code review**: Share project structure with instructors or peers

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

The `display` statement outputs text followed by a newline.

### Output Without Newline

```steps
indicate "Loading"
indicate "."
indicate "."
indicate "."
display " Done!"
```

The `indicate` statement outputs text **without** a newline. This is useful for creating progress bars and dynamic console output.

### Clear the Console

```steps
clear console
```

Clears the terminal screen. Works on Windows 10+, Linux, and macOS.

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

**Iteration Limit:**

To prevent infinite loops, Steps enforces a maximum iteration limit (default: 10,000,000). You can adjust this when needed:

```steps
set iteration limit to 100000

note: Your loop code here

set iteration limit to 10000000  # Reset to default
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

**Formatting Numbers:**
```steps
set pi to 3.14159265
display "Pi is " added to (pi as decimal(2))    # "Pi is 3.14"
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

### Floor Declaration

Floors are declared inline in the building file:

**my_project.building:**
```steps
building: my_project

    floors:
        floor: calculations
            step: calculate_tax
            step: calculate_total
            step: apply_discount

    call calculate_tax with 100, 8.5 storing result in tax
    exit
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

### Scaffolding Step Files Automatically

The recommended way to set up a new Steps project is:

1. **Create a project first**: Use **File → New Project...** to create the project folder and a starter `.building` file. This ensures the building file lives inside a proper project directory.
2. **Edit the `floors:` section** in the generated building file to define the floors and steps your project needs.
3. **Scaffold**: Press **Ctrl+Shift+G** or choose **File → Scaffold from Building...** — the IDE reads the `floors:` section and creates all missing floor folders and step files with boilerplate code.
4. **Fill in** the step implementations.
5. **Grow incrementally**: Add more steps to the `floors:` section and re-run Scaffold — only new files are created.

> **Important:** Always start with **File → New Project...** rather than manually saving a building file. The scaffold command places floor folders next to the building file, so the building file must already be inside a project directory for the structure to be correct.

Each generated `.step` file includes the `belongs to:`, `expects:`, `returns:`, `declare:`, and `do:` sections — ready for you to fill in.

**Key properties:**

- **Non-destructive**: Existing files are never overwritten. Safe to run repeatedly as you add new floors or steps.
- **Incremental**: Add more steps to your `floors:` section and re-run — only the new ones are created.
- The toolbar also has a 🏗️ **Scaffold** button for quick access.

**Workflow at a glance:**

```
1. File → New Project...               → Creates project folder + building file
2. Edit the floors: section to plan your project structure
3. File → Scaffold from Building...    → Auto-creates all floor folders and step files
4. Fill in the step implementations
5. Add more steps → re-run Scaffold → only new ones created
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
├── my_app.building         # Includes floors: section
├── user_management/        # User-related steps
│   ├── create_user.step
│   └── validate_user.step
├── payments/               # Payment-related steps
│   ├── process_payment.step
│   └── issue_refund.step
└── notifications/          # Notification-related steps
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

## Console Graphics (TUI)

Steps includes built-in functions for creating attractive console interfaces.

### Drawing Boxes and Banners

```steps
note: Create a decorative banner
call banner with "My Application", 40 storing result in b
display b

note: Draw a box around text
call box with "Welcome!", 30 storing result in bx
display bx
```

Output:
```
╔══════════════════════════════════════╗
║           My Application             ║
╚══════════════════════════════════════╝

┌────────────────────────────┐
│          Welcome!          │
└────────────────────────────┘
```

### Progress Bars

**Static progress bar:**
```steps
call progress_bar with 7, 10, 20 storing result in pb
display "Loading: " added to pb
```

Output: `Loading: [██████████████░░░░░░] 70%`

**Dynamic progress bar (updates in place):**
```steps
set i to 0
repeat while i is less than or equal to 100
    call progress_bar with i, 100, 40 storing result in bar
    indicate "\r" added to "Progress: " added to bar added to " " added to (i as text) added to "%"
    set i to i + 10
display ""  # Final newline after completion
```

This creates a progress bar that updates on the same line using `indicate` with the carriage return character `\r`.

### Menus

```steps
call menu with ["Add Contact", "Search", "Exit"]
```

Output:
```
  1. Add Contact
  2. Search
  3. Exit
```

See [STDLIB.md](STDLIB.md#tui-floor-text-user-interface) for the complete list of TUI functions.

---

## Next Steps

1. **Practice with the REPL**: Try out language features interactively
2. **Build a small project**: Start with a simple calculator or greeting program
3. **Read the Language Reference**: See [LANGUAGE-REFERENCE.md](LANGUAGE-REFERENCE.md) for complete details
4. **Explore the examples**: Check `dev-docs/examples/` for sample projects

Happy coding with Steps! 🏗️

