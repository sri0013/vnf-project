# Running the VNF Orchestration System

## 🚀 **CORRECT WAY TO RUN (Recommended)**

### **Option 1: Run as Python Module (Production)**

```bash
# Navigate to the project root directory
cd /path/to/vnf-project

# Run the integrated system as a module
python -m orchestration.integrated_system
```

### **Option 2: Use the Runner Script**

```bash
# Navigate to the project root directory
cd /path/to/vnf-project

# Use the runner script (which calls the module)
python run_orchestration.py
```

### **Option 3: Test Individual Components**

```bash
# Navigate to the project root directory
cd /path/to/vnf-project

# Run the test suite
python test_orchestration.py
```

## 🔧 **Why This Approach?**

The **relative import error** occurs because:

1. **Python Package Structure**: The `orchestration/` directory is a Python package
2. **Relative Imports**: Files use `from .metrics_registry import ...` syntax (correct for packages)
3. **Script vs Module**: Running `python orchestration/vnf_orchestrator.py` treats it as a script, not a module
4. **Import Resolution**: Python can't resolve relative imports when running as a script

## 📁 **Project Structure**

```
vnf-project/
├── orchestration/                 # Python package
│   ├── __init__.py               # Package initialization
│   ├── vnf_orchestrator.py      # VNF orchestration logic (uses relative imports)
│   ├── sdn_controller.py        # SDN controller (uses relative imports)
│   ├── metrics_registry.py      # Centralized metrics (uses relative imports)
│   └── ...                      # Other components
├── run_orchestration.py          # Runner script (calls module)
├── start_orchestration.py        # Alternative startup (absolute imports)
├── test_orchestration.py         # Test suite (absolute imports)
└── requirements.txt              # Dependencies
```

## 🎯 **Import Strategy**

### **Inside the Package (orchestration/ directory)**
- ✅ **Use relative imports**: `from .metrics_registry import ...`
- ✅ **Correct for package-internal imports**
- ✅ **Maintains package structure**

### **Outside the Package (project root)**
- ✅ **Use absolute imports**: `from orchestration.metrics_registry import ...`
- ✅ **Correct when importing from outside the package**
- ✅ **Works with module execution**

## 🧪 **Testing the System**

### **1. Test Metrics Registry**

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

### **2. Manual Component Testing**

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

## 🚨 **Common Errors and Solutions**

### **Error 1: ImportError: attempted relative import with no known parent package**

**Cause**: Running a file directly instead of as a module

**Solution**: 
```bash
# ❌ Wrong - runs as script
python orchestration/vnf_orchestrator.py

# ✅ Correct - runs as module
python -m orchestration.integrated_system
```

### **Error 2: ModuleNotFoundError: No module named 'orchestration'**

**Cause**: Not in the correct directory

**Solution**:
```bash
# ❌ Wrong directory
cd /some/other/path
python -m orchestration.integrated_system

# ✅ Correct directory
cd /path/to/vnf-project
python -m orchestration.integrated_system
```

### **Error 3: Port Already in Use**

**Cause**: Another instance is running

**Solution**:
```bash
# Check what's using the port
netstat -tulpn | grep :9090
netstat -tulpn | grep :8080

# Kill the process or use different ports
```

## 🔍 **Debugging Import Issues**

### **1. Check Python Path**

```python
import sys
print("Python path:")
for path in sys.path:
    print(f"  {path}")
```

### **2. Check Current Directory**

```python
import os
print(f"Current working directory: {os.getcwd()}")
print(f"Script location: {os.path.dirname(os.path.abspath(__file__))}")
```

### **3. Verify Package Structure**

```bash
# Check if __init__.py exists
ls -la orchestration/__init__.py

# Check Python package recognition
python -c "import orchestration; print('Package imported successfully')"
```

## 🎯 **Best Practices**

### **1. Always Run from Project Root**

```bash
cd vnf-project
python -m orchestration.integrated_system
```

### **2. Use Relative Imports Inside Package**

```python
# ✅ Good - relative import (inside orchestration/ directory)
from .metrics_registry import start_metrics_server

# ❌ Avoid - absolute import (inside package)
from orchestration.metrics_registry import start_metrics_server
```

### **3. Use Absolute Imports Outside Package**

```python
# ✅ Good - absolute import (from project root)
from orchestration.metrics_registry import start_metrics_server

# ❌ Avoid - relative import (from outside package)
from .metrics_registry import start_metrics_server
```

### **4. Test Before Running**

```bash
# Quick import test
python -c "from orchestration.vnf_orchestrator import VNFOrchestrator; print('OK')"

# Full test suite
python test_orchestration.py
```

## 📊 **System Endpoints**

Once running successfully:

- **Prometheus Metrics**: http://localhost:9090/metrics
- **SDN Controller**: http://localhost:8080
- **VNF Health Checks**: http://localhost:8080/health

## 🛠️ **Development Workflow**

### **1. Make Changes**

```bash
# Edit files in orchestration/ directory
vim orchestration/vnf_orchestrator.py
```

### **2. Test Changes**

```bash
# Run tests to verify
python test_orchestration.py
```

### **3. Run System**

```bash
# Start the complete system (recommended)
python -m orchestration.integrated_system

# OR use the runner script
python run_orchestration.py
```

### **4. Monitor**

```bash
# Check metrics
curl http://localhost:9090/metrics

# Check logs
tail -f orchestration.log
```

## 🔧 **Troubleshooting Checklist**

- [ ] Are you in the `vnf-project` root directory?
- [ ] Does `orchestration/__init__.py` exist?
- [ ] Are all dependencies installed (`pip install -r requirements.txt`)?
- [ ] Are the ports (9090, 8080) available?
- [ ] Are you using Python 3.8+?
- [ ] Have you run the test suite first?
- [ ] Are you using `python -m orchestration.integrated_system`?

## 📞 **Getting Help**

If you still encounter issues:

1. **Run the test suite**: `python test_orchestration.py`
2. **Check the logs**: Look for specific error messages
3. **Verify Python version**: `python --version`
4. **Check dependencies**: `pip list | grep prometheus`
5. **Review this guide**: Ensure you're following the correct steps
6. **Use module execution**: `python -m orchestration.integrated_system`

## 🎉 **Success Indicators**

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

## 🚀 **Quick Commands Summary**

```bash
# Navigate to project root
cd vnf-project

# Test the system
python test_orchestration.py

# Run the system (recommended)
python -m orchestration.integrated_system

# OR use runner script
python run_orchestration.py
```

The system is now running and ready for VNF orchestration! 🎉
