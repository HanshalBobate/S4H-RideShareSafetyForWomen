@echo off
REM Startup script for S4H-1 Flask Backend
REM Windows Batch File

echo ============================================================
echo S4H-1 Ride Safety Monitoring System - Backend Server
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo [1/4] Checking Python installation...
python --version
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo [2/4] Creating virtual environment...
    python -m venv venv
    echo Virtual environment created successfully
) else (
    echo [2/4] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo [3/4] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install dependencies
echo [4/4] Installing dependencies...
pip install -r requirements.txt
echo.

echo ============================================================
echo Starting Flask Server...
echo ============================================================
echo Server will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

REM Start the Flask application
python app.py

REM Deactivate virtual environment on exit
deactivate
