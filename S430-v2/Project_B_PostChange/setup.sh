#!/usr/bin/env bash
python -m venv .venv
source .venv/bin/activate || source .venv/scripts/activate || true
pip install -r requirements.txt
