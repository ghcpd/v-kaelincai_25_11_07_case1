"""
Mock API server for v1 /api/v1/checkStock endpoint.
Simulates legacy behavior without region awareness or async fields.
"""
import json
import sys
import time
from flask import Flask, request, jsonify
from typing import Dict, Any

app = Flask(__name__)

# Mock inventory database (in-memory)
INVENTORY_DB = {
    "ABC123": {"quantity": 12, "warehouse": "default"},
    "DEF456": {"quantity": 3, "warehouse": "default"},
    "GHI789": {"quantity": 25, "warehouse": "default"},
    "XYZ999": {"quantity": 0, "warehouse": "default"},
    "JKL012": {"quantity": 20, "warehouse": "default"},
    "MNO345": {"quantity": 5, "warehouse": "default"},
}

REQUEST_LATENCIES = {}  # Track request latencies for metrics


@app.route("/api/v1/checkStock", methods=["POST"])
def check_stock_v1():
    """
    Legacy v1 endpoint: simple stock check without region awareness.
    
    Request: {"sku": "ABC123", "quantity": 5}
    Response: {"sku": "ABC123", "available": true, "quantity": 12}
    """
    start_time = time.time()
    
    try:
        data = request.get_json()
        sku = data.get("sku")
        requested_quantity = data.get("quantity")
        
        if not sku or requested_quantity is None:
            return jsonify({"error": "Missing sku or quantity"}), 400
        
        if sku not in INVENTORY_DB:
            return jsonify({
                "sku": sku,
                "available": False,
                "quantity": 0
            }), 200
        
        available_quantity = INVENTORY_DB[sku]["quantity"]
        is_available = available_quantity >= requested_quantity
        
        latency_ms = (time.time() - start_time) * 1000
        REQUEST_LATENCIES[sku] = latency_ms
        
        response = {
            "sku": sku,
            "available": is_available,
            "quantity": available_quantity
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "version": "v1"}), 200


@app.route("/metrics", methods=["GET"])
def metrics():
    """Return latency metrics."""
    return jsonify({
        "endpoint": "v1",
        "total_requests": len(REQUEST_LATENCIES),
        "latencies": REQUEST_LATENCIES
    }), 200


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    print(f"Starting v1 mock server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
