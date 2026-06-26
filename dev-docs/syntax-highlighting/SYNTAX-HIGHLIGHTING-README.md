# Steps Syntax Highlighting Documentation

## Overview

This directory contains complete documentation for the Steps language syntax highlighting system. The system uses **tree-sitter** for fast, accurate, incremental parsing and highlighting.

## Documentation Files

### 📘 [SYNTAX-HIGHLIGHTING.md](./SYNTAX-HIGHLIGHTING.md)
**Start here!** Comprehensive guide covering:
- System architecture and data flow
- How tree-sitter works with Textual
- Current status and what's implemented
- How to expand highlighting safely
- Common issues and solutions
- Reference for highlight styles
- Testing procedures

**Read this first** to understand the system.

---

### 📋 [SYNTAX-HIGHLIGHTING-TODO.md](./SYNTAX-HIGHLIGHTING-TODO.md)
**Task list** for expanding the highlighting. Contains:
- 10 specific tasks to enhance highlighting
- Step-by-step instructions for each task
- Example code to test each feature
- Success criteria
- Testing protocol

**Use this** when you're ready to add more highlighting features.

---

### 🔧 [SYNTAX-HIGHLIGHTING-TROUBLESHOOTING.md](./SYNTAX-HIGHLIGHTING-TROUBLESHOOTING.md)
**Problem-solving guide** with:
- Quick diagnostic tests
- Common error messages and solutions
- Debugging workflow
- Cache clearing procedures
- How to view parse trees
- Debug mode instructions

**Refer to this** when something goes wrong.

---

## Quick Start for New Developers

### Understanding the System (15 minutes)
1. Read the "Overview" and "Architecture" sections of `SYNTAX-HIGHLIGHTING.md`
2. Look at the current working query: `tree-sitter-steps/queries/highlights_minimal.scm`
3. Run the test: `./venv/bin/python3 test_syntax_highlighting.py`

### Making Your First Enhancement (30 minutes)
1. Choose Task 1 from `SYNTAX-HIGHLIGHTING-TODO.md` (Add String Highlighting)
2. Follow the step-by-step instructions
3. Test your changes
4. If it works, commit and move to Task 2

### When Things Go Wrong (as needed)
1. Run the diagnostic tests in `SYNTAX-HIGHLIGHTING-TROUBLESHOOTING.md`
2. Find your error message in the "Common Error Messages" section
3. Follow the solution steps

---

## File Locations

### Source Files
- **Grammar**: `tree-sitter-steps/grammar.js`
- **Highlight Query**: `tree-sitter-steps/queries/highlights_minimal.scm`
- **Python Bindings**: `tree-sitter-steps/bindings/python/`
- **IDE Integration**: `src/steps_ide/editor/register_steps_language.py`
- **Editor Widget**: `src/steps_ide/editor/steps_editor.py`

### Generated Files (Don't Edit)
- **Parser**: `tree-sitter-steps/src/parser.c`
- **Node Types**: `tree-sitter-steps/src/node-types.json`

### Test Files
- **Main Test**: `test_syntax_highlighting.py`
- **Minimal Test**: `test_minimal_query.py`

### Reference
- **Language Spec**: `docs/LANGUAGE-REFERENCE.md`

---

## Common Workflows

### Adding a New Keyword to Highlight

1. **Verify it exists in the grammar**:
   ```bash
   grep '"your_keyword"' tree-sitter-steps/src/node-types.json
   ```

2. **Add to highlight query**:
   ```scheme
   "your_keyword" @keyword
   ```

3. **Test**:
   ```bash
   ./venv/bin/python3 test_syntax_highlighting.py
   ```

4. **Visual test**: Open a `.step` file in the IDE

---

### Adding a New Node Type to Highlight

1. **Check if it's a named node**:
   ```bash
   grep '"type": "your_node"' tree-sitter-steps/src/node-types.json
   ```

2. **Add to highlight query**:
   ```scheme
   (your_node) @style.name
   ```

3. **Test** (same as above)

---

### Modifying the Grammar

1. **Edit**: `tree-sitter-steps/grammar.js`

2. **Regenerate**:
   ```bash
   cd tree-sitter-steps && npm run generate
   ```

3. **Rebuild Python package**:
   ```bash
   cd ..
   ./venv/bin/pip uninstall -y tree-sitter-steps
   ./venv/bin/pip install -e tree-sitter-steps/
   ```

4. **Update highlight query** to use new nodes

5. **Test everything**

---

## Current Status

### ✅ Working
- Tree-sitter grammar for Steps language
- Python bindings installed and functional
- IDE integration complete
- Basic highlighting (keywords, comments, identifiers)
- Automated testing

### ⚠️ In Progress
- Comprehensive highlighting (strings, numbers, operators, etc.)
- See `SYNTAX-HIGHLIGHTING-TODO.md` for specific tasks

### 🔮 Future
- Semantic highlighting
- Error highlighting
- Custom color themes
- Bracket matching
- Code folding

---

## Testing

### Automated Tests
```bash
# Full test suite
./venv/bin/python3 test_syntax_highlighting.py

# Test individual query rules
./venv/bin/python3 test_minimal_query.py
```

### Manual Testing
1. Open the Steps IDE
2. Load a `.step` or `.building` file
3. Verify syntax highlighting appears
4. Check that all keywords are colored correctly

### Test Files
Create test files in `examples/` with various language features to verify highlighting.

---

## Best Practices

1. **Work incrementally**: Add one feature, test, commit
2. **Test before committing**: Always run `test_syntax_highlighting.py`
3. **Keep backups**: Copy `highlights_minimal.scm` before major changes
4. **Document changes**: Update this README if you add new features
5. **Check node types**: Always verify nodes exist before adding to query
6. **Use standard styles**: Stick to common highlight names for compatibility

---

## Getting Help

### Resources
- Tree-sitter documentation: https://tree-sitter.github.io/
- Tree-sitter query syntax: https://tree-sitter.github.io/tree-sitter/syntax-highlighting
- Textual documentation: https://textual.textualize.io/
- Example queries: Look at tree-sitter-python, tree-sitter-javascript

### Debugging
1. Start with `SYNTAX-HIGHLIGHTING-TROUBLESHOOTING.md`
2. Run diagnostic tests
3. Check error messages against known issues
4. Simplify to minimal working example
5. Build back up incrementally

---

## Contributing

When you enhance the highlighting:

1. Follow the tasks in `SYNTAX-HIGHLIGHTING-TODO.md`
2. Test thoroughly
3. Update documentation if you discover new patterns
4. Add your test cases to `test_syntax_highlighting.py`
5. Document any issues you encountered and how you solved them

---

## Version History

- **v1.0** (Current): Basic highlighting working with minimal query
  - Keywords, comments, identifiers
  - Tree-sitter integration complete
  - IDE integration functional

- **v2.0** (Planned): Comprehensive highlighting
  - All literals (strings, numbers, booleans)
  - All operators
  - Type annotations
  - Function calls and definitions

---

## Contact

For questions about the syntax highlighting system, refer to these docs first. If you're still stuck, check the troubleshooting guide.

