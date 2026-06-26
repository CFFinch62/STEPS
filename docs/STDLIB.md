# Steps Standard Library

The Steps standard library (stdlib) is automatically available to all buildings.

---

## Usage

Stdlib functions are called like any other step:

```steps
call abs with -5 storing result in x
call reverse with "hello" storing result in r
```

---

## Math Floor

### Basic Math (stdlib steps)

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `abs` | `n as number` | `number` | Absolute value |
| `max` | `a as number, b as number` | `number` | Larger of two numbers |
| `min` | `a as number, b as number` | `number` | Smaller of two numbers |
| `round` | `n as number` | `number` | Round to nearest integer |

```steps
call abs with -5 storing result in x        # 5
call max with 3, 7 storing result in y      # 7
call min with 3, 7 storing result in z      # 3
call round with 3.7 storing result in r     # 4
```

### Math Operators

| Operator | Keyword form | Example | Description |
|----------|--------------|---------|-------------|
| `%` | `modulo` | `10 % 3` → `1` | Remainder after division |

```steps
set remainder to 17 % 5     # 2
set remainder to 17 modulo 5  # same thing
```

### Power and Root (Native)

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `sqr` | `n` | `number` | Square (n²) |
| `sqrt` | `n` | `number` | Square root |
| `pow` | `base, exp` | `number` | base raised to exp |
| `pi` | *(none)* | `number` | π ≈ 3.14159… |

```steps
call sqr with 5 storing result in x         # 25
call sqrt with 16 storing result in y       # 4
call pow with 2, 10 storing result in z     # 1024
call pi storing result in p                 # 3.141592653589793
```

### Trigonometry (Native)

All trig functions use **radians**. Use `degrees` / `radians` to convert.

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `sin` | `n` | `number` | Sine |
| `cos` | `n` | `number` | Cosine |
| `tan` | `n` | `number` | Tangent |
| `asin` | `n` | `number` | Arcsine (input: -1 to 1) |
| `acos` | `n` | `number` | Arccosine (input: -1 to 1) |
| `atan` | `n` | `number` | Arctangent |
| `atan2` | `y, x` | `number` | Two-argument arctangent |
| `degrees` | `n` | `number` | Radians → degrees |
| `radians` | `n` | `number` | Degrees → radians |

```steps
call pi storing result in p
call sin with p / 2 storing result in s     # 1.0
call cos with 0 storing result in c         # 1.0
call degrees with p storing result in d     # 180.0
call radians with 90 storing result in r    # 1.5707963...
call atan2 with 1, 1 storing result in a    # 0.7853981... (45° in radians)
```

### Logarithms and Exponentials (Native)

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `log` | `n` | `number` | Natural logarithm (base e) |
| `log10` | `n` | `number` | Base-10 logarithm |
| `log2` | `n` | `number` | Base-2 logarithm |
| `exp` | `n` | `number` | e raised to n |

```steps
call log with 2.71828 storing result in x   # ≈ 1.0
call log10 with 100 storing result in y     # 2.0
call log2 with 8 storing result in z        # 3.0
call exp with 1 storing result in e         # 2.71828...
```

---

## Strings Floor

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `reverse` | `s as text` | `text` | Reverse text |
| `repeat_text` | `s as text, count as number` | `text` | Repeat text N times |

### Examples

```steps
call reverse with "hello" storing result in r      # "olleh"
call repeat_text with "*", 5 storing result in s   # "*****"
```

---

## Native String Functions

These string functions are *native* - implemented in Python for better performance.

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `lowercase` | `text` | `text` | Convert to lowercase |
| `uppercase` | `text` | `text` | Convert to uppercase |
| `trim` | `text` | `text` | Remove leading/trailing spaces |
| `slice` | `text, start, end` | `text` | Extract substring (start inclusive, end exclusive) |
| `index_of` | `text, search` | `number` | Find position of substring (-1 if not found) |
| `replace` | `text, old, new` | `text` | Replace all occurrences |
| `characters` | `text` | `list` | Convert text to list of characters |

