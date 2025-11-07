# API Migration Evaluation - Pre/Post Change Analysis

**Evaluation Scope**: S180, S390, S430-v2, Claude Haiku 4.5 and GPT-5-mini on Feature & improvement – API change

**Canonical Scenario**: Commerce platform migrating inventory checks from `/api/v1/checkStock` (legacy) to `/api/v2/stock/availability` (region-aware, async-capable).

---

## Quick Start

### One-Click Full Execution
```bash
cd /path/to/repo
bash run_all.sh
```

This script will:
1. Execute Project A tests (v1 pre-change)
2. Execute Project B tests (v2 post-change)  
3. Aggregate results
4. Generate comparison report
5. Output metrics and recommendations

---

## Project Structure

```
.
├── Project_A_PreChange/          # Legacy v1 integration
│   ├── src/
│   │   └── cart_service_v1.py    # Service using /api/v1/checkStock
│   ├── mocks/
│   │   └── mock_v1_server.py     # Mock v1 API server
│   ├── tests/
│   │   └── test_pre_change.py    # Test harness for v1
│   ├── data/
│   ├── results/
│   ├── logs/
│   ├── requirements.txt
│   ├── setup.sh
│   └── run_tests.sh
│
├── Project_B_PostChange/         # Updated v2 integration
│   ├── src/
│   │   └── cart_service_v2.py    # Service using /api/v2/stock/availability
│   ├── mocks/
│   │   └── mock_v2_server.py     # Mock v2 API server (async-capable)
│   ├── tests/
│   │   └── test_post_change.py   # Test harness for v2
│   ├── data/
│   ├── results/
│   ├── logs/
│   ├── requirements.txt
│   ├── setup.sh
│   └── run_tests.sh
│
├── test_data.json                 # Shared canonical test data
├── run_all.sh                     # Master execution script
├── generate_comparison_report.py  # Report generator
├── results/                       # Aggregated results
│   ├── results_pre.json
│   ├── results_post.json
│   ├── aggregated_metrics.json
│   └── compare_report.md
└── README.md                      # This file
```

---

## Test Scenario Description

### The Problem
A commerce platform's shopping cart service calls `/api/v1/checkStock` to validate inventory before adding items to cart. During peak promotions, this legacy endpoint causes:
- **Incorrect availability**: No region awareness; shows same stock globally
- **Increased latency**: No async support; clients wait for immediate response
- **Wrong "out of stock" displays**: Stock conflicts between regions reported as OOS

### The Solution
Migrate to `/api/v2/stock/availability` which:
- **Adds regionId and warehouseGroup parameters**: Enables region-specific inventory
- **Supports asynchronous responses**: 202 Accepted + polling for slow inventory systems
- **Returns availabilityStatus field**: More explicit status (confirmed, pending, out_of_stock, not_found)
- **Includes syncTimestamp**: Tracks eventual consistency

### Success Criteria
1. ✓ Correctly calls new endpoint with required parameters
2. ✓ Handles async responses and polling correctly
3. ✓ Falls back gracefully when v2 fails
4. ✓ Improves or maintains user-facing availability accuracy
5. ✓ Reduces latency or adds acceptable overhead for async handling
6. ✓ Adds robustness (retries, circuit breaker, validation)

---

## Test Data & Cases

**Location**: `test_data.json` (shared by both projects)

### TC001: Normal Case - Immediate Confirmed Availability
- **Input**: SKU=ABC123, quantity=5, regionId=ap-sg-1, warehouseGroup=WG-2
- **v1 Response**: `{sku: ABC123, available: true, quantity: 12}`
- **v2 Response**: `{sku: ABC123, available: true, quantity: 12, availabilityStatus: confirmed, syncTimestamp: ...}`
- **Validates**: Parameter mapping, response schema, basic availability logic

