#!/bin/bash

# ABSORB Platform Startup Script for Linux/Mac

echo "======================================"
echo "   ABSORB Platform Startup Script    "
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    exit 1
fi

echo "Step 1: Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created"
fi

source venv/bin/activate
echo "Virtual environment activated"

echo ""
echo "Step 2: Installing Python dependencies..."
pip install -q -r requirements.txt
echo "Python dependencies installed"

echo ""
echo "Step 3: Installing Node.js dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
    echo "Node.js dependencies installed"
else
    echo "Node.js dependencies already installed"
fi

echo ""
echo "Step 4: Building frontend..."
npm run build
cd ..

echo ""
echo "======================================"
echo "   Starting ABSORB Platform          "
echo "======================================"
echo ""
echo "Backend will run on: http://localhost:5000"
echo "Frontend dev server: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Start backend in background
cd backend
python app.py &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 2

# Start frontend dev server
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "Servers stopped"
    exit 0
}

# Set up trap to call cleanup on script exit
trap cleanup INT TERM

# Wait for both processes
wait
