#!/bin/bash
set -e

# Use venv if exists, else create
if [ ! -d "venv" ]; then
  ./setup.sh
fi
. venv/bin/activate

# Run pytest
pytest -q
