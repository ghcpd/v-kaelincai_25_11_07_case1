import json
import os
import time
import requests
import pytest
from multiprocessing import Process
import subprocess

from src.cart_service_v1 import CartServiceV1

MOCK_PORT = 5001
MOCK_URL = f'http://127.0.0.1:{MOCK_PORT}'

# Start mock server
def start_mock():
    import mocks.mock_server_v1 as server
    server.app.run(port=MOCK_PORT)

@pytest.fixture(scope='session', autouse=True)
def mock_server():
    p = Process(target=start_mock)
    p.start()
    time.sleep(1.0)
    yield
    p.terminate()
    p.join()

def configure_mock(behaviors):
    url = f"{MOCK_URL}/configure"
    requests.post(url, json={'behaviors': behaviors})


def run_test_case(tc):
    svc = CartServiceV1(MOCK_URL)
    sku = tc['input'].get('sku')
    res = svc.check_stock(sku)
    return res


def test_pre_change_all_cases(tmp_path):
    # load test data
    data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'test_data.json')
    with open(data_file) as f:
        cases = json.load(f)

    # Configure mock
    behaviors = {
        'ABC123': {'response': {'sku':'ABC123','available': True, 'quantity':12, 'note':'confirmed'}, 'delay':0},
        'ZERO': {'response': {'sku':'ZERO','available': False, 'quantity':0}, 'delay':0},
        'SLOW': {'response': {'sku':'SLOW','available': True, 'quantity':1}, 'delay':2},
        'OOS': {'response': {'sku':'OOS','available': False, 'quantity':0}, 'delay':0},
        12345: {'response': {'sku':12345,'available': False, 'quantity':0}, 'delay':0, 'status_code':500}
    }
    configure_mock(behaviors)

    results = []
    for tc in cases:
        r = run_test_case(tc)
        # Map result to expectation
        expected = tc['expected']
        passed = True
        note = ''
        if r.get('status_code') != expected.get('http_status', 200):
            passed = False
            note = f"status_code {r.get('status_code')} vs expected {expected.get('http_status')}"
        else:
            if r.get('result'):
                if expected.get('available') is not None and r['result'].get('available') != expected.get('available'):
                    passed = False
                    note = f"available mismatch {r['result'].get('available')} vs {expected.get('available')}"
        results.append({'id': tc['id'], 'passed': passed, 'result': r, 'expected': expected, 'note': note})

    out_file = os.path.join(os.path.dirname(__file__), '..', 'results', 'results_pre.json')
    with open(out_file, 'w') as f:
        json.dump(results, f, default=str, indent=2)

    log_file = os.path.join(os.path.dirname(__file__), '..', 'logs', 'log_pre.txt')
    with open(log_file, 'w') as lf:
        for r in results:
            lf.write(str(r) + '\n')

    # Assert all passed
    fails = [r for r in results if not r['passed']]
    assert len(fails) == 0, f"Failures: {fails}"
