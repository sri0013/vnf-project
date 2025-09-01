# VNF Orchestration System - Troubleshooting Guide

## 🚨 **Common Issues and Solutions**

### **Issue 1: ImportError: attempted relative import with no known parent package**

**Symptoms**: Error when running files directly from orchestration directory

**Root Cause**: Running Python files as scripts instead of modules

**Solutions**:
```bash
# ❌ Wrong - runs as script
python orchestration/vnf_orchestrator.py

# ✅ Correct - use universal launcher (works from anywhere)
python launch_orchestration.py

# ✅ Correct - run as module from project root
cd vnf-project
python -m orchestration.integrated_system
```

### **Issue 2: ModuleNotFoundError: No module named 'orchestration'**

**Symptoms**: Python can't find the orchestration package

**Root Cause**: Not in the correct directory or missing __init__.py

**Solutions**:
```bash
# 1. Use universal launcher (recommended)
python launch_orchestration.py

# 2. Navigate to project root manually
cd /path/to/vnf-project
python -m orchestration.integrated_system

# 3. Check if __init__.py exists
ls -la orchestration/__init__.py
```

### **Issue 3: Port Already in Use**

**Symptoms**: Error starting Prometheus server or SDN controller

**Root Cause**: Another instance is running or port is occupied

**Solutions**:
```bash
# Check what's using the ports
netstat -tulpn | grep :9090
netstat -tulpn | grep :8080

# Kill processes using the ports
sudo kill -9 <PID>

# Or use different ports in configuration
```

### **Issue 4: Python Version Issues**

**Symptoms**: Syntax errors or import failures

**Root Cause**: Using Python version below 3.8

**Solutions**:
```bash
# Check Python version
python --version

# Install Python 3.8+ if needed
# Ubuntu/Debian:
sudo apt update && sudo apt install python3.8

# macOS:
brew install python@3.8

# Windows: Download from python.org
```

### **Issue 5: Missing Dependencies**

**Symptoms**: ImportError for specific packages

**Root Cause**: Dependencies not installed

**Solutions**:
```bash
# Install all dependencies
pip install -r requirements.txt

# Install specific packages
pip install prometheus-client docker pandas numpy statsmodels

# Check installed packages
pip list
```

## 🔧 **Step-by-Step Troubleshooting**

### **Step 1: Quick Diagnosis**

```bash
# Test from anywhere
python test_anywhere.py

# Check Python version
python --version

# Check current directory
pwd
ls -la
```

### **Step 2: Verify Project Structure**

```bash
# Should show vnf-project directory structure
ls -la

# Should show orchestration package
ls -la orchestration/

# Should show __init__.py
ls -la orchestration/__init__.py
```

### **Step 3: Test Imports**

```bash
# Test basic import
python -c "import orchestration; print('✅ Package found')"

# Test specific component
python -c "from orchestration.vnf_orchestrator import VNFOrchestrator; print('✅ Component imported')"
```

### **Step 4: Run System**

```bash
# Use universal launcher (recommended)
python launch_orchestration.py

# Or run as module
python -m orchestration.integrated_system
```

## 🧪 **Testing Commands**

### **Test from Anywhere**
```bash
# Works from any directory
python test_anywhere.py
```

### **Test from Project Root**
```bash
# Navigate to project root
cd vnf-project

# Run test suite
python test_orchestration.py

# Test individual components
python -c "from orchestration.vnf_orchestrator import VNFOrchestrator; print('OK')"
```

### **Test Metrics Registry**
```bash
# Test metrics creation
python -c "
from orchestration.metrics_registry import start_metrics_server, get_vnf_orchestrator_metrics
print('✅ Metrics registry works')
"
```

## 🚀 **Universal Solutions**

### **Solution 1: Universal Launcher (Always Works)**

```bash
# This works from ANY directory
python launch_orchestration.py
```

**What it does**:
- ✅ Automatically finds the project root
- ✅ Creates missing __init__.py files
- ✅ Tests all imports
- ✅ Launches the system correctly

### **Solution 2: Manual Module Execution**

```bash
# Navigate to project root
cd /path/to/vnf-project

# Run as module
python -m orchestration.integrated_system
```

### **Solution 3: Use Platform-Specific Scripts**

**Windows**:
```cmd
launch_orchestration.bat
```

**Linux/macOS**:
```bash
./launch_orchestration.sh
```

## 🔍 **Debugging Commands**

### **Check Python Path**
```python
import sys
print("Python path:")
for path in sys.path:
    print(f"  {path}")
```

### **Check Current Directory**
```python
import os
print(f"Current working directory: {os.getcwd()}")
print(f"Script location: {os.path.dirname(os.path.abspath(__file__))}")
```

### **Check Package Recognition**
```bash
# Should work from project root
python -c "import orchestration; print('Package imported successfully')"
```

## 📋 **Troubleshooting Checklist**

- [ ] Are you using Python 3.8+?
- [ ] Are all dependencies installed (`pip install -r requirements.txt`)?
- [ ] Does `orchestration/__init__.py` exist?
- [ ] Are you in the correct directory?
- [ ] Have you tried the universal launcher?
- [ ] Are the required ports (9090, 8080) available?
- [ ] Have you run the test suite first?

## 🆘 **Getting Help**

If you still encounter issues:

1. **Run the universal test**: `python test_anywhere.py`
2. **Check the error messages**: Look for specific error details
3. **Verify your environment**: Python version, dependencies, ports
4. **Use the universal launcher**: `python launch_orchestration.py`
5. **Check this guide**: Ensure you've tried all solutions

## 🎯 **Quick Fix Summary**

| **Problem** | **Quick Fix** |
|-------------|---------------|
| Import errors | `python launch_orchestration.py` |
| Port conflicts | Kill processes or use different ports |
| Python version | Install Python 3.8+ |
| Missing deps | `pip install -r requirements.txt` |
| Wrong directory | Use universal launcher |

---

**Remember**: The universal launcher (`python launch_orchestration.py`) solves most issues automatically! 🚀
