# API Migration Evaluation: v1 → v2 Stock Availability API

This repository contains a comprehensive evaluation of migrating from the legacy `/api/v1/checkStock` endpoint to the new `/api/v2/stock/availability` endpoint with region awareness and async handling.

## Overview

**Scenario**: A commerce platform migrates inventory checks from a simple v1 API to a region-aware v2 API that requires additional parameters (`regionId`, `warehouseGroup`) and may return asynchronous availability status fields (`availabilityStatus`, `syncTimestamp`).

**Objective**: Demonstrate the before-and-after migration, validate correctness, measure performance impact, and provide automated testing infrastructure.

## Project Structure

```
.
├── Project_A_PreChange/          # Legacy implementation (v1 API)
│   ├── src/                      # Service code
│   ├── mocks/                    # Mock v1 API server
│   ├── tests/                    # Test harness
│   ├── data/                     # Test data
│   ├── results/                  # Test results
│   └── logs/                     # Runtime logs
│
├── Project_B_PostChange/         # Updated implementation (v2 API)
│   ├── src/                      # Service code with async handling
│   ├── mocks/                    # Mock v2 API server
│   ├── tests/                    # Test harness
│   ├── data/                     # Test data
│   ├── results/                  # Test results
│   └── logs/                     # Runtime logs
│
├── results/                      # Aggregated results
├── test_data.json                # Canonical test cases
├── run_all.sh                    # Master execution script
├── generate_comparison_report.py  # Report generator
├── compare_report.md              # Comparison report (generated)
└── README.md                     # This file
```

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip
- bash (for shell scripts; on Windows, use Git Bash or WSL)

### One-Click Execution

Run the complete evaluation:

```bash
bash run_all.sh
```

This will:
1. Run Project A (Pre-Change) tests
2. Run Project B (Post-Change) tests
3. Generate comparison report
4. Save aggregated metrics

### Individual Project Execution

#### Project A (Pre-Change)

```bash
cd Project_A_PreChange
bash setup.sh
bash run_tests.sh
```

#### Project B (Post-Change)

```bash
cd Project_B_PostChange
bash setup.sh
bash run_tests.sh
```

## API Change Details

### Legacy v1 API

**Endpoint**: `POST /api/v1/checkStock`

**Request**:
```json
{
  "sku": "ABC123"
}
```

**Response**:
```json
{
  "sku": "ABC123",
  "available": true,
  "quantity": 12
}
```

### New v2 API

**Endpoint**: `POST /api/v2/stock/availability`

**Request**:
```json
{
  "sku": "ABC123",
  "regionId": "ap-sg-1",
  "warehouseGroup": "WG-2"
}
```

**Response (Confirmed)**:
```json
{
  "sku": "ABC123",
  "available": true,
  "quantity": 12,
  "availabilityStatus": "confirmed",
  "syncTimestamp": "2025-11-01T12:00:00Z"
}
```

**Response (Pending)**:
```json
{
  "sku": "DEF456",
  "available": true,
  "quantity": 5,
  "availabilityStatus": "pending",
  "syncTimestamp": "2025-11-01T12:02:00Z"
}
```

## Key Differences

| Feature | v1 API | v2 API |
|---------|--------|--------|
| Parameters | `sku` only | `sku`, `regionId`, `warehouseGroup` |
| Region Awareness | No | Yes |
| Async Status | No | Yes (`availabilityStatus`, `syncTimestamp`) |
| Fallback Support | N/A | Yes (falls back to v1) |
| Error Handling | Basic | Enhanced with validation |

## Test Cases

The evaluation includes 6+ test cases covering:

1. **Normal case** - Standard availability check
2. **Boundary case** - Zero quantity handling
3. **Async case** - Pending availability status
4. **Invalid input** - Missing required parameters
5. **Non-existent SKU/Region** - Not found scenarios
6. **High latency** - Performance testing

See `test_data.json` for complete test case definitions.

## Evaluation Metrics

The comparison report includes:

- **Correctness**: Test pass rates, assertion validation
- **Latency**: P50, P95, P99 percentiles, mean latency
- **Error Rates**: HTTP errors, timeouts, fallbacks
- **Async Handling**: Pending response frequency
- **Fallback Usage**: v1 fallback trigger rate

## Results

After running `run_all.sh`, you'll find:

- `results/results_pre.json` - Pre-change test results
- `results/results_post.json` - Post-change test results
- `results/aggregated_metrics.json` - Aggregated metrics
- `compare_report.md` - Detailed comparison report

## Key Features Implemented

### Project A (Pre-Change)
- ✅ Legacy service calling v1 API
- ✅ Mock v1 API server
- ✅ Basic error handling
- ✅ Test harness with metrics

### Project B (Post-Change)
- ✅ Updated service calling v2 API
- ✅ Region and warehouse group support
- ✅ Async availability status handling
- ✅ Polling for pending confirmations
- ✅ Fallback to v1 API on errors
- ✅ Input validation
- ✅ Mock v2 API server with async simulation
- ✅ Comprehensive test harness

## Limitations

1. **Mock Fidelity**: Mock servers simulate behavior but may not capture all production edge cases
2. **Network Conditions**: Tests run in controlled environment
3. **Load Testing**: Functional tests only; load testing recommended separately
4. **Concurrent Requests**: Tests run sequentially

## Production Rollout Recommendations

1. **Feature Flags**: Toggle between v1/v2 APIs
2. **Canary Deployment**: Start with 5-10% traffic
3. **Gradual Rollout**: 10% → 25% → 50% → 100%
4. **Monitoring**: Error rates, latency, fallback frequency
5. **Circuit Breaker**: Protect against cascading failures
6. **Observability**: Distributed tracing and structured logging

See `compare_report.md` for detailed recommendations.

## Troubleshooting

### Mock API Not Starting

Ensure ports 8001 (v1) and 8002 (v2) are available:

```bash
# Check if ports are in use
lsof -i :8001
lsof -i :8002

# Kill processes if needed
kill -9 <PID>
```

### Tests Failing

1. Ensure mock APIs are running before tests
2. Check logs in `logs/` directories
3. Verify Python dependencies are installed
4. Ensure test data files exist

### Windows Users

On Windows, use Git Bash or WSL to run shell scripts. Alternatively:

```powershell
# Run Python scripts directly
cd Project_A_PreChange
python mocks/mock_v1_api.py 8001
# In another terminal:
python tests/test_pre_change.py
```

## Contributing

This is an evaluation project. For production use, consider:
- Adding more comprehensive error scenarios
- Implementing retry logic with exponential backoff
- Adding integration tests with real API endpoints
- Performance/load testing
- Security testing

## License

This project is provided as-is for evaluation purposes.

