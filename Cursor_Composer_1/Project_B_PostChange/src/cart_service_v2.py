"""
Updated Cart Service - Post-Change Implementation
Calls the new /api/v2/stock/availability endpoint with region awareness
and async availability status handling
"""
import requests
import json
import logging
from typing import Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CartServiceV2:
    """Updated cart service using v2 stock API with region awareness"""
    
    def __init__(self, base_url: str = "http://localhost:8002", enable_fallback: bool = True):
        self.base_url = base_url
        self.v2_endpoint = f"{base_url}/api/v2/stock/availability"
        self.timeout = 5.0
        self.enable_fallback = enable_fallback
        self.max_poll_attempts = 3
        self.poll_interval_seconds = 1.0
        
    def check_stock(
        self, 
        sku: str, 
        region_id: str, 
        warehouse_group: str,
        wait_for_confirmation: bool = False
    ) -> Dict[str, Any]:
        """
        Check stock availability using new v2 API
        
        Args:
            sku: Product SKU to check
            region_id: Region identifier (e.g., "ap-sg-1")
            warehouse_group: Warehouse group identifier (e.g., "WG-2")
            wait_for_confirmation: If True, poll for confirmation when status is "pending"
            
        Returns:
            Dict with availability information including async status handling
        """
        # Validate inputs
        if not sku:
            return {
                "available": False,
                "quantity": 0,
                "sku": sku,
                "source": "v2",
                "status_code": 400,
                "error": "Missing SKU",
                "note": "validation_error"
            }
        
        if not region_id:
            return {
                "available": False,
                "quantity": 0,
                "sku": sku,
                "source": "v2",
                "status_code": 400,
                "error": "Missing regionId",
                "note": "validation_error"
            }
        
        if not warehouse_group:
            return {
                "available": False,
                "quantity": 0,
                "sku": sku,
                "source": "v2",
                "status_code": 400,
                "error": "Missing warehouseGroup",
                "note": "validation_error"
            }
        
        try:
            payload = {
                "sku": sku,
                "regionId": region_id,
                "warehouseGroup": warehouse_group
            }
            
            logger.info(f"Checking stock for SKU: {sku}, region: {region_id}, warehouse: {warehouse_group} via v2 API")
            
            start_time = datetime.now()
            response = requests.post(
                self.v2_endpoint,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # Handle non-2xx responses
            if response.status_code >= 500:
                logger.warning(f"v2 API returned {response.status_code}, attempting fallback")
                if self.enable_fallback:
                    return self._fallback_to_v1(sku, elapsed_ms)
                else:
                    response.raise_for_status()
            
            if response.status_code == 400:
                result = response.json()
                return {
                    "available": False,
                    "quantity": 0,
                    "sku": sku,
                    "source": "v2",
                    "latency_ms": elapsed_ms,
                    "status_code": 400,
                    "error": result.get("error", "Bad request"),
                    "note": "validation_error"
                }
            
            response.raise_for_status()
            result = response.json()
            
            # Handle asynchronous availability status
            availability_status = result.get("availabilityStatus", "confirmed")
            sync_timestamp = result.get("syncTimestamp")
            
            # If status is pending and we should wait, poll for confirmation
            if availability_status == "pending" and wait_for_confirmation:
                logger.info(f"Availability status is pending, polling for confirmation...")
                poll_result = self._poll_for_confirmation(sku, region_id, warehouse_group, sync_timestamp)
                if poll_result:
                    result = poll_result
                    availability_status = result.get("availabilityStatus", "confirmed")
            
            # Determine availability based on status and quantity
            available = result.get("available", False)
            quantity = result.get("quantity", 0)
            
            # If status is pending but we have quantity, mark as available with note
            if availability_status == "pending" and quantity > 0:
                available = True  # Optimistic availability
            
            logger.info(f"v2 API response: available={available}, quantity={quantity}, status={availability_status}")
            
            return {
                "available": available,
                "quantity": quantity,
                "sku": sku,
                "region_id": region_id,
                "warehouse_group": warehouse_group,
                "source": "v2",
                "availability_status": availability_status,
                "sync_timestamp": sync_timestamp,
                "latency_ms": elapsed_ms,
                "status_code": response.status_code,
                "note": f"v2_{availability_status}"
            }
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout checking stock for SKU: {sku}")
            if self.enable_fallback:
                return self._fallback_to_v1(sku, self.timeout * 1000)
            return {
                "available": False,
                "quantity": 0,
                "sku": sku,
                "source": "v2",
                "latency_ms": self.timeout * 1000,
                "status_code": 504,
                "error": "timeout",
                "note": "timeout_error"
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error checking stock for SKU: {sku}, error: {str(e)}")
            if self.enable_fallback:
                return self._fallback_to_v1(sku, 0)
            return {
                "available": False,
                "quantity": 0,
                "sku": sku,
                "source": "v2",
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
                "source": "v2",
                "latency_ms": 0,
                "status_code": 500,
                "error": str(e),
                "note": "unexpected_error"
            }
    
    def _poll_for_confirmation(
        self, 
        sku: str, 
        region_id: str, 
        warehouse_group: str,
        initial_timestamp: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Poll for confirmation when availability status is pending"""
        for attempt in range(self.max_poll_attempts):
            time.sleep(self.poll_interval_seconds)
            try:
                response = requests.post(
                    self.v2_endpoint,
                    json={
                        "sku": sku,
                        "regionId": region_id,
                        "warehouseGroup": warehouse_group
                    },
                    timeout=self.timeout,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    status = result.get("availabilityStatus", "pending")
                    if status == "confirmed":
                        logger.info(f"Availability confirmed after {attempt + 1} poll attempts")
                        return result
                    elif status == "unavailable":
                        logger.info(f"Availability confirmed as unavailable after {attempt + 1} poll attempts")
                        return result
                
            except Exception as e:
                logger.warning(f"Poll attempt {attempt + 1} failed: {str(e)}")
        
        logger.warning(f"Could not confirm availability after {self.max_poll_attempts} attempts")
        return None
    
    def _fallback_to_v1(self, sku: str, v2_latency_ms: float) -> Dict[str, Any]:
        """Fallback to v1 API when v2 fails"""
        logger.info(f"Falling back to v1 API for SKU: {sku}")
        fallback_start = datetime.now()
        try:
            # In a real scenario, this would call the actual v1 API
            # For this demo, we simulate a fallback response
            fallback_response = requests.post(
                "http://localhost:8001/api/v1/checkStock",
                json={"sku": sku},
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            fallback_latency_ms = (datetime.now() - fallback_start).total_seconds() * 1000
            
            if fallback_response.status_code == 200:
                result = fallback_response.json()
                return {
                    "available": result.get("available", False),
                    "quantity": result.get("quantity", 0),
                    "sku": sku,
                    "source": "v1_fallback",
                    "latency_ms": v2_latency_ms + fallback_latency_ms,
                    "status_code": 200,
                    "note": "v1_fallback"
                }
        except Exception as e:
            logger.error(f"Fallback to v1 also failed: {str(e)}")
        
        fallback_latency_ms = (datetime.now() - fallback_start).total_seconds() * 1000
        return {
            "available": False,
            "quantity": 0,
            "sku": sku,
            "source": "v2_fallback_failed",
            "latency_ms": v2_latency_ms + fallback_latency_ms,
            "status_code": 500,
            "error": "Both v2 and v1 fallback failed",
            "note": "fallback_failed"
        }
    
    def is_available(
        self, 
        sku: str, 
        region_id: str, 
        warehouse_group: str,
        wait_for_confirmation: bool = False
    ) -> bool:
        """Simple availability check"""
        result = self.check_stock(sku, region_id, warehouse_group, wait_for_confirmation)
        return result.get("available", False)

