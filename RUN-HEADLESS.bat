@echo off
REM  Full suite with no visible browser - for a quick check before the demo.
cd /d "%~dp0"
title inride - Headless Run
.\.venv\Scripts\python.exe -m pytest
echo.
start "" "%~dp0reports\assertion_report.html"
pause
