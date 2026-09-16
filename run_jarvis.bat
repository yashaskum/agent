@echo off
title J.A.R.V.I.S. // Stark Industries Mark VII
cd /d "%~dp0"
color 0B
echo =========================================================
echo       INITIALIZING J.A.R.V.I.S. TACTICAL HUD
echo =========================================================
echo.
if exist ".venv\Scripts\python.exe" (
	.venv\Scripts\python.exe start.py
) else (
	python start.py
)
pause
