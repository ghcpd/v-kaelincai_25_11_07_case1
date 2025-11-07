"""
Test suite for Project A - Legacy API Integration
"""
import pytest
import json
import time
import logging
import subprocess
import sys
import os
from pathlib import Path
import requests
from datetime import datetime

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))
from cart_service_v1 import CartServiceV1

class TestPreChange:
    @classmethod
    def setup_class(cls):
        """Setup test environment"""
        cls.setup_logging()
        cls.load_test_data()
        cls.service = CartServiceV1(base_url="http://localhost:8001")
        
    @classmethod
    def setup_logging(cls):
        """Configure logging for tests"""
        log_file = Path(__file__).parent.parent / "logs" / "log_pre.txt"
        log_file.parent.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        cls.logger = logging.getLogger(__name__)
        
    @classmethod
    def load_test_data(cls):
        """Load test data from JSON file"""
        test_data_path = Path(__file__).parent.parent.parent.parent / "test_data.json"
        with open(test_data_path, 'r') as f:
            cls.test_data = json.load(f)
            
    def test_normal_case(self):
        """Test normal case - API returns confirmed availability"""
        test_case = next(tc for tc in self.test_data["test_cases"] if tc["id"] == "normal_case")
        
        sku = test_case["input"]["sku"]
        result = self.service.check_stock(sku)
        
        assert result["available"] == True
        assert result["quantity"] > 0
        assert result["api_version"] == "v1"
        assert result["response_time"] < 2.0
        
        self.logger.info(f"Normal case passed: {result}")
        
    def test_boundary_case_zero(self):
        """Test boundary case - zero quantity"""
        test_case = next(tc for tc in self.test_data["test_cases"] if tc["id"] == "boundary_case_zero")
        
        sku = test_case["input"]["sku"]
        result = self.service.check_stock(sku)
        
        assert result["available"] == False
        assert result["quantity"] == 0
        assert result["api_version"] == "v1"
        
        self.logger.info(f"Boundary case passed: {result}")
        
    def test_async_pending_case(self):
        """Test async case - v1 doesn't support async, so just normal processing"""
        test_case = next(tc for tc in self.test_data["test_cases"] if tc["id"] == "async_pending_case")
        
        sku = test_case["input"]["sku"]
        result = self.service.check_stock(sku)
        
        # v1 API doesn't have async concept, so it just returns current stock
        assert result["available"] == True
        assert result["quantity"] > 0
        assert result["api_version"] == "v1"
        
        self.logger.info(f"Async case (v1 behavior) passed: {result}")
        
    def test_invalid_input(self):
        """Test invalid input handling"""
        test_case = next(tc for tc in self.test_data["test_cases"] if tc["id"] == "invalid_input")
        
        sku = test_case["input"]["sku"]
        result = self.service.check_stock(sku)
        
        # v1 API should still work as it only needs SKU
        assert "available" in result
        assert result["api_version"] == "v1"
        
        self.logger.info(f"Invalid input case passed: {result}")
        
    def test_high_latency_case(self):
        """Test high latency / timeout case"""
        test_case = next(tc for tc in self.test_data["test_cases"] if tc["id"] == "high_latency_case")
        
        sku = test_case["input"]["sku"]
        result = self.service.check_stock(sku)
        
        # Should timeout and return error
        assert result["available"] == False
        assert "timeout" in result["note"]
        assert result["api_version"] == "v1"
        
        self.logger.info(f"High latency case passed: {result}")
        
    def test_process_multiple_items(self):
        """Test processing multiple cart items"""
        test_skus = ["ABC123", "XYZ789", "DEF456"]
        result = self.service.process_cart_items(test_skus)
        
        assert result["total_items"] == 3
        assert result["processed_items"] == 3
        assert len(result["results"]) == 3
        assert result["total_response_time"] > 0
        
        self.logger.info(f"Multiple items test passed: {result}")

def save_results(results):
    """Save test results to JSON file"""
    results_file = Path(__file__).parent.parent / "results" / "results_pre.json"
    results_file.parent.mkdir(exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    # Run tests and collect results
    import pytest
    
    # Configure pytest to generate JSON report
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    
    pytest_args = [
        __file__,
        "--json-report",
        f"--json-report-file={results_dir}/pytest_results_pre.json",
        "-v"
    ]
    
    exit_code = pytest.main(pytest_args)
    
    # Save additional results
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "project": "Project_A_PreChange",
        "api_version": "v1",
        "exit_code": exit_code,
        "summary": {
            "total_tests": 6,
            "passed_tests": 6 if exit_code == 0 else 0,
            "api_endpoint": "/api/v1/checkStock",
            "features_tested": [
                "basic_stock_check",
                "boundary_conditions", 
                "timeout_handling",
                "multiple_items_processing"
            ]
        }
    }
    
    save_results(test_results)