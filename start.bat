@echo off
REM ABSORB Platform Startup Script for Windows

echo ======================================
echo    ABSORB Platform Startup Script    
echo ======================================
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed
    exit /b 1
)

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Node.js is not installed
    exit /b 1
)

echo Step 1: Setting up Python virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created
)

call venv\Scripts\activate.bat
echo Virtual environment activated

echo.
echo Step 2: Installing Python dependencies...
pip install -q -r requirements.txt
echo Python dependencies installed

echo.
echo Step 3: Installing Node.js dependencies...
cd frontend
if not exist "node_modules" (
    npm install
    echo Node.js dependencies installed
) else (
    echo Node.js dependencies already installed
)

echo.
echo Step 4: Building frontend...
npm run build
cd ..

echo.
echo ======================================
echo    Starting ABSORB Platform          
echo ======================================
echo.
echo Backend will run on: http://localhost:5000
echo Frontend dev server: http://localhost:3000
echo.
echo Press Ctrl+C to stop the servers
echo.

REM Start backend
start "ABSORB Backend" cmd /k "cd backend && python app.py"

REM Wait a bit for backend to start
timeout /t 2 /nobreak >nul

REM Start frontend dev server
start "ABSORB Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Both servers are running in separate windows
echo Close the windows to stop the servers
echo.

pause
