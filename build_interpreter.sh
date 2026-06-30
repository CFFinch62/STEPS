#!/bin/bash
set -e

# Define project root
PROJECT_ROOT=$(pwd)
DIST_DIR="$PROJECT_ROOT/dist"
BUILD_DIR="$PROJECT_ROOT/build"

echo "🧹 Cleaning previous interpreter build..."
rm -rf "$DIST_DIR/steps" "$BUILD_DIR/steps" "$PROJECT_ROOT/steps.spec"

echo "📦 Installing build dependencies..."
pip install pyinstaller

echo "🔨 Building Steps Interpreter..."
# Build the standalone interpreter CLI as a single self-contained binary.
#
# --onefile:        Pack everything into one file, just like a compiled Go
#                   binary.  Copy it anywhere and it just works.
# --name:           Name of the resulting executable
# --console:        Keep terminal I/O (this is a CLI tool, not a GUI app)
# --paths:          Tell PyInstaller where to find the src packages
# --add-data:       Bundle the stdlib .step and .floor data files.
#                   These are plain text files (not Python), so PyInstaller
#                   won't find them automatically.  The loader resolves them
#                   at runtime via  Path(__file__).parent / "stdlib", so they
#                   must land at  steps/stdlib  inside the bundle.
# --hidden-import:  The "repl" subcommand imports steps_repl inside a function,
#                   so static analysis may miss it – force it to be included.
# --clean:          Clear PyInstaller's cache before building
# --noconfirm:      Overwrite existing output without prompting
pyinstaller --name="steps" \
            --onefile \
            --console \
            --clean \
            --noconfirm \
            --paths "src" \
            --add-data "src/steps/stdlib:steps/stdlib" \
            --hidden-import "steps_repl" \
            --hidden-import "steps_repl.repl" \
            --hidden-import "steps_repl.commands" \
            --hidden-import "steps_repl.environment" \
            --hidden-import "serial" \
            src/steps/main.py

echo ""
echo "✅ Build complete!"
echo "🚀 Single-file executable: dist/steps"
echo ""
echo "── Deploy to MyCode ──────────────────────────────────────────────────"
echo "   cp dist/steps /path/to/MyCode/steps"
echo ""
echo "── Use from MyCode terminal ──────────────────────────────────────────"
echo "  Run a project:   ./steps run   <project_directory>"
echo "  Validate only:   ./steps check <project_directory>"
echo "  Run a step file: ./steps run-step <file.step>"
echo "  Start REPL:      ./steps repl"
echo "─────────────────────────────────────────────────────────────────────"

