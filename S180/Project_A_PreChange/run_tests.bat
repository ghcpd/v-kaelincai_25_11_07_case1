@echo off
REM Test runner for Project A - Pre-Change (Windows)
echo Running tests for Project A - Legacy API Integration

REM Setup environment
call venv\Scripts\activate.bat

REM Start mock v1 API server in background
echo Starting mock v1 API server...
start /B python mocks\mock_v1_api.py

REM Wait for server to start
timeout /t 5 /nobreak >nul

REM Check if mock server is running
powershell -Command "try { Invoke-RestMethod -Uri 'http://localhost:8001/health' -Method Get; Write-Host 'Mock v1 API server is running' } catch { Write-Host 'Failed to start mock v1 API server'; exit 1 }"
if %errorlevel% neq 0 exit /b 1

REM Run tests
echo Running test suite...
cd tests
python test_pre_change.py

REM Capture test exit code
set TEST_EXIT_CODE=%errorlevel%

REM Stop mock server
echo Stopping mock server...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001') do taskkill /f /pid %%a >nul 2>&1

REM Copy test data for reference
copy ..\..\test_data.json ..\data\

echo Tests completed with exit code: %TEST_EXIT_CODE%
exit /b %TEST_EXIT_CODE%