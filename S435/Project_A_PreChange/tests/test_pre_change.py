import requests
import subprocess
import time
import json
import os
import signal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEST_DATA = os.path.join(ROOT, 'data', 'test_data.json')

# Helpers to start processes

def start_process(cmd, env=None):
    proc = subprocess.Popen(cmd, shell=False, env=env)
    return proc


def run_mock_and_service():
    # Start v1 mock
    mock_proc = start_process(['python', 'mocks/v1_mock.py'])
    # Start service
    env = os.environ.copy()
    env['V1_BASE'] = 'http://127.0.0.1:5001'
    svc_proc = start_process(['python', 'src/cart_service_v1.py'], env=env)
    time.sleep(1.0)  # wait for services
    return mock_proc, svc_proc


if __name__ == '__main__':
    os.makedirs('results', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    with open(TEST_DATA) as f:
        test_cases = json.load(f)

    mock_proc, svc_proc = run_mock_and_service()
    results = []
    errors = 0

    try:
        for c in test_cases:
            req = c['request']
            # For pre-change, only SKU is sent
            resp = requests.post('http://127.0.0.1:5002/cart/check', json={'sku': req.get('sku')}, timeout=8)
            elapsed = None
            try:
                if isinstance(body, dict) and 'meta' in body and 'duration' in body['meta']:
                    elapsed = body['meta']['duration']
                elif hasattr(resp, 'elapsed'):
                    elapsed = resp.elapsed.total_seconds()
            except Exception:
                elapsed = None
            status = resp.status_code
            body = resp.json()
            expected = c['expected']
            pass_case = False
            if status == expected['http_status']:
                # check availability based on pre-change behavior (v1)
                if 'result' in body:
                    r = body['result']
                    if r['available'] == (expected['available']) and r['quantity'] == expected['quantity']:
                        pass_case = True
            if not pass_case:
                errors += 1
            results.append({
                'id': c['id'],
                'status': status,
                'body': body,
                'expected': expected,
                'passed': pass_case,
                'latency': elapsed
            })
            print(f"Test {c['id']} - status {status} - passed: {pass_case}")

    finally:
        # Clean up
        svc_proc.terminate()
        mock_proc.terminate()
        svc_proc.wait()
        mock_proc.wait()

    with open('results/results_pre.json', 'w') as out:
        json.dump(results, out, indent=2)
    with open('logs/log_pre.txt', 'w') as log:
        log.write(f"errors: {errors}\n")
    print('done')
