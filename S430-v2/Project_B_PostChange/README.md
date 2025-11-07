Project B Post-Change

This project demonstrates the updated cart service calling `/api/v2/stock/availability` with `regionId` and `warehouseGroup`, and implementing adapter/fallback behavior.

- Start mock: `python mocks/mock_v2.py --port 5002`
- Run tests: `bash run_tests.sh`

Data: `data/expected_postchange.json`.

Feature toggles:
- `USE_V2`: toggle using environment variable.
- `V2_API_MODE`: set to `confirm|pending_first|error|slow` to simulate server behaviors.