### Examples

```steps
call lowercase with "HELLO" storing result in l    # "hello"
call uppercase with "hello" storing result in u    # "HELLO"
call trim with "  hi  " storing result in t        # "hi"
call slice with "hello", 0, 2 storing result in s  # "he"
call index_of with "hello", "ll" storing result in i  # 2
call replace with "hello", "l", "L" storing result in r  # "heLLo"

note: Iterate over a string character by character
call characters with "hello" storing result in chars
repeat for each char in chars
    display char
```

---

## List Creation (Native)

Create a pre-filled list of a given size in a single call. This is a **native** builtin — allocation happens at C speed inside Python, making it far faster than building the same list with a `repeat while` loop.

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `create_list` | `size as number, value as any` | `list` | Create a list of `size` elements all set to `value` |

```steps
note: Create a list of 10 zeros
call create_list with 10, 0 storing result in counters

note: Create a boolean sieve for prime-finding (much faster than a loop)
call create_list with 2000001, true storing result in sieve

note: Pre-fill a list of empty text
call create_list with 5, "" storing result in labels
```

> **Why use this instead of a loop?**
> A `repeat while` loop building a list of one million entries passes every iteration through the Steps interpreter — scope lookups, type dispatch, and object allocation on every step. `create_list` hands the whole job to Python's C-level list multiplication (`[value] * n`), which completes in milliseconds regardless of size.

---

## List Math (Native)

Aggregate functions that work on a **list of numbers**.

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `list_min` | `lst` | `number` | Smallest number in the list |
| `list_max` | `lst` | `number` | Largest number in the list |
| `list_sum` | `lst` | `number` | Sum of all numbers in the list |

```steps
set scores to [85, 92, 78, 95, 60]
call list_min with scores storing result in low    # 60
call list_max with scores storing result in high   # 95
call list_sum with scores storing result in total  # 410
```

---

## Date & Time Floor (Native)

These functions are *native* - implemented in Python, not Steps code.

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `time` | *(none)* | `number` | Current Unix timestamp (seconds since epoch, float precision) |
| `date` | *(none)* | `text` | Today's date as `"YYYY-MM-DD"` |
| `date_diff` | `date1 as text, date2 as text` | `number` | Days between two ISO dates (`date2 − date1`) |

### Examples

```steps
note: performance timing
call time storing result in start
repeat 10000 times
    set x to 1 + 1
call time storing result in finish
set elapsed to finish - start
display "Elapsed seconds: " added to elapsed as text

note: today's date
call date storing result in today
display today                                         # e.g. "2026-02-18"

note: days between two dates
call date_diff with "2026-01-01", "2026-12-31" storing result in days
display days                                          # 364

note: negative when first date is later
call date_diff with "2026-12-31", "2026-01-01" storing result in days
display days                                          # -364
```

---

## Random Floor (Native)

These functions are *native* - implemented in Python, not Steps code.

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `random_int` | `min_val, max_val as number` | `number` | Random integer in range (inclusive) |
| `random_choice` | `lst as list` | `any` | Pick random element from list |

### Examples

```steps
call random_int with 1, 100 storing result in r     # 42 (random)
call random_choice with my_list storing result in x # random element
```

---

## Files Floor (Native)

Text and CSV file operations.

### Text File Functions

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `read_file` | `path` | `text` | Read file contents |
| `write_file` | `path, content` | `nothing` | Write (overwrite) file |
| `append_file` | `path, content` | `nothing` | Append to file |
| `file_exists` | `path` | `boolean` | Check if file exists |

### CSV Functions

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `read_csv` | `path` | `list of tables` | Read CSV rows |
| `write_csv` | `path, data` | `nothing` | Write list of tables |

### Examples

