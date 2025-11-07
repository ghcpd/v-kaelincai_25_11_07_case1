import os
import json
import time
import threading
import requests
from src.cart_service_v1 import CartServiceV1


def start_mock():
    import mocks.mock_v1 as mv1
    t = threading.Thread(target=mv1.run_server, kwargs={'port':8001}, daemon=True)
    t.start()
    time.sleep(0.5)
    return t


def run_tests():
    data = json.load(open('C:/chatWorkspace/test_data.json'))
    start_mock()
    svc = CartServiceV1('http://localhost:8001')
    results = []
    for case in data:
        sku = case['input'].get('sku') if isinstance(case['input'].get('sku'), str) else str(case['input'].get('sku'))
        # For pre-change we only send sku; mocks accept quantity overrides via query but we'll rely on default
        start = time.time()
        res = svc.check_stock(sku)
        dur = time.time() - start
        expected = case['expect_pre']
        pass_flag = (res['available'] == expected['available'] and res['quantity'] == expected['quantity'])
        results.append({
            'id': case['id'], 'desc': case['desc'], 'result': res, 'expected': expected, 'pass': pass_flag, 'duration': dur
        })
        print(case['id'], 'pass' if pass_flag else 'FAIL', res)
    with open('C:/chatWorkspace/Project_A_PreChange/results/results_pre.json','w') as f:
        json.dump(results, f, indent=2)


if __name__ == '__main__':
    os.makedirs('C:/chatWorkspace/Project_A_PreChange/results', exist_ok=True)
    run_tests()
