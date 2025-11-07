@echo off
REM Run tests for Project B (Post-Change v2) - Windows batch

setlocal enabledelayedexpansion

set "PROJECT_DIR=%~dp0"
set "VENV_DIR=%PROJECT_DIR%venv"
set "LOG_DIR=%PROJECT_DIR%logs"
set "RESULTS_DIR=%PROJECT_DIR%results"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%RESULTS_DIR%" mkdir "%RESULTS_DIR%"

echo.
echo === Running Project B Tests ^(Post-Change v2^) ===
echo.

REM Check and setup venv if needed
if not exist "%VENV_DIR%" (
    echo Virtual environment not found. Running setup...
    call "%PROJECT_DIR%setup.bat"
) else (
    echo Virtual environment found
)

REM Activate venv
call "%VENV_DIR%\Scripts\activate.bat"

REM Start v2 mock server in background
echo Starting v2 mock server on port 8002...
start "v2_mock_server" python "%PROJECT_DIR%mocks\mock_v2_server.py" 8002
set "V2_PID=!ERRORLEVEL!"

REM Wait for server to start
timeout /t 2 /nobreak

REM Run tests
echo Running test suite...
python -m pytest "%PROJECT_DIR%tests\test_post_change.py" -v --tb=short

REM Run standalone test runner
echo Generating results...
python "%PROJECT_DIR%tests\test_post_change.py"

echo.
echo ✓ Project B tests complete
echo Results: %RESULTS_DIR%\results_post.json
echo Logs: %LOG_DIR%\
echo.

endlocal
