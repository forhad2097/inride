@echo off
REM  Opens the last generated reports. Runs no tests.
cd /d "%~dp0"
start "" "%~dp0reports\assertion_report.html"
start "" "%~dp0reports\report.html"
