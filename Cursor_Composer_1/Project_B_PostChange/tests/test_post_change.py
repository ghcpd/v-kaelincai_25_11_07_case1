"""
Test harness for Post-Change (v2) implementation
"""
import sys
import os
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cart_service_v2 import CartServiceV2

# Configuration
MOCK_API_URL = "http://localhost:8002"
SERVICE_TIMEOUT = 10
RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'results')
LOGS_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)


class TestRunner:
    """Test runner for post-change implementation"""
    
    def __init__(self):
        self.service = CartServiceV2(base_url=MOCK_API_URL, enable_fallback=True)
        self.test_results = []
        self.metrics = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "latencies": [],
            "errors": 0,
            "timeouts": 0,
            "fallbacks": 0,
            "pending_responses": 0
        }
        
    def wait_for_mock_api(self, max_retries=10, delay=1):
        """Wait for mock API to be ready"""
        for i in range(max_retries):
            try:
                response = requests.get(f"{MOCK_API_URL}/health", timeout=2)
                if response.status_code == 200:
                    print(f"✓ Mock API is ready")
                    return True
            except:
                pass
            time.sleep(delay)
        print(f"✗ Mock API not ready after {max_retries} retries")
        return False
    
    def load_test_data(self) -> List[Dict]:
        """Load test cases from JSON"""
        test_data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'test_data.json')
        with open(test_data_path, 'r') as f:
            return json.load(f)
    
    def validate_result(self, test_case: Dict, actual: Dict) -> Dict[str, Any]:
        """Validate test result against expected output"""
        expected = test_case["expected"]
        test_id = test_case["test_id"]
        
        validation_result = {
            "test_id": test_id,
            "name": test_case["name"],
            "passed": True,
            "assertions": [],
            "actual": actual,
            "expected": expected
        }
        
        # Check status code
        if "status_code" in expected:
            status_match = actual.get("status_code") == expected["status_code"]
            validation_result["assertions"].append({
                "check": "status_code",
                "expected": expected["status_code"],
                "actual": actual.get("status_code"),
                "passed": status_match
            })
            if not status_match:
                validation_result["passed"] = False
        
        # Check availability
        if "available" in expected:
            avail_match = actual.get("available") == expected["available"]
            validation_result["assertions"].append({
                "check": "available",
                "expected": expected["available"],
                "actual": actual.get("available"),
                "passed": avail_match
            })
            if not avail_match:
                validation_result["passed"] = False
        
        # Check quantity (if not error case)
        if "quantity" in expected and "error" not in expected:
            qty_match = actual.get("quantity") == expected["quantity"]
            validation_result["assertions"].append({
                "check": "quantity",
                "expected": expected["quantity"],
                "actual": actual.get("quantity"),
                "passed": qty_match
            })
            if not qty_match:
                validation_result["passed"] = False
        
        # Check availability status
        if "availability_status" in expected:
            status_match = actual.get("availability_status") == expected["availability_status"]
            validation_result["assertions"].append({
                "check": "availability_status",
                "expected": expected["availability_status"],
                "actual": actual.get("availability_status"),
                "passed": status_match
            })
            if not status_match:
                validation_result["passed"] = False
        
        # Check sync timestamp presence
        if "sync_timestamp" in expected and expected["sync_timestamp"] == "present":
            timestamp_present = actual.get("sync_timestamp") is not None
            validation_result["assertions"].append({
                "check": "sync_timestamp_present",
                "expected": "present",
                "actual": "present" if timestamp_present else "missing",
                "passed": timestamp_present
            })
            if not timestamp_present:
                validation_result["passed"] = False
        
        # Check latency threshold (if specified)
        if "latency_ms" in expected and isinstance(expected["latency_ms"], str):
            if expected["latency_ms"].startswith(">"):
                threshold = float(expected["latency_ms"][1:])
                latency_ok = actual.get("latency_ms", 0) > threshold
                validation_result["assertions"].append({
                    "check": "latency_threshold",
                    "expected": f">{threshold}",
                    "actual": actual.get("latency_ms"),
                    "passed": latency_ok
                })
                if not latency_ok:
                    validation_result["passed"] = False
        
        # Check error message (if error case)
        if "error" in expected:
            error_match = expected["error"] in str(actual.get("error", ""))
            validation_result["assertions"].append({
                "check": "error_message",
                "expected": expected["error"],
                "actual": actual.get("error", ""),
                "passed": error_match
            })
            if not error_match:
                validation_result["passed"] = False
        
        # Track fallback usage
        if "v1_fallback" in actual.get("source", "") or "fallback" in actual.get("note", ""):
            self.metrics["fallbacks"] += 1
        
        # Track pending responses
        if actual.get("availability_status") == "pending":
            self.metrics["pending_responses"] += 1
        
        return validation_result
    
    def run_test_case(self, test_case: Dict) -> Dict[str, Any]:
        """Run a single test case"""
        test_id = test_case["test_id"]
        print(f"\n[{test_id}] {test_case['name']}")
        print(f"  Input: {test_case['input']}")
        
        start_time = time.time()
        
        try:
            input_data = test_case["input"]
            sku = input_data.get("sku")
            region_id = input_data.get("regionId")
            warehouse_group = input_data.get("warehouseGroup")
            
            # Determine if we should wait for confirmation (for async cases)
            wait_for_confirmation = test_case.get("category") == "async"
            
            result = self.service.check_stock(
                sku=sku or "",
                region_id=region_id or "",
                warehouse_group=warehouse_group or "",
                wait_for_confirmation=wait_for_confirmation
            )
            
            elapsed = (time.time() - start_time) * 1000
            
            # Record metrics
            self.metrics["latencies"].append(result.get("latency_ms", elapsed))
            if result.get("status_code", 200) >= 500:
                self.metrics["errors"] += 1
            if result.get("error") == "timeout":
                self.metrics["timeouts"] += 1
            
            # Validate result
            validation = self.validate_result(test_case, result)
            
            if validation["passed"]:
                print(f"  ✓ PASSED")
                self.metrics["passed"] += 1
            else:
                print(f"  ✗ FAILED")
                for assertion in validation["assertions"]:
                    if not assertion["passed"]:
                        print(f"    - {assertion['check']}: expected {assertion['expected']}, got {assertion['actual']}")
                self.metrics["failed"] += 1
            
            validation["elapsed_ms"] = elapsed
            return validation
            
        except Exception as e:
            print(f"  ✗ ERROR: {str(e)}")
            self.metrics["failed"] += 1
            self.metrics["errors"] += 1
            return {
                "test_id": test_id,
                "name": test_case["name"],
                "passed": False,
                "error": str(e),
                "elapsed_ms": (time.time() - start_time) * 1000
            }
    
    def run_all_tests(self):
        """Run all test cases"""
        print("=" * 60)
        print("Post-Change Test Suite")
        print("=" * 60)
        
        if not self.wait_for_mock_api():
            print("ERROR: Mock API not available")
            return
        
        test_cases = self.load_test_data()
        self.metrics["total_tests"] = len(test_cases)
        
        for test_case in test_cases:
            result = self.run_test_case(test_case)
            self.test_results.append(result)
        
        # Calculate metrics
        if self.metrics["latencies"]:
            sorted_latencies = sorted(self.metrics["latencies"])
            n = len(sorted_latencies)
            self.metrics["latency_p50"] = sorted_latencies[n // 2]
            self.metrics["latency_p95"] = sorted_latencies[int(n * 0.95)]
            self.metrics["latency_p99"] = sorted_latencies[int(n * 0.99)]
            self.metrics["latency_mean"] = sum(sorted_latencies) / n
            self.metrics["latency_min"] = min(sorted_latencies)
            self.metrics["latency_max"] = max(sorted_latencies)
        
        # Print summary
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        print(f"Total tests: {self.metrics['total_tests']}")
        print(f"Passed: {self.metrics['passed']}")
        print(f"Failed: {self.metrics['failed']}")
        print(f"Errors: {self.metrics['errors']}")
        print(f"Timeouts: {self.metrics['timeouts']}")
        print(f"Fallbacks: {self.metrics['fallbacks']}")
        print(f"Pending responses: {self.metrics['pending_responses']}")
        if self.metrics["latencies"]:
            print(f"\nLatency Metrics:")
            print(f"  Mean: {self.metrics['latency_mean']:.2f}ms")
            print(f"  P50: {self.metrics['latency_p50']:.2f}ms")
            print(f"  P95: {self.metrics['latency_p95']:.2f}ms")
            print(f"  P99: {self.metrics['latency_p99']:.2f}ms")
            print(f"  Min: {self.metrics['latency_min']:.2f}ms")
            print(f"  Max: {self.metrics['latency_max']:.2f}ms")
    
    def save_results(self):
        """Save test results to JSON"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "project": "Project_B_PostChange",
            "metrics": self.metrics,
            "test_results": self.test_results
        }
        
        results_path = os.path.join(RESULTS_DIR, "results_post.json")
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to: {results_path}")


if __name__ == '__main__':
    runner = TestRunner()
    runner.run_all_tests()
    runner.save_results()

