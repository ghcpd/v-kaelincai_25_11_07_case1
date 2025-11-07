#!/bin/bash

# Test runner for Project A - Pre-Change
echo "Running tests for Project A - Legacy API Integration"

# Setup environment
source venv/bin/activate

# Start mock v1 API server in background
echo "Starting mock v1 API server..."
python mocks/mock_v1_api.py &
MOCK_PID=$!

# Wait for server to start
sleep 3

# Check if mock server is running
if curl -s http://localhost:8001/health > /dev/null; then
    echo "Mock v1 API server is running"
else
    echo "Failed to start mock v1 API server"
    exit 1
fi

# Run tests
echo "Running test suite..."
cd tests
python test_pre_change.py

# Capture test exit code
TEST_EXIT_CODE=$?

# Stop mock server
echo "Stopping mock server..."
kill $MOCK_PID

# Copy test data for reference
cp ../../test_data.json ../data/

echo "Tests completed with exit code: $TEST_EXIT_CODE"
exit $TEST_EXIT_CODE