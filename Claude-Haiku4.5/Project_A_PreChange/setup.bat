@echo off
REM Setup script for Project A (Pre-Change) - Windows batch

setlocal enabledelayedexpansion

set "PROJECT_DIR=%~dp0"
set "VENV_DIR=%PROJECT_DIR%venv"

echo.
echo === Setting up Project A ^(Pre-Change v1^) ===
echo.

REM Create virtual environment if it doesn't exist
if not exist "%VENV_DIR%" (
    echo Creating virtual environment...
    python -m venv "%VENV_DIR%"
) else (
    echo Virtual environment already exists
)

REM Activate and install
echo Installing dependencies...
call "%VENV_DIR%\Scripts\activate.bat"
python -m pip install --upgrade pip
pip install -r "%PROJECT_DIR%requirements.txt"

echo.
echo ✓ Project A setup complete
echo To activate environment: %VENV_DIR%\Scripts\activate.bat
echo.

endlocal
