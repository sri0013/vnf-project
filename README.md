# VNF Service Function Chain Orchestration System

## 🚀 **Quick Start**

```bash
# Navigate to project root
cd vnf-project

# Test the system first
python test_orchestration.py

# Run the orchestration system (RECOMMENDED)
python -m orchestration.integrated_system
```

## 🔧 **What This System Does**

This is a **Virtual Network Function (VNF) Service Function Chain (SFC) Orchestration System** that provides:

- **Intelligent VNF Scaling** using Deep Reinforcement Learning (DRL)
- **Predictive Scaling** with ARIMA time series forecasting
- **Service Function Chaining** for email security workflows
- **Centralized Metrics** with Prometheus monitoring
- **SDN Controller** for network flow management

## 📁 **Project Structure**

```
vnf-project/
├── orchestration/                 # Main orchestration package
│   ├── __init__.py               # Package initialization
│   ├── vnf_orchestrator.py      # VNF orchestration logic
│   ├── sdn_controller.py        # SDN controller
│   ├── sfc_orchestrator.py      # SFC management
│   ├── drl_agent.py             # Deep RL agent
│   ├── enhanced_arima.py        # ARIMA forecasting
│   ├── metrics_registry.py      # Centralized metrics
│   └── integrated_system.py     # Main system entry point
├── antivirus/                    # Antivirus VNF
├── firewall/                     # Firewall VNF
├── spamfilter/                   # Spam filter VNF
├── content_filtering/            # Content filtering VNF
├── encryption_gateway/           # Encryption VNF
├── run_orchestration.py          # Runner script
├── test_orchestration.py         # Test suite
└── requirements.txt              # Dependencies
```

## 🎯 **Key Features**

- ✅ **DRL + ARIMA Orchestration**: Intelligent scaling decisions
- ✅ **Prometheus Metrics**: Comprehensive monitoring and alerting
- ✅ **Docker Integration**: Containerized VNF deployment
- ✅ **SDN Control**: Software-defined networking management
- ✅ **Service Function Chaining**: Email security workflows
- ✅ **Auto-scaling**: Predictive resource management

## 🧪 **Testing**

```bash
# Run comprehensive tests
python test_orchestration.py

# Test individual components
python -c "from orchestration.vnf_orchestrator import VNFOrchestrator; print('OK')"
```

## 🚨 **Important Notes**

### **Correct Way to Run**
- ✅ **Use module execution**: `python -m orchestration.integrated_system`
- ✅ **Run from project root**: `cd vnf-project`
- ❌ **Don't run files directly**: `python orchestration/vnf_orchestrator.py`

### **Why This Approach?**
- **Package Structure**: `orchestration/` is a Python package
- **Relative Imports**: Internal files use `from .module import ...`
- **Module Execution**: Python resolves imports correctly as a module

## 📊 **System Endpoints**

Once running:
- **Prometheus Metrics**: http://localhost:9090/metrics
- **SDN Controller**: http://localhost:8080
- **VNF Health**: http://localhost:8080/health

## 🔧 **Installation**

```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python test_orchestration.py
```

## 📚 **Documentation**

- **Running the System**: [RUNNING_THE_SYSTEM.md](RUNNING_THE_SYSTEM.md)
- **Metrics Fix**: [orchestration/METRICS_COLLISION_FIX.md](orchestration/METRICS_COLLISION_FIX.md)
- **Project Structure**: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

## 🎉 **Success**

When everything works, you'll see:
```
🚀 VNF Service Function Chain Orchestration System
✅ All orchestration components imported successfully
✅ VNF Orchestrator initialized
✅ SDN Controller initialized
🎉 All components initialized successfully!
```

## 🆘 **Need Help?**

1. **Check this README** for quick start
2. **Read RUNNING_THE_SYSTEM.md** for detailed instructions
3. **Run tests first**: `python test_orchestration.py`
4. **Use module execution**: `python -m orchestration.integrated_system`

---

**Happy VNF Orchestrating! 🚀**
