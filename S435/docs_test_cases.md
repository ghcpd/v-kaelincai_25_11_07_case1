# Test Cases and Descriptions

This document describes each test case in `test_data.json` and explains what it verifies.

1. normal
   - Input: SKU=ABC123 with region and warehouse
   - Verifies: v2 returns confirmed availability; service uses v2 result; no fallback.

2. boundary_zero
   - Input: SKU=BOUNDARY1 with region
   - Verifies: v2 returns quantity 0 and confirmed; service marks unavailable.

3. async_pending
   - Input: SKU=ASYNC1 with region/warehouse
   - Verifies: v2 returns pending initially; service polls until confirmed; demonstrates polling behavior and eventual consistency.

4. invalid_input
   - Input: SKU numeric 12345 and missing regionId
   - Verifies: v2 rejects the request; service falls back to v1 which returns a valid result; ensures backward-compatible behavior.

5. high_latency_error
   - Input: SKU=LATENCY1
   - Verifies: v2 is slow or returns 500; service retries or times out and falls back to v1; ensures robustness against errors/timeouts.
