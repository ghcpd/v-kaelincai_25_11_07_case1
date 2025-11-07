#!/usr/bin/env bash
set -e
ROOT=$(dirname "$0")
cd "$ROOT"
if [ ! -d .venv ]; then
  python -m venv .venv
fi
source .venv/bin/activate || source .venv/scripts/activate || true
pip install -r requirements.txt
mkdir -p results logs
pytest -q tests/test_post_change.py
