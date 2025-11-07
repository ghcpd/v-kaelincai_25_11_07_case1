from flask import Flask, request, jsonify
import requests
import os
import time

app = Flask(__name__)
V1_BASE = os.environ.get('V1_BASE', 'http://127.0.0.1:5001')

@app.route('/cart/check', methods=['POST'])
def check():
    payload = request.get_json() or {}
    sku = payload.get('sku')
    if sku is None:
        return jsonify({'error':'missing_sku'}), 400
    # Call legacy v1 endpoint
    start = time.time()
    try:
        r = requests.post(f"{V1_BASE}/api/v1/checkStock", json={'sku': sku}, timeout=5)
        duration = time.time() - start
        r.raise_for_status()
        data = r.json()
        result = {
            'sku': data.get('sku'),
            'available': data.get('available', False),
            'quantity': data.get('quantity', 0),
            'note': 'v1'
        }
        return jsonify({'result': result, 'meta': {'duration': duration}}), 200
    except Exception as e:
        duration = time.time() - start
        return jsonify({'error': str(e), 'meta': {'duration': duration}}), 500

if __name__ == '__main__':
    app.run(port=5002)
