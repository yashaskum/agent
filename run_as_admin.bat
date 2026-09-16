@echo off
title J.A.R.V.I.S. // Stark Industries (Admin Launcher)
cd /d "%~dp0"

:: Check if already elevated
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [JARVIS] Requesting Administrator Elevation...
    powershell -Command "Start-Process cmd -ArgumentList '/k \"cd /d %~dp0 && python start.py\"' -Verb RunAs"
    exit /b
)

:: If already admin
color 0B
echo =========================================================
echo       INITIALIZING J.A.R.V.I.S. (ADMINISTRATOR)
echo =========================================================
echo.
python start.py
pause
