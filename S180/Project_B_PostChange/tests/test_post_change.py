"""
Test suite for Project B - New API Integration
"""
import pytest
import json
import logging
from pathlib import Path
import sys
import time

sys.path.append(str(Path(__file__).parent.parent / "src"))
from cart_service_v2 import CartServiceV2

class TestPostChange:
    @classmethod
    def setup_class(cls):
        cls.setup_logging()
        cls.load_test_data()
        cls.service = CartServiceV2(base_url="http://localhost:8002", fallback_url="http://localhost:8001")

    @classmethod
    def setup_logging(cls):
        log_file = Path(__file__).parent.parent / "logs" / "log_post.txt"
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
        test_data_path = Path(__file__).parent.parent.parent.parent / "test_data.json"
        with open(test_data_path, 'r') as f:
            cls.test_data = json.load(f)

    def test_normal_case_v2(self):
        tc = next(tc for tc in self.test_data["test_cases"] if tc["id"] == "normal_case")
        res = self.service.check_stock(tc["input"]["sku"], tc["input"]["regionId"], tc["input"]["warehouseGroup"])
        assert res["available"] == True
        assert res["quantity"] == 12
        assert res["note"] == "confirmed"
        assert res["api_version"] == "v2"

    def test_boundary_case_zero_v2(self):
        tc = next(tc for tc in self.test_data["test_cases"] if tc["id"] == "boundary_case_zero")
        res = self.service.check_stock(tc["input"]["sku"], tc["input"]["regionId"], tc["input"]["warehouseGroup"])
        assert res["available"] == False
        assert res["quantity"] == 0
        assert res["note"] == "confirmed"

    def test_async_pending_case_v2(self):
        tc = next(tc for tc in self.test_data["test_cases"] if tc["id"] == "async_pending_case")
        res = self.service.check_stock(tc["input"]["sku"], tc["input"]["regionId"], tc["input"]["warehouseGroup"])
        # Service should poll and eventually get confirmed
        assert res["available"] == True
        assert res["quantity"] == 5
        assert res["note"] == "confirmed"

    def test_invalid_input_v2(self):
        tc = next(tc for tc in self.test_data["test_cases"] if tc["id"] == "invalid_input")
        # Missing regionId should cause a graceful validation failure or v2 400 and fallback
        res = self.service.check_stock(tc["input"]["sku"], tc["input"].get("regionId"), tc["input"].get("warehouseGroup"))
        assert res.get("available") in (False,)
        assert "fallback" in res.get("note") or "validation" in res.get("note")

    def test_high_latency_case_v2(self):
        tc = next(tc for tc in self.test_data["test_cases"] if tc["id"] == "high_latency_case")
        res = self.service.check_stock(tc["input"]["sku"], tc["input"]["regionId"], tc["input"]["warehouseGroup"])
        assert res.get("available") == False
        assert "fallback" in res.get("note") or "timeout" in res.get("note")

    def test_process_multiple_items_v2(self):
        items = [
            {"sku": "ABC123", "regionId": "ap-sg-1", "warehouseGroup": "WG-2"},
            {"sku": "XYZ789", "regionId": "us-east-1", "warehouseGroup": "WG-1"},
            {"sku": "DEF456", "regionId": "eu-west-1", "warehouseGroup": "WG-3"}
        ]
        res = self.service.process_cart_items(items)
        assert res["total_items"] == 3
        assert res["processed_items"] == 3
        assert len(res["results"]) == 3


def save_results(results):
    results_file = Path(__file__).parent.parent / "results" / "results_post.json"
    results_file.parent.mkdir(exist_ok=True)
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    pytest_args = [
        __file__,
        "--json-report",
        f"--json-report-file={Path(__file__).parent.parent / 'results' / 'pytest_results_post.json'}",
        "-v"
    ]
    exit(pytest.main(pytest_args))