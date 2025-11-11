#!/bin/bash
# Master script to run both Project A and Project B tests and generate comparison report

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "API Migration Evaluation - Full Test Suite"
echo "=========================================="
echo ""

# Create results directory
mkdir -p results

# Step 1: Run Project A (Pre-Change) tests
echo "=========================================="
echo "Step 1: Running Project A - Pre-Change Tests"
echo "=========================================="
cd Project_A_PreChange
bash run_tests.sh
cd ..

# Step 2: Run Project B (Post-Change) tests
echo ""
echo "=========================================="
echo "Step 2: Running Project B - Post-Change Tests"
echo "=========================================="
cd Project_B_PostChange
bash run_tests.sh
cd ..

# Step 3: Generate comparison report
echo ""
echo "=========================================="
echo "Step 3: Generating Comparison Report"
echo "=========================================="

# Copy results to shared results directory
cp Project_A_PreChange/results/results_pre.json results/ 2>/dev/null || true
cp Project_B_PostChange/results/results_post.json results/ 2>/dev/null || true

# Run comparison script
python generate_comparison_report.py

echo ""
echo "=========================================="
echo "Evaluation Complete!"
echo "=========================================="
echo "Results available in:"
echo "  - results/results_pre.json"
echo "  - results/results_post.json"
echo "  - results/aggregated_metrics.json"
echo "  - compare_report.md"
echo "=========================================="

