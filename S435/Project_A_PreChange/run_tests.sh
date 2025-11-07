#!/usr/bin/env bash
set -e
ROOT=$(pwd)
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python tests/test_pre_change.py
