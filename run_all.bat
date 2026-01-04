@echo off
cd /d %~dp0

echo ==========================================
echo  Starting Mamameal Servers...
echo ==========================================

:: Start Backend
start "Mamameal Backend (DO NOT CLOSE)" cmd /k "cd backend && .venv\Scripts\python -m uvicorn main:app --reload --port 8000"

:: Start Frontend
start "Mamameal Frontend (DO NOT CLOSE)" cmd /k "cd frontend && npm run dev"

echo.
echo Servers are launching in new windows.
echo Please wait for "Ready in..." to appear in the Frontend window.
echo.
echo Then go to: http://localhost:3000
echo.
pause
