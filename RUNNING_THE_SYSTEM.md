# Running the VNF Orchestration System

## 🚀 Quick Start

### Option 1: Run from Project Root (Recommended)

```bash
# Navigate to the project root directory
cd /path/to/vnf-project

# Run the startup script
python start_orchestration.py
```

### Option 2: Run as Python Module

```bash
# Navigate to the project root directory
cd /path/to/vnf-project

# Run the integrated system as a module
python -m orchestration.integrated_system
```

### Option 3: Test Individual Components

```bash
# Navigate to the project root directory
cd /path/to/vnf-project

# Run the test suite
python test_orchestration.py
```

## 🔧 Why This Approach?

The **relative import error** occurs because:

1. **Python Package Structure**: The `orchestration/` directory is a Python package
2. **Relative Imports**: Files use `from .metrics_registry import ...` syntax
3. **Script vs Module**: Running `python orchestration/vnf_orchestrator.py` treats it as a script, not a module
4. **Import Resolution**: Python can't resolve relative imports when running as a script

## 📁 Project Structure

```
vnf-project/
├── orchestration/                 # Python package
│   ├── __init__.py               # Package initialization
│   ├── vnf_orchestrator.py      # VNF orchestration logic
│   ├── sdn_controller.py        # SDN controller
│   ├── metrics_registry.py      # Centralized metrics
│   └── ...                      # Other components
├── start_orchestration.py        # Main startup script
├── test_orchestration.py         # Test suite
└── requirements.txt              # Dependencies
```

## 🧪 Testing the System

### 1. Test Metrics Registry

```bash
cd vnf-project
python test_orchestration.py
```

This will:
- ✅ Test metrics creation without collisions
- ✅ Verify Prometheus server startup
- ✅ Test VNF orchestrator initialization
- ✅ Test SDN controller
- ✅ Test async operations

### 2. Manual Component Testing

```bash
cd vnf-project

# Test metrics registry only
python -c "
from orchestration.metrics_registry import start_metrics_server, get_vnf_orchestrator_metrics
print('✅ Metrics registry imported successfully')
"

# Test VNF orchestrator only
python -c "
from orchestration.vnf_orchestrator import VNFOrchestrator
print('✅ VNF orchestrator imported successfully')
"
```

## 🚨 Common Errors and Solutions

### Error 1: ImportError: attempted relative import with no known parent package

**Cause**: Running a file directly instead of as a module

**Solution**: 
```bash
# ❌ Wrong - runs as script
python orchestration/vnf_orchestrator.py

# ✅ Correct - runs as module
python -m orchestration.vnf_orchestrator
# OR
python start_orchestration.py
```

### Error 2: ModuleNotFoundError: No module named 'orchestration'

**Cause**: Not in the correct directory

**Solution**:
```bash
# ❌ Wrong directory
cd /some/other/path
python start_orchestration.py

# ✅ Correct directory
cd /path/to/vnf-project
python start_orchestration.py
```

### Error 3: Port Already in Use

**Cause**: Another instance is running

**Solution**:
```bash
# Check what's using the port
netstat -tulpn | grep :9090
netstat -tulpn | grep :8080

# Kill the process or use different ports
```

## 🔍 Debugging Import Issues

### 1. Check Python Path

```python
import sys
print("Python path:")
for path in sys.path:
    print(f"  {path}")
```

### 2. Check Current Directory

```python
import os
print(f"Current working directory: {os.getcwd()}")
print(f"Script location: {os.path.dirname(os.path.abspath(__file__))}")
```

### 3. Verify Package Structure

```bash
# Check if __init__.py exists
ls -la orchestration/__init__.py

# Check Python package recognition
python -c "import orchestration; print('Package imported successfully')"
```

## 🎯 Best Practices

### 1. Always Run from Project Root

```bash
cd vnf-project
python start_orchestration.py
```

### 2. Use Absolute Imports in Scripts

```python
# ✅ Good - absolute import
from orchestration.metrics_registry import start_metrics_server

# ❌ Avoid - relative import in scripts
from .metrics_registry import start_metrics_server
```

### 3. Test Before Running

```bash
# Quick import test
python -c "from orchestration.vnf_orchestrator import VNFOrchestrator; print('OK')"

# Full test suite
python test_orchestration.py
```

## 📊 System Endpoints

Once running successfully:

- **Prometheus Metrics**: http://localhost:9090/metrics
- **SDN Controller**: http://localhost:8080
- **VNF Health Checks**: http://localhost:8080/health

## 🛠️ Development Workflow

### 1. Make Changes

```bash
# Edit files in orchestration/ directory
vim orchestration/vnf_orchestrator.py
```

### 2. Test Changes

```bash
# Run tests to verify
python test_orchestration.py
```

### 3. Run System

```bash
# Start the complete system
python start_orchestration.py
```

### 4. Monitor

```bash
# Check metrics
curl http://localhost:9090/metrics

# Check logs
tail -f orchestration.log
```

## 🔧 Troubleshooting Checklist

- [ ] Are you in the `vnf-project` root directory?
- [ ] Does `orchestration/__init__.py` exist?
- [ ] Are all dependencies installed (`pip install -r requirements.txt`)?
- [ ] Are the ports (9090, 8080) available?
- [ ] Are you using Python 3.8+?
- [ ] Have you run the test suite first?

## 📞 Getting Help

If you still encounter issues:

1. **Run the test suite**: `python test_orchestration.py`
2. **Check the logs**: Look for specific error messages
3. **Verify Python version**: `python --version`
4. **Check dependencies**: `pip list | grep prometheus`
5. **Review this guide**: Ensure you're following the correct steps

## 🎉 Success Indicators

When everything is working correctly, you should see:

```
🚀 VNF Service Function Chain Orchestration System
============================================================
🔧 Starting intelligent orchestration with DRL+ARIMA...
✅ All orchestration components imported successfully
✅ VNF Orchestrator initialized
✅ SDN Controller initialized
✅ SFC Orchestrator initialized
✅ DRL Agent initialized
✅ ARIMA Forecaster initialized
🎉 All components initialized successfully!
📊 Metrics available at: http://localhost:9090/metrics
🌐 SDN Controller at: http://localhost:8080
```

The system is now running and ready for VNF orchestration! 🚀
