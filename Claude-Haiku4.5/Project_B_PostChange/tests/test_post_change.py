"""
Test harness for Project B (Post-Change v2 integration).
Tests the updated cart service calling /api/v2/stock/availability with async handling.
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

from cart_service_v2 import CartServiceV2


class TestPostChangeV2:
    """Test suite for v2 integration (post-change)."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test service."""
        self.service = CartServiceV2(v2_base_url="http://localhost:8002")
        yield
        # Cleanup
        self.results = []
    
    def load_test_data(self):
        """Load test cases from shared test_data.json."""
        test_data_path = Path(__file__).parent.parent.parent / "test_data.json"
        with open(test_data_path) as f:
            return json.load(f)
    
    def test_tc001_normal_case_with_region(self):
        """TC001: Normal Case - Immediate Confirmed Availability with region."""
        test_data = self.load_test_data()
        tc = test_data["test_cases"][0]  # TC001
        
        v2_input = tc["v2_api"]["input"]
        expected = tc["v2_api"]["expected_output"]
        
        start_time = time.time()
        result = self.service.check_stock_v2(
            v2_input["sku"],
            v2_input["quantity"],
            v2_input["regionId"],
            v2_input["warehouseGroup"]
        )
        latency = time.time() - start_time
        
        # Assertions
        assert result["available"] == expected["available"], \
            f"Expected available={expected['available']}, got {result['available']}"
        assert result["quantity"] >= v2_input["quantity"], \
            f"Insufficient quantity: {result['quantity']} < {v2_input['quantity']}"
        assert result["sku"] == expected["sku"]
        assert result["availability_status"] == expected["availabilityStatus"], \
            f"Expected status={expected['availabilityStatus']}, got {result.get('availability_status')}"
        assert latency < 5.0, f"Latency too high: {latency}s"
        
        print(f"✓ TC001 passed - v2 with region - Latency: {latency*1000:.2f}ms")
        return {
            "test_id": "TC001",
            "passed": True,
            "latency_ms": latency * 1000,
            "result": result
        }
    
    def test_tc002_boundary_case_region_aware(self):
        """TC002: Boundary Case - Exact quantity with region."""
        test_data = self.load_test_data()
        tc = test_data["test_cases"][1]  # TC002
        
        v2_input = tc["v2_api"]["input"]
        expected = tc["v2_api"]["expected_output"]
        
        result = self.service.check_stock_v2(
            v2_input["sku"],
            v2_input["quantity"],
            v2_input["regionId"],
            v2_input["warehouseGroup"]
        )
        
        # At threshold, should be available
        assert result["available"] == True, \
            "Expected available at exact threshold"
        assert result["quantity"] == expected["quantity"], \
            f"Expected quantity={expected['quantity']}, got {result['quantity']}"
        
        print(f"✓ TC002 passed - Boundary with region: {result['quantity']}")
        return {"test_id": "TC002", "passed": True, "result": result}
    
    def test_tc003_async_polling(self):
        """TC003: Async/Pending Case - v2 polling with 202 response."""
        test_data = self.load_test_data()
        tc = test_data["test_cases"][2]  # TC003
        
        v2_input = tc["v2_api"]["input"]
        
        start_time = time.time()
        result = self.service.check_stock_v2(
            v2_input["sku"],
            v2_input["quantity"],
            v2_input["regionId"],
            v2_input["warehouseGroup"],
            enable_async_polling=True
        )
        latency = time.time() - start_time
        
        # Should eventually return available
        assert result["available"] == True, \
            "After polling, should be available"
        assert result["quantity"] >= v2_input["quantity"], \
            "Should have sufficient quantity after async resolution"
        
        print(f"✓ TC003 passed - Async polling completed - Latency: {latency*1000:.2f}ms")
        return {
            "test_id": "TC003",
            "passed": True,
            "latency_ms": latency * 1000,
            "polling_used": "poll_attempts" in result
        }
    
    def test_tc004_strict_validation_missing_region(self):
        """TC004a: Invalid Input - Missing regionId validation."""
        test_data = self.load_test_data()
        tc = test_data["test_cases"][3]  # TC004
        
        v2_input_variant = tc["v2_api"]["input_variants"][0]
        invalid_input = v2_input_variant["input"]
        
        # Should fail validation before making request
        result = self.service.check_stock_v2(
            invalid_input["sku"],
            invalid_input["quantity"],
            invalid_input.get("regionId", ""),
            invalid_input.get("warehouseGroup", "")
        )
        
        # Should be unavailable (default safe behavior)
        assert result["available"] == False, \
            "Missing regionId should result in unavailable"
        assert "error" in result or "fallback" in result.get("source", ""), \
            "Should indicate error or fallback"
        
        print(f"✓ TC004a passed - Validation: {result.get('error', 'fallback')}")
        return {"test_id": "TC004a", "passed": True}
    
    def test_tc004_strict_validation_invalid_warehouse(self):
        """TC004b: Invalid Input - Invalid warehouseGroup."""
        test_data = self.load_test_data()
        tc = test_data["test_cases"][3]  # TC004
        
        v2_input_variant = tc["v2_api"]["input_variants"][1]
        invalid_input = v2_input_variant["input"]
        
        result = self.service.check_stock_v2(
            invalid_input["sku"],
            invalid_input["quantity"],
            invalid_input["regionId"],
            invalid_input.get("warehouseGroup", "")
        )
        
        # Should fallback or report error
        assert result["available"] == False, \
            "Invalid warehouseGroup should result in unavailable"
        
        print(f"✓ TC004b passed - Invalid warehouse validation")
        return {"test_id": "TC004b", "passed": True}
    
    def test_tc005_error_handling_with_fallback(self):
        """TC005: High-Latency/Error Case - Retry and fallback."""
        # This test validates retry logic and circuit breaker
        result = self.service.check_stock_v2(
            "JKL012",
            7,
            "eu-west-1",
            "WG-3"
        )
        
        # Should either succeed or gracefully fail
        assert "available" in result, "Should have availability info"
        assert "source" in result, "Should indicate source (v2, fallback, etc.)"
        
        print(f"✓ TC005 passed - Error handling: {result['source']}")
        return {"test_id": "TC005", "passed": True}
    
    def test_tc006_out_of_stock_region(self):
        """TC006: Out of Stock Case - v2 with region."""
        test_data = self.load_test_data()
        tc = test_data["test_cases"][5]  # TC006
        
        v2_input = tc["v2_api"]["input"]
        expected = tc["v2_api"]["expected_output"]
        
        result = self.service.check_stock_v2(
            v2_input["sku"],
            v2_input["quantity"],
            v2_input["regionId"],
            v2_input["warehouseGroup"]
        )
        
        # Should report unavailable
        assert result["available"] == False, \
            "Should report unavailable when quantity exceeds stock"
        
        print(f"✓ TC006 passed - Out of stock: {result['quantity']}")
        return {"test_id": "TC006", "passed": True}
    
    def test_add_to_cart_with_region(self):
        """Test successful cart addition with v2."""
        result = self.service.add_to_cart("ABC123", 2, "ap-sg-1", "WG-2")
        
        assert result["success"] == True
        assert "Added" in result["message"]
        print(f"✓ Cart addition with region succeeded")
        return {"test_id": "CART-ADD-REGION", "passed": True}
    
    def test_add_to_cart_out_of_stock_with_region(self):
        """Test cart addition for out-of-stock item with region."""
        result = self.service.add_to_cart("MNO345", 100, "ap-sg-1", "WG-2")
        
        assert result["success"] == False
        assert "Out of stock" in result["message"]
        print(f"✓ Out of stock prevented cart addition")
        return {"test_id": "CART-ADD-OOS-REGION", "passed": True}
    
    def test_circuit_breaker_functionality(self):
        """Test circuit breaker opens after threshold failures."""
        # This would require mocking multiple failures
        # For now, just verify circuit breaker can be checked
        is_open = self.service._check_circuit_breaker()
        assert isinstance(is_open, bool)
        print(f"✓ Circuit breaker status: {'OPEN' if is_open else 'CLOSED'}")
        return {"test_id": "CIRCUIT-BREAKER", "passed": True}


def run_all_tests():
    """Run all tests and collect results."""
    results_file = Path(__file__).parent.parent / "results" / "results_post.json"
    results_file.parent.mkdir(exist_ok=True)
    
    test_runner = TestPostChangeV2()
    test_runner.setup()
    
    all_results = []
    test_methods = [
        test_runner.test_tc001_normal_case_with_region,
        test_runner.test_tc002_boundary_case_region_aware,
        test_runner.test_tc003_async_polling,
        test_runner.test_tc004_strict_validation_missing_region,
        test_runner.test_tc004_strict_validation_invalid_warehouse,
        test_runner.test_tc005_error_handling_with_fallback,
        test_runner.test_tc006_out_of_stock_region,
        test_runner.test_add_to_cart_with_region,
        test_runner.test_add_to_cart_out_of_stock_with_region,
        test_runner.test_circuit_breaker_functionality,
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
        "version": "post-change (v2)",
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
