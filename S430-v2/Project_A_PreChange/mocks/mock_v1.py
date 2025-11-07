from flask import Flask, request, jsonify
import time
import argparse

app = Flask(__name__)

# Configurable responses
responses = {
    "normal": {"available": True, "qty": 12},
    "out_of_stock": {"available": False, "qty": 0},
}

@app.route('/api/v1/checkStock', methods=['POST'])
def check_stock():
    payload = request.get_json() or {}
    sku = payload.get('sku')
    q = payload.get('quantity', 0)
    mode = request.args.get('mode', 'normal')
    delay = float(request.args.get('delay', 0))
    if delay:
        time.sleep(delay)
    if sku == 'ERRSKU' or mode == 'error':
        return jsonify({"error": "server error"}), 500

    if q == 0:
        return jsonify(responses['out_of_stock'])

    return jsonify(responses['normal'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5001)
    args = parser.parse_args()
    app.run(port=args.port)
