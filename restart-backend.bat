@echo off
echo ========================================
echo CareerFit Backend Service Restart
echo ========================================
echo.

echo [Step 1/3] Stopping backend service on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo Found process %%a on port 8000
    taskkill /F /PID %%a 2>nul
    if errorlevel 1 (
        echo Failed to stop process %%a
    ) else (
        echo Successfully stopped process %%a
    )
)
echo.

echo [Step 2/3] Waiting 2 seconds...
timeout /t 2 /nobreak >nul
echo.

echo [Step 3/3] Starting backend service...
echo Backend will start on http://localhost:8000
echo.
echo Press Ctrl+C to stop the service
echo ========================================
echo.

cd /d "%~dp0backend"
python -m uvicorn app.main:app --reload --port 8000
