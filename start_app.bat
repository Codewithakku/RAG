@echo off
echo ============================================
echo   Starting RAG PDF App
echo ============================================
echo.

REM Start Backend in new window
echo Starting Backend (FastAPI) on http://localhost:8000 ...
start "RAG Backend" cmd /k "cd /d %~dp0backend && venv\Scripts\activate && python main.py"

REM Wait 3 seconds for backend to start
timeout /t 3 /nobreak >nul

REM Start Frontend in new window
echo Starting Frontend (React/Vite) on http://localhost:5173 ...
start "RAG Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

REM Wait 4 seconds then open browser
timeout /t 4 /nobreak >nul
echo Opening browser...
start http://localhost:5173

echo.
echo ============================================
echo   App is running!
echo   Backend  -> http://localhost:8000
echo   Frontend -> http://localhost:5173
echo   API Docs -> http://localhost:8000/docs
echo ============================================
