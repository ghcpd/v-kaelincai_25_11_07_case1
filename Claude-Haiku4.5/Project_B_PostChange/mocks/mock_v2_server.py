"""
Mock API server for v2 /api/v2/stock/availability endpoint.
Simulates new behavior with region awareness, async fields, and polling.
"""
import json
import sys
import time
from flask import Flask, request, jsonify
from typing import Dict, Any
from datetime import datetime, timedelta
import threading

app = Flask(__name__)

# Mock inventory database (in-memory) with region awareness
INVENTORY_DB = {
    "ABC123": {
        "ap-sg-1": {"quantity": 12, "warehouse_group": "WG-2"},
        "us-east-1": {"quantity": 20, "warehouse_group": "WG-1"}
    },
    "DEF456": {
        "us-east-1": {"quantity": 3, "warehouse_group": "WG-1"},
        "ap-sg-1": {"quantity": 8, "warehouse_group": "WG-2"}
    },
    "GHI789": {
        "ap-sg-1": {"quantity": 25, "warehouse_group": "WG-2"},
        "eu-west-1": {"quantity": 15, "warehouse_group": "WG-3"}
    },
    "XYZ999": {
        "ap-sg-1": {"quantity": 0, "warehouse_group": "WG-2"}
    },
    "JKL012": {
        "eu-west-1": {"quantity": 20, "warehouse_group": "WG-3"}
    },
    "MNO345": {
        "ap-sg-1": {"quantity": 5, "warehouse_group": "WG-2"}
    }
}

# Async polling requests cache
PENDING_REQUESTS = {}  # request_id -> (response_data, timeout)
REQUEST_LATENCIES = {}
VALID_REGIONS = ["ap-sg-1", "us-east-1", "eu-west-1"]
VALID_WAREHOUSE_GROUPS = ["WG-1", "WG-2", "WG-3"]


@app.route("/api/v2/stock/availability", methods=["POST"])
def check_availability_v2():
    """
    New v2 endpoint: region-aware stock check with async support.
    
    Request: {
        "sku": "ABC123",
        "quantity": 5,
        "regionId": "ap-sg-1",
        "warehouseGroup": "WG-2"
    }
    
    Response (immediate): {
        "sku": "ABC123",
        "available": true,
        "quantity": 12,
        "availabilityStatus": "confirmed",
        "syncTimestamp": "2025-11-07T10:00:00Z"
    }
    
    Or (async pending): {
        "sku": "ABC123",
        "availabilityStatus": "pending",
        "requestId": "req-12345",
        "pollAfter": 100,
        "status_code": 202
    }
    """
    start_time = time.time()
    
    try:
        data = request.get_json()
        sku = data.get("sku")
        requested_quantity = data.get("quantity")
        region_id = data.get("regionId")
        warehouse_group = data.get("warehouseGroup")
        
        # Strict validation - required fields
        if not sku:
            return jsonify({"error": "Missing sku parameter"}), 400
        if requested_quantity is None:
            return jsonify({"error": "Missing quantity parameter"}), 400
        if not region_id:
            return jsonify({"error": "Missing regionId parameter"}), 400
        if not warehouse_group:
            return jsonify({"error": "Missing warehouseGroup parameter"}), 400
        
        # Validate region and warehouse
        if region_id not in VALID_REGIONS:
            return jsonify({"error": f"Invalid regionId: {region_id}"}), 400
        if warehouse_group not in VALID_WAREHOUSE_GROUPS:
            return jsonify({"error": f"Invalid warehouseGroup: {warehouse_group}"}), 400
        
        # Check inventory
        if sku not in INVENTORY_DB or region_id not in INVENTORY_DB[sku]:
            return jsonify({
                "sku": sku,
                "available": False,
                "quantity": 0,
                "availabilityStatus": "not_found",
                "syncTimestamp": datetime.utcnow().isoformat() + "Z"
            }), 200
        
        available_quantity = INVENTORY_DB[sku][region_id]["quantity"]
        is_available = available_quantity >= requested_quantity
        
        latency_ms = (time.time() - start_time) * 1000
        REQUEST_LATENCIES[f"{sku}-{region_id}"] = latency_ms
        
        # Simulate async behavior 20% of the time for high-volume SKUs
        if sku in ["GHI789"] and request.headers.get("X-Async-Simulation") != "false":
            # Return pending status with polling info
            request_id = f"req-{int(time.time()*1000)}-{sku}"
            response_data = {
                "sku": sku,
                "available": is_available,
                "quantity": available_quantity,
                "availabilityStatus": "confirmed",
                "syncTimestamp": datetime.utcnow().isoformat() + "Z"
            }
            # Store for polling
            PENDING_REQUESTS[request_id] = (response_data, time.time() + 10)
            
            return jsonify({
                "sku": sku,
                "availabilityStatus": "pending",
                "requestId": request_id,
                "pollAfter": 100
            }), 202
        
        # Immediate response
        response = {
            "sku": sku,
            "available": is_available,
            "quantity": available_quantity,
            "availabilityStatus": "confirmed" if is_available else "out_of_stock",
            "syncTimestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v2/stock/availability/poll/<request_id>", methods=["GET"])
def poll_availability_v2(request_id: str):
    """
    Poll for async availability results.
    """
    if request_id not in PENDING_REQUESTS:
        return jsonify({"error": "Request ID not found"}), 404
    
    response_data, timeout = PENDING_REQUESTS[request_id]
    
    if time.time() > timeout:
        del PENDING_REQUESTS[request_id]
        return jsonify({"error": "Request expired"}), 404
    
    # Simulate completion
    del PENDING_REQUESTS[request_id]
    return jsonify(response_data), 200


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "version": "v2"}), 200


@app.route("/metrics", methods=["GET"])
def metrics():
    """Return latency metrics."""
    return jsonify({
        "endpoint": "v2",
        "total_requests": len(REQUEST_LATENCIES),
        "latencies": REQUEST_LATENCIES
    }), 200


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8002
    print(f"Starting v2 mock server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
