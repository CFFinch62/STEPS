# Steps Programming Language - Interactive Tutorial

> **Learn Steps step-by-step with hands-on examples!**

This tutorial will guide you through the Steps programming language with practical examples you can run and modify. Each lesson builds on the previous one, introducing new concepts gradually.

---

## Table of Contents

1. [Getting Started](#lesson-1-getting-started)
2. [Variables and Data Types](#lesson-2-variables-and-data-types)
3. [User Input and Output](#lesson-3-user-input-and-output)
4. [Making Decisions](#lesson-4-making-decisions)
5. [Loops and Repetition](#lesson-5-loops-and-repetition)
6. [Working with Lists](#lesson-6-working-with-lists)
7. [Working with Tables](#lesson-7-working-with-tables)
8. [Creating Your First Step](#lesson-8-creating-your-first-step)
9. [Steps with Parameters](#lesson-9-steps-with-parameters)
10. [Organizing with Floors](#lesson-10-organizing-with-floors)
11. [Building a Complete Project](#lesson-11-building-a-complete-project)
12. [Error Handling](#lesson-12-error-handling)
13. [Working with Files](#lesson-13-working-with-files)
14. [Randomness and Games](#lesson-14-randomness-and-games)
15. [Using the Debugger](#lesson-15-using-the-debugger)
16. [Visualizing Your Code](#lesson-16-visualizing-your-code)

---

## How to Use This Tutorial

Each lesson has:
- **Concept**: What you'll learn
- **Example Program**: A working Steps program in `/projects/tutorial/`
- **Try It**: Exercises to practice
- **Key Takeaways**: Summary of important points

### Running the Examples

```bash
# From the Steps directory
python -m steps.main run projects/tutorial/lesson_01_hello

# Or use the IDE
python -m steps_ide.main
# Then open the lesson's .building file and press F5
```

---

## Lesson 1: Getting Started

### Concept: Your First Program

Every Steps program is a **building**. The simplest building just displays a message and exits.

### Example: `lesson_01_hello.building`

```steps
building: lesson_01_hello
    note: My first Steps program!
    
    display "Hello, Steps!"
    display "Welcome to programming!"
    
    exit
```

### What's Happening?

- `building: lesson_01_hello` - Declares this is a building named "lesson_01_hello"
- `note:` - A comment explaining what the code does
- `display` - Shows text to the user
- `exit` - Ends the program

### Try It

1. Run the program
2. Change the messages to say something different
3. Add more `display` statements

### Key Takeaways

✓ Every program starts with `building: name`  
✓ Use `display` to show output  
✓ Use `note:` for comments  
✓ End with `exit`

---

## Lesson 2: Variables and Data Types

### Concept: Storing and Using Data

Variables hold data. Steps has five data types: **number**, **text**, **boolean**, **list**, and **table**.

### Example: `lesson_02_variables.building`

See `/projects/tutorial/lesson_02_variables/lesson_02_variables.building`

### What's Happening?

- `set variable_name to value` - Creates or updates a variable
- Variables can hold different types of data
- You can do math with numbers
- You can combine text with `added to`

### Try It

1. Create a variable with your age
2. Calculate your age in months (age × 12)
3. Display the result

### Key Takeaways

✓ Use `set` to create variables
✓ Numbers can be whole or decimal
✓ Text goes in "quotes"
✓ Booleans are `true` or `false`

### Naming Rules

When naming variables, steps, floors, and buildings, follow these rules:

| ✓ Valid | ✗ Invalid |
|---------|-----------|
| `my_variable` | `my-variable` (no hyphens) |
| `count2` | `2count` (can't start with digit) |
| `firstName` | `first name` (no spaces) |
| `_private` | `set` (reserved word) |

> **Remember:** Names are case-sensitive! `myAge` and `myage` are different variables.

---

## Lesson 3: User Input and Output

### Concept: Interactive Programs

Programs are more interesting when they interact with users!

### Output Statements

Steps provides two ways to output text:

- **`display`** - Outputs text followed by a newline
- **`indicate`** - Outputs text without a newline (useful for progress indicators)

### Example: `lesson_03_input.building`

See `/projects/tutorial/lesson_03_input/lesson_03_input.building`

### What's Happening?

- `set variable to input as type` - Gets input from the user
- `as number` - Converts input to a number
- `as text` - Keeps input as text (default)

### Try It

1. Ask for the user's favorite color
2. Ask for their lucky number
3. Display a message using both

### Key Takeaways

✓ Use `input as number` for numeric input
✓ Use `input as text` for text input
✓ Always display a prompt before asking for input

---

## Lesson 4: Making Decisions

### Concept: Conditional Logic

Programs need to make decisions based on conditions.

### Example: `lesson_04_decisions.building`

See `/projects/tutorial/lesson_04_decisions/lesson_04_decisions.building`

### What's Happening?

- `if condition` - Executes code if condition is true
- `otherwise if condition` - Checks another condition
- `otherwise` - Executes if all conditions are false
- Comparison operators: `is equal to`, `is greater than`, `is less than`

### Try It

1. Ask for a temperature
2. Display "Hot" if > 80, "Cold" if < 60, "Nice" otherwise
3. Add more temperature ranges

### Key Takeaways

✓ Use `if` for conditional execution
✓ Use `otherwise if` for multiple conditions
✓ Use `otherwise` as a catch-all
✓ Conditions use English phrases like "is equal to"

---

## Lesson 5: Loops and Repetition

### Concept: Repeating Actions

Loops let you repeat code multiple times.

### Example: `lesson_05_loops.building`

See `/projects/tutorial/lesson_05_loops/lesson_05_loops.building`

### What's Happening?

- `repeat N times` - Repeats code N times
- `while condition` - Repeats while condition is true
- `for each item in list` - Iterates over a list

### Try It

1. Create a countdown from 10 to 1
2. Ask the user to guess a number (1-10) until they get it right
3. Display all even numbers from 2 to 20

### Key Takeaways

✓ Use `repeat N times` for fixed repetition
✓ Use `while` for conditional repetition
✓ Use `for each` to process lists
✓ Be careful to avoid infinite loops!

---

## Lesson 6: Working with Lists

### Concept: Collections of Data

Lists store multiple values in order.

### Example: `lesson_06_lists.building`

See `/projects/tutorial/lesson_06_lists/lesson_06_lists.building`

### What's Happening?

- `[1, 2, 3]` - Creates a list
- `add value to list_name` - Adds to the end
- `remove value from list_name` - Removes first occurrence
- `list_name[index]` - Accesses an item (0-based)
- `length of list_name` - Gets the number of items

### Try It

1. Create a shopping list
2. Add 5 items
3. Display each item with a number
4. Remove an item and display the updated list

### Key Takeaways

✓ Lists hold multiple values
✓ Use `add` and `remove` to modify lists
✓ Access items with `[index]` (starts at 0)
✓ Use `length of` to get the size

---

## Lesson 7: Working with Tables

### Concept: Key-Value Storage

Tables (dictionaries/maps) store data with named keys.

### Example: `lesson_07_tables.building`

See `/projects/tutorial/lesson_07_tables/lesson_07_tables.building`

### What's Happening?

- `["key": value]` - Creates a table
- `table["key"]` - Accesses a value
- `set table["key"] to value` - Sets a value
- Tables can store any type of data

### Try It

1. Create a table for a book (title, author, year, pages)
2. Display each piece of information
3. Update the year and display again

### Key Takeaways

✓ Tables store key-value pairs
✓ Use `["key"]` to access values
✓ Keys are text, values can be any type
✓ Great for structured data

---

## Lesson 8: Creating Your First Step

### Concept: Reusable Code

Steps are reusable pieces of code. They're like functions in other languages.

### Example: `lesson_08_first_step/`

See the complete project in `/projects/tutorial/lesson_08_first_step/`

### What's Happening?

- Steps go in their own `.step` files
- Steps belong to floors
- Use `call step_name` to run a step
- Steps can return values

### Try It

1. Create a step that displays your name
2. Call it multiple times from the building
3. Create another step that displays the date

### Key Takeaways

✓ Steps are reusable code units
✓ One step per file
✓ Steps must belong to a floor
✓ Use `call` to execute a step

---

## Lesson 9: Steps with Parameters

### Concept: Passing Data to Steps

Steps can accept input (parameters) and return output.

### Example: `lesson_09_parameters/`

See the complete project in `/projects/tutorial/lesson_09_parameters/`

### What's Happening?

- `expects: param1, param2` - Declares parameters
- `returns: result` - Declares return value
- `call step_name with arg1, arg2 storing result in variable` - Calls with arguments
- Parameters are like variables inside the step

### Try It

1. Create a step that adds two numbers
2. Create a step that greets a person by name
3. Create a step that calculates the area of a rectangle

### Key Takeaways

✓ Use `expects:` to declare parameters
✓ Use `returns:` to declare return value
✓ Use `with` to pass arguments
✓ Use `storing result in` to capture return value

---

## Lesson 10: Organizing with Floors

### Concept: Grouping Related Steps

Floors organize related steps into logical groups.

### Example: `lesson_10_floors/`

See the complete project in `/projects/tutorial/lesson_10_floors/`

### What's Happening?

- Floors are folders containing related steps
- Floors are declared in the `floors:` section of the building file
- Steps declare which floor they belong to
- Floors help organize large projects

### Try It

1. Create a "math" floor with add, subtract, multiply steps
2. Create a "text" floor with uppercase, lowercase steps
3. Use steps from both floors in your building

### Tip: Use Scaffold from Building

Instead of creating each floor folder and step file by hand, let the IDE do it:

1. Start with **File → New Project...** to create your project folder and building file
2. Edit the `floors:` section in the building file to define your floors and steps
3. Press **Ctrl+Shift+G** (or **File → Scaffold from Building...**)
4. The IDE creates all the missing folders and step files with boilerplate code

Always start with **New Project** — this ensures the building file is inside a proper project folder so that scaffold places everything in the right location. The process is non-destructive, so you can run it repeatedly as you add more steps.

### Key Takeaways

✓ Floors group related functionality
✓ One floor per folder
✓ Floors are declared in the building's `floors:` section
✓ Use **Scaffold from Building** (Ctrl+Shift+G) to auto-create floor folders and step files
✓ Good organization makes code easier to understand

---

## Lesson 11: Building a Complete Project

### Concept: Putting It All Together

Let's build a complete project using everything we've learned!

### Example: `lesson_11_complete_project/`

See the complete project in `/projects/tutorial/lesson_11_complete_project/`

This is a **Contact Manager** that demonstrates:
- Multiple floors (contacts, display, input)
- Steps with parameters
- Lists and tables
- User input
- Control flow
- Loops

### What's Happening?

The project is organized into:
- **contacts floor**: Managing contact data
- **display floor**: Showing information
- **input floor**: Getting user input
- **Main building**: Coordinating everything

### Try It

1. Run the contact manager
2. Add some contacts
3. Search for a contact
4. Modify it to add phone numbers
5. Add a feature to delete contacts

### Key Takeaways

✓ Real projects use multiple floors
✓ Each floor has a clear purpose
✓ Steps are small and focused
✓ Good organization makes projects maintainable

---

## Lesson 12: Error Handling

### Concept: Handling Things That Go Wrong

Programs can fail for many reasons: invalid user input, missing files, division by zero. **Error handling** lets you deal with these problems gracefully instead of crashing.

### Example: `lesson_12_error_handling/`

See the complete project in `/projects/tutorial/lesson_12_error_handling/`

### What's Happening?

- `attempt:` - Contains code that might fail
- `if unsuccessful:` - Runs if something went wrong
- `then continue:` - Always runs (for cleanup)
- `problem_message` - Describes what went wrong

### The Pattern

```steps
attempt:
    set num to input as number
if unsuccessful:
    display "Error: " added to problem_message
then continue:
    display "Done processing"
```

### Try It

1. Run the lesson and try entering invalid input
2. Create a step that safely divides two numbers
3. Add error handling to a file reading operation

### Key Takeaways

✓ Use `attempt:` around risky code  
✓ Use `if unsuccessful:` to handle errors  
✓ Use `problem_message` to see what went wrong  
✓ Use `then continue:` for cleanup that always runs

---

## Lesson 13: Working with Files

### Concept: Saving and Loading Data

Files let your programs save data that persists after the program ends.

### Example: `lesson_13_files/`

See the complete project in `/projects/tutorial/lesson_13_files/`

### What's Happening?

- `write_file` - Saves text to a file
- `read_file` - Reads file contents
- `append_file` - Adds to end of file
- `file_exists` - Checks if file exists
- `write_csv` / `read_csv` - For structured data

### Try It

1. Run the lesson and see files being created
2. Create a simple note-taking program
3. Store and retrieve a list of names

### Key Takeaways

✓ `write_file` overwrites, `append_file` adds  
✓ CSV files store rows as tables  
✓ Always check if files exist before reading  
✓ Great for saving game scores, settings, data

---

## Lesson 14: Randomness and Games

### Concept: Adding Unpredictability

Randomness makes programs more interesting! Use it for games, simulations, and testing.

### Example: `lesson_14_random/`

See the complete project in `/projects/tutorial/lesson_14_random/`

### What's Happening?

- `random_int` with min, max - Random number in range
- `random_choice` with list - Pick random item

### Try It

1. Run the lesson and play the mini-game
2. Create a dice-rolling simulator
3. Build a random story generator

### Key Takeaways

✓ `random_int` for random numbers  
✓ `random_choice` for random list items  
✓ Combine with loops for simulations  
✓ Perfect for games and testing

---

## Lesson 15: Using the Debugger

### Concept: Understanding Your Code

The Steps IDE includes a debugger that lets you step through your code line by line, inspect variables, and understand exactly how your program runs.

### Why Use a Debugger?

- See exactly what your code is doing
- Find and fix bugs faster
- Understand how variables change
- Learn how steps call each other

### Debug Keyboard Shortcuts

| Key | Action |
|-----|--------|
| F5 | Start debugging |
| Shift+F5 | Stop debugging |
| F9 | Toggle breakpoint |
| F11 | Step Into |
| F10 | Step Over |
| Shift+F11 | Step Out |
| Ctrl+Shift+D | Toggle debug panel |

### Setting Breakpoints

Breakpoints tell the debugger where to pause. You can set them by:

1. **Clicking in the gutter** - Click the left margin next to a line number
2. **Pressing F9** - Toggle breakpoint on the current line

A red circle appears next to lines with breakpoints.

### Stepping Through Code

1. **Start Debugging (F5)** - Your program runs until it hits a breakpoint or the first line
2. The current line is highlighted in yellow
3. Use stepping commands to move through your code:

   - **Step Into (F11)** - Execute the line. If it calls a step, enter that step.
   - **Step Over (F10)** - Execute the line. If it calls a step, run it completely.
   - **Step Out (Shift+F11)** - Run until the current step returns.

### The Debug Panel

Open it with **Ctrl+Shift+D** or from the Debug menu.

**Variables Tab:**
- 🌐 **Globals** - Variables in your main building
- 📦 **Step Name** - Local variables when inside a step
- Changed variables are highlighted in green

**Call Stack Tab:**
- Shows nested step calls
- Click to jump to a location

### Try It: Debug the Tip Calculator

1. Open `/projects/tip_calculator/tip_calculator.building`
2. Click in the gutter on line 6 (the first `set` statement) to add a breakpoint
3. Press **F5** to start debugging
4. Use **F11** (Step Into) to move through the code
5. Watch the Variables panel as values change
6. When you reach `call calculate_tip`, use **F11** to step into the step
7. See the call stack show the step you're inside
8. Use **Shift+F11** to step out and return to the building

### Debugging Tips

1. **Start at the beginning** - Set a breakpoint on the first line of code you want to understand
2. **Watch variables** - Check that values are what you expect at each step
3. **Use Step Over for trusted code** - If a step works correctly, skip into it with F10
4. **Check the call stack** - When debugging errors in steps, the call stack shows how you got there

### Key Takeaways

✓ Use breakpoints to pause execution where you want  
✓ F11 steps into code, F10 steps over it  
✓ The Variables tab shows current values  
✓ The Call Stack shows nested step calls  
✓ Debugging helps you understand and fix your code

---

## Lesson 16: Visualizing Your Code

### Concept: Project Diagrams

The Steps CLI includes a diagram tool that generates ASCII art visualizations of your project structure. This helps you understand and document how your building, floors, and steps are organized.

### Usage

```bash
# From the Steps directory
python -m steps.main diagram <path_to_project>

# Example
python -m steps.main diagram projects/tip_calculator
```

### What the Diagram Shows

- **🏢 Building**: Your main program
- **📂 Floors**: Groups of related steps
- **🔷 Steps**: Individual tasks with their parameters (`needs:`) and return types (`returns:`)
- **Arrows**: Flow between components

### Example Output

```
┌──────────────────────────────────────────────────────┐
│ 🏢 BUILDING: my_project                               │
├──────────────────────────────────────────────────────┤
│                                                       │
│  ┌────────────────────────────────────────────────┐  │
│  │ 📂 FLOOR: math                                  │  │
│  ├────────────────────────────────────────────────┤  │
│  │                                                 │  │
│  │    ┌────────────────────────────────────────┐   │  │
│  │    │ 🔷 add_numbers                          │   │  │
│  │    │   needs: a, b                           │   │  │
│  │    │   returns: number                       │   │  │
│  │    └────────────────────────────────────────┘   │  │
│  │            │                                    │  │
│  │            ▼                                    │  │
│  │    ┌────────────────────────────────────────┐   │  │
│  │    │ 🔷 multiply                             │   │  │
│  │    └────────────────────────────────────────┘   │  │
│  │                                                 │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

### Try It

1. Generate a diagram for the tip calculator: `python -m steps.main diagram projects/tip_calculator`
2. Generate a diagram for one of your own projects
3. Compare the diagram to the project folder structure

### When to Use Diagrams

- **Understanding existing projects**: See how they're organized at a glance
- **Planning new projects**: Design your structure before coding
- **Documentation**: Include diagrams in your README files
- **Teaching**: Show others how your code is structured

### Key Takeaways

✓ Use `steps diagram <path>` to visualize project structure  
✓ Diagrams show buildings, floors, and steps  
✓ Step parameters and return types are displayed  
✓ Great for documentation and understanding code

---

## Next Steps

Congratulations! You've completed the Steps tutorial! 🎉

### Where to Go From Here

1. **Read the Language Reference** (`docs/LANGUAGE-REFERENCE.md`) for complete details
2. **Explore Example Projects** in `/projects/` for more complex examples
3. **Build Your Own Project** - Start small and grow it!
4. **Use the IDE** (`python -m steps_ide.main`) for a better development experience

### Project Ideas

- **Calculator**: Basic arithmetic with a menu
- **Quiz Game**: Ask questions and keep score
- **Todo List**: Add, complete, and remove tasks
- **Grade Calculator**: Input grades and calculate average
- **Simple Database**: Store and search records
- **Text Adventure**: A choose-your-own-adventure game

### Getting Help

- Check the **User Guide** (`docs/USER-GUIDE.md`)
- Review the **Language Reference** (`docs/LANGUAGE-REFERENCE.md`)
- Look at existing projects for examples
- Experiment in the REPL (`python -m steps_repl.main`)

---

## Summary of Key Concepts

| Concept | Syntax | Example |
|---------|--------|---------|
| Display output | `display` | `display "Hello!"` |
| Create variable | `set` | `set age to 25` |
| Get input | `input as type` | `set name to input as text` |
| Condition | `if` / `otherwise` | `if age is greater than 18` |
| Loop (fixed) | `repeat N times` | `repeat 5 times` |
| Loop (conditional) | `while` | `while count is less than 10` |
| Loop (list) | `for each` | `for each item in list` |
| Create list | `[]` | `set nums to [1, 2, 3]` |
| Create table | `[:]` or `["key": val]` | `set person to ["name": "Alice"]` |
| Call step | `call` | `call greet with "Bob"` |
| Return value | `return` | `return result` |

Happy coding with Steps! 🏗️


