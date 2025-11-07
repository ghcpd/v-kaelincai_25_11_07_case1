import json
import os
import time
import requests
import pytest
from multiprocessing import Process

from src.cart_service_v2 import CartServiceV2

MOCK_V2_PORT = 5002
MOCK_V2_URL = f'http://127.0.0.1:{MOCK_V2_PORT}'
MOCK_V1_PORT = 5001
MOCK_V1_URL = f'http://127.0.0.1:{MOCK_V1_PORT}'

# Start both mock servers using subprocesses
@pytest.fixture(scope='session', autouse=True)
def mock_servers():
    import subprocess, sys, os
    # Start mock v2
    v2_script = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mocks', 'mock_server_v2.py'))
    p2 = subprocess.Popen([sys.executable, v2_script], shell=False)
    # Start mock v1 from Project A path
    v1_script = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Project_A_PreChange', 'mocks', 'mock_server_v1.py'))
    p1 = subprocess.Popen([sys.executable, v1_script], shell=False)

    time.sleep(1.0)
    yield
    p2.terminate()
    p2.wait()
    p1.terminate()
    p1.wait()


def configure_mock_v1(behaviors):
    url = f"{MOCK_V1_URL}/configure"
    requests.post(url, json={'behaviors': behaviors})


def configure_mock_v2(behaviors):
    url = f"{MOCK_V2_URL}/configure"
    requests.post(url, json={'behaviors': behaviors})


def run_test_case(tc, svc):
    inp = tc['input']
    sku = inp.get('sku')
    region = inp.get('regionId')
    wg = inp.get('warehouseGroup')
    return svc.check_stock(sku, region, wg)


def test_post_change_all_cases(tmp_path):
    # load test data
    data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'test_data.json')
    with open(data_file) as f:
        cases = json.load(f)

    # Configure mocks
    behaviors_v2 = {
        'ABC123': {'response': {'sku':'ABC123','available': True, 'quantity':12, 'availabilityStatus':'confirmed'}, 'delay':0},
        'ZERO': {'response': {'sku':'ZERO','available': False, 'quantity':0, 'availabilityStatus':'confirmed'}, 'delay':0},
        'PEND': {'response': {'sku':'PEND','available': False, 'quantity':2, 'availabilityStatus':'pending', 'syncTimestamp': (time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(time.time()+2)))}, 'delay':0},
        'SLOW': {'response': {'sku':'SLOW','available': True, 'quantity':1, 'availabilityStatus':'confirmed'}, 'delay':6},
        # malformed SKU's behavior left default
    }
    configure_mock_v2(behaviors_v2)

    behaviors_v1 = {
        'ABC123': {'response': {'sku':'ABC123','available': True, 'quantity':12}, 'delay':0},
        'ZERO': {'response': {'sku':'ZERO','available': False, 'quantity':0}, 'delay':0},
        'SLOW': {'response': {'sku':'SLOW','available': True, 'quantity':1}, 'delay':0},
    }
    configure_mock_v1(behaviors_v1)

    svc = CartServiceV2(MOCK_V2_URL, v1_fallback_url=MOCK_V1_URL, use_v2=True, poll_interval=1, poll_timeout=5)

    results = []
    for tc in cases:
        r = run_test_case(tc, svc)
        expected = tc['expected']
        passed = True
        note = ''
        # If expected http_status is 400 (malformed), we expect fallback with status code 400 or error
        if expected.get('http_status') == 400:
            if r.get('status_code', 200) == 200:
                passed = False
                note = 'expected 400 but got 200'
        else:
            if r.get('status_code') != expected.get('http_status', 200) and expected.get('http_status') != 200:
                passed = False
                note = f"status_code {r.get('status_code')} vs expected {expected.get('http_status')}"
            else:
                if r.get('result'):
                    if expected.get('available') is not None and r['result'].get('available') != expected.get('available'):
                        passed = False
                        note = f"available mismatch {r['result'].get('available')} vs {expected.get('available')}"
                    if expected.get('note_contains'):
                        if expected.get('note_contains') not in r['result'].get('note', ''):
                            passed = False
                            note = f"note does not contain expected fragment"
        results.append({'id': tc['id'], 'passed': passed, 'result': r, 'expected': expected, 'note': note})

    out_file = os.path.join(os.path.dirname(__file__), '..', 'results', 'results_post.json')
    with open(out_file, 'w') as f:
        json.dump(results, f, default=str, indent=2)

    log_file = os.path.join(os.path.dirname(__file__), '..', 'logs', 'log_post.txt')
    with open(log_file, 'w') as lf:
        for r in results:
            lf.write(str(r) + '\n')

    fails = [r for r in results if not r['passed']]
    assert len(fails) == 0, f"Failures: {fails}"
