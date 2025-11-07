from flask import Flask, request, jsonify
from threading import Lock
import time
import datetime

app = Flask(__name__)

# behavior per sku: response, delay, status_code
behaviors = {}
behaviors_lock = Lock()

@app.route('/configure', methods=['POST'])
def configure():
    data = request.json or {}
    with behaviors_lock:
        behaviors.update(data.get('behaviors', {}))
    return jsonify({"status": "configured"})

@app.route('/api/v2/stock/availability', methods=['POST'])
def availability():
    payload = request.json or {}
    sku = payload.get('sku')
    region = payload.get('regionId')
    wg = payload.get('warehouseGroup')

    if not region or not wg:
        return (jsonify({'error': 'missing regionId or warehouseGroup'}), 400)

    with behaviors_lock:
        behavior = behaviors.get(sku, {})

    # Default response
    default = { 'sku': sku, 'available': True, 'quantity': 5, 'availabilityStatus': 'confirmed' }
    resp = behavior.get('response', default)
    delay = behavior.get('delay', 0)
    status_code = behavior.get('status_code', 200)

    if delay > 0:
        time.sleep(delay)

    # If response is marked as 'pending' and has a future syncTimestamp, return pending
    if resp.get('availabilityStatus') == 'pending':
        # If current time >= syncTimestamp, change to confirmed
        sync_ts = resp.get('syncTimestamp')
        if sync_ts:
            try:
                t = datetime.datetime.fromisoformat(sync_ts)
            except Exception:
                # bad timestamp format; return as-is
                return (jsonify(resp), status_code)
            if datetime.datetime.utcnow() >= t:
                resp = { 'sku': sku, 'available': True, 'quantity': resp.get('quantity', 1), 'availabilityStatus': 'confirmed' }

    return (jsonify(resp), status_code)

if __name__ == '__main__':
    app.run(port=5002, host='0.0.0.0')
