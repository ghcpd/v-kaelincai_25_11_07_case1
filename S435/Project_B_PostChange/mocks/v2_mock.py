from flask import Flask, request, jsonify
import time
import threading

app = Flask(__name__)

STATE = {
    'ASYNC1_pending': True
}

@app.route('/api/v2/stock/availability', methods=['POST'])
def availability():
    payload = request.get_json() or {}
    sku = payload.get('sku')
    region = payload.get('regionId')
    wg = payload.get('warehouseGroup')

    # Invalid input simulation
    if sku is None or not isinstance(sku, (str, int)) or not region or not wg:
        return jsonify({'error':'invalid_parameters','message':'regionId or warehouseGroup missing or sku invalid'}), 400

    sku_str = str(sku)

    if sku_str == 'ABC123':
        return jsonify({"sku":"ABC123","available":True,"quantity":12,"availabilityStatus":"confirmed"}), 200
    elif sku_str == 'BOUNDARY1':
        return jsonify({"sku":"BOUNDARY1","available":False,"quantity":0,"availabilityStatus":"confirmed"}), 200
    elif sku_str == 'ASYNC1':
        # first responses are pending; later will be confirmed
        if STATE.get('ASYNC1_pending'):
            # flip after returning pending
            STATE['ASYNC1_pending'] = False
            return jsonify({"sku":"ASYNC1","available":False,"quantity":0,"availabilityStatus":"pending","syncTimestamp":"2025-11-01T12:00:00Z"}), 200
        else:
            return jsonify({"sku":"ASYNC1","available":True,"quantity":1,"availabilityStatus":"confirmed"}), 200
    elif sku_str == 'LATENCY1':
        # Simulate high latency or error
        time.sleep(1.8)
        return jsonify({"error":"timeout","status":500}), 500
    else:
        # default: unknown SKU -> not available
        return jsonify({"sku": sku_str, "available": False, "quantity": 0, "availabilityStatus": "confirmed"}), 200

if __name__ == '__main__':
    app.run(port=6001)
