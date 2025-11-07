Project A - Pre-Change (Legacy Integration)

This project simulates the legacy cart service calling `/api/v1/checkStock`.

Structure:
- `src/cart_service_v1.py` - service implementation calling v1 endpoint
- `mocks/mock_v1.py` - mock upstream supporting delay/status/quantity
- `tests/test_pre_change.py` - test harness that runs mock and cases
- `results/results_pre.json` - produced by tests

Run tests (PowerShell):
	`./run_tests.sh` or run `python tests/test_pre_change.py`

