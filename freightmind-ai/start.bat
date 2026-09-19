@echo off
echo ============================================================
echo   FreightMind AI - Starting Backend and Frontend
echo ============================================================
echo.
cd /d "%~dp0"

echo [*] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "FreightMind Backend" cmd /k ".\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo [*] Starting React Frontend on http://localhost:5173 ...
cd /d "%~dp0frontend"
start "FreightMind Frontend" cmd /k "npm run dev"

echo.
echo [OK] Both services have been started!
echo      Frontend: http://localhost:5173
echo      Backend:  http://localhost:8000/docs
echo ============================================================
pause
