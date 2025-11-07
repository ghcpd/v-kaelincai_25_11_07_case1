# API Change Evaluation: /api/v1/checkStock -> /api/v2/stock/availability

This workspace contains two projects demonstrating a before-and-after migration and automated tests to evaluate correctness and performance.

Structure:
- Project_A_PreChange: legacy integration using /api/v1/checkStock
- Project_B_PostChange: updated integration using /api/v2/stock/availability with adapter and async handling
- test_data.json: canonical test cases
- run_all.sh: master script to run both projects and aggregate results
- aggregate_results.py: script to produce compare_report.md and aggregated_metrics.json

Requirements:
- Python 3.8+ (recommend 3.10)
- Git Bash or Bash shell available for run_all.sh (or run steps manually on PowerShell)

Quickstart:
1. Run ./run_all.sh (on bash) or ./run_all.ps1 (PowerShell)
2. Open compare_report.md and results/aggregated_metrics.json for summaries

Test cases in test_data.json:
- normal: v2 returns confirmed; both pre and post should report available.
- boundary_zero: quantity 0; should be reported out of stock.
- async_pending: v2 returns pending with syncTimestamp; post-change service should poll and return confirmed.
- malformed: v2 missing regionId; post-change service returns 400 and does not fall back; pre-change uses v1 and behaves normally.
- high_latency_error: v2 times out; post-change should fallback to v1.

Outputs and artifacts:
- Project_A_PreChange/results/results_pre.json: per-case pass/fail and durations
- Project_B_PostChange/results/results_post.json: per-case pass/fail and durations
- results/aggregated_metrics.json: pass rates and latency p50/p95
- compare_report.md: human readable summary and recommendations

Project notes:
- Each project's tests start their own Flask mock servers; mocks are configurable for each test case.
- Post-change service implements v2 adapter with polling for 'pending' availabilityStatus and fallback to v1.

Acceptance criteria implemented in test harness:
- Updated service calls new endpoint with regionId and warehouseGroup where required.
- v2 service correctly handles 'confirmed' and 'pending' availabilityStatus (polls until confirmed or times out).
- Fallback to v1 occurs when v2 errors, returns invalid schema, or times out.
- Tests collect per-case durations, decisions, and fallback occurrences.

Pitfalls and mitigations:
- Schema drift: validate presence of required parameters and types.
- Asynchronous finalization: implement a robust polling policy, max timeouts and alerts for pending states.
- Circuit breakers: avoid cascading failures when v2 is degraded.
- Observability: log request IDs, response statuses, syncTimestamp, and tracing for correlation.

Limitations:
- Mocks emulate behavior but not production externalities (real networking, auth, retries at HTTP client library level, etc.)
- Polling behavior uses short timeouts suitable for tests, but production should use backoff and idempotent notifications.
- This is a minimal reproducible example for evaluation purposes.

