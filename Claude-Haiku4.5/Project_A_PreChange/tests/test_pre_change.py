"""
Test harness for Project A (Pre-Change v1 integration).
Tests the legacy cart service calling /api/v1/checkStock.
"""
import json
import time
import pytest
import sys
import os
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cart_service_v1 import CartServiceV1


class TestPreChangeV1:
    """Test suite for v1 integration (pre-change)."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test service."""
        self.service = CartServiceV1(v1_base_url="http://localhost:8001")
        yield
        # Cleanup
        self.results = []
    
    def load_test_data(self):
        """Load test cases from shared test_data.json."""
        test_data_path = Path(__file__).parent.parent.parent / "test_data.json"
        with open(test_data_path) as f:
            return json.load(f)
    
    def test_tc001_normal_case_immediate_availability(self):
        """TC001: Normal Case - Immediate Confirmed Availability."""
        test_data = self.load_test_data()
        tc = test_data["test_cases"][0]  # TC001
        
        v1_input = tc["v1_api"]["input"]
        expected = tc["v1_api"]["expected_output"]
        
        start_time = time.time()
        result = self.service.check_stock(v1_input["sku"], v1_input["quantity"])
        latency = time.time() - start_time
        
        # Assertions
        assert result["available"] == expected["available"], \
            f"Expected available={expected['available']}, got {result['available']}"
        assert result["quantity"] >= v1_input["quantity"], \
            f"Insufficient quantity: {result['quantity']} < {v1_input['quantity']}"
        assert result["sku"] == expected["sku"]
        assert latency < 5.0, f"Latency too high: {latency}s"
        
        print(f"✓ TC001 passed - Latency: {latency*1000:.2f}ms")
        return {
            "test_id": "TC001",
            "passed": True,
            "latency_ms": latency * 1000,
            "result": result
        }
    
    def test_tc002_boundary_case_exact_quantity(self):
        """TC002: Boundary Case - Zero Quantity at Threshold."""
        test_data = self.load_test_data()
        tc = test_data["test_cases"][1]  # TC002
        
        v1_input = tc["v1_api"]["input"]
        expected = tc["v1_api"]["expected_output"]
        
        result = self.service.check_stock(v1_input["sku"], v1_input["quantity"])
        
        # At threshold, should be available
        assert result["available"] == True, \
            f"Expected available at exact threshold"
        assert result["quantity"] == expected["quantity"], \
            f"Expected quantity={expected['quantity']}, got {result['quantity']}"
        
        print(f"✓ TC002 passed - Boundary quantity: {result['quantity']}")
        return {"test_id": "TC002", "passed": True, "result": result}
    
    def test_tc003_async_case_v1_sync_baseline(self):
        """TC003: Async Case - v1 returns synchronously (baseline)."""
        test_data = self.load_test_data()
        tc = test_data["test_cases"][2]  # TC003
        
        v1_input = tc["v1_api"]["input"]
        
        start_time = time.time()
        result = self.service.check_stock(v1_input["sku"], v1_input["quantity"])
        latency = time.time() - start_time
        
        # v1 is always synchronous - no polling needed
        assert result["available"] == True, \
            "v1 should return available for this SKU"
        assert result["quantity"] >= v1_input["quantity"]
        assert latency < 2.0, f"v1 should be fast: {latency}s"
        
        print(f"✓ TC003 passed - v1 sync baseline: {latency*1000:.2f}ms")
        return {"test_id": "TC003", "passed": True, "latency_ms": latency * 1000}
    
    def test_tc004_invalid_input_v1_permissive(self):
        """TC004: Invalid Input - v1 is permissive with validation."""
        test_data = self.load_test_data()
        tc = test_data["test_cases"][3]  # TC004
        
        v1_input = tc["v1_api"]["input"]
        
        # v1 handles missing regionId gracefully (legacy behavior)
        result = self.service.check_stock(v1_input["sku"], v1_input["quantity"])
        
        # v1 is lenient - it should still work
        assert "error" not in result or result.get("available") is not None, \
            "v1 should handle missing region gracefully"
        
        print(f"✓ TC004 passed - v1 permissive validation")
        return {"test_id": "TC004", "passed": True, "result": result}
    
    def test_tc005_high_latency_case(self):
        """TC005: High-Latency / Error Case - Timeout handling."""
        test_data = self.load_test_data()
        tc = test_data["test_cases"][4]  # TC005
        
        v1_input = tc["v1_api"]["input"]
        
        # v1 should handle gracefully or timeout
        result = self.service.check_stock(v1_input["sku"], v1_input["quantity"])
        
        # Should either succeed or have error field
        assert "available" in result or "error" in result, \
            "Should have either availability or error info"
        
        print(f"✓ TC005 passed - Error handling: {result.get('error', 'Success')}")
        return {"test_id": "TC005", "passed": True, "result": result}
    
    def test_tc006_out_of_stock(self):
        """TC006: Out of Stock Case."""
        test_data = self.load_test_data()
        tc = test_data["test_cases"][5]  # TC006
        
        v1_input = tc["v1_api"]["input"]
        expected = tc["v1_api"]["expected_output"]
        
        result = self.service.check_stock(v1_input["sku"], v1_input["quantity"])
        
        # Should report unavailable
        assert result["available"] == False, \
            "Should report unavailable when quantity exceeds stock"
        assert result["quantity"] == expected["quantity"], \
            f"Expected quantity={expected['quantity']}, got {result['quantity']}"
        
        print(f"✓ TC006 passed - Out of stock detected")
        return {"test_id": "TC006", "passed": True, "result": result}
    
    def test_add_to_cart_success(self):
        """Test successful cart addition."""
        result = self.service.add_to_cart("ABC123", 2)
        
        assert result["success"] == True
        assert "Added" in result["message"]
        print(f"✓ Cart addition succeeded")
        return {"test_id": "CART-ADD-SUCCESS", "passed": True}
    
    def test_add_to_cart_out_of_stock(self):
        """Test cart addition for out-of-stock item."""
        result = self.service.add_to_cart("MNO345", 100)
        
        assert result["success"] == False
        assert "Out of stock" in result["message"]
        print(f"✓ Out of stock prevented cart addition")
        return {"test_id": "CART-ADD-OOS", "passed": True}


