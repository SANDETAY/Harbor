@echo off
title Harbor dual preview
cd /d "%~dp0"
echo.
echo  Starting Harbor dual preview...
echo  (Do not double-click dual-preview.html — this launcher starts the server.)
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start-server.ps1"
if errorlevel 1 (
  echo.
  echo  Server failed. Is Python installed? Try: py --version
  pause
)
