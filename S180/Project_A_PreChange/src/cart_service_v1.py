"""
Cart Service V1 - Legacy API Integration
Uses the old /api/v1/checkStock endpoint
"""
import requests
import json
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime

class CartServiceV1:
    def __init__(self, base_url: str = "http://localhost:8001", timeout: float = 5.0):
        self.base_url = base_url
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        
    def check_stock(self, sku: str) -> Dict[str, Any]:
        """
        Check stock using legacy v1 API
        
        Args:
            sku: Product SKU to check
            
        Returns:
            Dict with availability information
        """
        start_time = time.time()
        
        try:
            # Legacy v1 API only takes SKU parameter
            payload = {"sku": sku}
            
            self.logger.info(f"Calling legacy v1 API for SKU: {sku}")
            
            response = requests.post(
                f"{self.base_url}/api/v1/checkStock",
                json=payload,
                timeout=self.timeout
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                result = {
                    "available": data.get("inStock", False),
                    "quantity": data.get("stockLevel", 0),
                    "note": "legacy api response",
                    "response_time": duration,
                    "api_version": "v1"
                }
                self.logger.info(f"v1 API success for {sku}: {result}")
                return result
            else:
                self.logger.error(f"v1 API error {response.status_code} for {sku}")
                return {
                    "available": False,
                    "quantity": 0,
                    "note": f"api error {response.status_code}",
                    "response_time": duration,
                    "api_version": "v1"
                }
                
        except requests.exceptions.Timeout:
            duration = time.time() - start_time
            self.logger.error(f"v1 API timeout for {sku}")
            return {
                "available": False,
                "quantity": 0,
                "note": "timeout",
                "response_time": duration,
                "api_version": "v1"
            }
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"v1 API error for {sku}: {str(e)}")
            return {
                "available": False,
                "quantity": 0,
                "note": f"error: {str(e)}",
                "response_time": duration,
                "api_version": "v1"
            }
    
    def process_cart_items(self, items: list) -> Dict[str, Any]:
        """
        Process multiple cart items for stock checking
        
        Args:
            items: List of items with SKU information
            
        Returns:
            Dict with processing results
        """
        results = []
        total_time = 0
        errors = 0
        
        for item in items:
            if isinstance(item, dict) and "sku" in item:
                sku = item["sku"]
            elif isinstance(item, str):
                sku = item
            else:
                self.logger.error(f"Invalid item format: {item}")
                continue
                
            result = self.check_stock(sku)
            results.append({
                "sku": sku,
                "result": result
            })
            
            total_time += result.get("response_time", 0)
            if not result.get("available", False):
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