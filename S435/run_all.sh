#!/usr/bin/env bash
set -e
ROOT=$(pwd)

# Run Project A
pushd Project_A_PreChange
./run_tests.sh
popd

# Copy results
cp Project_A_PreChange/results/results_pre.json results/results_pre.json || true

# Run Project B
pushd Project_B_PostChange
./run_tests.sh
popd

cp Project_B_PostChange/results/results_post.json results/results_post.json || true

# Generate comparison report
python generate_report.py
