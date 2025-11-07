"""
Mock Server for Legacy v1 API
Simulates /api/v1/checkStock endpoint behavior
"""
from flask import Flask, request, jsonify
import time
import random
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Mock data for different SKUs
MOCK_INVENTORY = {
    "ABC123": {"inStock": True, "stockLevel": 12},
    "XYZ789": {"inStock": False, "stockLevel": 0},
    "DEF456": {"inStock": True, "stockLevel": 5},
    "GHI789": {"inStock": True, "stockLevel": 8},
    "JKL012": {"inStock": True, "stockLevel": 3},
    "DEFAULT": {"inStock": False, "stockLevel": 0}
}

@app.route('/api/v1/checkStock', methods=['POST'])
def check_stock():
    """Legacy v1 checkStock endpoint"""
    
    # Simulate some processing time
    time.sleep(random.uniform(0.1, 0.3))
    
    data = request.get_json()
    
    if not data or 'sku' not in data:
        return jsonify({"error": "SKU required"}), 400
    
    sku = data['sku']
    
    # Special case for timeout simulation
    if sku == "JKL012":
        # Simulate high latency/timeout
        time.sleep(10)  # This will cause timeout in client
    
    # Get mock inventory data
    inventory = MOCK_INVENTORY.get(sku, MOCK_INVENTORY["DEFAULT"])
    
    app.logger.info(f"v1 API: Checking stock for SKU {sku}")
    
    response = {
        "sku": sku,
        "inStock": inventory["inStock"],
        "stockLevel": inventory["stockLevel"],
        "timestamp": time.time()
    }
    
    return jsonify(response)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "mock-v1-api"})

if __name__ == '__main__':
    print("Starting Mock v1 API Server on port 8001")
    app.run(host='0.0.0.0', port=8001, debug=False)