#!/usr/bin/env bash
python -m venv .venv
source .venv/bin/activate || source .venv/scripts/activate || true
pip install -r Project_A_PreChange/requirements.txt
pip install -r Project_B_PostChange/requirements.txt