def run_all_tests():
    """Run all tests and collect results."""
    results_file = Path(__file__).parent.parent / "results" / "results_pre.json"
    results_file.parent.mkdir(exist_ok=True)
    
    test_runner = TestPreChangeV1()
    test_runner.setup()
    
    all_results = []
    test_methods = [
        test_runner.test_tc001_normal_case_immediate_availability,
        test_runner.test_tc002_boundary_case_exact_quantity,
        test_runner.test_tc003_async_case_v1_sync_baseline,
        test_runner.test_tc004_invalid_input_v1_permissive,
        test_runner.test_tc005_high_latency_case,
        test_runner.test_tc006_out_of_stock,
        test_runner.test_add_to_cart_success,
        test_runner.test_add_to_cart_out_of_stock,
    ]
    
    for test_method in test_methods:
        try:
            result = test_method()
            all_results.append(result)
        except AssertionError as e:
            all_results.append({
                "test_id": test_method.__name__,
                "passed": False,
                "error": str(e)
            })
            print(f"✗ {test_method.__name__} failed: {e}")
        except Exception as e:
            all_results.append({
                "test_id": test_method.__name__,
                "passed": False,
                "error": str(e)
            })
            print(f"✗ {test_method.__name__} error: {e}")
    
    # Save results
    summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "version": "pre-change (v1)",
        "total_tests": len(all_results),
        "passed": sum(1 for r in all_results if r.get("passed", False)),
        "failed": sum(1 for r in all_results if not r.get("passed", False)),
        "results": all_results
    }
    
    with open(results_file, "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✓ Results saved to {results_file}")
    return summary


if __name__ == "__main__":
    summary = run_all_tests()
    print(f"\nSummary: {summary['passed']}/{summary['total_tests']} tests passed")
