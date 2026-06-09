#!/bin/bash

# Unix/Linux/Mac shell script to start the Legal Document Creator UI

echo ""
echo "========================================"
echo "Legal Document Creator - Web UI Startup"
echo "========================================"
echo ""

# Change to the script directory
cd "$(dirname "$0")/legal_doc_creator"

# Check if app.py exists
if [ ! -f "app.py" ]; then
    echo "Error: app.py not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7+ and ensure it's in your PATH"
    exit 1
fi

# Install/upgrade dependencies
echo "Installing dependencies..."
pip3 install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo ""
echo "========================================"
echo "Starting Flask server..."
echo "========================================"
echo ""
echo "Server will run on: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start Flask app
python3 app.py
