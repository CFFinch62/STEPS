# Steps Language — Improvement Roadmap

A living checklist of proposed improvements to the Steps programming language, IDE, documentation, and ecosystem. Organized by category and priority. Items are independent unless noted.

**Last Updated**: June 2026
**Context**: Steps is an educational programming language designed for teaching CS fundamentals, with particular strength for neurodivergent learners due to its explicit, no-ambiguity design.

---

## Completed Work

### [x] Proposal 1: STEPS 2.0 Architecture (commit 308b059)
- [x] Inline `floors:` declarations in `.building` files
- [x] Removed all `.floor` files from project structure
- [x] Updated interpreter core (parser, loader, ast_nodes, errors)
- [x] Updated IDE, documentation, and marketing website

### [x] Proposal 2: IDE Intellisense (commit a8f7235)
- [x] CompletionEngine with 5 trigger categories
- [x] CompletionPopup with keyboard navigation
- [x] Automatic and Manual (Ctrl+Space) modes
- [x] Project step name scanning
- [x] Settings integration and comprehensive documentation

---

## Proposal 3: Smarter Error Messages

**Goal**: Make every error message a teaching moment. Catch common beginner mistakes and suggest exactly how to fix them before the student gets frustrated.

**Priority**: 🔴 High — this is the #1 way to reduce learner frustration

### Syntax Error Improvements
- [ ] Detect `=` used instead of `equals` or `to` — suggest the Steps equivalent
- [ ] Detect `==` or `!=` used instead of `is equal to` / `is not equal to`
- [ ] Detect `else` used instead of `otherwise` — suggest the correct keyword
- [ ] Detect `print` used instead of `display` — suggest the correct keyword
- [ ] Detect `while` used without `repeat` — suggest `repeat while`
- [ ] Detect `for` used without `repeat` — suggest `repeat for each`
- [ ] Detect `def` or `function` used instead of `step:` — suggest the correct structure
- [ ] Detect missing `to` in `set x 5` — suggest `set x to 5`
- [ ] Detect missing `is` in `if x equal to 5` — suggest `if x is equal to`

### Runtime Error Improvements
- [ ] When a `fixed` variable is reassigned, show where it was declared and explain what `fixed` means
- [ ] When a step is called with wrong argument count, show expected vs. actual and name the parameters
- [ ] When a type mismatch occurs in comparison, show both types and suggest a conversion
- [ ] When `as number` fails on text, show the actual text content that couldn't convert
- [ ] When a variable is used before being set, suggest adding it to the `declare:` section

### IDE Integration
- [ ] "Explain This Error" button in the terminal that expands into a plain-English walkthrough
- [ ] Clickable file:line references in error output that jump to the source location
- [ ] Squiggly underlines in the editor for errors detected during `check` (F6)

---

## Proposal 4: IDE Quality-of-Life

**Goal**: Bring the IDE closer to VS Code ergonomics while keeping it beginner-friendly.

**Priority**: 🟠 High-Medium — these make daily use much more pleasant

### Navigation
- [ ] **Go-to-Definition**: Ctrl+click on `call step_name` opens that `.step` file
- [ ] **Go-to-Definition**: Ctrl+click on a floor name opens the building file at that floor's section
- [ ] **Find All References**: Right-click a step name → find everywhere it's called
- [ ] **Outline/Symbol Panel**: Sidebar listing all steps, risers, and floors in the project with click-to-jump

### Editing
- [ ] **Inline Parameter Hints**: After typing `call my_step with`, show ghost text of expected parameter names
- [ ] **Declaration Validation**: Warn if a `fixed` variable is assigned to after declaration
- [ ] **Missing Section Warnings**: Flag `.step` files missing `belongs to:`, `expects:`, or `returns:` lines
- [ ] **Unused Variable Warning**: Highlight variables in `declare:` that are never used
- [ ] **Duplicate Step Name Detection**: Warn if two `.step` files have the same step name

### Visual
- [ ] **Breadcrumb Bar**: Show `building > floor > step` path at the top of the editor
- [ ] **Minimap**: Small code overview on the right side of the editor
- [ ] **Matching Keyword Highlighting**: When cursor is on `if`, highlight the matching `otherwise` blocks

---

## Proposal 5: Accessibility & Neurodivergent-Friendly Features

**Goal**: Leverage Steps' explicit design to create the most accessible beginner programming experience possible.

**Priority**: 🔴 High — this is the core differentiator

### Visual Execution Mode
- [ ] **Step-Through Visualization**: Highlight the currently executing line in real-time (not just debugger — a "slow motion run" mode)
- [ ] **Variable Value Overlay**: Show current variable values as inline annotations next to the code while running
- [ ] **Execution Speed Slider**: Let the student control how fast the visualization runs (from very slow to full speed)

### Cognitive Load Reduction
- [ ] **Template Enforcement**: The IDE validates that every `.step` file strictly follows the structure template, flagging deviations immediately — no guessing "did I format this right?"
- [ ] **Consistent Indentation Enforcement**: Auto-correct indentation on paste, never let the student have a file with mixed indentation
- [ ] **Line Length Guideline**: Soft visual guide at a reasonable line length to prevent overwhelming horizontal scrolling

### Sensory Accommodations
- [ ] **High-Contrast Theme**: Add a dedicated WCAG AAA-compliant high-contrast theme
- [ ] **Dyslexia-Friendly Font Option**: Add OpenDyslexic or similar font to the font picker
- [ ] **Reduced Motion Mode**: Settings toggle that disables all animations (popup fades, cursor blink, etc.)
- [ ] **Customizable Syntax Colors**: Per-token-type color picker in Settings for full personalization

