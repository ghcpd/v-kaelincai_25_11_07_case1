@echo off
REM Test execution script for Project B - Post-Change (Windows)

cd /d "%~dp0"

echo ==========================================
echo Project B - Post-Change Test Execution
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
echo Starting mock v2 API server...
start /B python mocks\mock_v2_api.py 8002 > logs\mock_v2.log 2>&1

REM Wait for mock API to be ready
echo Waiting for mock API to be ready...
timeout /t 3 /nobreak >nul

REM Run tests
echo Running test suite...
python tests\test_post_change.py

REM Stop mock API (find and kill Python process on port 8002)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo ==========================================
echo Test execution complete!
echo Results saved to: results\results_post.json
echo ==========================================

