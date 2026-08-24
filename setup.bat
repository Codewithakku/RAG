@echo off
echo ============================================
echo   RAG PDF App - Windows Setup Script
echo ============================================
echo.

REM --- Check Python ---
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found! Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)
echo [OK] Python found.

REM --- Check Node.js ---
node --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js not found! Please install Node.js 18+ from https://nodejs.org
    pause
    exit /b 1
)
echo [OK] Node.js found.

echo.
echo --- Setting up Backend ---
cd backend

IF NOT EXIST venv (
    echo Creating Python virtual environment...
    python -m venv venv
)

echo Activating venv and installing packages...
call venv\Scripts\activate
pip install -r requirements.txt

IF NOT EXIST .env (
    echo Creating .env file from example...
    copy .env.example .env
    echo.
    echo [ACTION REQUIRED] Open backend\.env and add your GOOGLE_API_KEY!
    notepad .env
)

cd ..

echo.
echo --- Setting up Frontend ---
cd frontend
echo Installing Node.js packages...
npm install
cd ..

echo.
echo ============================================
echo   Setup Complete! 
echo   Now run: start_app.bat to launch the app
echo ============================================
pause
