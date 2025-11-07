from flask import Flask, request, jsonify
import requests
import time
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('cart_service_v2')

app = Flask(__name__)
V2_BASE = os.environ.get('V2_BASE', 'http://127.0.0.1:6001')
V1_BASE = os.environ.get('V1_BASE', 'http://127.0.0.1:6002')
POLL_INTERVAL = float(os.environ.get('POLL_INTERVAL', '1.0'))
POLL_TIMEOUT = float(os.environ.get('POLL_TIMEOUT', '5.0'))


def call_v2(payload, timeout: float = 3.0):
    return requests.post(f"{V2_BASE}/api/v2/stock/availability", json=payload, timeout=timeout)


def call_v1(sku, timeout=5):
    return requests.post(f"{V1_BASE}/api/v1/checkStock", json={'sku': sku}, timeout=timeout)


@app.route('/cart/check', methods=['POST'])
def check():
    payload = request.get_json() or {}
    sku = payload.get('sku')
    region = payload.get('regionId')
    wg = payload.get('warehouseGroup')
    if not sku:
        return jsonify({'error': 'missing_sku'}), 400

    # Validate params for v2
    v2_payload = {'sku': sku, 'regionId': region, 'warehouseGroup': wg}

    start = time.time()
    fallback = False
    try:
        r = call_v2(v2_payload, timeout=2.0)
        duration = time.time() - start
        if r.status_code == 200:
            data = r.json()
            status = data.get('availabilityStatus')
            if status == 'confirmed':
                result = {
                    'sku': data.get('sku'),
                    'available': data.get('available', False),
                    'quantity': data.get('quantity', 0),
                    'note': 'v2_confirmed'
                }
                return jsonify({'result': result, 'meta': {'duration': duration, 'fallback': fallback}}), 200
            elif status == 'pending':
                # Poll until confirmed or timeout
                elapsed = 0.0
                logger.info('v2: pending for sku %s; starting poll', sku)
                while elapsed < POLL_TIMEOUT:
                    time.sleep(POLL_INTERVAL)
                    elapsed += POLL_INTERVAL
                    try:
                        pr = call_v2(v2_payload, timeout=2.0)
                        if pr.status_code == 200:
                            pdata = pr.json()
                            if pdata.get('availabilityStatus') == 'confirmed':
                                result = {
                                    'sku': pdata.get('sku'),
                                    'available': pdata.get('available', False),
                                    'quantity': pdata.get('quantity', 0),
                                    'note': 'v2_confirmed_after_poll'
                                }
                                logger.info('v2: confirmed after poll for sku %s', sku)
                                return jsonify({'result': result, 'meta': {'duration': time.time()-start, 'fallback': fallback}}), 200
                    except Exception as e:
                        logger.warning('v2: poll error for sku %s: %s', sku, e)
                        # continue polling until timeout
                        continue
                # Poll timed out; fallback to v1
                logger.info('v2: poll timed out for sku %s; falling back to v1', sku)
                fallback = True
                v1r = call_v1(sku)
                v1r.raise_for_status()
                v1data = v1r.json()
                result = {
                    'sku': v1data.get('sku'),
                    'available': v1data.get('available', False),
                    'quantity': v1data.get('quantity', 0),
                    'note': 'fallback_to_v1_after_pending'
                }
                return jsonify({'result': result, 'meta': {'duration': time.time()-start, 'fallback': fallback}}), 200
            else:
                # Unknown status; fallback
                fallback = True
                v1r = call_v1(sku)
                v1r.raise_for_status()
                v1data = v1r.json()
                result = {
                    'sku': v1data.get('sku'),
                    'available': v1data.get('available', False),
                    'quantity': v1data.get('quantity', 0),
                    'note': 'fallback_to_v1_unknown_status'
                }
                return jsonify({'result': result, 'meta': {'duration': time.time()-start, 'fallback': fallback}}), 200
        else:
            # v2 returned an error - fallback
            fallback = True
            v1r = call_v1(sku)
            v1r.raise_for_status()
            v1data = v1r.json()
            result = {
                'sku': v1data.get('sku'),
                'available': v1data.get('available', False),
                'quantity': v1data.get('quantity', 0),
                'note': 'fallback_to_v1_v2_error'
            }
            return jsonify({'result': result, 'meta': {'duration': time.time()-start, 'fallback': fallback}}), 200

    except requests.exceptions.RequestException as e:
        # network error / timeout
        fallback = True
        try:
            v1r = call_v1(sku)
            v1r.raise_for_status()
            v1data = v1r.json()
            result = {
                'sku': v1data.get('sku'),
                'available': v1data.get('available', False),
                'quantity': v1data.get('quantity', 0),
                'note': 'fallback_to_v1_exception'
            }
            return jsonify({'result': result, 'meta': {'duration': time.time()-start, 'fallback': fallback}}), 200
        except Exception as e2:
            return jsonify({'error': str(e2), 'note': 'both_v2_and_v1_failed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=6003)
