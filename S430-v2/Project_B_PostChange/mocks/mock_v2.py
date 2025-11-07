from flask import Flask, request, jsonify
import time
import argparse

app = Flask(__name__)

# Mode storage for SKUs: mode maps sku->state
sku_states = {}

@app.route('/api/v2/stock/availability', methods=['POST'])
def availability():
    payload = request.get_json() or {}
    sku = payload.get('sku')
    region = payload.get('regionId')
    wg = payload.get('warehouseGroup')
    qty = payload.get('quantity', 1)
    # behavior modifiers via query params
    mode = request.args.get('mode', 'confirm')
    delay = float(request.args.get('delay', 0))
    if delay:
        time.sleep(delay)

    # Support asynchronous pending flow: if mode==pending_first then first call returns pending then subsequent returns confirmed
    if mode == 'error':
        return jsonify({"error":"server error v2"}), 500

    if mode == 'pending_first':
        state = sku_states.get(sku, 'first')
        if state == 'first':
            sku_states[sku] = 'confirm'
            return jsonify({"sku": sku, "available": False, "quantity": 0, "availabilityStatus": "pending", "syncTimestamp": "2025-11-01T12:00:00Z"})
        else:
            return jsonify({"sku": sku, "available": True, "quantity": 12, "availabilityStatus": "confirmed", "syncTimestamp": "2025-11-01T12:00:01Z"})

    # Normal confirmed
    if mode == 'confirm':
        return jsonify({"sku": sku, "available": True, "quantity": 12, "availabilityStatus": "confirmed", "syncTimestamp": "2025-11-01T12:00:00Z"})

    if mode == 'out_of_stock':
        return jsonify({"sku": sku, "available": False, "quantity": 0, "availabilityStatus": "confirmed"})

    if mode == 'slow':
        time.sleep(2)
        return jsonify({"sku": sku, "available": True, "quantity": 2, "availabilityStatus": "confirmed"})

    # Default fallback
    return jsonify({"sku": sku, "available": False, "quantity": 0, "availabilityStatus": "confirmed"})

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5002)
    args = parser.parse_args()
    app.run(port=args.port)
