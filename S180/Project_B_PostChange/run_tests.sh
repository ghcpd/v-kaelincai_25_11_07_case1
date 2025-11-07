#!/bin/bash
set -e
source venv/bin/activate

# Start mock v1 and v2
python ../Project_A_PreChange/mocks/mock_v1_api.py &
V1_PID=$!
python mocks/mock_v2_api.py &
V2_PID=$!

sleep 3

# Run tests
cd tests
python test_post_change.py || TEST_EXIT_CODE=$?

# Stop mocks
kill $V2_PID || true
kill $V1_PID || true

exit ${TEST_EXIT_CODE:-0}