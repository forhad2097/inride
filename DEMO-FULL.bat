@echo off
REM ============================================================
REM   inride - CLIENT DEMO (full suite, all 18 tests)
REM   Double-click this file. Takes about 6 minutes.
REM ============================================================
cd /d "%~dp0"
title inride - Full Demo

set HEADLESS=false
set SLOW_MO=250
set HIGHLIGHT_MS=700

echo.
echo  ============================================================
echo    INRIDE AUTOMATION - FULL SUITE (headed)
echo    18 tests, 133 validations. Roughly 6 minutes.
echo  ============================================================
echo.

.\.venv\Scripts\python.exe -m pytest

echo.
start "" "%~dp0reports\assertion_report.html"
echo.
pause
