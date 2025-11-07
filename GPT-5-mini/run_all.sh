#!/usr/bin/env bash
set -e
echo "Running Project A (pre-change) tests..."
pushd Project_A_PreChange > /dev/null
bash run_tests.sh
popd > /dev/null

echo "Running Project B (post-change) tests..."
pushd Project_B_PostChange > /dev/null
bash run_tests.sh
popd > /dev/null

echo "Aggregating results and generating report..."
python compare_results.py
echo "Done. See compare_report.md and results/"
