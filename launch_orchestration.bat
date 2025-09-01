@echo off
REM Windows Batch File for VNF Orchestration System
REM This file can be run from anywhere to launch the system

echo 🚀 VNF Orchestration System Launcher
echo ================================================

REM Find Python executable
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python not found in PATH
    echo Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)

echo ✅ Python found
echo 🧪 Testing system...

REM Test the system
python test_anywhere.py
if errorlevel 1 (
    echo ❌ System test failed
    pause
    exit /b 1
)

echo.
echo 🚀 Launching VNF Orchestration System...
echo ================================================

REM Launch the system
python launch_orchestration.py

echo.
echo 🎉 System execution completed
pause
