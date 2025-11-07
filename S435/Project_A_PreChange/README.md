# Project A - Pre-Change (Legacy Integration)

This project implements the legacy service behavior which calls /api/v1/checkStock.

How to run tests:
1. Run `./setup.sh` to install dependencies (optional).
2. Run `./run_tests.sh` to start the v1 mock and the service and run tests.

Files:
- `src/cart_service_v1.py`: Flask service implementing the only SKU-based v1 call
- `mocks/v1_mock.py`: Flask mock server for /api/v1/checkStock
- `tests/test_pre_change.py`: Test harness

Note: `V1_BASE` can be configured via environment variable to point to a live v1 upstream.
