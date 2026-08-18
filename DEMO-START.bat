@echo off
REM ============================================================
REM   inride - CLIENT DEMO (quick)
REM   Double-click this file. A Chromium window opens and the
REM   automation runs in front of the audience, about 2 minutes.
REM ============================================================
cd /d "%~dp0"
title inride - Client Demo

set HEADLESS=false
set SLOW_MO=250
set HIGHLIGHT_MS=700

echo.
echo  ============================================================
echo    INRIDE AUTOMATION - CLIENT DEMO
echo    A browser window will open. Each element being validated
echo    is highlighted in yellow before it is asserted.
echo  ============================================================
echo.

.\.venv\Scripts\python.exe -m pytest -m smoke

echo.
echo  ============================================================
echo    Opening the assertion report...
echo  ============================================================
start "" "%~dp0reports\assertion_report.html"
echo.
pause
