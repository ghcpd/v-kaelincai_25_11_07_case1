"""
Mock Server for v2 API
Simulates /api/v2/stock/availability behavior with configurable scenarios
"""
from flask import Flask, request, jsonify
import time
import random
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

MOCK_RESPONSES = {
    "ABC123": {"available": True, "quantity": 12, "availabilityStatus": "confirmed", "syncTimestamp": "2025-11-01T12:00:00Z"},
    "XYZ789": {"available": False, "quantity": 0, "availabilityStatus": "confirmed", "syncTimestamp": "2025-11-01T12:01:00Z"},
    "DEF456": {"available": True, "quantity": 5, "availabilityStatus": "pending", "syncTimestamp": "2025-11-01T12:02:00Z"},
    "GHI789": {"error": "Missing required parameter: regionId", "status": 400},
    "JKL012": "TIMEOUT"
}

@app.route('/api/v2/stock/availability', methods=['POST'])
def check_availability():
    data = request.get_json()
    sku = data.get('sku') if data else None

    # Validate inputs
    if not data:
        return jsonify({"error": "payload required"}), 400
    if 'regionId' not in data or 'warehouseGroup' not in data:
        return jsonify({"error": "Missing regionId or warehouseGroup"}), 400

    if sku not in MOCK_RESPONSES:
        # Default response
        return jsonify({"sku": sku, "available": False, "quantity": 0, "availabilityStatus": "confirmed", "syncTimestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ')}), 200

    resp = MOCK_RESPONSES[sku]

    # Simulate timeout
    if resp == "TIMEOUT":
        time.sleep(10)
        # Will trigger client timeout
        return "", 504

    # Simulate pending confirmation update on subsequent polls
    if resp.get('availabilityStatus') == 'pending':
        # Return pending for first call, and confirmed on poll if a query param 'poll' is provided
        if request.args.get('poll') == '1':
            return jsonify({"sku": sku, "available": True, "quantity": 5, "availabilityStatus": "confirmed", "syncTimestamp": "2025-11-01T12:05:00Z"}), 200
        return jsonify(resp)

    status = resp.get('status') or 200
    return jsonify(resp), status

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "mock-v2-api"})

if __name__ == '__main__':
    print("Starting Mock v2 API Server on port 8002")
    app.run(host='0.0.0.0', port=8002, debug=False)