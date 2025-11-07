
# API Migration Evaluation

This workspace contains two projects demonstrating migration from `/api/v1/checkStock` to `/api/v2/stock/availability`.

Test Scenario:
- Legacy endpoint: `/api/v1/checkStock` accepts `{sku}` and returns `{sku,available,quantity}`.
- New endpoint: `/api/v2/stock/availability` requires `{sku,regionId,warehouseGroup}` and may return `availabilityStatus` ("confirmed"|"pending"), `available`, `quantity`, and `syncTimestamp`.

Acceptance Criteria:
- Post-change service calls v2 with required parameters and interprets `availabilityStatus`.
- If `pending`, it polls `.../poll` endpoint up to configured retries and falls back gracefully if unresolved.
- Tests show equal or improved correctness and acceptable latency.

Run the full workflow (on Windows Git Bash, WSL or Linux):

  bash run_all.sh

Outputs: `compare_report.md`, `results/aggregated_metrics.json`, `Project_*/results/*.json`.

Pitfalls & Mitigations:
- Schema drift: add validation and strict parsing. Use feature flags for gradual rollout.
- Async delays: implement polling with backoff, or webhook-based confirmations in production.
- Observability: log request IDs, latencies, and fallback events.

