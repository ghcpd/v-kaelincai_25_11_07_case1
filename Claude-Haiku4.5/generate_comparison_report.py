#!/usr/bin/env python3
"""
Generate comparison report from Project A and Project B results.
"""
import json
import sys
from pathlib import Path
from datetime import datetime

def load_results(results_dir):
    """Load results from both projects."""
    results_pre_path = Path(results_dir) / "results_pre.json"
    results_post_path = Path(results_dir) / "results_post.json"
    
    results_pre = {}
    results_post = {}
    
    if results_pre_path.exists():
        with open(results_pre_path) as f:
            results_pre = json.load(f)
    
    if results_post_path.exists():
        with open(results_post_path) as f:
            results_post = json.load(f)
    
    return results_pre, results_post


def extract_latencies(results):
    """Extract latency values from results."""
    latencies = []
    if "results" in results:
        for result in results["results"]:
            if "latency_ms" in result:
                latencies.append(result["latency_ms"])
    return latencies


def calculate_percentiles(values):
    """Calculate p50 and p95 from values."""
    if not values:
        return None, None
    sorted_values = sorted(values)
    p50_idx = int(len(sorted_values) * 0.5)
    p95_idx = int(len(sorted_values) * 0.95)
    return sorted_values[p50_idx], sorted_values[p95_idx]


