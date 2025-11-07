from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import time
import threading
import urllib.parse as urlparse

class MockV1Handler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def do_POST(self):
        parsed = urlparse.urlparse(self.path)
        qs = urlparse.parse_qs(parsed.query)
        length = int(self.headers.get('content-length', 0))
        body = self.rfile.read(length).decode('utf-8') if length else '{}'
        payload = json.loads(body)
        # behavior modifiers: ?delay=seconds&status=500&quantity=...
        delay = float(qs.get('delay', [0])[0])
        status = int(qs.get('status', [200])[0])
        quantity = int(qs.get('quantity', [5])[0])

        if delay:
            time.sleep(delay)

        if status >= 400:
            self._set_headers(status)
            self.wfile.write(json.dumps({'error':'mock error'}).encode())
            return

        sku = payload.get('sku')
        # SKU-based behavior to support test cases
        if sku == 'ABC123':
            quantity = 12
        elif sku == 'ZERO01':
            quantity = 0
        elif sku == 'PEND01':
            quantity = 0
        elif sku == 'SLOW01':
            quantity = 3
        else:
            # handle numeric or unknown SKUs
            try:
                if int(sku) == 12345:
                    quantity = 0
            except Exception:
                pass
        available = quantity > 0
        resp = {"sku": sku, "available": available, "quantity": quantity}
        self._set_headers(200)
        self.wfile.write(json.dumps(resp).encode())


def run_server(port=8001):
    server = HTTPServer(('0.0.0.0', port), MockV1Handler)
    print(f"Mock v1 running on :{port}")
    server.serve_forever()

if __name__ == '__main__':
    run_server()
