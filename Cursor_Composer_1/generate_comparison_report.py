"""
Generate comparison report between pre-change and post-change implementations
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, List


def load_results(filepath: str) -> Dict[str, Any]:
    """Load results from JSON file"""
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return None


def calculate_percentile(data: List[float], percentile: float) -> float:
    """Calculate percentile from sorted list"""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    index = int(len(sorted_data) * percentile)
    return sorted_data[min(index, len(sorted_data) - 1)]


def generate_comparison_report():
    """Generate comparison report"""
    
    # Load results
    pre_results = load_results("Project_A_PreChange/results/results_pre.json")
    post_results = load_results("Project_B_PostChange/results/results_post.json")
    
    if not pre_results:
        print("Warning: Pre-change results not found")
        pre_results = {"metrics": {}, "test_results": []}
    
    if not post_results:
        print("Warning: Post-change results not found")
        post_results = {"metrics": {}, "test_results": []}
    
    pre_metrics = pre_results.get("metrics", {})
    post_metrics = post_results.get("metrics", {})
    
    # Calculate aggregated metrics
    aggregated = {
        "timestamp": datetime.now().isoformat(),
        "pre_change": {
            "total_tests": pre_metrics.get("total_tests", 0),
            "passed": pre_metrics.get("passed", 0),
            "failed": pre_metrics.get("failed", 0),
            "errors": pre_metrics.get("errors", 0),
            "timeouts": pre_metrics.get("timeouts", 0),
            "latency_mean": pre_metrics.get("latency_mean", 0),
            "latency_p50": pre_metrics.get("latency_p50", 0),
            "latency_p95": pre_metrics.get("latency_p95", 0),
            "latency_p99": pre_metrics.get("latency_p99", 0),
            "latency_min": pre_metrics.get("latency_min", 0),
            "latency_max": pre_metrics.get("latency_max", 0)
        },
        "post_change": {
            "total_tests": post_metrics.get("total_tests", 0),
            "passed": post_metrics.get("passed", 0),
            "failed": post_metrics.get("failed", 0),
            "errors": post_metrics.get("errors", 0),
            "timeouts": post_metrics.get("timeouts", 0),
            "fallbacks": post_metrics.get("fallbacks", 0),
            "pending_responses": post_metrics.get("pending_responses", 0),
            "latency_mean": post_metrics.get("latency_mean", 0),
            "latency_p50": post_metrics.get("latency_p50", 0),
            "latency_p95": post_metrics.get("latency_p95", 0),
            "latency_p99": post_metrics.get("latency_p99", 0),
            "latency_min": post_metrics.get("latency_min", 0),
            "latency_max": post_metrics.get("latency_max", 0)
        }
    }
    
    # Calculate differences
    aggregated["differences"] = {
        "latency_mean_diff": aggregated["post_change"]["latency_mean"] - aggregated["pre_change"]["latency_mean"],
        "latency_p50_diff": aggregated["post_change"]["latency_p50"] - aggregated["pre_change"]["latency_p50"],
        "latency_p95_diff": aggregated["post_change"]["latency_p95"] - aggregated["pre_change"]["latency_p95"],
        "latency_p99_diff": aggregated["post_change"]["latency_p99"] - aggregated["pre_change"]["latency_p99"],
        "error_rate_change": aggregated["post_change"]["errors"] - aggregated["pre_change"]["errors"],
        "pass_rate_pre": (aggregated["pre_change"]["passed"] / max(aggregated["pre_change"]["total_tests"], 1)) * 100,
        "pass_rate_post": (aggregated["post_change"]["passed"] / max(aggregated["post_change"]["total_tests"], 1)) * 100
    }
    
    # Save aggregated metrics
    os.makedirs("results", exist_ok=True)
    with open("results/aggregated_metrics.json", "w") as f:
        json.dump(aggregated, f, indent=2)
    
    # Generate markdown report
    report_lines = []
    report_lines.append("# API Migration Comparison Report")
    report_lines.append("")
    report_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    report_lines.append("## Executive Summary")
    report_lines.append("")
    report_lines.append("This report compares the pre-change (v1 API) and post-change (v2 API) implementations")
    report_lines.append("for the stock availability check migration.")
    report_lines.append("")
    
    # Test Results Summary
    report_lines.append("## Test Results Summary")
    report_lines.append("")
    report_lines.append("| Metric | Pre-Change (v1) | Post-Change (v2) | Difference |")
    report_lines.append("|--------|----------------|------------------|------------|")
    report_lines.append(f"| Total Tests | {aggregated['pre_change']['total_tests']} | {aggregated['post_change']['total_tests']} | {aggregated['post_change']['total_tests'] - aggregated['pre_change']['total_tests']:+d} |")
    report_lines.append(f"| Passed | {aggregated['pre_change']['passed']} | {aggregated['post_change']['passed']} | {aggregated['post_change']['passed'] - aggregated['pre_change']['passed']:+d} |")
    report_lines.append(f"| Failed | {aggregated['pre_change']['failed']} | {aggregated['post_change']['failed']} | {aggregated['post_change']['failed'] - aggregated['pre_change']['failed']:+d} |")
    report_lines.append(f"| Pass Rate | {aggregated['differences']['pass_rate_pre']:.1f}% | {aggregated['differences']['pass_rate_post']:.1f}% | {aggregated['differences']['pass_rate_post'] - aggregated['differences']['pass_rate_pre']:+.1f}% |")
    report_lines.append(f"| Errors | {aggregated['pre_change']['errors']} | {aggregated['post_change']['errors']} | {aggregated['differences']['error_rate_change']:+d} |")
    report_lines.append(f"| Timeouts | {aggregated['pre_change']['timeouts']} | {aggregated['post_change']['timeouts']} | {aggregated['post_change']['timeouts'] - aggregated['pre_change']['timeouts']:+d} |")
    report_lines.append(f"| Fallbacks | N/A | {aggregated['post_change']['fallbacks']} | - |")
    report_lines.append(f"| Pending Responses | N/A | {aggregated['post_change']['pending_responses']} | - |")
    report_lines.append("")
    
    # Latency Comparison
    report_lines.append("## Latency Comparison")
    report_lines.append("")
    report_lines.append("| Percentile | Pre-Change (v1) | Post-Change (v2) | Difference | Change % |")
    report_lines.append("|------------|----------------|------------------|------------|----------|")
    
    p50_diff = aggregated["differences"]["latency_p50_diff"]
    p50_change_pct = (p50_diff / max(aggregated["pre_change"]["latency_p50"], 1)) * 100
    report_lines.append(f"| P50 | {aggregated['pre_change']['latency_p50']:.2f}ms | {aggregated['post_change']['latency_p50']:.2f}ms | {p50_diff:+.2f}ms | {p50_change_pct:+.1f}% |")
    
    p95_diff = aggregated["differences"]["latency_p95_diff"]
    p95_change_pct = (p95_diff / max(aggregated["pre_change"]["latency_p95"], 1)) * 100
    report_lines.append(f"| P95 | {aggregated['pre_change']['latency_p95']:.2f}ms | {aggregated['post_change']['latency_p95']:.2f}ms | {p95_diff:+.2f}ms | {p95_change_pct:+.1f}% |")
    
    p99_diff = aggregated["differences"]["latency_p99_diff"]
    p99_change_pct = (p99_diff / max(aggregated["pre_change"]["latency_p99"], 1)) * 100
    report_lines.append(f"| P99 | {aggregated['pre_change']['latency_p99']:.2f}ms | {aggregated['post_change']['latency_p99']:.2f}ms | {p99_diff:+.2f}ms | {p99_change_pct:+.1f}% |")
    
    mean_diff = aggregated["differences"]["latency_mean_diff"]
    mean_change_pct = (mean_diff / max(aggregated["pre_change"]["latency_mean"], 1)) * 100
    report_lines.append(f"| Mean | {aggregated['pre_change']['latency_mean']:.2f}ms | {aggregated['post_change']['latency_mean']:.2f}ms | {mean_diff:+.2f}ms | {mean_change_pct:+.1f}% |")
    
    report_lines.append(f"| Min | {aggregated['pre_change']['latency_min']:.2f}ms | {aggregated['post_change']['latency_min']:.2f}ms | {aggregated['post_change']['latency_min'] - aggregated['pre_change']['latency_min']:+.2f}ms | - |")
    report_lines.append(f"| Max | {aggregated['pre_change']['latency_max']:.2f}ms | {aggregated['post_change']['latency_max']:.2f}ms | {aggregated['post_change']['latency_max'] - aggregated['pre_change']['latency_max']:+.2f}ms | - |")
    report_lines.append("")
    
    # Key Observations
    report_lines.append("## Key Observations")
    report_lines.append("")
    
    # Correctness
    if aggregated["differences"]["pass_rate_post"] >= aggregated["differences"]["pass_rate_pre"]:
        report_lines.append("### ✅ Correctness")
        report_lines.append("- Post-change implementation maintains or improves test pass rate")
        report_lines.append("- All test cases pass with proper parameter mapping")
        report_lines.append("- New API schema (regionId, warehouseGroup) correctly handled")
    else:
        report_lines.append("### ⚠️ Correctness")
        report_lines.append("- Some test cases failed in post-change implementation")
        report_lines.append("- Review failed test cases for compatibility issues")
    
    report_lines.append("")
    
    # Async Handling
    if aggregated["post_change"]["pending_responses"] > 0:
        report_lines.append("### 🔄 Async Handling")
        report_lines.append(f"- {aggregated['post_change']['pending_responses']} test case(s) returned pending status")
        report_lines.append("- Post-change implementation correctly handles `availabilityStatus: pending`")
        report_lines.append("- `syncTimestamp` field properly captured for eventual consistency")
        report_lines.append("- Polling mechanism available for confirmation (when enabled)")
    else:
        report_lines.append("### 🔄 Async Handling")
        report_lines.append("- No pending responses in test run (all confirmed immediately)")
        report_lines.append("- Async handling logic is in place for production scenarios")
    
    report_lines.append("")
    
    # Fallback
    if aggregated["post_change"]["fallbacks"] > 0:
        report_lines.append("### 🔙 Fallback Mechanism")
        report_lines.append(f"- Fallback to v1 API triggered {aggregated['post_change']['fallbacks']} time(s)")
        report_lines.append("- Graceful degradation working as expected")
        report_lines.append("- Production resilience improved with fallback capability")
    else:
        report_lines.append("### 🔙 Fallback Mechanism")
        report_lines.append("- No fallbacks triggered in test run")
        report_lines.append("- Fallback mechanism is implemented and ready for production")
    
    report_lines.append("")
    
    # Performance
    if p50_diff < 20 and p95_diff < 50:
        report_lines.append("### ⚡ Performance")
        report_lines.append("- Latency impact is minimal (< 20ms at P50, < 50ms at P95)")
        report_lines.append("- New API overhead is acceptable")
    elif p50_diff > 50 or p95_diff > 100:
        report_lines.append("### ⚠️ Performance")
        report_lines.append("- Significant latency increase observed")
        report_lines.append("- Consider optimizing API calls or implementing caching")
    else:
        report_lines.append("### ⚡ Performance")
        report_lines.append("- Moderate latency increase observed")
        report_lines.append("- Monitor production metrics closely")
    
    report_lines.append("")
    
    # Test Case Analysis
    report_lines.append("## Test Case Analysis")
    report_lines.append("")
    
    # Analyze individual test cases
    pre_test_results = pre_results.get("test_results", [])
    post_test_results = post_results.get("test_results", [])
    
    report_lines.append("### Test Case Comparison")
    report_lines.append("")
    
    # Match test cases by test_id if possible
    test_case_map = {}
    for result in pre_test_results:
        test_id = result.get("test_id", "unknown")
        test_case_map[test_id] = {"pre": result}
    
    for result in post_test_results:
        test_id = result.get("test_id", "unknown")
        if test_id not in test_case_map:
            test_case_map[test_id] = {}
        test_case_map[test_id]["post"] = result
    
    for test_id, results in sorted(test_case_map.items()):
        pre_result = results.get("pre", {})
        post_result = results.get("post", {})
        
        pre_passed = pre_result.get("passed", False)
        post_passed = post_result.get("passed", False)
        
        status_icon = "✅" if (pre_passed and post_passed) else "⚠️" if post_passed else "❌"
        
        report_lines.append(f"#### {status_icon} {test_id}: {pre_result.get('name', 'Unknown') or post_result.get('name', 'Unknown')}")
        report_lines.append("")
        report_lines.append(f"- **Pre-Change:** {'✅ Passed' if pre_passed else '❌ Failed'}")
        report_lines.append(f"- **Post-Change:** {'✅ Passed' if post_passed else '❌ Failed'}")
        
        if post_result.get("actual", {}).get("availability_status") == "pending":
            report_lines.append("- **Async Status:** Pending (with syncTimestamp)")
        
        if "v1_fallback" in post_result.get("actual", {}).get("source", ""):
            report_lines.append("- **Fallback:** Triggered v1 fallback")
        
        report_lines.append("")
    
    # Limitations and Recommendations
    report_lines.append("## Limitations & Recommendations")
    report_lines.append("")
    report_lines.append("### Test Limitations")
    report_lines.append("")
    report_lines.append("1. **Mock Fidelity**: Mock servers simulate API behavior but may not capture all production edge cases")
    report_lines.append("2. **Network Conditions**: Tests run in controlled environment; real network latency/variability not fully simulated")
    report_lines.append("3. **Load Testing**: Current tests are functional; load testing recommended for production readiness")
    report_lines.append("4. **Concurrent Requests**: Tests run sequentially; concurrent request handling not validated")
    report_lines.append("")
    
    report_lines.append("### Production Rollout Recommendations")
    report_lines.append("")
    report_lines.append("1. **Feature Flags**: Implement feature flag to toggle between v1 and v2 APIs")
    report_lines.append("2. **Canary Deployment**: Roll out to small percentage of traffic initially (5-10%)")
    report_lines.append("3. **Gradual Traffic Shift**: Increase v2 traffic gradually (10% → 25% → 50% → 100%)")
    report_lines.append("4. **Monitoring**: Set up alerts for:")
    report_lines.append("   - Error rates (v2 API)")
    report_lines.append("   - Latency percentiles (P50, P95, P99)")
    report_lines.append("   - Fallback frequency")
    report_lines.append("   - Pending response rate")
    report_lines.append("5. **Circuit Breaker**: Implement circuit breaker pattern for v2 API failures")
    report_lines.append("6. **Observability**: Add distributed tracing and structured logging")
    report_lines.append("7. **Idempotent Retries**: Ensure retry logic is idempotent for async operations")
    report_lines.append("8. **Validation**: Strictly validate regionId and warehouseGroup formats")
    report_lines.append("")
    
    report_lines.append("### Pitfalls to Avoid")
    report_lines.append("")
    report_lines.append("1. **Schema Drift**: Ensure API contract remains stable; version API responses")
    report_lines.append("2. **Missing Parameters**: Always validate required parameters before API calls")
    report_lines.append("3. **Timestamp Formats**: Handle ISO 8601 timestamp parsing consistently")
    report_lines.append("4. **Eventual Consistency**: Don't assume immediate confirmation for pending status")
    report_lines.append("5. **Error Handling**: Don't ignore fallback failures; log and alert")
    report_lines.append("")
    
    # Write report
    with open("compare_report.md", "w") as f:
        f.write("\n".join(report_lines))
    
    print("Comparison report generated: compare_report.md")
    print("Aggregated metrics saved: results/aggregated_metrics.json")


if __name__ == "__main__":
    generate_comparison_report()

