@echo off
echo.
echo ===============================================
echo   Urban Issue Reporter - Startup Script
echo ===============================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo [ERROR] Virtual environment not found!
    echo Please create it first: python -m venv venv
    pause
    exit /b 1
)

REM Activate virtual environment
echo [1/4] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if MongoDB is accessible (optional - will continue anyway)
echo [2/4] Checking MongoDB connection...
python -c "from pymongo import MongoClient; from config import get_config; config=get_config(); client=MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=3000); client.admin.command('ping'); print('  ✓ MongoDB connected')" 2>nul
if %errorlevel% neq 0 (
    echo   ⚠ Warning: Could not connect to MongoDB
    echo   Please ensure MongoDB is running or check your connection string
    echo.
)

REM Check Python dependencies
echo [3/4] Checking dependencies...
python -c "import flask; import pymongo; import werkzeug; print('  ✓ Core dependencies installed')" 2>nul
if %errorlevel% neq 0 (
    echo   ⚠ Warning: Some dependencies might be missing
    echo   Installing dependencies...
    pip install -r requirements.txt
)

REM Start the application
echo [4/4] Starting application...
echo.
echo ===============================================
echo   Application is starting...
echo   Access at: http://localhost:5000
echo   Press Ctrl+C to stop
echo ===============================================
echo.

python run.py

pause
