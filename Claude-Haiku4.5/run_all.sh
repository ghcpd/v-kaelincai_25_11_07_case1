#!/bin/bash
# Master test execution script - runs both projects and generates comparison report

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="$REPO_ROOT/results"
LOGS_DIR="$REPO_ROOT/logs"

mkdir -p "$RESULTS_DIR" "$LOGS_DIR"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  API Migration Evaluation - Full Test Suite                     ║"
echo "║  Pre-Change (v1) vs Post-Change (v2)                           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Track overall status
OVERALL_STATUS=0

# ============================================================================
# Phase 1: Run Project A (Pre-Change v1)
# ============================================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Phase 1: Running Project A (Pre-Change - v1 Integration)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if bash "$REPO_ROOT/Project_A_PreChange/run_tests.sh" 2>&1 | tee "$LOGS_DIR/project_a_run.log"; then
    echo "✓ Project A tests completed"
else
    echo "✗ Project A tests failed"
    OVERALL_STATUS=1
fi

# ============================================================================
# Phase 2: Run Project B (Post-Change v2)
# ============================================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Phase 2: Running Project B (Post-Change - v2 Integration)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if bash "$REPO_ROOT/Project_B_PostChange/run_tests.sh" 2>&1 | tee "$LOGS_DIR/project_b_run.log"; then
    echo "✓ Project B tests completed"
else
    echo "✗ Project B tests failed"
    OVERALL_STATUS=1
fi

# ============================================================================
# Phase 3: Copy results to shared results directory
# ============================================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Phase 3: Aggregating Results"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -f "$REPO_ROOT/Project_A_PreChange/results/results_pre.json" ]; then
    cp "$REPO_ROOT/Project_A_PreChange/results/results_pre.json" "$RESULTS_DIR/"
    echo "✓ Copied Project A results"
fi

if [ -f "$REPO_ROOT/Project_B_PostChange/results/results_post.json" ]; then
    cp "$REPO_ROOT/Project_B_PostChange/results/results_post.json" "$RESULTS_DIR/"
    echo "✓ Copied Project B results"
fi

# ============================================================================
# Phase 4: Generate comparison report
# ============================================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Phase 4: Generating Comparison Report"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 "$REPO_ROOT/generate_comparison_report.py" "$RESULTS_DIR"

# ============================================================================
# Summary
# ============================================================================
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    EXECUTION COMPLETE                           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Results Location:       $RESULTS_DIR/"
echo "Logs Location:          $LOGS_DIR/"
echo "Comparison Report:      $RESULTS_DIR/compare_report.md"
echo ""
echo "Key Output Files:"
echo "  - results/results_pre.json       (Project A results)"
echo "  - results/results_post.json      (Project B results)"
echo "  - results/aggregated_metrics.json (Combined metrics)"
echo "  - results/compare_report.md      (Comparison report)"
echo ""

if [ $OVERALL_STATUS -eq 0 ]; then
    echo "✓ All tests executed successfully"
else
    echo "⚠ Some tests encountered issues - see logs above"
fi

echo ""
exit $OVERALL_STATUS
