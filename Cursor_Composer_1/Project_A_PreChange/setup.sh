#!/bin/bash
# Setup script for Project A - Pre-Change

echo "Setting up Project A - Pre-Change environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
mkdir -p logs
mkdir -p results
mkdir -p data

echo "Setup complete!"
echo "To activate the environment, run: source venv/bin/activate"

