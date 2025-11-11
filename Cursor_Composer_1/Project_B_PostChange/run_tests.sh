#!/bin/bash
# Test execution script for Project B - Post-Change

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Project B - Post-Change Test Execution"
echo "=========================================="

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found. Running setup.sh..."
    bash setup.sh
    source venv/bin/activate
fi

# Start mock API in background
echo "Starting mock v2 API server..."
python mocks/mock_v2_api.py 8002 > logs/mock_v2.log 2>&1 &
MOCK_PID=$!
echo "Mock API started with PID: $MOCK_PID"

# Wait for mock API to be ready
echo "Waiting for mock API to be ready..."
sleep 3

# Run tests
echo "Running test suite..."
python tests/test_post_change.py

# Stop mock API
echo "Stopping mock API..."
kill $MOCK_PID 2>/dev/null || true
wait $MOCK_PID 2>/dev/null || true

echo "=========================================="
echo "Test execution complete!"
echo "Results saved to: results/results_post.json"
echo "=========================================="

