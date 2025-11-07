@echo off
REM Setup script for Project A - Pre-Change (Windows)
echo Setting up Project A - Legacy API Integration

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create necessary directories
if not exist "logs" mkdir logs
if not exist "results" mkdir results
if not exist "data" mkdir data

echo Setup complete for Project A