### TC002: Boundary Case - Exact Quantity Threshold
- **Input**: SKU=DEF456, quantity=3, regionId=us-east-1, warehouseGroup=WG-1
- **Expected**: Both v1 and v2 report available when quantity >= requested
- **Validates**: Edge case handling, threshold correctness

### TC003: Asynchronous/Partial Case - Pending with Polling
- **v1 Response**: Synchronous only (no polling)
- **v2 Response**: 202 Accepted with requestId → client polls /poll/{requestId} → 200 confirmed
- **Validates**: Async handling, polling retry logic, eventual consistency

### TC004: Invalid/Malformed Input Case
- **Variants**: 
  - Missing regionId → v2 returns 400
  - Invalid warehouseGroup → v2 returns 400
  - Non-string SKU → v2 returns 400
- **v1 Behavior**: Permissive (legacy)
- **v2 Behavior**: Strict validation
- **Validates**: Input validation, fallback mechanism

### TC005: High-Latency / Error Case - Timeout and Retry
- **Scenario**: v2 returns 504 twice, then succeeds
- **Expected**: 
  - v1: Timeout after ~5s
  - v2: Exponential backoff (100ms, 200ms, 400ms) → eventually succeeds or falls back
- **Validates**: Retry logic, circuit breaker, resilience

### TC006: Out of Stock Case
- **Input**: SKU=MNO345, quantity=100, available_quantity=5
- **Expected**: Both report unavailable
- **v2 Returns**: availabilityStatus: out_of_stock
- **Validates**: Boundary at zero, status messaging

---

## Running Individual Projects

### Project A (Pre-Change - v1)
```bash
# Setup
cd Project_A_PreChange
bash setup.sh

# Run tests (includes starting mock v1 server)
bash run_tests.sh

# Results
cat results/results_pre.json
cat logs/test_run.log
```

**Key Files**:
- `src/cart_service_v1.py`: CartServiceV1 class using v1 API
- `mocks/mock_v1_server.py`: Flask app simulating /api/v1/checkStock
- `tests/test_pre_change.py`: 6 test cases + cart integration tests

### Project B (Post-Change - v2)
```bash
# Setup
cd Project_B_PostChange
bash setup.sh

# Run tests (includes starting mock v2 server)
bash run_tests.sh

# Results
cat results/results_post.json
cat logs/test_run.log
```

**Key Features**:
- `src/cart_service_v2.py`: CartServiceV2 with adapter pattern:
  - Parameter validation
  - Async polling (202 Accepted)
  - Exponential backoff retry (100ms, 200ms, 400ms)
  - Circuit breaker (opens after 5 failures)
  - Graceful fallback to v1 or safe default
- `mocks/mock_v2_server.py`: Flask app with:
  - Strict parameter validation
  - Region awareness (ap-sg-1, us-east-1, eu-west-1)
  - Async simulation (20% of requests return 202)
  - Polling endpoint /api/v2/stock/availability/poll/{requestId}

---

## Understanding Results Files

### results_pre.json (Project A)
```json
{
  "timestamp": "2025-11-07T12:00:00",
  "version": "pre-change (v1)",
  "total_tests": 8,
  "passed": 8,
  "failed": 0,
  "results": [
    {
      "test_id": "TC001",
      "passed": true,
      "latency_ms": 145.23,
      "result": {
        "available": true,
        "quantity": 12,
        "sku": "ABC123",
        "source": "v1"
      }
    }
    ...
  ]
}
```

### results_post.json (Project B)
```json
{
  "timestamp": "2025-11-07T12:05:00",
  "version": "post-change (v2)",
  "total_tests": 10,
  "passed": 10,
  "failed": 0,
  "results": [
    {
      "test_id": "TC001",
      "passed": true,
      "latency_ms": 156.89,
      "result": {
        "available": true,
        "quantity": 12,
        "sku": "ABC123",
        "availability_status": "confirmed",
        "sync_timestamp": "2025-11-07T12:05:00Z",
        "source": "v2"
      }
    }
    ...
  ]
}
```

