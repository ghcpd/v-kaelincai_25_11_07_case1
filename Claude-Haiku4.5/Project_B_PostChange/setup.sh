#!/bin/bash
# Setup script for Project B (Post-Change)

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

echo "=== Setting up Project B (Post-Change v2) ==="

# Create virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r "$PROJECT_DIR/requirements.txt"

echo "✓ Project B setup complete"
echo "To activate environment: source $VENV_DIR/bin/activate"
