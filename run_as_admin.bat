@echo off
title J.A.R.V.I.S. // Stark Industries (Admin Launcher)
cd /d "%~dp0"

:: Check if already elevated
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [JARVIS] Requesting Administrator Elevation...
    powershell -Command "Start-Process '%~dp0run_as_admin.bat' -Verb RunAs"
    exit /b
)

:: If already admin
color 0B
echo =========================================================
echo       INITIALIZING J.A.R.V.I.S. (ADMINISTRATOR)
echo =========================================================
echo.
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe start.py
) else (
    python start.py
)
pause