### aggregated_metrics.json
```json
{
  "pre_change": {
    "tests_passed": 8,
    "pass_rate": 100,
    "latency_p50_ms": 120,
    "latency_p95_ms": 200
  },
  "post_change": {
    "tests_passed": 10,
    "pass_rate": 100,
    "latency_p50_ms": 150,
    "latency_p95_ms": 250
  },
  "improvements": {
    "correctness": "Region-aware inventory",
    "resilience": "Retry logic + circuit breaker",
    "async_support": "Polling for eventual consistency"
  }
}
```

### compare_report.md
Detailed comparison including:
- Test results summary
- Per-test case analysis
- Correctness improvements
- Performance analysis (latency p50/p95)
- Robustness comparison
- Key observations
- Pitfalls and mitigations
- Recommended rollout strategy
- Production observability checklist

---

## Test Execution Details

### What Happens During run_all.sh

1. **Phase 1: Project A Tests**
   - Activates venv and installs requirements
   - Starts mock v1 server on port 8001
   - Runs 8 test cases from test_pre_change.py
   - Captures logs and results
   - Stops mock server
   - Outputs results_pre.json

2. **Phase 2: Project B Tests**
   - Activates venv and installs requirements
   - Starts mock v2 server on port 8002
   - Runs 10 test cases from test_post_change.py
   - Captures logs and results
   - Stops mock server
   - Outputs results_post.json

3. **Phase 3: Results Aggregation**
   - Copies results_pre.json → results/
   - Copies results_post.json → results/
   - Invokes generate_comparison_report.py

4. **Phase 4: Report Generation**
   - Loads both results files
   - Calculates latency percentiles
   - Generates markdown report with:
     - Test results summary
     - Per-test case analysis
     - Performance comparison
     - Robustness analysis
     - Key observations
     - Pitfalls and mitigations
     - Rollout recommendations

---

## Test Coverage Matrix

| Test Case | v1 Validates | v2 Validates | Acceptance Criteria |
|-----------|--------------|--------------|---------------------|
| TC001 | Immediate response | Region awareness + confirmed status | Both return available=true |
| TC002 | Boundary logic | Boundary logic + regional context | Correct threshold handling |
| TC003 | Sync response | Async polling + 202 handling | v2 eventually confirmed |
| TC004 | Permissive validation | Strict validation + error handling | v2 rejects invalid params |
| TC005 | Timeout handling | Retry + circuit breaker | v2 more resilient |
| TC006 | Out of stock logic | Out of stock status + regional detail | Both report unavailable |

---

## Pitfalls & Mitigations

### Pitfall 1: Schema Drift
**Problem**: v1 returns `status` field; v2 returns `availabilityStatus`
**Mitigation**:
- Use strict response parsing
- Add schema validation tests
- Version-specific response handlers

### Pitfall 2: Missing Required Parameters
**Problem**: Existing code doesn't pass regionId/warehouseGroup
**Mitigation**:
- Set default region from configuration
- Add request validation before v2 call
- Fallback to v1 for unmapped regions

### Pitfall 3: Eventual Consistency
**Problem**: v2 may return 202 pending; client must poll
**Mitigation**:
- Implement exponential backoff polling
- Set max poll retries (30 attempts, ~30 seconds)
- Timeout gracefully to fallback

### Pitfall 4: Timestamp Inconsistency
**Problem**: syncTimestamp format varies
**Mitigation**:
- Parse using ISO8601 libraries
- Add explicit format validation
- Handle missing timestamps

### Pitfall 5: Idempotency
**Problem**: Retries cause duplicate requests
**Mitigation**:
- Add `idempotency-key` header
- API deduplicates on server side
- Client-side deduplication cache

---

## Recommended Rollout Strategy

