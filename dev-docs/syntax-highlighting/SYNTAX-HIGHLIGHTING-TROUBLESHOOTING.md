# Syntax Highlighting Troubleshooting Guide

## Quick Diagnostics

### Test 1: Can Python import the module?

```bash
./venv/bin/python3 -c "import tree_sitter_steps; print('OK')"
```

**Expected**: `OK`

**If fails**: Reinstall the package:
```bash
./venv/bin/python3 -m pip uninstall -y tree-sitter-steps
./venv/bin/python3 -m pip install -e tree-sitter-steps/
```

---

### Test 2: Can we get the language object?

```bash
./venv/bin/python3 -c "import tree_sitter_steps; print(tree_sitter_steps.get_language())"
```

**Expected**: `<Language id=... version=14, name=None>`

**If fails**: The C binding wasn't compiled. Rebuild:
```bash
cd tree-sitter-steps
npm run generate
cd ..
./venv/bin/python3 -m pip install -e tree-sitter-steps/ --force-reinstall
```

---

### Test 3: Can we load the highlight query?

```bash
./venv/bin/python3 -c "import tree_sitter_steps; q = tree_sitter_steps.get_highlight_query(); print(f'Loaded {len(q)} chars')"
```

**Expected**: `Loaded XXX chars`

**If fails**: Check that `tree-sitter-steps/queries/highlights_minimal.scm` exists.

---

### Test 4: Can we compile the query?

```bash
./venv/bin/python3 << 'EOF'
from tree_sitter import Language, Query
import tree_sitter_steps

lang = tree_sitter_steps.get_language()
query_text = tree_sitter_steps.get_highlight_query()
query = Query(lang, query_text)
print("Query compiled successfully!")
EOF
```

**Expected**: `Query compiled successfully!`

**If fails**: See "Invalid Node Type Errors" below.

---

### Test 5: Does registration work?

```bash
./venv/bin/python3 test_syntax_highlighting.py
```

**Expected**: All three tests pass.

**If fails**: See specific error messages below.

---

## Common Error Messages

### Error: "Invalid node type at row X, column Y: NODE_NAME"

**Meaning**: The highlight query references a node type that doesn't exist in the grammar.

**Solution**:
1. Find the problematic line in the query:
   ```bash
   sed -n 'Xp' tree-sitter-steps/queries/highlights_minimal.scm
   ```
   (Replace X with the row number from the error)

2. Check if the node exists:
   ```bash
   grep '"type": "NODE_NAME"' tree-sitter-steps/src/node-types.json
   ```

3. If it doesn't exist:
   - Remove the line from the query, OR
   - Add it to the grammar and regenerate

4. If it does exist but is a literal string, use quotes:
   - Change `(node_name)` to `"node_name"`

---

### Error: "No module named 'tree_sitter_steps'"

**Meaning**: The Python package isn't installed.

**Solution**:
```bash
./venv/bin/python3 -m pip install -e tree-sitter-steps/
```

---

### Error: "ImportError: ... binding.cpython-XXX.so"

**Meaning**: The C extension wasn't compiled.

**Solution**:
```bash
cd tree-sitter-steps
npm run generate  # Regenerate the parser
cd ..
./venv/bin/pip install -e tree-sitter-steps/ --force-reinstall --no-cache-dir
```

---

### Error: "FileNotFoundError: Highlight query not found"

**Meaning**: The query file is missing or in the wrong location.

**Solution**:
```bash
# Check if the file exists
ls -la tree-sitter-steps/queries/highlights_minimal.scm

# If missing, create it or check the path in __init__.py
```

---

### Error: "Unresolved conflict for symbol sequence"

**Meaning**: The grammar has ambiguities.

**Solution**:
1. This happens during `npm run generate`
2. Add precedence rules to the grammar:
   ```javascript
   rule_name: $ => prec.left(seq(...))
   ```
3. See `tree-sitter-steps/grammar.js` for examples

---

### Error: Highlighting doesn't appear in the IDE

**Possible causes**:

1. **Language not registered**:
   - Check that `register_steps_language()` returns `True`
   - Add debug print in `steps_editor.py`

2. **Wrong language set**:
   - Check that `detect_language()` returns `"steps"`
   - Verify file extension is `.step` or `.building`

3. **Query has errors**:
   - Run Test 4 above to verify query compiles
   - Check IDE logs for errors

4. **Textual theme doesn't support the styles**:
   - Try using standard styles like `@keyword`, `@comment`
   - Avoid custom styles like `@keyword.custom`

---

## Debugging Workflow

### Step 1: Isolate the Problem

Start with a minimal query that works:

```scheme
; Minimal working query
(comment) @comment
"step:" @keyword
(identifier) @variable
```

Save this as `highlights_minimal.scm` and test. If this works, the problem is in the query content.

---

### Step 2: Binary Search

Add back half of the removed rules. If it works, add half of the remaining. If it fails, remove half. Repeat until you find the problematic rule.

---

### Step 3: Test Individual Rules

Create a test script:

```python
from tree_sitter import Language, Query
import tree_sitter_steps

lang = tree_sitter_steps.get_language()

# Test each rule individually
rules = [
    '(comment) @comment',
    '"step:" @keyword',
    '(number) @number',
    # Add more...
]

for rule in rules:
    try:
        Query(lang, rule)
        print(f"✓ {rule}")
    except Exception as e:
        print(f"✗ {rule}: {e}")
```

---

### Step 4: Check Node Types

List all available node types:

```bash
# Named nodes (use with parentheses)
grep '"named": true' tree-sitter-steps/src/node-types.json -B 1 | grep '"type"'

# Anonymous nodes (use with quotes)
grep '"named": false' tree-sitter-steps/src/node-types.json -B 1 | grep '"type"'
```

---

## Grammar Changes

If you need to modify the grammar:

### 1. Edit the Grammar

Edit `tree-sitter-steps/grammar.js`

### 2. Regenerate the Parser

```bash
cd tree-sitter-steps
npm run generate
```

### 3. Rebuild the Python Package

```bash
cd ..
./venv/bin/python3 -m pip uninstall -y tree-sitter-steps
./venv/bin/python3 -m pip install -e tree-sitter-steps/
```

### 4. Verify Node Types Changed

```bash
grep '"type": "your_new_node"' tree-sitter-steps/src/node-types.json
```

### 5. Update the Highlight Query

Add rules for the new nodes in `highlights_minimal.scm`

---

## Cache Issues

If changes don't seem to take effect:

```bash
# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null

# Clear pip cache
./venv/bin/pip cache purge

# Reinstall package
./venv/bin/pip install -e tree-sitter-steps/ --force-reinstall --no-cache-dir
```

---

## Getting More Information

### View the Parse Tree

```python
from tree_sitter import Parser
import tree_sitter_steps

parser = Parser()
parser.set_language(tree_sitter_steps.get_language())

code = b'step: my_step\ndo:\n    display "hello"'
tree = parser.parse(code)

print(tree.root_node.sexp())
```

This shows you exactly what nodes the parser creates.

---

### Enable Textual Debug Mode

In your IDE code, add:

```python
from textual import log

log("Language registered:", self._steps_language_registered)
log("Detected language:", self.detect_language(path))
```

Then run with:
```bash
textual console
# In another terminal:
./venv/bin/python3 -m steps_ide.main
```

---

## Still Stuck?

1. Check `tree-sitter-steps/src/node-types.json` for available nodes
2. Look at working tree-sitter queries for other languages
3. Review the tree-sitter documentation: https://tree-sitter.github.io/
4. Check if the grammar correctly parses your test code (use parse tree viewer)
5. Simplify the query to the absolute minimum and build up from there

