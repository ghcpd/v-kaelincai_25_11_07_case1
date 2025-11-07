#!/usr/bin/env bash
set -e
ROOT=$(dirname "$0")
cd "$ROOT"
# Create venv and install
if [ ! -d .venv ]; then
  python -m venv .venv
fi
source .venv/bin/activate || source .venv/scripts/activate || true
pip install -r requirements.txt
# Ensure results dir exists
mkdir -p results logs
# Run pytest
pytest -q tests/test_pre_change.py
