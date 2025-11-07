import requests
import subprocess
import time
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEST_DATA = os.path.join(ROOT, 'data', 'test_data.json')

# Helpers to start processes

def start_process(cmd, env=None):
    proc = subprocess.Popen(cmd, shell=False, env=env)
    return proc


def run_mocks_and_service():
    # Start v2 mock and v1 mock for fallback
    mock_v2 = start_process(['python', 'mocks/v2_mock.py'])
    mock_v1 = start_process(['python', 'mocks/v1_mock.py'])
    env = os.environ.copy()
    env['V2_BASE'] = 'http://127.0.0.1:6001'
    env['V1_BASE'] = 'http://127.0.0.1:6002'
    svc_proc = start_process(['python', 'src/cart_service_v2.py'], env=env)
    time.sleep(1.0)  # wait for services
    return mock_v2, mock_v1, svc_proc


if __name__ == '__main__':
    os.makedirs('results', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    with open(TEST_DATA) as f:
        test_cases = json.load(f)

    mock_v2, mock_v1, svc_proc = run_mocks_and_service()

    results = []
    errors = 0

    try:
        for c in test_cases:
            req = c['request']
            # For v2, we send full payload
            payload = {k: v for k, v in req.items() if v is not None}
            try:
                resp = requests.post('http://127.0.0.1:6003/cart/check', json=payload, timeout=10)
            except Exception as e:
                resp = None
                body = {'error': str(e)}
                status = 500
            if resp is not None:
                status = resp.status_code
                body = resp.json()
            expected = c['expected']
            pass_case = False
            # Compare based on expected note (fallback or confirmed)
            if status == expected['http_status']:
                if 'result' in body:
                    r = body['result']
                    if r['available'] == expected['available'] and r['quantity'] == expected['quantity']:
                        pass_case = True
            if not pass_case:
                errors += 1
            # pick up duration from service meta if available
            lat = None
            try:
                if isinstance(body, dict) and 'meta' in body and 'duration' in body['meta']:
                    lat = body['meta']['duration']
                elif resp and hasattr(resp, 'elapsed'):
                    lat = resp.elapsed.total_seconds()
            except Exception:
                lat = None
            results.append({
                'id': c['id'],
                'status': status,
                'body': body,
                'expected': expected,
                'passed': pass_case,
                'latency': lat
            })
            print(f"Test {c['id']} - status {status} - passed: {pass_case}")
    finally:
        svc_proc.terminate()
        mock_v2.terminate()
        mock_v1.terminate()
        svc_proc.wait()
        mock_v2.wait()
        mock_v1.wait()

    with open('results/results_post.json', 'w') as out:
        json.dump(results, out, indent=2)
    with open('logs/log_post.txt', 'w') as log:
        log.write(f"errors: {errors}\n")
    print('done')
