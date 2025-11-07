# Project B - Post-Change (v2 Integration)

This project implements the new v2 integration, including:
- Region/warehouse aware request payload (sku, regionId, warehouseGroup)
- Handling of `availabilityStatus` field with `pending` and `confirmed`
- Polling with timeout to resolve `pending` responses
- Fallback to legacy v1 when v2 returns error/invalid or polling times out

How to run tests:
1. `./setup.sh`
2. `./run_tests.sh`

Files:
- `src/cart_service_v2.py`: Flask service calling v2 and falling back to v1
- `mocks/v2_mock.py`: v2 mock server with pending, confirmed and error scenarios
- `mocks/v1_mock.py`: v1 mock used for fallback testing
- `tests/test_post_change.py`: end-to-end test harness

Configuration:
- `V2_BASE` and `V1_BASE` environment variables allow pointing to live endpoints or mocks.
- `POLL_INTERVAL` and `POLL_TIMEOUT` configure polling behavior for pending responses.
