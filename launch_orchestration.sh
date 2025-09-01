#!/bin/bash
# Linux/macOS Shell Script for VNF Orchestration System
# This script can be run from anywhere to launch the system

echo "🚀 VNF Orchestration System Launcher"
echo "==============================================="

# Find Python executable
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ Error: Python not found in PATH"
        echo "Please install Python 3.8+ and add it to your PATH"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "✅ Python found: $($PYTHON_CMD --version)"
echo "🧪 Testing system..."

# Test the system
$PYTHON_CMD test_anywhere.py
if [ $? -ne 0 ]; then
    echo "❌ System test failed"
    exit 1
fi

echo ""
echo "🚀 Launching VNF Orchestration System..."
echo "==============================================="

# Launch the system
$PYTHON_CMD launch_orchestration.py

echo ""
echo "🎉 System execution completed"
