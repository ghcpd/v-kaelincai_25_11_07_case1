import pytest
import subprocess
import requests
import time
import json
import os
import threading
from multiprocessing import Process

# start mock server using flask app
from werkzeug.serving import make_server

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Import service
from src.cart_service_v1 import check_stock_v1


def start_mock_v1(port=5001, mode=None, delay=0):
    # Run the mock_v1 app in subprocess
    cmd = ["python", "mocks/mock_v1.py", "--port", str(port)]
    env = os.environ.copy()
    if mode:
        env['MODE'] = mode
    p = subprocess.Popen(cmd, cwd=ROOT, env=env)
    time.sleep(0.5)
    return p


def stop_proc(p):
    p.terminate()
    try:
        p.wait(timeout=2)
    except Exception:
        p.kill()


def load_cases():
    path = os.path.join(ROOT, 'data', 'test_data.json')
    return json.load(open(path))


def test_pre_change_all_cases(tmp_path):
    p = start_mock_v1(5001)
    cases = load_cases()
    results = []
    base = os.environ.get('V1_API_BASE', 'http://127.0.0.1:5001')
    for case in cases:
        c = case['input']
        expected = case['expected']
        sku = c.get('sku')
        qty = c.get('quantity', 1)
        start = time.time()
        try:
            out = check_stock_v1(sku, qty)
            duration = (time.time() - start) * 1000
            success = (out['available'] == expected['available'])
            fallback = False if out['note'] != 'error' else True
            results.append({'id': case['id'], 'passed': success, 'duration_ms': duration, 'result': out, 'expected': expected, 'fallback': fallback})
        except Exception as e:
            results.append({'id': case['id'], 'passed': False, 'error': str(e)})

    stop_proc(p)

    # Save results
    out_file = os.path.join(ROOT, 'results', 'results_pre.json')
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, 'w') as fh:
        json.dump(results, fh, indent=2)

    # Basic asserts
    assert any(r['id'] == 'normal' and r['passed'] for r in results)
    assert any(r['id'] == 'boundary_zero' and not r['result']['available'] for r in results)

    for r in results:
        if r['id'] == 'server_error':
            assert (not r['passed']) or r['fallback']

