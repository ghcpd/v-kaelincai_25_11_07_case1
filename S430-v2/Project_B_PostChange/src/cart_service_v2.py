import os
import requests
import logging
import time

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("cart_service_v2")

V2_BASE = os.environ.get("V2_API_BASE", "http://127.0.0.1:5002")
V1_BASE = os.environ.get("V1_API_BASE", "http://127.0.0.1:5001")
USE_V2 = os.environ.get("USE_V2", "true").lower() in ("1","true","yes")


def call_v2(sku, regionId, warehouseGroup, quantity, timeout=5, poll_attempts=3, poll_interval=0.5):
    mode = os.environ.get('V2_API_MODE')
    mode_q = f"?mode={mode}" if mode else ""
    url = f"{V2_BASE}/api/v2/stock/availability{mode_q}"
    payload = {"sku": sku, "regionId": regionId, "warehouseGroup": warehouseGroup, "quantity": quantity}
    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        # Expected v2 shape: {"sku":"ABC","available":true,"quantity":12,"availabilityStatus":"confirmed","syncTimestamp":"2025-11-01T12:00:00Z"}
        status = data.get("availabilityStatus", "confirmed")
        if status == "confirmed":
            return {"available": bool(data.get("available", False)), "quantity": int(data.get("quantity", 0)), "note": "v2_confirmed"}
        elif status == "pending":
            # Polling loop to check for update (this is a simple approach; in prod use polling with backoff or webhooks)
            attempts = 0
            while attempts < poll_attempts:
                time.sleep(poll_interval)
                r2 = requests.post(url, json=payload, timeout=timeout)
                if r2.ok:
                    d2 = r2.json()
                    if d2.get('availabilityStatus') == 'confirmed':
                        return {"available": bool(d2.get("available", False)), "quantity": int(d2.get("quantity", 0)), "note": "v2_confirmed_after_poll"}
                attempts += 1
            # fallback to partial info
            return {"available": False, "quantity": 0, "note": "v2_pending_partial"}
        else:
            return {"available": False, "quantity": 0, "note": "v2_unknown_status"}
    except Exception as e:
        logger.exception("v2 call failed")
        return {"available": False, "quantity": 0, "note": "v2_error"}


def check_stock(sku, quantity, regionId=None, warehouseGroup=None):
    # Basic validation
    if not sku or not isinstance(sku, str):
        return {"available": False, "quantity": 0, "note": "invalid_input"}

    if USE_V2:
        if not regionId or not warehouseGroup:
            # Missing new params -> degrade gracefully to v1
            logger.warning("v2 required params missing; falling back to v1")
            return call_v1(sku, quantity)

        out = call_v2(sku, regionId, warehouseGroup, quantity)
        if out.get('note','').startswith('v2_') and out['note'] != 'v2_error':
            return out
        else:
            # On error or partial, fall back
            logger.info("v2 unavailable or error; falling back to v1")
            return call_v1(sku, quantity)

    else:
        return call_v1(sku, quantity)


def call_v1(sku, quantity):
    url = f"{V1_BASE}/api/v1/checkStock"
    payload = {"sku": sku, "quantity": quantity}
    try:
        resp = requests.post(url, json=payload, timeout=3)
        resp.raise_for_status()
        d = resp.json()
        return {"available": bool(d.get('available', False)), "quantity": int(d.get('qty', 0)), "note": "fallback_v1"}
    except Exception as e:
        logger.exception("fallback v1 call failed")
        return {"available": False, "quantity": 0, "note": "fallback_v1_error"}
