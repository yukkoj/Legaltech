@echo off
REM Windows batch script to start the Legal Document Creator UI

echo.
echo ========================================
echo Legal Document Creator - Web UI Startup
echo ========================================
echo.

cd /d "%~dp0legal_doc_creator"

REM Check if app.py exists
if not exist "app.py" (
    echo Error: app.py not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ and add it to your PATH
    pause
    exit /b 1
)

REM Install/upgrade dependencies
echo Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo Starting Flask server...
echo ========================================
echo.
echo Server will run on: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start Flask app
python app.py

pause
