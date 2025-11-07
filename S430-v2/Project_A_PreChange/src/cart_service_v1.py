import requests
import logging
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("cart_service_v1")

API_BASE = os.environ.get("V1_API_BASE", "http://127.0.0.1:5001")


def check_stock_v1(sku, quantity):
    """Calls legacy /api/v1/checkStock endpoint.

    Input: sku: str, quantity: int
    Returns: dict {"available": bool, "quantity": int, "note": str}
    """
    payload = {"sku": sku, "quantity": quantity}
    url = f"{API_BASE}/api/v1/checkStock"
    try:
        resp = requests.post(url, json=payload, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        # Legacy returns {"sku":"ABC123","available":true,"qty":12}
        return {
            "available": bool(data.get("available", False)),
            "quantity": int(data.get("qty", 0)),
            "note": data.get("note", "legacy")
        }
    except Exception as e:
        logger.exception("v1 check_stock failed")
        return {"available": False, "quantity": 0, "note": "error"}
