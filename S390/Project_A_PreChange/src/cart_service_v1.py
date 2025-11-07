import requests
import time

class CartServiceV1:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')

    def check_stock(self, sku):
        url = f"{self.base_url}/api/v1/checkStock"
        start = time.perf_counter()
        try:
            r = requests.post(url, json={'sku': sku}, timeout=5)
            duration = time.perf_counter() - start
            r.raise_for_status()
            payload = r.json()
            # Normalize to standard structure
            result = {
                'sku': payload.get('sku', sku),
                'available': bool(payload.get('available', False)),
                'quantity': int(payload.get('quantity', 0)),
                'note': payload.get('note', 'v1')
            }
            return {'status_code': r.status_code, 'result': result, 'duration': duration}
        except Exception as e:
            duration = time.perf_counter() - start
            return {'status_code': 500, 'error': str(e), 'duration': duration}

if __name__ == '__main__':
    svc = CartServiceV1('http://localhost:5001')
    print(svc.check_stock('ABC123'))
