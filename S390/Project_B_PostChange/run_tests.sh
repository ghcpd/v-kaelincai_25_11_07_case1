#!/bin/bash
set -e

if [ ! -d "venv" ]; then
  ./setup.sh
fi
. venv/bin/activate

pytest -q