### Structured Feedback
- [ ] **Success Confirmations**: When a program runs without errors, show a clear visual success indicator (not just silent completion)
- [ ] **Progress Badges**: Track milestones (first program, first loop, first step call) and show them in the status bar
- [ ] **Error Count Trend**: Show "3 errors → 1 error → 0 errors!" to reinforce progress

---

## Proposal 6: Language Features

**Goal**: Add commonly-requested language features that maintain the explicit, readable philosophy.

**Priority**: 🟡 Medium — these extend capability without changing the core

### Syntax Additions
- [ ] **String Interpolation**: `display "Hello, {name}! You are {age} years old."` instead of concatenation
- [ ] **Range Loops**: `repeat from 1 to 10` as a more intuitive counted loop alternative
- [ ] **`repeat until`**: `repeat until score is greater than 100` — the inverse of `repeat while`
- [ ] **Multi-line Text**: Triple-quote syntax `"""multi\nline"""` for long text values
- [ ] **`nothing` checks**: `if value is nothing` / `if value is not nothing`

### Standard Library Expansion
- [ ] **Math riser library**: `round`, `floor`, `ceiling`, `absolute`, `minimum`, `maximum`, `random number from X to Y`
- [ ] **Text riser library**: `uppercase`, `lowercase`, `trim`, `replace`, `character at position`
- [ ] **List riser library**: `sort`, `reverse`, `find position of`, `join with`
- [ ] **File I/O risers**: `read file`, `write file` — simple text file operations for persistence projects

### Structural
- [ ] **Import system**: `use risers from "math_helpers"` — share risers across projects
- [ ] **Module-level risers**: Risers that belong to a floor rather than being nested inside a step
- [ ] **Default parameter values**: `expects: name as text, greeting as text default "Hello"` 

---

## Proposal 7: Learning Materials & Examples

**Goal**: Create a comprehensive learning path that takes a student from zero to building real projects.

**Priority**: 🟠 High-Medium — great language + poor materials = unused language

### New Example Projects
- [ ] **Quiz Game**: Multiple choice questions, score tracking, feedback messages
- [ ] **To-Do List**: Add, remove, display items — teaches list operations
- [ ] **Gradebook Calculator**: Student grades, averages, letter grade conversion
- [ ] **Number Guessing Game** (already exists — verify it works with 2.0)
- [ ] **Mad Libs Generator**: Text input, string building, display formatted output
- [ ] **Temperature Converter**: Unit conversion, user menu, repeat until quit

### Interactive IDE Tutorials
- [ ] **Tutorial System**: Built-in lesson panel in the IDE with step-by-step instructions
- [ ] **Lesson 1**: "Your First Building" — create a building, add a floor, write a step
- [ ] **Lesson 2**: "Variables and Input" — declare, set, display, input
- [ ] **Lesson 3**: "Making Decisions" — if/otherwise with comparison operators
- [ ] **Lesson 4**: "Loops" — repeat times, repeat while, repeat for each
- [ ] **Lesson 5**: "Organizing with Steps" — multi-step programs, call, parameters

### Documentation
- [ ] **"Steps → Python" Migration Guide**: When students are ready, show how each Steps concept maps to Python
- [ ] **Teacher's Guide**: How to use Steps in a classroom, suggested lesson plans, common student mistakes
- [ ] **Video Walkthroughs**: Screen recordings of building each example project (could link from the marketing site)

---

## Proposal 8: Quality & Stability

**Goal**: Harden the interpreter and IDE for classroom use where reliability is critical.

**Priority**: 🟡 Medium — important but less visible than features

### Testing
- [ ] **IDE unit tests**: Test CompletionEngine trigger logic with pytest (no GUI needed)
- [ ] **Example project regression suite**: Automatically run all example projects and verify expected output
- [ ] **Parser edge case tests**: Empty files, files with only comments, deeply nested structures
- [ ] **Error message tests**: Verify every error code produces the expected message text

### Bug Fixes (Known)
- [ ] **E207 parse error**: `price_calculator_advanced` has a persistent parse issue (pre-existing)
- [ ] **Example project bugs**: Audit all example projects for type declaration errors (like the `fixed` bug found in `get_number_input.step`)

### Performance
- [ ] **Large project handling**: Test and optimize for projects with 50+ step files
- [ ] **IDE startup time**: Profile and optimize if noticeable delay on launch
- [ ] **Completion engine responsiveness**: Ensure popup never causes editor lag

---

## Proposal 9: Distribution & Packaging

**Goal**: Make Steps trivially easy to install on any platform.

**Priority**: 🟢 Low (for now) — focus on the product first, then distribution

- [ ] **PyPI package**: Publish `steps-lang` to PyPI so `pip install steps-lang` works
- [ ] **Standalone installer (Linux)**: AppImage or .deb package with all dependencies bundled
- [ ] **Standalone installer (Windows)**: MSI or .exe installer with Python bundled
- [ ] **Standalone installer (macOS)**: .dmg with bundled Python runtime
- [ ] **Docker image**: For classroom lab environments
- [ ] **Web playground**: A browser-based Steps interpreter (could use Pyodide) for try-before-install

---

## How to Use This Document

1. **Pick a proposal** to work on based on current priorities
2. **Check off items** as they are completed
3. **Add new proposals** at the bottom as ideas emerge
4. **Reference commits** next to completed sections for traceability
5. **Each proposal can span multiple sessions** — no pressure to finish in one sitting

---

*This document lives in the repo and should be updated as work progresses.*
