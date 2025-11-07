import os
import json
import time
import threading
from src.cart_service_v2 import CartServiceV2


def start_mock():
    import mocks.mock_v2 as mv2
    t = threading.Thread(target=mv2.run_server, kwargs={'port':8002}, daemon=True)
    t.start()
    time.sleep(0.5)
    return t


def run_tests():
    data = json.load(open('C:/chatWorkspace/test_data.json'))
    start_mock()
    svc = CartServiceV2('http://localhost:8002', poll_interval=1.0, max_poll=5)
    results = []
    for case in data:
        inp = case['input']
        start = time.time()
        res = svc.check_stock(inp)
        dur = time.time() - start
        expected = case['expect_post']
        pass_flag = (res['available'] == expected['available'] and res['quantity'] == expected['quantity'])
        results.append({
            'id': case['id'], 'desc': case['desc'], 'result': res, 'expected': expected, 'pass': pass_flag, 'duration': dur
        })
        print(case['id'], 'pass' if pass_flag else 'FAIL', res)
    with open('C:/chatWorkspace/Project_B_PostChange/results/results_post.json','w') as f:
        json.dump(results, f, indent=2)


if __name__ == '__main__':
    os.makedirs('C:/chatWorkspace/Project_B_PostChange/results', exist_ok=True)
    run_tests()
