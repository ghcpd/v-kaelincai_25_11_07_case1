"""
Mock Server for v2 Stock API (/api/v2/stock/availability)
Simulates new API behavior with region awareness and async status
"""
from flask import Flask, request, jsonify
import time
import random
import logging
from datetime import datetime, timedelta

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration for mock behavior
MOCK_CONFIG = {
    "latency_ms": 60,  # Base latency in milliseconds
    "error_rate": 0.0,  # Error rate (0.0 to 1.0)
    "timeout_rate": 0.0,  # Timeout rate
    "pending_rate": 0.2,  # Rate of pending responses (0.0 to 1.0)
    "port": 8002
}

# Mock stock database with region/warehouse awareness
# Format: {sku: {region_id: {warehouse_group: {available, quantity, status}}}}
STOCK_DB = {
    "ABC123": {
        "ap-sg-1": {
            "WG-1": {"available": True, "quantity": 8, "status": "confirmed"},
            "WG-2": {"available": True, "quantity": 12, "status": "confirmed"}
        },
        "us-east-1": {
            "WG-1": {"available": True, "quantity": 5, "status": "confirmed"}
        }
    },
    "XYZ789": {
        "ap-sg-1": {
            "WG-1": {"available": True, "quantity": 0, "status": "confirmed"},  # Boundary case
            "WG-2": {"available": False, "quantity": 0, "status": "confirmed"}
        }
    },
    "DEF456": {
        "ap-sg-1": {
            "WG-1": {"available": True, "quantity": 5, "status": "pending"},  # Async case
            "WG-2": {"available": True, "quantity": 10, "status": "confirmed"}
        }
    },
    "GHI789": {
        "ap-sg-1": {
            "WG-1": {"available": False, "quantity": 0, "status": "confirmed"},
            "WG-2": {"available": False, "quantity": 0, "status": "confirmed"}
        }
    },
    "JKL012": {
        "ap-sg-1": {
            "WG-1": {"available": True, "quantity": 100, "status": "confirmed"}
        }
    },
}

# Track pending requests for async simulation
pending_requests = {}


@app.route('/api/v2/stock/availability', methods=['POST'])
def check_availability():
    """v2 stock availability endpoint with region awareness"""
    try:
        data = request.get_json()
        sku = data.get("sku")
        region_id = data.get("regionId")
        warehouse_group = data.get("warehouseGroup")
        
        # Validation
        if not sku:
            return jsonify({"error": "Missing SKU"}), 400
        
        if not region_id:
            return jsonify({"error": "Missing regionId"}), 400
        
        if not warehouse_group:
            return jsonify({"error": "Missing warehouseGroup"}), 400
        
        # Simulate latency
        latency_ms = MOCK_CONFIG["latency_ms"] + random.randint(0, 30)
        time.sleep(latency_ms / 1000.0)
        
        # Simulate errors
        if random.random() < MOCK_CONFIG["error_rate"]:
            return jsonify({"error": "Internal server error"}), 500
        
        # Simulate timeouts
        if random.random() < MOCK_CONFIG["timeout_rate"]:
            time.sleep(10)
        
        # Check stock in database
        sku_data = STOCK_DB.get(sku)
        if not sku_data:
            return jsonify({
                "sku": sku,
                "available": False,
                "quantity": 0,
                "availabilityStatus": "confirmed",
                "syncTimestamp": datetime.now().isoformat() + "Z"
            }), 200
        
        region_data = sku_data.get(region_id)
        if not region_data:
            return jsonify({
                "sku": sku,
                "available": False,
                "quantity": 0,
                "availabilityStatus": "confirmed",
                "syncTimestamp": datetime.now().isoformat() + "Z"
            }), 200
        
        warehouse_data = region_data.get(warehouse_group)
        if not warehouse_data:
            return jsonify({
                "sku": sku,
                "available": False,
                "quantity": 0,
                "availabilityStatus": "confirmed",
                "syncTimestamp": datetime.now().isoformat() + "Z"
            }), 200
        
        # Determine status (may be pending for async cases)
        status = warehouse_data.get("status", "confirmed")
        
        # Simulate pending responses based on config
        if status == "confirmed" and random.random() < MOCK_CONFIG["pending_rate"]:
            status = "pending"
        
        # If status is pending, simulate eventual consistency
        if status == "pending":
            # Store request for potential confirmation later
            request_key = f"{sku}:{region_id}:{warehouse_group}"
            pending_requests[request_key] = {
                "timestamp": datetime.now(),
                "warehouse_data": warehouse_data
            }
        
        available = warehouse_data["available"]
        quantity = warehouse_data["quantity"]
        
        # If pending but we have data, return pending status
        if status == "pending":
            logger.info(f"v2 API: Returning pending status for {sku} in {region_id}/{warehouse_group}")
            return jsonify({
                "sku": sku,
                "available": available,  # Optimistic availability
                "quantity": quantity,
                "availabilityStatus": "pending",
                "syncTimestamp": (datetime.now() + timedelta(seconds=2)).isoformat() + "Z"
            }), 200
        
        logger.info(f"v2 API: Stock check for SKU {sku} in {region_id}/{warehouse_group} -> available={available}, qty={quantity}")
        
        return jsonify({
            "sku": sku,
            "available": available,
            "quantity": quantity,
            "availabilityStatus": "confirmed",
            "syncTimestamp": datetime.now().isoformat() + "Z"
        }), 200
        
    except Exception as e:
        logger.error(f"Error in v2 mock API: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "version": "v2"}), 200


def update_config(latency_ms=None, error_rate=None, timeout_rate=None, pending_rate=None):
    """Update mock configuration"""
    if latency_ms is not None:
        MOCK_CONFIG["latency_ms"] = latency_ms
    if error_rate is not None:
        MOCK_CONFIG["error_rate"] = error_rate
    if timeout_rate is not None:
        MOCK_CONFIG["timeout_rate"] = timeout_rate
    if pending_rate is not None:
        MOCK_CONFIG["pending_rate"] = pending_rate


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
        MOCK_CONFIG["port"] = port
    logger.info(f"Starting v2 mock API on port {MOCK_CONFIG['port']}")
    app.run(host='0.0.0.0', port=MOCK_CONFIG['port'], debug=False)

