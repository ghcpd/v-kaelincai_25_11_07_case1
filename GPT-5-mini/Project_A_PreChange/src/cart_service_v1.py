import requests
import time
import logging

logger = logging.getLogger("cart_service_v1")
logging.basicConfig(level=logging.INFO)

class CartServiceV1:
    def __init__(self, base_url, timeout=2.0):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

    def check_stock(self, sku):
        """Call legacy /api/v1/checkStock with payload {"sku": ...}
        Expected response: {"sku":"ABC","available":true,"quantity":5}
        """
        url = f"{self.base_url}/api/v1/checkStock"
        payload = {"sku": sku}
        start = time.time()
        try:
            resp = requests.post(url, json=payload, timeout=self.timeout)
            duration = time.time() - start
            logger.info("v1 request duration=%.3fs status=%s", duration, resp.status_code)
            resp.raise_for_status()
            data = resp.json()
            # Simple mapping
            return {
                "http_status": resp.status_code,
                "available": bool(data.get("available")),
                "quantity": int(data.get("quantity", 0)),
                "note": data.get("note") if data.get("note") else "v1"
            }
        except Exception as e:
            duration = time.time() - start
            logger.exception("v1 request failed duration=%.3fs", duration)
            return {"http_status": 0, "available": False, "quantity": 0, "note": f"error:{e}"}


if __name__ == '__main__':
    import sys
    base = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8001'
    svc = CartServiceV1(base)
    print(svc.check_stock('ABC123'))
