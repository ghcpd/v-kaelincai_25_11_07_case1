from flask import Flask, request, jsonify
from threading import Lock
import time

app = Flask(__name__)

# Simple in-memory behavior map: sku -> behavior dict
behaviors = {}
behaviors_lock = Lock()

@app.route('/configure', methods=['POST'])
def configure():
    data = request.json or {}
    with behaviors_lock:
        behaviors.update(data.get('behaviors', {}))
    return jsonify({"status": "configured"})

@app.route('/api/v1/checkStock', methods=['POST'])
def check_stock():
    payload = request.json or {}
    sku = payload.get('sku')
    with behaviors_lock:
        behavior = behaviors.get(sku, {})

    # Default behavior if not configured
    resp = behavior.get('response', { 'sku': sku, 'available': True, 'quantity': 5 })
    delay = behavior.get('delay', 0)
    status_code = behavior.get('status_code', 200)

    if delay > 0:
        time.sleep(delay)

    return (jsonify(resp), status_code)

if __name__ == '__main__':
    app.run(port=5001, host='0.0.0.0')