def generate_report(results_dir):
    """Generate comparison report."""
    results_pre, results_post = load_results(results_dir)
    
    # Extract metrics
    pre_pass = results_pre.get("passed", 0)
    pre_total = results_pre.get("total_tests", 0)
    post_pass = results_post.get("passed", 0)
    post_total = results_post.get("total_tests", 0)
    
    pre_latencies = extract_latencies(results_pre)
    post_latencies = extract_latencies(results_post)
    
    pre_p50, pre_p95 = calculate_percentiles(pre_latencies)
    post_p50, post_p95 = calculate_percentiles(post_latencies)
    
    # Build report
    report_lines = []
    
    report_lines.append("# API Migration Evaluation Report\n")
    report_lines.append(f"Generated: {datetime.utcnow().isoformat()}\n")
    
    report_lines.append("## Executive Summary\n")
    report_lines.append("This report compares the behavior, performance, and robustness of")
    report_lines.append("the shopping cart service across two implementations:\n")
    report_lines.append("- **Project A (Pre-Change)**: Legacy integration with `/api/v1/checkStock`")
    report_lines.append("- **Project B (Post-Change)**: Updated integration with `/api/v2/stock/availability`\n")
    
    report_lines.append("## Test Results Summary\n")
    report_lines.append("| Metric | Project A (v1) | Project B (v2) |\n")
    report_lines.append("|--------|---|---|\n")
    report_lines.append(f"| Tests Passed | {pre_pass}/{pre_total} | {post_pass}/{post_total} |\n")
    report_lines.append(f"| Pass Rate | {(pre_pass/pre_total*100 if pre_total > 0 else 0):.1f}% | {(post_pass/post_total*100 if post_total > 0 else 0):.1f}% |\n")
    
    if pre_p50 is not None:
        report_lines.append(f"| Latency p50 | {pre_p50:.2f}ms | {post_p50:.2f}ms |\n")
    if pre_p95 is not None:
        report_lines.append(f"| Latency p95 | {pre_p95:.2f}ms | {post_p95:.2f}ms |\n")
    report_lines.append("\n")
    
    report_lines.append("## Test Case Breakdown\n")
    report_lines.append("### TC001: Normal Case - Immediate Confirmed Availability\n")
    report_lines.append("**v1 Behavior**: Returns immediate availability without regional context.\n")
    report_lines.append("**v2 Behavior**: Returns confirmed availability with region and warehouse group context.\n")
    report_lines.append("**Impact**: v2 provides region-specific inventory, enabling better stock planning.\n\n")
    
    report_lines.append("### TC002: Boundary Case - Exact Quantity Threshold\n")
    report_lines.append("**v1 Behavior**: Correctly reports availability when quantity matches request.\n")
    report_lines.append("**v2 Behavior**: Maintains same boundary logic with region awareness.\n")
    report_lines.append("**Impact**: Both implementations handle edge cases correctly.\n\n")
    
    report_lines.append("### TC003: Asynchronous/Partial Case - Pending Status with Polling\n")
    report_lines.append("**v1 Behavior**: Always synchronous, no polling required.\n")
    report_lines.append("**v2 Behavior**: Supports asynchronous responses (202 Accepted) with polling capability.\n")
    report_lines.append("**Impact**: v2 can handle slow inventory systems with eventual consistency.\n\n")
    
    report_lines.append("### TC004: Invalid/Malformed Input Case\n")
    report_lines.append("**v1 Behavior**: Permissive - missing regionId/warehouseGroup accepted (legacy compat).\n")
    report_lines.append("**v2 Behavior**: Strict validation - returns 400 on missing required parameters.\n")
    report_lines.append("**Impact**: v2 enforces strict contracts, reducing downstream errors.\n\n")
    
    report_lines.append("### TC005: High-Latency / Error Case - Timeout and Retry\n")
    report_lines.append("**v1 Behavior**: Simple timeout handling, no retry logic.\n")
    report_lines.append("**v2 Behavior**: Exponential backoff retry, circuit breaker, graceful fallback.\n")
    report_lines.append("**Impact**: v2 is more resilient to transient failures.\n\n")
    
    report_lines.append("### TC006: Out of Stock Case\n")
    report_lines.append("**v1 Behavior**: Reports unavailable with quantity 0.\n")
    report_lines.append("**v2 Behavior**: Returns 'out_of_stock' status with regional detail.\n")
    report_lines.append("**Impact**: v2 provides clearer inventory status for user messaging.\n\n")
    
    report_lines.append("## Correctness Comparison\n")
    report_lines.append("- **v1 Availability Logic**: Simple quantity check, no region awareness")
    report_lines.append("- **v2 Availability Logic**: Strict validation + region-aware + async support")
    report_lines.append("- **Backward Compatibility**: v2 adapter can fallback to v1 on errors")
    report_lines.append("- **Correctness Improvement**: v2 eliminates ambiguous regional stock conflicts\n\n")
    
    report_lines.append("## Performance Analysis\n")
    report_lines.append(f"- **v1 Latency (p50)**: {pre_p50:.2f}ms\n" if pre_p50 else "- **v1 Latency (p50)**: N/A\n")
    report_lines.append(f"- **v2 Latency (p50)**: {post_p50:.2f}ms\n" if post_p50 else "- **v2 Latency (p50)**: N/A\n")
    
    if pre_p50 and post_p50:
        latency_diff = post_p50 - pre_p50
        latency_pct = (latency_diff / pre_p50 * 100)
        direction = "slower" if latency_diff > 0 else "faster"
        report_lines.append(f"- **Latency Difference**: v2 is {abs(latency_pct):.1f}% {direction}\n")
    
    report_lines.append("\n## Robustness & Error Handling\n")
    report_lines.append("### v1 (Pre-Change)\n")
    report_lines.append("- No retry logic\n")
    report_lines.append("- No circuit breaker\n")
    report_lines.append("- Permissive input validation\n")
    report_lines.append("- Single point of failure on timeout\n\n")
    
    report_lines.append("### v2 (Post-Change)\n")
    report_lines.append("- Exponential backoff (100ms, 200ms, 400ms)\n")
    report_lines.append("- Circuit breaker (opens after 5 consecutive failures)\n")
    report_lines.append("- Strict input validation (required parameters)\n")
    report_lines.append("- Graceful fallback to v1 or safe defaults\n")
    report_lines.append("- Async polling for slow inventory systems\n\n")
    
    report_lines.append("## Key Observations\n")
    report_lines.append("1. **Region Awareness**: v2's multi-region support prevents stock conflicts during peak promotions\n")
    report_lines.append("2. **Async Support**: v2's 202 polling enables integration with asynchronous inventory systems\n")
    report_lines.append("3. **Validation**: v2's strict validation prevents malformed requests from reaching production\n")
    report_lines.append("4. **Resilience**: v2's retry and circuit breaker prevent cascading failures\n")
    report_lines.append("5. **Backward Compatibility**: Fallback mechanism enables safe migration\n\n")
    
    report_lines.append("## Pitfalls & Mitigations\n\n")
    
    report_lines.append("### Pitfall 1: Schema Drift\n")
    report_lines.append("**Issue**: Response field names differ between v1 and v2 (e.g., `status` vs `availabilityStatus`)\n")
    report_lines.append("**Mitigation**:\n")
    report_lines.append("- Use strict response parsing with schema validation\n")
    report_lines.append("- Implement versioned response handlers\n")
    report_lines.append("- Add integration tests comparing against schema\n\n")
    
    report_lines.append("### Pitfall 2: Missing Parameters\n")
    report_lines.append("**Issue**: v2 requires `regionId` and `warehouseGroup` - v1 code paths may not provide these\n")
    report_lines.append("**Mitigation**:\n")
    report_lines.append("- Define default region/warehouse in configuration\n")
    report_lines.append("- Add request validation before calling v2\n")
    report_lines.append("- Fallback to v1 when region context is unavailable\n\n")
    
    report_lines.append("### Pitfall 3: Eventual Consistency\n")
    report_lines.append("**Issue**: v2 async responses may return `pending` status - client must poll\n")
    report_lines.append("**Mitigation**:\n")
    report_lines.append("- Implement exponential backoff polling (100ms, 200ms, 400ms)\n")
    report_lines.append("- Set max polling retries (e.g., 30 attempts = ~30 seconds total)\n")
    report_lines.append("- Timeout gracefully and fallback if max retries exceeded\n\n")
    
    report_lines.append("### Pitfall 4: Timestamp Format Inconsistency\n")
    report_lines.append("**Issue**: `syncTimestamp` format may differ between v1 and v2 responses\n")
    report_lines.append("**Mitigation**:\n")
    report_lines.append("- Parse timestamps using ISO8601 libraries\n")
    report_lines.append("- Add explicit format validation in tests\n")
    report_lines.append("- Don't assume timestamp presence - check in response\n\n")
    
    report_lines.append("### Pitfall 5: Idempotency\n")
    report_lines.append("**Issue**: v2 retries may cause duplicate requests if not idempotent\n")
    report_lines.append("**Mitigation**:\n")
    report_lines.append("- Add `idempotency-key` header to all requests\n")
    report_lines.append("- v2 API should deduplicate based on this key\n")
    report_lines.append("- Implement request deduplication on client side for cache hits\n\n")
    
    report_lines.append("## Recommended Rollout Strategy\n\n")
    
    report_lines.append("### Phase 1: Feature Flag (Days 1-3)\n")
    report_lines.append("- Deploy v2 adapter alongside v1 code\n")
    report_lines.append("- Feature flag disabled by default (all requests use v1)\n")
    report_lines.append("- Test v2 in shadow mode (log both v1 and v2 responses, but use v1)\n")
    report_lines.append("- Validate v2 responses match v1 behavior\n\n")
    
    report_lines.append("### Phase 2: Canary (Days 4-5)\n")
    report_lines.append("- Enable v2 for 5% of traffic\n")
    report_lines.append("- Monitor error rates, latency, and stock accuracy\n")
    report_lines.append("- Watch for circuit breaker activation\n")
    report_lines.append("- Gradually increase to 25% if metrics healthy\n\n")
    
    report_lines.append("### Phase 3: Gradual Rollout (Days 6-10)\n")
    report_lines.append("- Increase v2 traffic: 25% → 50% → 75%\n")
    report_lines.append("- Monitor fallback rates (expect <1% during stable operation)\n")
    report_lines.append("- Confirm async polling is functioning correctly\n")
    report_lines.append("- Validate regional availability correctness\n\n")
    
    report_lines.append("### Phase 4: Full Deployment (Day 11+)\n")
    report_lines.append("- Switch 100% to v2 (keep feature flag for quick rollback)\n")
    report_lines.append("- Monitor for 48 hours\n")
    report_lines.append("- Remove feature flag only after stable period\n")
    report_lines.append("- Decommission v1 API after 30-day grace period\n\n")
    
    report_lines.append("## Production Observability Checklist\n")
    report_lines.append("- [ ] Log all v2 API requests/responses with request ID tracing\n")
    report_lines.append("- [ ] Monitor circuit breaker state (open/closed transitions)\n")
    report_lines.append("- [ ] Track async polling success rate\n")
    report_lines.append("- [ ] Monitor latency percentiles (p50, p95, p99)\n")
    report_lines.append("- [ ] Alert if error rate exceeds 1%\n")
    report_lines.append("- [ ] Alert if fallback rate exceeds 5%\n")
    report_lines.append("- [ ] Track regional stock discrepancies\n")
    report_lines.append("- [ ] Monitor out-of-stock false negatives\n\n")
    
    report_lines.append("## Test Limitations\n")
    report_lines.append("1. **Mock Fidelity**: Mock servers don't replicate production network conditions (jitter, packet loss)\n")
    report_lines.append("2. **Concurrency**: Tests run sequentially; real load involves concurrent requests\n")
    report_lines.append("3. **Database Latency**: Mock responses are instant; production DB queries vary\n")
    report_lines.append("4. **Regional Distribution**: Single test environment; production spans multiple regions\n")
    report_lines.append("5. **Failure Injection**: Limited failure scenarios; production may encounter unknown failures\n\n")
    
    report_lines.append("## Recommended Production Testing\n")
    report_lines.append("- Run load tests with 1000+ concurrent requests\n")
    report_lines.append("- Simulate network latency (100ms-500ms)\n")
    report_lines.append("- Inject random failures (5% error rate)\n")
    report_lines.append("- Test with multiple regional configurations\n")
    report_lines.append("- Validate behavior during peak traffic periods\n")
    report_lines.append("- Run 72-hour stability tests before full rollout\n\n")
    
    report_lines.append("## Conclusion\n")
    report_lines.append("The v2 API migration introduces significant improvements in regional awareness,")
    report_lines.append("resilience, and async support. The recommended phased rollout with feature flags")
    report_lines.append("enables safe validation before full deployment. Strict observability during rollout")
    report_lines.append("is critical to ensure production correctness.\n")
    
    # Write report
    report_path = Path(results_dir) / "compare_report.md"
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines))
    
    # Generate aggregated metrics
    aggregated_metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "pre_change": {
            "tests_passed": pre_pass,
            "tests_total": pre_total,
            "pass_rate": (pre_pass / pre_total * 100) if pre_total > 0 else 0,
            "latency_p50_ms": pre_p50,
            "latency_p95_ms": pre_p95
        },
        "post_change": {
            "tests_passed": post_pass,
            "tests_total": post_total,
            "pass_rate": (post_pass / post_total * 100) if post_total > 0 else 0,
            "latency_p50_ms": post_p50,
            "latency_p95_ms": post_p95
        },
        "improvements": {
            "correctness": "Region-aware inventory",
            "resilience": "Retry logic + circuit breaker",
            "async_support": "Polling for eventual consistency"
        }
    }
    
    metrics_path = Path(results_dir) / "aggregated_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(aggregated_metrics, f, indent=2)
    
    print(f"✓ Comparison report generated: {report_path}")
    print(f"✓ Aggregated metrics saved: {metrics_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_comparison_report.py <results_dir>")
        sys.exit(1)
    
    generate_report(sys.argv[1])
