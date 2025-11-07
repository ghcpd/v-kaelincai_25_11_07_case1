#!/bin/bash
set -e

# Setup and run Project A
pushd Project_A_PreChange
if [ ! -d "venv" ]; then
  ./setup.sh
fi
. venv/bin/activate
pytest -q || true
popd

# Setup and run Project B
pushd Project_B_PostChange
if [ ! -d "venv" ]; then
  ./setup.sh
fi
. venv/bin/activate
pytest -q || true
popd

# Collect results
mkdir -p results
cp Project_A_PreChange/results/results_pre.json results/ || true
cp Project_B_PostChange/results/results_post.json results/ || true

# Aggregate
python aggregate_results.py

# Done
echo 'All done. See compare_report.md and results/aggregated_metrics.json'
