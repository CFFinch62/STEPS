#!/bin/bash
# Setup script for Steps programming language
# Creates virtual environment and installs dependencies

set -e  # Exit on error

VENV_DIR="venv"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔧 Steps Setup Script"
echo "===================="

# Check if venv exists
if [ -d "$VENV_DIR" ]; then
    echo "✓ Virtual environment already exists at $VENV_DIR"
else
    echo "📦 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install the Steps package in editable mode
echo "📥 Installing Steps package..."
pip install -e .

# Install IDE dependencies
echo "📥 Installing IDE dependencies (PyQt6, PyQt6-WebEngine)..."
pip install PyQt6 PyQt6-WebEngine

# Install serial port support
echo "📥 Installing serial port support (pyserial)..."
pip install pyserial

# Install development dependencies (optional)
read -p "Install development dependencies (pytest, mypy, black, isort)? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📥 Installing development dependencies..."
    pip install pytest pytest-cov mypy black isort
    echo "✓ Development dependencies installed"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the virtual environment manually, run:"
echo "  source $VENV_DIR/bin/activate"
echo ""
echo "To run the Steps IDE, use:"
echo "  ./run.sh"

