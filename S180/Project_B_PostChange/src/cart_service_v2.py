"""
Cart Service V2 - New API Integration
Calls /api/v2/stock/availability with regionId and warehouseGroup
Supports async/pending status with polling and fallback to v1 adapter
"""
import requests
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime

class V2AdapterException(Exception):
    pass

class CartServiceV2:
    def __init__(self, base_url: str = "http://localhost:8002", fallback_url: str = "http://localhost:8001", timeout: float = 5.0, poll_interval: float = 1.0, max_poll_attempts: int = 3):
        self.base_url = base_url
        self.fallback_url = fallback_url
        self.timeout = timeout
        self.poll_interval = poll_interval
        self.max_poll_attempts = max_poll_attempts
        self.logger = logging.getLogger(__name__)

    def call_v2(self, sku: str, regionId: str, warehouseGroup: str, poll: bool = False) -> Dict[str, Any]:
        start_time = time.time()
        payload = {
            "sku": sku,
            "regionId": regionId,
            "warehouseGroup": warehouseGroup
        }
        try:
            self.logger.info(f"Calling v2 API for SKU {sku} with region {regionId} and wg {warehouseGroup} (poll={poll})")
            url = f"{self.base_url}/api/v2/stock/availability"
            if poll:
                url = url + "?poll=1"
            resp = requests.post(url, json=payload, timeout=self.timeout)
            duration = time.time() - start_time
            if resp.status_code == 200:
                data = resp.json()
                data["response_time"] = duration
                return data
            else:
                raise V2AdapterException(f"v2 API returned status {resp.status_code}")
        except requests.exceptions.Timeout:
            duration = time.time() - start_time
            raise V2AdapterException("timeout")
        except Exception as e:
            raise V2AdapterException(str(e))

    def poll_for_update(self, sku: str, regionId: str, warehouseGroup: str, syncTimestamp: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Poll the v2 API for eventual consistency updates after a pending result"""
        attempts = 0
        while attempts < self.max_poll_attempts:
            attempts += 1
            self.logger.info(f"Polling v2 for SKU {sku} attempt {attempts}")
            try:
                res = self.call_v2(sku, regionId, warehouseGroup)
                if res.get("availabilityStatus") != "pending":
                    return res
            except V2AdapterException as e:
                self.logger.warning(f"Polling attempt error: {e}")
            time.sleep(self.poll_interval)
        return None

    def fallback_to_v1(self, sku: str) -> Dict[str, Any]:
        # Minimal v1 fallback logic: call legacy endpoint
        try:
            resp = requests.post(f"{self.fallback_url}/api/v1/checkStock", json={"sku": sku}, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "available": data.get("inStock", False),
                    "quantity": data.get("stockLevel", 0),
                    "note": "fallback to v1",
                    "api_version": "v1"
                }
        except Exception:
            pass
        return {"available": False, "quantity": 0, "note": "fallback failed", "api_version": "v1"}

    def check_stock(self, sku: str, regionId: Optional[str], warehouseGroup: Optional[str]) -> Dict[str, Any]:
        start_time = time.time()
        # Input validation
        if not isinstance(sku, str) or not isinstance(regionId, str) or not isinstance(warehouseGroup, str):
            return {"available": False, "quantity": 0, "note": "validation error - fallback applied"}

        try:
            v2_resp = self.call_v2(sku, regionId, warehouseGroup)
        except V2AdapterException as e:
            self.logger.warning(f"v2 call failed for SKU {sku}: {e}")
            # fallback
            return self.fallback_to_v1(sku)

        # Handle v2 response shape
        status = v2_resp.get("availabilityStatus")
        if status == "pending":
            # Poll for eventual confirmation
            self.logger.info(f"v2 returned pending for {sku}, polling for update")
            polled = self.poll_for_update(sku, regionId, warehouseGroup, v2_resp.get("syncTimestamp"))
            if polled:
                v2_resp = polled
            else:
                # Try final poll with explicit poll flag
                try:
                    final = self.call_v2(sku, regionId, warehouseGroup, poll=True)
                    if final.get('availabilityStatus') != 'pending':
                        v2_resp = final
                    else:
                        return {
                            "available": v2_resp.get("available", False),
                            "quantity": v2_resp.get("quantity", 0),
                            "note": "pending - best effort",
                            "api_version": "v2"
                        }
                except V2AdapterException:
                    return {
                        "available": v2_resp.get("available", False),
                        "quantity": v2_resp.get("quantity", 0),
                        "note": "pending - best effort",
                        "api_version": "v2"
                    }
        # Final mapping
        return {
            "available": v2_resp.get("available", False),
            "quantity": v2_resp.get("quantity", 0),
            "note": v2_resp.get("availabilityStatus", "unknown"),
            "syncTimestamp": v2_resp.get("syncTimestamp"),
            "api_version": "v2",
            "response_time": v2_resp.get("response_time", 0)
        }

    def process_cart_items(self, items: list) -> Dict[str, Any]:
        results = []
        total_time = 0
        errors = 0
        for item in items:
            sku = item["sku"] if isinstance(item, dict) else item
            region = item.get("regionId") if isinstance(item, dict) else None
            wg = item.get("warehouseGroup") if isinstance(item, dict) else None

            res = self.check_stock(sku, region, wg)
            results.append({"sku": sku, "result": res})
            total_time += res.get("response_time", 0)
            if not res.get("available", False):
                errors += 1

        return {
            "timestamp": datetime.now().isoformat(),
            "total_items": len(items),
            "processed_items": len(results),
            "total_response_time": total_time,
            "average_response_time": total_time / len(results) if results else 0,
            "error_count": errors,
            "results": results
        }