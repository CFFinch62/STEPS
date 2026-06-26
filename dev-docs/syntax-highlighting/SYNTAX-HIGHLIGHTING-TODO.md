# Syntax Highlighting Enhancement Tasks

## Quick Start

Read `SYNTAX-HIGHLIGHTING.md` first for background. This document contains specific tasks to enhance the highlighting.

## Current File to Edit

**File**: `tree-sitter-steps/queries/highlights_minimal.scm`

This is the working highlight query. Add new rules here incrementally.

## Task List

### Task 1: Add String Literal Highlighting

**Goal**: Highlight string literals in Steps code.

**Steps**:
1. Verify the node type exists:
   ```bash
   grep '"type": "string"' tree-sitter-steps/src/node-types.json
   ```

2. Add to `highlights_minimal.scm`:
   ```scheme
   ; String literals
   (string) @string
   ```

3. Test:
   ```bash
   ./venv/bin/python3 test_syntax_highlighting.py
   ```

4. If successful, test in IDE with a `.step` file containing strings.

**Example Steps code to test**:
```steps
set message to "Hello, World!"
display message
```

---

### Task 2: Add Number Literal Highlighting

**Goal**: Highlight numeric literals.

**Steps**:
1. Verify: `grep '"type": "number"' tree-sitter-steps/src/node-types.json`

2. Add to `highlights_minimal.scm`:
   ```scheme
   ; Number literals
   (number) @number
   ```

3. Test with code like:
   ```steps
   set count to 42
   set pi to 3.14
   ```

---

### Task 3: Add Boolean and Nothing Highlighting

**Goal**: Highlight special constants.

**Steps**:
1. Add to `highlights_minimal.scm`:
   ```scheme
   ; Boolean and null literals
   "true" @boolean
   "false" @boolean
   "nothing" @constant.builtin
   ```

2. Test with:
   ```steps
   set is_valid to true
   set result to nothing
   ```

---

### Task 4: Add Operator Highlighting

**Goal**: Highlight arithmetic and logical operators.

**Steps**:
1. Check which operators exist as literals:
   ```bash
   grep '"type": "+"' tree-sitter-steps/src/node-types.json
   grep '"type": "and"' tree-sitter-steps/src/node-types.json
   ```

2. Add to `highlights_minimal.scm`:
   ```scheme
   ; Arithmetic operators
   "+" @operator
   "-" @operator
   "*" @operator
   "/" @operator
   
   ; Logical operators
   "and" @keyword.operator
   "or" @keyword.operator
   "not" @keyword.operator
   
   ; Comparison operators
   "equals" @keyword.operator
   "is greater than" @keyword.operator
   "is less than" @keyword.operator
   "contains" @keyword.operator
   ```

3. Test with:
   ```steps
   set sum to 5 + 3
   if count is greater than 10 and is_valid equals true
   ```

---

### Task 5: Add More Control Flow Keywords

**Goal**: Complete the control flow keyword highlighting.

**Steps**:
1. Add to `highlights_minimal.scm`:
   ```scheme
   ; Additional control flow
   "repeat" @keyword.control
   "times" @keyword.control
   "for each" @keyword.control
   "in" @keyword.control
   "otherwise if" @keyword.control
   "otherwise" @keyword.control
   "attempt:" @keyword.control
   "if unsuccessful:" @keyword.control
   "then continue:" @keyword.control
   ```

2. Test with:
   ```steps
   repeat 5 times
       display "Hello"
   
   for each item in my_list
       display item
   ```

---

### Task 6: Add Statement Keywords

**Goal**: Highlight common statement keywords.

**Steps**:
1. Add to `highlights_minimal.scm`:
   ```scheme
   ; Statement keywords
   "set" @keyword
   "to" @keyword
   "as" @keyword
   "call" @keyword.function
   "with" @keyword
   "storing result in" @keyword
   "return" @keyword.return
   "add" @keyword
   "remove" @keyword
   "from" @keyword
   ```

