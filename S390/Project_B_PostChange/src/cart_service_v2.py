import requests
import time
import datetime

class CartServiceV2:
    def __init__(self, v2_base_url, v1_fallback_url=None, use_v2=True, poll_interval=1, poll_timeout=10):
        self.v2_base_url = v2_base_url.rstrip('/')
        self.v1_fallback_url = v1_fallback_url.rstrip('/') if v1_fallback_url else None
        self.use_v2 = use_v2
        self.poll_interval = poll_interval
        self.poll_timeout = poll_timeout

    def check_stock_v1(self, sku):
        if not self.v1_fallback_url:
            return {'status_code': 500, 'error': 'no v1 fallback configured'}
        url = f"{self.v1_fallback_url}/api/v1/checkStock"
        try:
            r = requests.post(url, json={'sku': sku}, timeout=5)
            r.raise_for_status()
            payload = r.json()
            return {'status_code': r.status_code, 'result': {'sku': payload.get('sku', sku), 'available': bool(payload.get('available', False)), 'quantity': int(payload.get('quantity', 0)), 'note': 'v1-fallback'}}
        except Exception as e:
            return {'status_code': 500, 'error': str(e)}

    def check_stock(self, sku, regionId, warehouseGroup):
        if not self.use_v2:
            return self.check_stock_v1(sku)

        # Validate required parameters
        if not regionId or not warehouseGroup:
            return {'status_code': 400, 'error': 'missing regionId or warehouseGroup'}

        url = f"{self.v2_base_url}/api/v2/stock/availability"
        start = time.perf_counter()
        try:
            r = requests.post(url, json={'sku': sku, 'regionId': regionId, 'warehouseGroup': warehouseGroup}, timeout=5)
            duration = time.perf_counter() - start
            r.raise_for_status()
            payload = r.json()

            status = payload.get('availabilityStatus')
            if status == 'confirmed' or status is None:
                return {'status_code': r.status_code, 'result': {'sku': payload.get('sku', sku), 'available': bool(payload.get('available', False)), 'quantity': int(payload.get('quantity', 0)), 'note': 'v2-confirmed'}, 'duration': duration}
            elif status == 'pending':
                # Poll until confirmed or timeout
                sync_timestamp = payload.get('syncTimestamp')
                # Poll strategy: wait until syncTimestamp or until poll_timeout
                deadline = time.time() + self.poll_timeout
                while time.time() < deadline:
                    time.sleep(self.poll_interval)
                    try:
                        r2 = requests.post(url, json={'sku': sku, 'regionId': regionId, 'warehouseGroup': warehouseGroup}, timeout=5)
                        r2.raise_for_status()
                        payload2 = r2.json()
                        if payload2.get('availabilityStatus') == 'confirmed':
                            duration2 = time.perf_counter() - start
                            return {'status_code': r2.status_code, 'result': {'sku': payload2.get('sku', sku), 'available': bool(payload2.get('available', False)), 'quantity': int(payload2.get('quantity', 0)), 'note': 'v2-confirmed-after-polling'}, 'duration': duration2}
                    except Exception:
                        # if poll fails, try again until deadline
                        pass
                # if not confirmed after polling, fallback
                fb = self.check_stock_v1(sku)
                fb.setdefault('result', {})
                fb['result']['note'] = 'fallback-after-timeout'
                fb['duration_v2'] = time.perf_counter() - start
                return fb
            else:
                # Unknown status; fallback
                fb = self.check_stock_v1(sku)
                fb.setdefault('result', {})
                fb['result']['note'] = 'fallback-unknown-status'
                return fb
        except Exception as e:
            # fallback
            fb = self.check_stock_v1(sku)
            fb.setdefault('result', {})
            fb['result']['note'] = 'fallback-on-exception'
            fb['error'] = str(e)
            return fb

if __name__ == '__main__':
    svc = CartServiceV2('http://localhost:5002', v1_fallback_url='http://localhost:5001', use_v2=True)
    print(svc.check_stock('ABC123', 'ap-sg-1', 'WG-2'))
