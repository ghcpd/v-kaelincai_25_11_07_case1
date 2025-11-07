#!/bin/bash
# Run tests for Project A (Pre-Change v1)

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="$PROJECT_DIR/logs"
RESULTS_DIR="$PROJECT_DIR/results"

mkdir -p "$LOG_DIR" "$RESULTS_DIR"

echo "=== Running Project A Tests (Pre-Change v1) ==="

# Activate virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Running setup..."
    bash "$PROJECT_DIR/setup.sh"
fi

source "$VENV_DIR/bin/activate"

# Start v1 mock server in background
echo "Starting v1 mock server..."
python "$PROJECT_DIR/mocks/mock_v1_server.py" 8001 > "$LOG_DIR/v1_server.log" 2>&1 &
V1_PID=$!
echo "v1 mock server PID: $V1_PID"

# Wait for server to start
sleep 2

# Check if server is running
if ! kill -0 $V1_PID 2>/dev/null; then
    echo "✗ Failed to start v1 mock server"
    cat "$LOG_DIR/v1_server.log"
    exit 1
fi

# Run tests
echo "Running test suite..."
python -m pytest "$PROJECT_DIR/tests/test_pre_change.py" -v --tb=short \
    | tee "$LOG_DIR/test_run.log"

# Also run standalone test runner for results JSON
echo "Generating results..."
python "$PROJECT_DIR/tests/test_pre_change.py" > "$LOG_DIR/test_output.log" 2>&1

# Kill mock server
echo "Stopping v1 mock server..."
kill $V1_PID 2>/dev/null || true
sleep 1

echo "✓ Project A tests complete"
echo "Results: $RESULTS_DIR/results_pre.json"
echo "Logs: $LOG_DIR/"
