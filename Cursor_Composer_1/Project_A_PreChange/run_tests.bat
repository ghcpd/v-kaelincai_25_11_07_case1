@echo off
REM Test execution script for Project A - Pre-Change (Windows)

cd /d "%~dp0"

echo ==========================================
echo Project A - Pre-Change Test Execution
echo ==========================================

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Running setup...
    call setup.bat
    call venv\Scripts\activate.bat
)

REM Start mock API in background
echo Starting mock v1 API server...
start /B python mocks\mock_v1_api.py 8001 > logs\mock_v1.log 2>&1

REM Wait for mock API to be ready
echo Waiting for mock API to be ready...
timeout /t 3 /nobreak >nul

REM Run tests
echo Running test suite...
python tests\test_pre_change.py

REM Stop mock API (find and kill Python process on port 8001)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo ==========================================
echo Test execution complete!
echo Results saved to: results\results_pre.json
echo ==========================================

