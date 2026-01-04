@echo off
echo Starting Mamameal Application...

:: Start Backend in a new window
echo Starting Backend (FastAPI)...
start "Mamameal Backend" cmd /k "cd backend & .venv\Scripts\activate & python -m uvicorn main:app --reload --port 8000"

:: Wait a moment giving backend time to init
timeout /t 5

:: Start Frontend in a new window
echo Starting Frontend (Next.js)...
start "Mamameal Frontend" cmd /k "cd frontend & npm run dev"

echo.
echo ========================================================
echo  Application is starting!
echo  Please wait for the Frontend window to show:
echo  "Ready in ...ms"
echo.
echo  Then open: http://localhost:3000
echo ========================================================
pause
