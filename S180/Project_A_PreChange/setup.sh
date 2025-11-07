#!/bin/bash

# Setup script for Project A - Pre-Change
echo "Setting up Project A - Legacy API Integration"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
mkdir -p logs results data

echo "Setup complete for Project A"