#!/usr/bin/env bash
set -e
ROOT=$(pwd)
# Run Project A
(cd Project_A_PreChange && bash run_tests.sh)
# Run Project B
(cd Project_B_PostChange && bash run_tests.sh)
# Copy results
mkdir -p results
cp Project_A_PreChange/results/results_pre.json results/results_pre.json || true
cp Project_B_PostChange/results/results_post.json results/results_post.json || true
# Generate aggregated metrics via compare script
python scripts/compare_results.py

echo "All done: results in results/ and compare_report.md"