2. Test with:
   ```steps
   set x to 10
   call calculate_sum with x, 5 storing result in total
   return total
   ```

---

### Task 7: Add Built-in Function Highlighting

**Goal**: Highlight built-in functions differently from keywords.

**Steps**:
1. Add to `highlights_minimal.scm`:
   ```scheme
   ; Built-in functions
   "display" @function.builtin
   "input" @function.builtin
   ```

2. Test with:
   ```steps
   display "Enter your name:"
   input user_name
   ```

---

### Task 8: Add Type Annotation Highlighting

**Goal**: Highlight type names.

**Steps**:
1. Add to `highlights_minimal.scm`:
   ```scheme
   ; Type keywords
   "number" @type.builtin
   "text" @type.builtin
   "boolean" @type.builtin
   "list" @type.builtin
   "table" @type.builtin
   "fixed" @keyword
   ```

2. Test with:
   ```steps
   declare:
       count as number
       message as text
       items as list
   ```

---

### Task 9: Add Punctuation Highlighting

**Goal**: Highlight delimiters and brackets.

**Steps**:
1. Add to `highlights_minimal.scm`:
   ```scheme
   ; Punctuation
   ":" @punctuation.delimiter
   "," @punctuation.delimiter
   "[" @punctuation.bracket
   "]" @punctuation.bracket
   "(" @punctuation.bracket
   ")" @punctuation.bracket
   ```

2. Test with:
   ```steps
   set items to [1, 2, 3]
   set first to items[0]
   ```

---

### Task 10: Add Structured Highlighting (Advanced)

**Goal**: Highlight identifiers based on context.

**Steps**:
1. Add to `highlights_minimal.scm`:
   ```scheme
   ; Function definitions
   (step_def (identifier) @function)
   (riser_def (identifier) @function)
   (building_def (identifier) @namespace)
   (floor_def (identifier) @namespace)
   
   ; Function calls
   (call_statement (identifier) @function.call)
   
   ; Parameters
   (parameter (identifier) @variable.parameter)
   ```

2. Test with a complete step definition:
   ```steps
   step: calculate_sum
   belongs to: math_operations
   expects: a as number, b as number
   returns: number
   
   do:
       set result to a + b
       return result
   ```

---

## Testing Protocol

After each task:

1. **Run automated tests**:
   ```bash
   ./venv/bin/python3 test_syntax_highlighting.py
   ```
   All three tests must pass.

2. **Visual test in IDE**:
   - Open `examples/calculator.step` (or create a test file)
   - Verify the new highlighting appears
   - Check that existing highlighting still works

3. **If tests fail**:
   - Remove the last addition
   - Check the error message for the problematic node type
   - Verify the node exists in `src/node-types.json`
   - Try testing the rule individually

## Success Criteria

When all tasks are complete:
- [ ] All literal types are highlighted (strings, numbers, booleans)
- [ ] All keywords are highlighted appropriately
- [ ] Operators are visually distinct
- [ ] Built-in functions stand out
- [ ] Type annotations are clear
- [ ] Punctuation is subtle but visible
- [ ] Function definitions are prominent
- [ ] No errors when opening any `.step` or `.building` file

## Notes

- **Work incrementally**: Add one section, test, commit, repeat
- **Keep backups**: Copy `highlights_minimal.scm` before major changes
- **Reference the full query**: `highlights.scm` has examples (but doesn't work as-is)
- **Check the language spec**: `docs/LANGUAGE-REFERENCE.md` lists all keywords

## When You're Done

1. Rename `highlights_minimal.scm` to `highlights.scm` (backup the old one)
2. Update `tree-sitter-steps/bindings/python/tree_sitter_steps/__init__.py` to use `highlights.scm` instead of `highlights_minimal.scm`
3. Run full test suite
4. Update this document with any lessons learned

