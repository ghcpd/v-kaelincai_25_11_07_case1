"""
Mock Server for v1 Stock API (/api/v1/checkStock)
Simulates legacy API behavior
"""
from flask import Flask, request, jsonify
import time
import random
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration for mock behavior
MOCK_CONFIG = {
    "latency_ms": 50,  # Base latency in milliseconds
    "error_rate": 0.0,  # Error rate (0.0 to 1.0)
    "timeout_rate": 0.0,  # Timeout rate
    "port": 8001
}

# Mock stock database
STOCK_DB = {
    "ABC123": {"available": True, "quantity": 12},
    "XYZ789": {"available": True, "quantity": 0},  # Boundary case
    "DEF456": {"available": True, "quantity": 5},
    "GHI789": {"available": False, "quantity": 0},
    "JKL012": {"available": True, "quantity": 100},
}


@app.route('/api/v1/checkStock', methods=['POST'])
def check_stock():
    """Legacy v1 stock check endpoint"""
    try:
        data = request.get_json()
        sku = data.get("sku")
        
        if not sku:
            return jsonify({"error": "Missing SKU"}), 400
        
        # Simulate latency
        latency_ms = MOCK_CONFIG["latency_ms"] + random.randint(0, 20)
        time.sleep(latency_ms / 1000.0)
        
        # Simulate errors
        if random.random() < MOCK_CONFIG["error_rate"]:
            return jsonify({"error": "Internal server error"}), 500
        
        # Simulate timeouts (by taking too long)
        if random.random() < MOCK_CONFIG["timeout_rate"]:
            time.sleep(10)  # Longer than timeout
        
        # Check stock
        stock_info = STOCK_DB.get(sku, {"available": False, "quantity": 0})
        
        logger.info(f"v1 API: Stock check for SKU {sku} -> {stock_info}")
        
        return jsonify({
            "sku": sku,
            "available": stock_info["available"],
            "quantity": stock_info["quantity"]
        }), 200
        
    except Exception as e:
        logger.error(f"Error in v1 mock API: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "version": "v1"}), 200


def update_config(latency_ms=None, error_rate=None, timeout_rate=None):
    """Update mock configuration"""
    if latency_ms is not None:
        MOCK_CONFIG["latency_ms"] = latency_ms
    if error_rate is not None:
        MOCK_CONFIG["error_rate"] = error_rate
    if timeout_rate is not None:
        MOCK_CONFIG["timeout_rate"] = timeout_rate


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
        MOCK_CONFIG["port"] = port
    logger.info(f"Starting v1 mock API on port {MOCK_CONFIG['port']}")
    app.run(host='0.0.0.0', port=MOCK_CONFIG['port'], debug=False)

