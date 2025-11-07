import subprocess
import time
import os
import json

from src.cart_service_v2 import check_stock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def start_mock_v1(port=5001):
    cmd = ["python", "Project_A_PreChange/mocks/mock_v1.py", "--port", str(port)]
    p = subprocess.Popen(cmd, cwd=os.path.join(ROOT, '..'))
    time.sleep(0.5)
    return p


def start_mock_v2(port=5002, mode=None, delay=0):
    cmd = ["python", "mocks/mock_v2.py", "--port", str(port)]
    env = os.environ.copy()
    p = subprocess.Popen(cmd, cwd=ROOT, env=env)
    time.sleep(0.5)
    return p


def load_cases():
    path = os.path.join(os.path.dirname(ROOT), 'test_data.json')
    return json.load(open(path))


def test_post_change_all(tmp_path):
    # start v1 and v2 mocks
    v1 = start_mock_v1()
    v2 = start_mock_v2()
    os.environ['USE_V2'] = 'true'
    cases = load_cases()
    results = []
    for case in cases:
        c = case['input']
        expected = case['expected']
        mode = c.get('mode')
        # call is parameterized by query param on mock
        os.environ['V2_API_BASE'] = 'http://127.0.0.1:5002'
        os.environ['V2_API_MODE'] = mode

        sku = c.get('sku')
        qty = c.get('quantity', 1)
        region = c.get('regionId')
        wg = c.get('warehouseGroup')
        start = time.time()
        out = check_stock(sku, qty, region, wg)
        duration = (time.time()-start)*1000
        passed = (out['available'] == expected['available'])
        fallback = out.get('note','').startswith('fallback') or expected.get('fallback', False)
        results.append({'id': case['id'], 'expected': expected, 'result': out, 'duration_ms':duration,'passed':passed,'fallback':fallback})

    # save results
    out_file = os.path.join(ROOT, 'results', 'results_post.json')
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    json.dump(results, open(out_file, 'w'), indent=2)

    # basic asserts
    assert any(r['id']=='normal' and r['result']['available'] for r in results)
    assert any(r['id']=='async_pending' and r['result']['available'] for r in results)

    # tear down
    v1.terminate(); v2.terminate()

