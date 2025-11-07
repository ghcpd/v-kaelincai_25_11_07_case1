from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import time
import threading
import urllib.parse as urlparse

# Simple in-memory store to simulate pending -> confirmed
PENDING_STORE = {}

class MockV2Handler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def _read_json(self):
        length = int(self.headers.get('content-length', 0))
        body = self.rfile.read(length).decode('utf-8') if length else '{}'
        return json.loads(body)

    def do_POST(self):
        parsed = urlparse.urlparse(self.path)
        path = parsed.path
        qs = urlparse.parse_qs(parsed.query)
        delay = float(qs.get('delay', [0])[0])
        status = int(qs.get('status', [200])[0])

        if delay:
            time.sleep(delay)

        if path.endswith('/api/v2/stock/availability'):
            payload = self._read_json()
            sku = payload.get('sku')
            # special behavior by sku to drive tests
            if sku == 'PEND01':
                # create a pending entry that will be confirmed after 2 seconds
                PENDING_STORE[sku] = {'available': True, 'quantity': 7, 'confirmed_after': time.time() + 2}
                resp = {"sku": sku, "availabilityStatus": "pending"}
                self._set_headers(200)
                self.wfile.write(json.dumps(resp).encode())
                return
            if sku == 'SLOW01':
                self._set_headers(500)
                self.wfile.write(json.dumps({'error':'internal slow error'}).encode())
                return
            # normal
            quantity = 12 if sku == 'ABC123' else 3 if sku == 'SLOW01' else 0
            resp = {"sku": sku, "availabilityStatus": "confirmed", "available": quantity>0, "quantity": quantity}
            self._set_headers(200)
            self.wfile.write(json.dumps(resp).encode())
            return

        if path.endswith('/api/v2/stock/availability/poll'):
            payload = self._read_json()
            sku = payload.get('sku')
            entry = PENDING_STORE.get(sku)
            if entry and time.time() >= entry['confirmed_after']:
                resp = {"sku": sku, "availabilityStatus": "confirmed", "available": entry['available'], "quantity": entry['quantity']}
                # remove after confirming
                del PENDING_STORE[sku]
                self._set_headers(200)
                self.wfile.write(json.dumps(resp).encode())
                return
            # still pending
            resp = {"sku": sku, "availabilityStatus": "pending"}
            self._set_headers(200)
            self.wfile.write(json.dumps(resp).encode())
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({'error':'not found'}).encode())


def run_server(port=8002):
    server = HTTPServer(('0.0.0.0', port), MockV2Handler)
    print(f"Mock v2 running on :{port}")
    server.serve_forever()

if __name__ == '__main__':
    run_server()