### Phase 1: Feature Flag (Days 1-3)
```python
if feature_flags.use_v2_api:
    result = service_v2.check_stock_v2(...)
else:
    result = service_v1.check_stock(...)
```
- Deploy with flag disabled
- Log both v1 and v2 responses in shadow mode
- Verify v2 responses match v1

### Phase 2: Canary (Days 4-5)
- Enable v2 for 5% of traffic
- Monitor:
  - Error rate (alert if >1%)
  - Latency (alert if p95 >2x baseline)
  - Fallback rate (expect <1%)
  - Stock accuracy (manual spot checks)

### Phase 3: Gradual Rollout (Days 6-10)
- 5% → 25% → 50% → 75%
- Continue monitoring
- Confirm async polling success rate
- Validate regional correctness

### Phase 4: Full Deployment (Day 11+)
- 100% to v2
- Keep feature flag for quick rollback
- Monitor 48 hours
- Remove flag after stable period
- Decommission v1 after 30-day grace

---

## Production Observability Requirements

**Logging**:
- All v2 API requests/responses with request ID
- Circuit breaker state transitions
- Retry attempts and backoff timing
- Async polling attempts and success

**Metrics**:
- Latency: p50, p95, p99 percentiles
- Error rate by status code
- Circuit breaker state (open/closed)
- Fallback rate and reasons
- Async polling success rate

**Alerts**:
- Error rate >1%
- Fallback rate >5%
- Circuit breaker open for >5 minutes
- Out-of-stock false negatives (stock=0 but available=true)
- Regional stock discrepancies

---

## Test Limitations

1. **Mock Fidelity**: Mock servers don't replicate network jitter/packet loss
2. **Concurrency**: Tests run sequentially; production is concurrent
3. **Database Latency**: Mocks respond instantly; production DBs vary
4. **Regional Distribution**: Single test environment; production spans regions
5. **Failure Injection**: Limited scenarios; production may encounter unknowns
6. **Load Profile**: Tests are light; production has peak traffic patterns

### Recommended Production Testing
- Load tests: 1000+ concurrent requests
- Network simulation: 100ms-500ms latency
- Failure injection: 5% error rate
- Duration: 72 hours before full rollout
- Regional validation: Test each region's inventory

---

## Configuration

### Environment Variables
```bash
# Project A
export V1_BASE_URL=http://localhost:8001

# Project B
export V2_BASE_URL=http://localhost:8002
export V1_FALLBACK_URL=http://localhost:8001  # For fallback
export V2_MAX_RETRIES=3
export V2_RETRY_BACKOFF_MS=100
```

### Mock Server Ports
- v1 Mock: `8001`
- v2 Mock: `8002`

### Default Test Configuration (from test_data.json)
```json
{
  "v1_base_url": "http://localhost:8001",
  "v2_base_url": "http://localhost:8002",
  "timeouts": {
    "normal_request": 5000,
    "polling_max_wait": 30000,
    "retry_max_attempts": 3
  }
}
```

---

## Troubleshooting

### Tests Won't Start - Port in Use
```bash
# Kill existing processes
lsof -i :8001  # Find v1 mock process
lsof -i :8002  # Find v2 mock process
kill -9 <PID>
```

### Virtual Environment Issues
```bash
# Recreate venv
rm -rf Project_A_PreChange/venv
rm -rf Project_B_PostChange/venv
bash run_all.sh
```

### Import Errors
```bash
# Ensure you're in correct venv
source Project_A_PreChange/venv/bin/activate
python -c "import flask; print(flask.__version__)"
```

### Mock Server Won't Start
```bash
# Check logs
cat Project_A_PreChange/logs/v1_server.log
cat Project_B_PostChange/logs/v2_server.log

# Manual start for debugging
python Project_A_PreChange/mocks/mock_v1_server.py 8001
```

---

## Code Examples

