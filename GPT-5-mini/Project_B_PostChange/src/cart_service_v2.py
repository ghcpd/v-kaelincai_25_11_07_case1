import requests
import time
import logging
from datetime import datetime, timezone

logger = logging.getLogger("cart_service_v2")
logging.basicConfig(level=logging.INFO)


class CartServiceV2:
    def __init__(self, base_url, timeout=2.0, poll_interval=1.0, max_poll=3, feature_flag_v2=True):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.poll_interval = poll_interval
        self.max_poll = max_poll
        self.feature_flag_v2 = feature_flag_v2

    def _validate_input(self, payload):
        if not isinstance(payload.get('sku'), str):
            raise ValueError('sku must be string')
        if 'regionId' not in payload or 'warehouseGroup' not in payload:
            raise ValueError('regionId and warehouseGroup required')

    def check_stock(self, payload):
        """Call v2 endpoint with payload: {sku, regionId, warehouseGroup}
        v2 response may include availabilityStatus: 'confirmed'|'pending' and optional syncTimestamp
        If pending, poll until confirmed or max_poll reached, else fallback.
        """
        start = time.time()
        try:
            self._validate_input(payload)
        except Exception as e:
            logger.exception('invalid input')
            return {"http_status": 0, "available": False, "quantity": 0, "note": f"validation:{e}"}

        if not self.feature_flag_v2:
            # Feature disabled: use adapter to v1 (not implemented here)
            return {"http_status": 0, "available": False, "quantity": 0, "note": "v2_disabled"}

        url = f"{self.base_url}/api/v2/stock/availability"
        try:
            resp = requests.post(url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            status = data.get('availabilityStatus', 'confirmed')
            if status == 'confirmed':
                return {"http_status": resp.status_code, "available": bool(data.get('available', False)), "quantity": int(data.get('quantity', 0)), "note": 'confirmed'}
            elif status == 'pending':
                # Polling strategy
                polls = 0
                while polls < self.max_poll:
                    polls += 1
                    time.sleep(self.poll_interval)
                    poll_url = f"{self.base_url}/api/v2/stock/availability/poll"
                    poll_payload = {"sku": payload['sku'], "regionId": payload['regionId'], "warehouseGroup": payload['warehouseGroup']}
                    p = requests.post(poll_url, json=poll_payload, timeout=self.timeout)
                    if p.status_code == 200:
                        pdata = p.json()
                        if pdata.get('availabilityStatus') == 'confirmed':
                            return {"http_status": p.status_code, "available": bool(pdata.get('available', False)), "quantity": int(pdata.get('quantity', 0)), "note": 'confirmed_after_poll'}
                    else:
                        logger.warning('poll returned status %s', p.status_code)
                # fallback if still pending
                return {"http_status": resp.status_code, "available": False, "quantity": 0, "note": 'pending_timeout'}
            else:
                return {"http_status": resp.status_code, "available": bool(data.get('available', False)), "quantity": int(data.get('quantity', 0)), "note": status}
        except Exception as e:
            logger.exception('v2 request failed')
            return {"http_status": 0, "available": False, "quantity": 0, "note": f"error:{e}"}


if __name__ == '__main__':
    svc = CartServiceV2('http://localhost:8002')
    print(svc.check_stock({'sku':'ABC123','regionId':'ap-sg-1','warehouseGroup':'WG-2'}))
