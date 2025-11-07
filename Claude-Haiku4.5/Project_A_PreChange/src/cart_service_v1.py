"""
Cart service using legacy v1 API endpoint.
This is the "before" state - calling /api/v1/checkStock without region awareness.
"""
import requests
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime

class CartServiceV1:
    """Shopping cart service using v1 inventory check."""
    
    def __init__(self, v1_base_url: str = "http://localhost:8001"):
        self.v1_base_url = v1_base_url
        self.session = requests.Session()
        self.request_log = []
    
    def check_stock(self, sku: str, quantity: int) -> Dict[str, Any]:
        """
        Check stock availability using legacy v1 endpoint.
        
        Args:
            sku: Product SKU
            quantity: Requested quantity
            
        Returns:
            Dictionary with availability status and metadata
        """
        start_time = time.time()
        
        try:
            url = f"{self.v1_base_url}/api/v1/checkStock"
            payload = {
                "sku": sku,
                "quantity": quantity
            }
            
            response = self.session.post(
                url,
                json=payload,
                timeout=5
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Log request
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "endpoint": "v1",
                "sku": sku,
                "quantity": quantity,
                "status_code": response.status_code,
                "latency_ms": latency_ms,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                data = response.json()
                log_entry["response"] = data
                self.request_log.append(log_entry)
                return {
                    "available": data.get("available", False),
                    "quantity": data.get("quantity", 0),
                    "sku": sku,
                    "source": "v1",
                    "latency_ms": latency_ms,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                log_entry["error"] = response.text
                self.request_log.append(log_entry)
                return {
                    "available": False,
                    "quantity": 0,
                    "sku": sku,
                    "source": "v1",
                    "error": f"HTTP {response.status_code}",
                    "latency_ms": latency_ms,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except requests.Timeout:
            latency_ms = (time.time() - start_time) * 1000
            self.request_log.append({
                "timestamp": datetime.utcnow().isoformat(),
                "endpoint": "v1",
                "sku": sku,
                "quantity": quantity,
                "error": "Timeout",
                "latency_ms": latency_ms,
                "success": False
            })
            return {
                "available": False,
                "quantity": 0,
                "sku": sku,
                "source": "v1",
                "error": "Timeout",
                "latency_ms": latency_ms,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            self.request_log.append({
                "timestamp": datetime.utcnow().isoformat(),
                "endpoint": "v1",
                "sku": sku,
                "quantity": quantity,
                "error": str(e),
                "latency_ms": latency_ms,
                "success": False
            })
            return {
                "available": False,
                "quantity": 0,
                "sku": sku,
                "source": "v1",
                "error": str(e),
                "latency_ms": latency_ms,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def add_to_cart(self, sku: str, quantity: int, cart_id: str = "cart-001") -> Dict[str, Any]:
        """
        Add item to cart after checking availability.
        
        Returns: {"success": bool, "message": str, "item": {...}}
        """
        availability = self.check_stock(sku, quantity)
        
        if availability["available"]:
            return {
                "success": True,
                "message": f"Added {quantity} x {sku} to cart",
                "item": {
                    "sku": sku,
                    "quantity": quantity,
                    "cart_id": cart_id
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "success": False,
                "message": f"Out of stock: {sku} (available: {availability['quantity']})",
                "item": {
                    "sku": sku,
                    "quantity": quantity,
                    "cart_id": cart_id
                },
                "available_quantity": availability["quantity"],
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_request_log(self):
        """Return all request logs for analysis."""
        return self.request_log


if __name__ == "__main__":
    # Simple test
    service = CartServiceV1()
    result = service.check_stock("ABC123", 5)
    print(json.dumps(result, indent=2))
