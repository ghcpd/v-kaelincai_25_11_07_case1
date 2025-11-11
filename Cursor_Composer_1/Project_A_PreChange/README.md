# Project A - Pre-Change (Legacy Implementation)

This project demonstrates the **pre-change** implementation using the legacy `/api/v1/checkStock` endpoint.

## Overview

The legacy cart service calls the v1 stock API which:
- Accepts only `sku` parameter
- Returns simple availability and quantity
- Has no region awareness
- No support for asynchronous availability status

## Project Structure

```
Project_A_PreChange/
├── src/
│   └── cart_service_v1.py      # Legacy service implementation
├── mocks/
│   └── mock_v1_api.py          # Mock v1 API server
├── data/
│   └── test_data.json          # Test cases
├── tests/
│   └── test_pre_change.py      # Test harness
├── logs/                        # Runtime logs
├── results/                     # Test results
├── requirements.txt
├── setup.sh
├── run_tests.sh
└── README.md
```

## Setup

### Prerequisites
- Python 3.8+
- pip

### Installation

```bash
# Run setup script
bash setup.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running Tests

```bash
# Run the test suite
bash run_tests.sh

# Or manually:
source venv/bin/activate
python mocks/mock_v1_api.py 8001 &
python tests/test_pre_change.py
```

## Test Cases

The test suite includes 6 test cases covering:
1. **Normal case** - Available stock (SKU: ABC123)
2. **Boundary case** - Zero quantity (SKU: XYZ789)
3. **Out of stock** - Unavailable SKU (SKU: GHI789)
4. **Invalid input** - Missing SKU parameter
5. **Non-existent SKU** - SKU not in database
6. **High latency** - Performance test

## API Endpoint

### Legacy v1 Endpoint
- **URL**: `POST /api/v1/checkStock`
- **Request**: `{"sku": "ABC123"}`
- **Response**: 
  ```json
  {
    "sku": "ABC123",
    "available": true,
    "quantity": 12
  }
  ```

## Limitations

- No region awareness
- No warehouse group support
- No asynchronous availability status
- Limited error handling
- No fallback mechanisms

## Results

Test results are saved to `results/results_pre.json` including:
- Test case outcomes
- Latency metrics (mean, p50, p95, p99)
- Error counts
- Detailed assertions

