"""
Legacy Cart Service - Pre-Change Implementation
Calls the old /api/v1/checkStock endpoint
"""
import requests
import json
import logging
from typing import Dict, Optional, Any
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CartServiceV1:
    """Legacy cart service using v1 stock API"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.v1_endpoint = f"{base_url}/api/v1/checkStock"
        self.timeout = 5.0
        
    def check_stock(self, sku: str) -> Dict[str, Any]:
        """
        Check stock availability using legacy v1 API
        
        Args:
            sku: Product SKU to check
            
        Returns:
            Dict with availability information
        """
        try:
            payload = {"sku": sku}
            logger.info(f"Checking stock for SKU: {sku} via v1 API")
            
            start_time = datetime.now()
            response = requests.post(
                self.v1_endpoint,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"v1 API response received in {elapsed_ms:.2f}ms: {result}")
            
            return {
                "available": result.get("available", False),
                "quantity": result.get("quantity", 0),
                "sku": sku,
                "source": "v1",
                "latency_ms": elapsed_ms,
                "status_code": response.status_code,
                "note": "legacy_api"
            }
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout checking stock for SKU: {sku}")
            return {
                "available": False,
                "quantity": 0,
                "sku": sku,
                "source": "v1",
                "latency_ms": self.timeout * 1000,
                "status_code": 504,
                "error": "timeout",
                "note": "timeout_error"
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error checking stock for SKU: {sku}, error: {str(e)}")
            return {
                "available": False,
                "quantity": 0,
                "sku": sku,
                "source": "v1",
                "latency_ms": 0,
                "status_code": 500,
                "error": str(e),
                "note": "request_error"
            }
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {
                "available": False,
                "quantity": 0,
                "sku": sku,
                "source": "v1",
                "latency_ms": 0,
                "status_code": 500,
                "error": str(e),
                "note": "unexpected_error"
            }
    
    def is_available(self, sku: str) -> bool:
        """Simple availability check"""
        result = self.check_stock(sku)
        return result.get("available", False)

