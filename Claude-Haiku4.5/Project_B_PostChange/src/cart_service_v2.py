"""
Cart service using new v2 API endpoint with adapter pattern, async handling, and fallback.
This is the "after" state - calling /api/v2/stock/availability with region awareness.
"""
import requests
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime
import threading

class CartServiceV2:
    """Shopping cart service using v2 inventory check with advanced features."""
    
    def __init__(self, v2_base_url: str = "http://localhost:8002", 
                 v1_fallback_url: Optional[str] = None,
                 max_retries: int = 3,
                 retry_backoff_ms: int = 100):
        self.v2_base_url = v2_base_url
        self.v1_fallback_url = v1_fallback_url
        self.session = requests.Session()
        self.request_log = []
        self.max_retries = max_retries
        self.retry_backoff_ms = retry_backoff_ms
        self.circuit_breaker_failures = 0
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_open = False
    
    def _validate_parameters(self, sku: str, quantity: int, 
                            region_id: str, warehouse_group: str) -> Optional[str]:
        """Validate v2 parameters. Returns error message if invalid."""
        if not isinstance(sku, str) or not sku:
            return "SKU must be a non-empty string"
        if not isinstance(quantity, int) or quantity <= 0:
            return "Quantity must be a positive integer"
        if not isinstance(region_id, str) or not region_id:
            return "regionId must be a non-empty string"
        if not isinstance(warehouse_group, str) or not warehouse_group:
            return "warehouseGroup must be a non-empty string"
        return None
    
    def _check_circuit_breaker(self) -> bool:
        """Check if circuit breaker is open."""
        if self.circuit_breaker_open:
            if time.time() % 10 > 5:  # Reset after ~5 seconds
                self.circuit_breaker_open = False
                self.circuit_breaker_failures = 0
                return False
            return True
        return False
    
    def _handle_circuit_breaker_failure(self):
        """Record failure and potentially open circuit breaker."""
        self.circuit_breaker_failures += 1
        if self.circuit_breaker_failures >= self.circuit_breaker_threshold:
            self.circuit_breaker_open = True
    
    def check_stock_v2(self, sku: str, quantity: int, 
                      region_id: str, warehouse_group: str,
                      enable_async_polling: bool = True) -> Dict[str, Any]:
        """
        Check stock availability using v2 endpoint with validation and async handling.
        
        Args:
            sku: Product SKU
            quantity: Requested quantity
            region_id: Region identifier (e.g., "ap-sg-1")
            warehouse_group: Warehouse group (e.g., "WG-2")
            enable_async_polling: Whether to poll for pending responses
            
        Returns:
            Dictionary with availability status and metadata
        """
        start_time = time.time()
        
        # Parameter validation
        validation_error = self._validate_parameters(sku, quantity, region_id, warehouse_group)
        if validation_error:
            latency_ms = (time.time() - start_time) * 1000
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "endpoint": "v2",
                "sku": sku,
                "quantity": quantity,
                "region_id": region_id,
                "warehouse_group": warehouse_group,
                "error": f"Validation: {validation_error}",
                "latency_ms": latency_ms,
                "success": False
            }
            self.request_log.append(log_entry)
            return {
                "available": False,
                "quantity": 0,
                "sku": sku,
                "source": "v2",
                "error": validation_error,
                "latency_ms": latency_ms,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Check circuit breaker
        if self._check_circuit_breaker():
            return self._fallback_to_v1_or_safe_default(sku, quantity, 
                                                        "Circuit breaker open - too many failures")
        
        # Try v2 with retries
        for attempt in range(1, self.max_retries + 1):
            try:
                url = f"{self.v2_base_url}/api/v2/stock/availability"
                payload = {
                    "sku": sku,
                    "quantity": quantity,
                    "regionId": region_id,
                    "warehouseGroup": warehouse_group
                }
                
                attempt_start = time.time()
                response = self.session.post(
                    url,
                    json=payload,
                    timeout=5
                )
                attempt_latency = time.time() - attempt_start
                
                # Success cases
                if response.status_code == 200:
                    data = response.json()
                    latency_ms = (time.time() - start_time) * 1000
                    
                    log_entry = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "endpoint": "v2",
                        "sku": sku,
                        "quantity": quantity,
                        "region_id": region_id,
                        "warehouse_group": warehouse_group,
                        "status_code": response.status_code,
                        "latency_ms": latency_ms,
                        "success": True,
                        "response": data
                    }
                    self.request_log.append(log_entry)
                    self.circuit_breaker_failures = 0
                    
                    return {
                        "available": data.get("available", False),
                        "quantity": data.get("quantity", 0),
                        "sku": sku,
                        "availability_status": data.get("availabilityStatus", "unknown"),
                        "sync_timestamp": data.get("syncTimestamp"),
                        "source": "v2",
                        "latency_ms": latency_ms,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                
                # Async polling case (202 Accepted)
                elif response.status_code == 202 and enable_async_polling:
                    data = response.json()
                    request_id = data.get("requestId")
                    poll_after_ms = data.get("pollAfter", 100)
                    
                    log_entry = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "endpoint": "v2",
                        "sku": sku,
                        "quantity": quantity,
                        "region_id": region_id,
                        "warehouse_group": warehouse_group,
                        "status_code": 202,
                        "request_id": request_id,
                        "note": "Async polling required"
                    }
                    self.request_log.append(log_entry)
                    
                    # Poll for result
                    return self._poll_for_result(request_id, poll_after_ms, 
                                               sku, quantity, start_time)
                
                # Validation error
                elif response.status_code == 400:
                    error_data = response.json()
                    return self._fallback_to_v1_or_safe_default(
                        sku, quantity,
                        f"v2 validation error: {error_data.get('error', 'Unknown')}"
                    )
                
                # Server error - retry
                elif response.status_code >= 500:
                    latency_ms = (time.time() - start_time) * 1000
                    if attempt < self.max_retries:
                        wait_ms = self.retry_backoff_ms * (2 ** (attempt - 1))
                        self.request_log.append({
                            "timestamp": datetime.utcnow().isoformat(),
                            "endpoint": "v2",
                            "sku": sku,
                            "status_code": response.status_code,
                            "attempt": attempt,
                            "retry_after_ms": wait_ms
                        })
                        time.sleep(wait_ms / 1000)
                        continue
                    else:
                        self._handle_circuit_breaker_failure()
                        return self._fallback_to_v1_or_safe_default(
                            sku, quantity,
                            f"v2 returned {response.status_code} after {attempt} retries"
                        )
                
                else:
                    return self._fallback_to_v1_or_safe_default(
                        sku, quantity,
                        f"Unexpected status code: {response.status_code}"
                    )
                    
            except requests.Timeout:
                latency_ms = (time.time() - start_time) * 1000
                if attempt < self.max_retries:
                    wait_ms = self.retry_backoff_ms * (2 ** (attempt - 1))
                    self.request_log.append({
                        "timestamp": datetime.utcnow().isoformat(),
                        "endpoint": "v2",
                        "sku": sku,
                        "error": "Timeout",
                        "attempt": attempt,
                        "retry_after_ms": wait_ms
                    })
                    time.sleep(wait_ms / 1000)
                    continue
                else:
                    self._handle_circuit_breaker_failure()
                    return self._fallback_to_v1_or_safe_default(
                        sku, quantity,
                        "v2 timeout - exceeded retry limit"
                    )
            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                self._handle_circuit_breaker_failure()
                self.request_log.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "endpoint": "v2",
                    "sku": sku,
                    "error": str(e),
                    "latency_ms": latency_ms,
                    "success": False
                })
                return self._fallback_to_v1_or_safe_default(
                    sku, quantity,
                    f"v2 exception: {str(e)}"
                )
        
        return self._fallback_to_v1_or_safe_default(
            sku, quantity,
            "All v2 retry attempts exhausted"
        )
    
    def _poll_for_result(self, request_id: str, poll_after_ms: int, 
                        sku: str, quantity: int, start_time: float) -> Dict[str, Any]:
        """Poll for async result from v2."""
        max_polls = 10
        poll_count = 0
        
        while poll_count < max_polls:
            time.sleep(poll_after_ms / 1000)
            poll_count += 1
            
            try:
                url = f"{self.v2_base_url}/api/v2/stock/availability/poll/{request_id}"
                response = self.session.get(url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    latency_ms = (time.time() - start_time) * 1000
                    
                    self.request_log.append({
                        "timestamp": datetime.utcnow().isoformat(),
                        "endpoint": "v2",
                        "sku": sku,
                        "request_id": request_id,
                        "poll_attempts": poll_count,
                        "status": "completed",
                        "latency_ms": latency_ms
                    })
                    
                    return {
                        "available": data.get("available", False),
                        "quantity": data.get("quantity", 0),
                        "sku": sku,
                        "availability_status": data.get("availabilityStatus"),
                        "sync_timestamp": data.get("syncTimestamp"),
                        "source": "v2-polled",
                        "latency_ms": latency_ms,
                        "poll_attempts": poll_count,
                        "timestamp": datetime.utcnow().isoformat()
                    }
            except Exception as e:
                self.request_log.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "endpoint": "v2",
                    "sku": sku,
                    "request_id": request_id,
                    "poll_attempt": poll_count,
                    "error": str(e)
                })
        
        # Polling exhausted
        return self._fallback_to_v1_or_safe_default(
            sku, quantity,
            "Async polling exceeded max attempts"
        )
    
    def _fallback_to_v1_or_safe_default(self, sku: str, quantity: int, 
                                       reason: str) -> Dict[str, Any]:
        """Fallback to v1 or safe default when v2 fails."""
        latency_ms = time.time() * 1000 - time.time() * 1000
        
        self.request_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "endpoint": "fallback",
            "sku": sku,
            "quantity": quantity,
            "reason": reason
        })
        
        # Could call v1 here if available
        if self.v1_fallback_url:
            try:
                response = self.session.post(
                    f"{self.v1_fallback_url}/api/v1/checkStock",
                    json={"sku": sku, "quantity": quantity},
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "available": data.get("available", False),
                        "quantity": data.get("quantity", 0),
                        "sku": sku,
                        "source": "v1-fallback",
                        "fallback_reason": reason,
                        "latency_ms": latency_ms,
                        "timestamp": datetime.utcnow().isoformat()
                    }
            except:
                pass
        
        # Conservative default: mark as unavailable
        return {
            "available": False,
            "quantity": 0,
            "sku": sku,
            "source": "safe-default",
            "fallback_reason": reason,
            "latency_ms": latency_ms,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def add_to_cart(self, sku: str, quantity: int, 
                   region_id: str, warehouse_group: str,
                   cart_id: str = "cart-001") -> Dict[str, Any]:
        """
        Add item to cart after checking availability with v2.
        """
        availability = self.check_stock_v2(sku, quantity, region_id, warehouse_group)
        
        if availability["available"]:
            return {
                "success": True,
                "message": f"Added {quantity} x {sku} to cart",
                "item": {
                    "sku": sku,
                    "quantity": quantity,
                    "region_id": region_id,
                    "warehouse_group": warehouse_group,
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
                    "region_id": region_id,
                    "warehouse_group": warehouse_group,
                    "cart_id": cart_id
                },
                "available_quantity": availability["quantity"],
                "fallback_reason": availability.get("fallback_reason"),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_request_log(self):
        """Return all request logs for analysis."""
        return self.request_log


if __name__ == "__main__":
    # Simple test
    service = CartServiceV2()
    result = service.check_stock_v2("ABC123", 5, "ap-sg-1", "WG-2")
    print(json.dumps(result, indent=2))