```steps
note: Text file operations
call write_file with "output.txt", "Hello!"
call read_file with "output.txt" storing result in content

note: CSV operations
set rows to []
set row to ["name": "Alice", "age": "30"]
add row to data
call write_csv with "data.csv", rows

call read_csv with "data.csv" storing result in loaded
repeat for each person in loaded
    display person["name"]
```

### Creating Empty Tables

Use `[:]` to create an empty table:

```steps
set row to [:]              # Creates an empty table
set row["name"] to "Bob"
set row["age"] to "30"
```



## TUI Floor (Text User Interface)

Create attractive console interfaces with boxes, banners, menus, and more.

### Native TUI Functions

Core drawing primitives implemented in Python:

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `box` | `content, width` | `text` | Draw single-line box around text |
| `line` | `width, style` | `text` | Horizontal line (styles: "single", "double", "dashed", "thick") |
| `banner` | `title, width` | `text` | Decorative title banner (double-line box) |
| `center_text` | `text, width` | `text` | Center-pad text to width |
| `pad_text` | `text, width, align` | `text` | Pad text ("left", "right", "center") |
| `progress_bar` | `current, total, width` | `text` | Text progress bar |

### Examples

```steps
note: Draw a banner
call banner with "My App", 40 storing result in b
display b

note: Draw a box
call box with "Welcome!", 30 storing result in bx
display bx

note: Draw a line
call line with 40, "double" storing result in ln
display ln

note: Show progress (static)
call progress_bar with 7, 10, 20 storing result in pb
display pb

note: Show progress (dynamic - updates in place)
set i to 0
repeat while i is less than or equal to 100
    call progress_bar with i, 100, 40 storing result in bar
    indicate "\r" added to "Progress: " added to bar
    set i to i + 10
display ""  # Final newline
```

Output:
```
╔══════════════════════════════════════╗
║                My App                ║
╚══════════════════════════════════════╝

┌────────────────────────────┐
│         Welcome!           │
└────────────────────────────┘

════════════════════════════════════════

[██████████████░░░░░░] 70%
```

---

### Stdlib TUI Functions

Higher-level helpers written in Steps (extendable):

| Step | Parameters | Description |
|------|------------|-------------|
| `menu` | `options as list` | Display numbered menu |
| `table_display` | `rows as list, columns as list` | Display aligned columns |
| `divider` | `label as text, width as number` | Labeled divider line |

### Examples

```steps
note: Display a menu
call menu with ["Add Contact", "Search", "Exit"]

note: Display a table
set cols to ["name", "age"]
set data to []
add ["name": "Alice", "age": "30"] to data
add ["name": "Bob", "age": "25"] to data
call table_display with data, cols

note: Display a divider
call divider with "Options", 40
```

---



Project floors can override stdlib definitions. If your project has a floor with the same name as a stdlib floor, your project's definitions take precedence.

---

## Extending Stdlib

To add new stdlib functions:

1. Create a new `.step` file in the appropriate floor folder
2. The loader will auto-discover it from the floor directory
3. Rebuild/reinstall the package

### Naming Conventions

> [!CAUTION]
> **Avoid reserved words** when naming floors, steps, and parameters.

These caused conflicts and had to be renamed:
- `text` → `strings` (floor name)
- `times` → `count` (parameter name)

See [Reserved Words](LANGUAGE-REFERENCE.md#14-reserved-words) for the complete list.

---

## Stdlib Location

The stdlib is bundled at: `src/steps/stdlib/`

```
stdlib/
├── math/
│   ├── abs.step
│   ├── max.step
│   ├── min.step
│   └── round.step
├── strings/
│   ├── reverse.step
│   └── repeat_text.step
└── tui/
    ├── menu.step
    ├── table_display.step
    └── divider.step
```

> [!NOTE]
> Native functions (string operations like `lowercase`, `trim`, `slice` and TUI primitives like `box`, `banner`, `line`) are implemented in Python in `builtins/`, not as stdlib .step files.

