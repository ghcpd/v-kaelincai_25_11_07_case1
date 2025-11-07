Project B - Post-Change (v2 Integration & Adapter)

This project simulates the updated cart service calling `/api/v2/stock/availability` which requires `regionId` and `warehouseGroup`, and supports asynchronous availability via `availabilityStatus` and `syncTimestamp`.

Structure:
- `src/cart_service_v2.py` - service implementation with validation, polling, and fallback
- `mocks/mock_v2.py` - mock upstream supporting confirmed/pending/poll endpoints
- `tests/test_post_change.py` - test harness that runs mock and cases
- `results/results_post.json` - produced by tests

Run tests (PowerShell):
	`./run_tests.sh` or run `python tests/test_post_change.py`

