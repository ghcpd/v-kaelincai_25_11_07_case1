#!/bin/bash
set -e

ROOT=$(pwd)

# Run Project A tests
cd Project_A_PreChange
./setup.sh || true
./run_tests.sh || echo "Project A tests failed"
cd $ROOT

# Run Project B tests
cd Project_B_PostChange
./setup.sh || true
./run_tests.sh || echo "Project B tests failed"
cd $ROOT

# Aggregate results
python scripts/generate_metrics.py
python scripts/generate_report.py

echo "run_all complete"