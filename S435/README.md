# API Change Migration Demo: Pre-Change vs Post-Change

This repository contains two projects that demonstrate migration of a shopping cart's inventory check service from an old API to a new API with region-aware & async features.

Projects:
- Project_A_PreChange: Legacy integration with /api/v1/checkStock
- Project_B_PostChange: New integration with /api/v2/stock/availability including adapter and fallback logic

Usage:
- Install dependencies and run tests for each project via run_tests.sh inside the project folders.
- Or run root run_all.sh to execute both projects and generate a compare report.

See compare_report.md for detailed comparisons and metrics.

Acceptance Criteria:
- Updated service calls v2 with sku, regionId and warehouseGroup where applicable.
- Service handles `availabilityStatus: pending` by polling and falling back to v1 when unresolved.
- Fallback is implemented for invalid inputs or v2 errors.
- Tests validate correctness, latency, fallback frequency.

How toggles and configuration work:
- Each service reads `V1_BASE` and `V2_BASE` env vars to switch between live and mock endpoints.
- `POLL_INTERVAL` and `POLL_TIMEOUT` control async polling for v2.

Limitations & Known Differences in this Demo:
- Mocks provide deterministic behavior and limited concurrency.
- Network conditions are simulated using sleep/delays but don't cover real-world jitter.
- Authentication, rate limiting, and webhook-based async callbacks are not fully simulated.

Recommended Production Steps:
- Add observability: trace IDs, metrics for pending responses, and error rates.
- Use feature flags and canary deployments per region.
- Implement circuit-breakers and retries with exponential backoff.
- Add schema validation and strict parameter checks for both requests and responses.
