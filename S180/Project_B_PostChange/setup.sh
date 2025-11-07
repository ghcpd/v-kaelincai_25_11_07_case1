#!/bin/bash

# Setup Project B
if [ ! -d "venv" ]; then
    python -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
mkdir -p logs results data

echo "Project B setup complete"