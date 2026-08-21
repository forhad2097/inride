@echo off
REM ============================================================
REM   inride - LOGIN PAGE ONLY (headed)
REM   Double-click this file. A Chromium window opens and the
REM   3 login page tests run, about 2 minutes.
REM ============================================================
cd /d "%~dp0"
title inride - Login Page Tests

set HEADLESS=false
set SLOW_MO=300
set HIGHLIGHT_MS=800

echo.
echo  ============================================================
echo    INRIDE - LOGIN PAGE VALIDATION
echo    3 tests, 87 validations. Roughly 2 minutes.
echo    Each element is highlighted in yellow before it is checked.
echo  ============================================================
echo.

.\.venv\Scripts\python.exe -m pytest tests/ui/test_login_page.py

echo.
echo  ============================================================
echo    Opening the assertion report...
echo  ============================================================
start "" "%~dp0reports\assertion_report.html"
echo.
pause
