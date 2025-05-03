@echo off
title CLEM
echo Starting CLEM Application...
echo Installing required packages...
cd /d %~dp0

REM Install only the required Node.js packages directly
call npm install python-shell@5.0.0 electron-store@8.1.0 node-hide-console-window@2.2.0 --no-save --force

REM Fix Python environments if needed
echo Checking Python environments...
if not exist "env\Scripts\python.exe" (
    echo Main Python environment not found. Running setup...
    call installer.bat
) else (
    echo Main Python environment found.
)

echo Launching CLEM...
start "" npx electron . --enable-logging=false
exit
