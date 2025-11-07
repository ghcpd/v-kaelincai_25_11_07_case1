#!/usr/bin/env bash
set -e
echo "Setting up venv and installing requirements..."
python -m venv .venv; .venv/Scripts/activate; pip install -r requirements.txt
echo "Running Project A tests..."
python -u tests/test_pre_change.py