### Using CartServiceV1 (Pre-Change)
```python
from cart_service_v1 import CartServiceV1

service = CartServiceV1(v1_base_url="http://localhost:8001")

# Check stock
result = service.check_stock("ABC123", quantity=5)
print(result)
# Output: {
#   "available": true,
#   "quantity": 12,
#   "sku": "ABC123",
#   "source": "v1",
#   "latency_ms": 145.23,
#   "timestamp": "2025-11-07T12:00:00"
# }

# Add to cart
cart_result = service.add_to_cart("ABC123", quantity=2)
print(cart_result)
# Output: {
#   "success": true,
#   "message": "Added 2 x ABC123 to cart",
#   "item": {"sku": "ABC123", "quantity": 2, ...},
#   "timestamp": "2025-11-07T12:00:01"
# }
```

### Using CartServiceV2 (Post-Change)
```python
from cart_service_v2 import CartServiceV2

service = CartServiceV2(
    v2_base_url="http://localhost:8002",
    v1_fallback_url="http://localhost:8001"
)

# Check stock with region awareness
result = service.check_stock_v2(
    sku="ABC123",
    quantity=5,
    region_id="ap-sg-1",
    warehouse_group="WG-2"
)
print(result)
# Output: {
#   "available": true,
#   "quantity": 12,
#   "sku": "ABC123",
#   "availability_status": "confirmed",
#   "sync_timestamp": "2025-11-07T12:00:00Z",
#   "source": "v2",
#   "latency_ms": 156.89,
#   "timestamp": "2025-11-07T12:00:00"
# }

# Or if async (returns 202):
# result.get("poll_attempts") indicates polling was used

# Add to cart with region
cart_result = service.add_to_cart(
    sku="ABC123",
    quantity=2,
    region_id="ap-sg-1",
    warehouse_group="WG-2"
)
```

### Handling Async Responses
```python
# v2 client handles this automatically
result = service.check_stock_v2(
    sku="GHI789",
    quantity=10,
    region_id="ap-sg-1",
    warehouse_group="WG-2",
    enable_async_polling=True  # Enable polling for 202 responses
)

# If 202 was received, result contains polling metadata:
if "poll_attempts" in result:
    print(f"Required {result['poll_attempts']} polling attempts")
    print(f"Source was v2-polled")
```

---

## Key Metrics Interpretation

### Latency Percentiles
- **p50** (median): 50% of requests are faster
- **p95** (95th percentile): 95% of requests are faster; 5% may be slower
- **Example**: p50=150ms, p95=250ms means most requests are ~150ms, but occasional ones hit 250ms

### Pass Rate
- **Target**: 100% for both v1 and v2
- **Acceptable**: >95% (allows for transient failures)
- **Investigation needed**: <95%

### Latency Regression
- **Acceptable**: <20% increase from v1 to v2 (overhead is reasonable)
- **Watch**: 20-50% increase (needs optimization review)
- **Unacceptable**: >50% increase (indicates design problem)

---

## Next Steps

1. **Review Results**
   ```bash
   cat results/compare_report.md
   ```

2. **Evaluate Recommendations**
   - Review rollout strategy
   - Assess production readiness
   - Plan staging validation

3. **Implement Feature Flag**
   - Add configuration for v2 enable/disable
   - Deploy to staging with v2 disabled
   - Shadow-run v2 responses

4. **Production Deployment**
   - Follow phased rollout (canary, gradual increase)
   - Monitor observability metrics
   - Keep fallback mechanism active

5. **Post-Migration**
   - Monitor v2 metrics for 2 weeks
   - Collect user feedback on stock accuracy
   - Plan v1 decommissioning

---

## Support & Questions

For issues or clarifications:
1. Check test logs: `Project_A_PreChange/logs/` and `Project_B_PostChange/logs/`
2. Review comparison report: `results/compare_report.md`
3. Validate test data: `test_data.json`
4. Check mock server behavior: review mock_v1_server.py and mock_v2_server.py

---

**Generated**: 2025-11-07  
**Scope**: AI Model Evaluation - API Change (Feature & improvement)
