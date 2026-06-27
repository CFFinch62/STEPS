# Steps IDE — Code Completion Reference

The Steps IDE includes an intelligent code completion system that suggests completions as you type. This document is the **complete reference** for every trigger, shortcut, expansion, and setting.

---

## Table of Contents

1. [How It Works](#how-it-works)
2. [Modes](#modes)
3. [Popup Controls](#popup-controls)
4. [Settings](#settings)
5. [Comparison Operators](#comparison-operators)
6. [Statement Shortcuts](#statement-shortcuts)
7. [Shortcut Abbreviations](#shortcut-abbreviations)
8. [Structure Snippets](#structure-snippets)
9. [Step Name Completion](#step-name-completion)
10. [Call Clause Completion](#call-clause-completion)
11. [Manual Trigger](#manual-trigger)
12. [How Matching Works](#how-matching-works)
13. [Where Completion Works](#where-completion-works)
14. [Cursor Placement](#cursor-placement)

---

## How It Works

As you type in a `.step` or `.building` file, the completion engine analyzes the current line and cursor position to determine if a suggestion should be offered. When a match is found, a popup appears below your cursor with one or more suggestions. You can accept a suggestion or keep typing to dismiss it.

There are **five categories** of completions:

| Icon | Category | When It Triggers |
|------|----------|-----------------|
| ⚖️ | **Comparison** | After typing `is ` (the keyword `is` followed by a space) |
| 📝 | **Statement** | When typing a keyword or abbreviation at the start of a line |
| 📦 | **Snippet** | When typing a structure keyword like `newstep` at the start of a line |
| 🔷 | **Step** | After typing `call ` (the keyword `call` followed by a space) |
| 🔗 | **Call Clause** | After typing `call step_name ` (a call with step name, followed by a space) |

---

## Modes

The completion system operates in one of two modes:

### Automatic Mode (Default)

Suggestions appear automatically after a configurable delay as you type. You do not need to press any special key — just type and suggestions will appear when a trigger is detected.

### Manual Mode

Suggestions appear **only** when you press `Ctrl+Space`. No suggestions will appear automatically. This mode is useful if you find the automatic popups distracting.

You can switch between modes in **Settings → Editor → Autocomplete Mode**.

---

## Popup Controls

When the completion popup is visible, use these keys:

| Key | Action |
|-----|--------|
| `↓` (Down Arrow) | Select the next suggestion |
| `↑` (Up Arrow) | Select the previous suggestion |
| `Enter` or `Tab` | Accept the selected suggestion |
| `Escape` | Dismiss the popup without accepting |
| Double-click | Accept the clicked suggestion |

When the popup is **not** visible:

| Key | Action |
|-----|--------|
| `Ctrl+Space` | Open the completion popup manually (works in both modes) |

---

## Settings

Found in **Settings → Editor** (at the bottom of the Editor tab):

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| Autocomplete Mode | Automatic / Manual (Ctrl+Space) | Automatic | Controls when suggestions appear |
| Suggestion Delay | 100–1000 ms (in 50ms steps) | 300 ms | How long to wait after typing before showing suggestions (Automatic mode only) |

Settings are saved to `~/.config/steps-ide/settings.json` (Linux) or `%APPDATA%/Steps-IDE/settings.json` (Windows) and persist across sessions.

---

## Comparison Operators

**Trigger**: Type the keyword `is` followed by a **space** after any expression.

**Example**: `if score is ` → popup appears with all comparison operators.

The popup shows **12 comparison options**:

| You Type | Suggestion Inserted | What It Means |
|----------|-------------------|---------------|
| `is ` | `equal to ` | Checks if two values are the same |
| `is ` | `not equal to ` | Checks if two values are different |
| `is ` | `less than ` | Checks if left value is smaller |
| `is ` | `greater than ` | Checks if left value is larger |
| `is ` | `less than or equal to ` | Checks if left value is smaller or the same |
| `is ` | `greater than or equal to ` | Checks if left value is larger or the same |
| `is ` | `in ` | Checks if a value exists inside a list or text |
| `is ` | `a number` | Checks if the value is a number type |
| `is ` | `a text` | Checks if the value is a text (string) type |
| `is ` | `a boolean` | Checks if the value is true or false |
| `is ` | `a list` | Checks if the value is a list type |
| `is ` | `a table` | Checks if the value is a table (dictionary) type |

**Filtering**: After `is `, keep typing to narrow the list. For example, `is le` shows only `less than` and `less than or equal to`.

**Complete example**:
```
if age is greater than or equal to 18
    display "You may enter"
```

---

## Statement Shortcuts

**Trigger**: Type 2 or more characters at the **start of a line** (after any indentation). The engine matches your typed text against all 14 built-in statements.

### Complete Statement List

| Statement | What Gets Inserted | Description |
|-----------|-------------------|-------------|
| `if` | `if ▌` | Conditional branch — cursor placed after `if` |
| `otherwise if` | `otherwise if ▌` | Else-if branch — cursor placed after `otherwise if` |
| `otherwise` | `otherwise` | Else branch (no cursor marker — complete as-is) |
| `repeat … times` | `repeat ▌ times` | Count-based loop — cursor placed between `repeat` and `times` |
| `repeat while` | `repeat while ▌` | While loop — cursor placed after `while` |
| `repeat for each` | `repeat for each ▌ in ` | For-each loop — cursor placed between `each` and `in` |
| `display` | `display ▌` | Print to console — cursor placed after `display` |
| `input` | `input` | Read user input (complete as-is) |
| `set … to` | `set ▌ to ` | Variable assignment — cursor placed between `set` and `to` |
| `call` | `call ▌` | Call a step — cursor placed after `call` |
| `return` | `return ▌` | Return a value — cursor placed after `return` |
| `attempt:` | Multi-line scaffold (see below) | Try/catch block |
| `exit` | `exit` | End the program (complete as-is) |
| `clear console` | `clear console` | Clear the terminal (complete as-is) |

**▌** = where your cursor is placed after accepting the suggestion.

### The `attempt:` Scaffold

When you accept the `attempt:` completion, a multi-line template is inserted:

```
attempt:
    ▌
if unsuccessful:
    
```

The cursor is placed inside the `attempt:` block, ready for you to type the guarded code.

---

## Shortcut Abbreviations

Each statement can be triggered by typing just the first few characters. Additionally, special **short abbreviations** are provided for common statements that would otherwise require many keystrokes.

### Special Abbreviations

These are unique shortcuts that don't match the natural prefix of any keyword:

| You Type | Suggestions Shown |
|----------|------------------|
| `oi` | `otherwise if` |
| `ow` | `otherwise` |
| `rw` | `repeat while` |
| `rfe` | `repeat for each` |
| `att` | `attempt:` |
| `cl` | `clear console` |
| `inp` | `input` |

### Natural Prefix Matching

Every statement also responds to typing any prefix of its **first keyword**. For example, for `display`:

| You Type | Matches |
|----------|---------|
| `di` | `display` |
| `dis` | `display` |
| `disp` | `display` |
| `displ` | `display` |
| `displa` | `display` |
| `display` | `display` |

### Prefixes That Match Multiple Statements

Some prefixes are shared. When this happens, all matching statements appear in the popup and you can pick the one you want:

| You Type | All Suggestions Shown |
|----------|----------------------|
| `re` | `repeat … times`, `repeat while`, `repeat for each`, `return` |
| `rep` | `repeat … times`, `repeat while`, `repeat for each` |
| `ot` | `otherwise if`, `otherwise` |
| `se` | `set … to` |
| `ex` | `exit` |
| `ca` | `call` |
| `at` | `attempt:` |
| `if` | `if` |
| `in` | `input` |

### Complete Abbreviation Quick Reference

For fast typing, here are the shortest possible abbreviations for each statement:

| Shortest | Statement |
|----------|-----------|
| `if` | `if` |
| `oi` | `otherwise if` |
| `ow` | `otherwise` |
| `re` | `repeat … times` (also shows `repeat while`, `repeat for each`, `return`) |
| `rw` | `repeat while` (unique) |
| `rfe` | `repeat for each` (unique) |
| `di` | `display` |
| `inp` | `input` (unique — `in` also works but also shows `input`) |
| `se` | `set … to` |
| `ca` | `call` |
| `ret` | `return` (unique — `re` also works but shows all repeat variants) |
| `att` | `attempt:` (unique — `at` also works) |
| `ex` | `exit` |
| `cl` | `clear console` (unique) |

---

## Structure Snippets

**Trigger**: Type one of the snippet keywords at the **start of a line** (after at least 3 characters). These insert multi-line templates for creating new Steps program structures.

### `newstep` — New Step Template

Typing `newstep` (or `news`, `newst`, etc.) and accepting inserts:

```
step: ▌
    belongs to: 
    expects: nothing
    returns: nothing

    do:
        
```

The cursor is placed after `step:` so you can immediately type the step name.

### `newbuild` — New Building Template

Typing `newbuild` (or `newb`, `newbu`, etc.) and accepting inserts:

```
building: ▌
    note: 

    floors:
        floor: user_input
            step: get_input
        floor: output
            step: show_output
        floor: actions
            step: main_action
        floor: data
            step: manage_data

    exit
```

The cursor is placed after `building:` so you can immediately type the building name.

### `newriser` — New Riser Template

Typing `newriser` (or `newr`, `newri`, etc.) and accepting inserts:

```
riser: ▌
    expects: nothing
    returns: nothing

    do:
        
```

The cursor is placed after `riser:` so you can immediately type the riser name.

**Indentation**: Snippets automatically respect your current indentation level. If you type `newstep` at 4-space indent, the entire template will be indented by 4 spaces.

---

## Step Name Completion

**Trigger**: Type `call ` (the keyword `call` followed by a space) in any `.step` or `.building` file.

When triggered, the popup shows **all step names found in the current project**. Step names are discovered by scanning the project directory for all `.step` files.

### How It Works

1. When you open or save a file, the IDE scans the project directory for `.step` files
2. The file names (without the `.step` extension) become the available step names
3. After typing `call `, all discovered step names appear in the popup
4. Continue typing to filter the list — e.g., `call calc` shows only steps starting with "calc"

### Example

If your project has these step files:
```
project/
├── math/
│   ├── calculate_subtotal.step
│   └── apply_discount.step
└── output/
    └── show_header.step
```

Then typing `call ` shows:
```
🔷 apply_discount
🔷 calculate_subtotal
🔷 show_header
```

Typing `call calc` narrows it to:
```
🔷 calculate_subtotal
```

---

## Call Clause Completion

**Trigger**: After typing a complete `call <step_name> ` (with a space after the step name), the popup offers **call clause** options.

| Suggestion | What Gets Inserted | Purpose |
|------------|-------------------|---------|
| `with` | `with ▌` | Pass arguments to the step |
| `storing result in` | `storing result in ▌` | Capture the step's return value in a variable |

### Example

```
call calculate_subtotal with price, quantity
call apply_discount with subtotal, 0.1 storing result in final_price
```

---

## Manual Trigger

**Shortcut**: `Ctrl+Space`

This works in **both** Automatic and Manual modes. When pressed:

1. If a specific trigger is detected (e.g., you're after `is ` or after `call `), those targeted suggestions appear
2. If no specific trigger is detected, a **broad list** of all available completions appears:
   - All 14 statements
   - All 3 structure snippets
   - All project step names (as `call <name>` insertions)
3. If you've typed a partial word, the list is filtered to matching items

This is useful for:
- Exploring what completions are available
- Getting suggestions in Manual mode
- Forcing suggestions to appear when Automatic mode hasn't triggered yet

---

## How Matching Works

The completion engine uses **case-insensitive prefix matching**:

- `dis` matches `display` (prefix of display)
- `DIS` matches `display` (case-insensitive)
- `equal` matches `equal to` (prefix of first word)
- Comparison filtering after `is ` matches any prefix: `is le` matches `less than` and `less than or equal to`

For step names, the same prefix matching applies: `call calc` matches `calculate_subtotal` and `calculator`.

---

## Where Completion Works

| File Type | Completion Available |
|-----------|---------------------|
| `.step` files | ✅ All categories |
| `.building` files | ✅ All categories |
| New untitled files | ✅ All categories (treated as Steps files) |
| Other file types (`.py`, `.txt`, etc.) | ❌ No completions |

### Position Rules

| Category | Position Requirement |
|----------|---------------------|
| Comparison operators | Anywhere on the line, after the word `is ` |
| Statement shortcuts | At the effective start of a line (after indentation only) |
| Structure snippets | At the effective start of a line (after indentation only) |
| Step names | After `call ` anywhere on the line |
| Call clauses | After `call <name> ` anywhere on the line |

---

## Cursor Placement

When a completion is accepted, the cursor is intelligently placed at the most useful position:

- **`$CURSOR` marker**: Many completions contain an internal cursor marker. After insertion, your cursor jumps to that position so you can immediately start typing the next required piece.
- **No marker**: Some completions (like `otherwise`, `exit`, `input`) are complete as-is. The cursor is placed at the end.

### Examples

| Accept This | Cursor Lands Here |
|------------|-------------------|
| `display` | `display ▌` — ready to type what to display |
| `set … to` | `set ▌ to ` — ready to type the variable name |
| `repeat … times` | `repeat ▌ times` — ready to type the count |
| `repeat for each` | `repeat for each ▌ in ` — ready to type the item variable |
| `otherwise` | `otherwise▌` — at the end, ready for next line |
| `newstep` | `step: ▌` — ready to type the step name |
