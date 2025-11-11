# Project B - Post-Change (v2 Implementation)

This project demonstrates the **post-change** implementation using the new `/api/v2/stock/availability` endpoint with region awareness and async handling.

## Overview

The updated cart service calls the v2 stock API which:
- Requires `sku`, `regionId`, and `warehouseGroup` parameters
- Returns availability with `availabilityStatus` (confirmed/pending/unavailable)
- Includes `syncTimestamp` for async operations
- Supports fallback to v1 API on errors
- Handles pending status with polling capability

## Project Structure

```
Project_B_PostChange/
├── src/
│   └── cart_service_v2.py      # Updated service with v2 API and async handling
├── mocks/
│   └── mock_v2_api.py          # Mock v2 API server with async simulation
├── data/
│   ├── test_data.json          # Test cases
│   └── expected_postchange.json # Expected outputs
├── tests/
│   └── test_post_change.py     # Test harness
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
python mocks/mock_v2_api.py 8002 &
python tests/test_post_change.py
```

## Test Cases

The test suite includes 8 test cases covering:
1. **Normal case** - Confirmed availability (SKU: ABC123, region: ap-sg-1, warehouse: WG-2)
2. **Boundary case** - Zero quantity (SKU: XYZ789)
3. **Async case** - Pending availability status (SKU: DEF456)
4. **Invalid input** - Missing regionId
5. **Invalid input** - Missing warehouseGroup
6. **Non-existent region/warehouse** - Valid SKU but wrong region
7. **Out of stock** - Unavailable SKU (SKU: GHI789)
8. **High latency** - Performance test

## API Endpoint

### New v2 Endpoint
- **URL**: `POST /api/v2/stock/availability`
- **Request**: 
  ```json
  {
    "sku": "ABC123",
    "regionId": "ap-sg-1",
    "warehouseGroup": "WG-2"
  }
  ```
- **Response (Confirmed)**:
  ```json
  {
    "sku": "ABC123",
    "available": true,
    "quantity": 12,
    "availabilityStatus": "confirmed",
    "syncTimestamp": "2025-11-01T12:00:00Z"
  }
  ```
- **Response (Pending)**:
  ```json
  {
    "sku": "DEF456",
    "available": true,
    "quantity": 5,
    "availabilityStatus": "pending",
    "syncTimestamp": "2025-11-01T12:02:00Z"
  }
  ```

## Key Features

### 1. Region Awareness
- Supports region-specific stock checks
- Handles multiple warehouse groups per region

### 2. Async Handling
- Detects `availabilityStatus: "pending"`
- Optional polling for confirmation
- Handles `syncTimestamp` for eventual consistency

### 3. Fallback Mechanism
- Falls back to v1 API on v2 errors/timeouts
- Graceful degradation for production resilience

### 4. Input Validation
- Validates required parameters (sku, regionId, warehouseGroup)
- Returns clear error messages for missing parameters

## Results

Test results are saved to `results/results_post.json` including:
- Test case outcomes
- Latency metrics (mean, p50, p95, p99)
- Error counts
- Fallback frequency
- Pending response handling
- Detailed assertions

