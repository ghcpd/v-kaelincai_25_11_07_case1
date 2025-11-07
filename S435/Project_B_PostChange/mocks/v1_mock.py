from flask import Flask, request, jsonify
import time

app = Flask(__name__)
DATA = {
    "ABC123": {"sku":"ABC123","available":True,"quantity":12},
    "BOUNDARY1": {"sku":"BOUNDARY1","available":False,"quantity":0},
    "ASYNC1": {"sku":"ASYNC1","available":True,"quantity":1},
    "12345": {"sku":"12345","available":True,"quantity":5},
    "LATENCY1": {"sku":"LATENCY1","available":True,"quantity":3},
}

@app.route('/api/v1/checkStock', methods=['POST'])
def check_stock():
    payload = request.get_json() or {}
    sku = payload.get('sku')
    if isinstance(sku, int):
        sku = str(sku)
    if not sku:
        return jsonify({"error":"missing_sku"}), 400
    if sku == 'LATENCY1':
        time.sleep(1.5)
    data = DATA.get(sku)
    if not data:
        return jsonify({"sku": sku, "available": False, "quantity": 0}), 200
    return jsonify(data), 200

if __name__ == '__main__':
    app.run(port=6002)
