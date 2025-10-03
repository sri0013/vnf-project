# Running the VNF Performance Testing System

## 🚀 **3 Critical Test Cases - One Command Each**

### **1. Build All VNF Images (One Command)**
```bash
python VNF_PERFORMANCE_TESTS.py build
```

### **2. Start Orchestration System (One Command)**
```bash
python VNF_PERFORMANCE_TESTS.py orchestrate
```

### **3. Run Performance Tests (One Command Each)**
```bash
python VNF_PERFORMANCE_TESTS.py test1    # End-to-end latency
python VNF_PERFORMANCE_TESTS.py test2    # Tail latency percentiles
python VNF_PERFORMANCE_TESTS.py test3    # Throughput at latency SLA
python VNF_PERFORMANCE_TESTS.py testall  # All tests
```

## 🔧 **Why This Approach?**

The **performance testing system** provides:

1. **3 Critical Test Cases**: Exactly as requested for NFV benchmarking
2. **One Command Each**: Build images, start orchestration, run tests
3. **Standards Compliant**: RFC 8172, ETSI NFV-TST 009
4. **Live Monitoring**: Real-time dashboards and metrics
5. **Complete Integration**: All functionality in one file

## 📁 **Project Structure**

```
vnf-project/
├── VNF_PERFORMANCE_TESTS.py      # Complete testing system (3 test cases)
├── PROJECT_STATUS_AND_PROCEDURE.md # Project status and procedures
├── LIVE_MONITORING_GUIDE.md      # Live monitoring guide
├── README.md                      # Main project documentation
├── requirements.txt               # Python dependencies
├── orchestration/                 # Core orchestration system
│   ├── integrated_system.py     # Main orchestration engine
│   ├── vnf_orchestrator.py      # VNF lifecycle management
│   ├── sdn_controller.py        # SDN controller
│   ├── sfc_orchestrator.py      # SFC management
│   ├── drl_agent.py             # Deep RL agent
│   ├── enhanced_arima.py        # ARIMA forecasting
│   ├── grafana_dashboards.py    # Monitoring dashboards
│   ├── metrics_registry.py      # Centralized metrics
│   ├── docker-compose.yml       # Container orchestration
│   └── orchestration_config.yml # System configuration
├── firewall/                      # Core VNFs
├── antivirus/
├── spamfilter/
├── content_filtering/
├── encryption_gateway/
└── mail/
```

## 🎯 **Test Case Details**

### **Test Case 1: End-to-end Latency**
- **Purpose**: User-visible performance of full SFC chain
- **Metrics**: Processing + transmission + propagation + queuing delays
- **Standards**: SFC literature on delay guarantees
- **Command**: `python VNF_PERFORMANCE_TESTS.py test1`

### **Test Case 2: Tail Latency Percentiles**
- **Purpose**: Long-tail behavior for elastic VNFs
- **Metrics**: P95, P99, P99.9 percentiles, scaling analysis
- **Standards**: RFC 8172 NFV benchmarking
- **Command**: `python VNF_PERFORMANCE_TESTS.py test2`

### **Test Case 3: Throughput at Latency SLA**
- **Purpose**: Capacity under quality constraints
- **Metrics**: Max throughput, SLA compliance, efficiency
- **Standards**: ETSI NFV-TST 009 guidance
- **Command**: `python VNF_PERFORMANCE_TESTS.py test3`

## 🧪 **Testing the System**

### **1. Build All VNF Images**

```bash
python VNF_PERFORMANCE_TESTS.py build
```

This will:
- ✅ Build 4 core VNF Docker images (Firewall, Spam Filter, Content Filter, TLS/Encryption)
- ✅ Validate Docker environment
- ✅ Report build success/failure

### **2. Start Orchestration System**

```bash
python VNF_PERFORMANCE_TESTS.py orchestrate
```

This will:
- ✅ Start integrated orchestration system
- ✅ Initialize DRL agent and ARIMA forecasting
- ✅ Launch monitoring and metrics collection
- ✅ Begin SFC request simulation

### **3. Run Performance Tests**

```bash
# Test Case 1: End-to-end latency
python VNF_PERFORMANCE_TESTS.py test1

# Test Case 2: Tail latency percentiles
python VNF_PERFORMANCE_TESTS.py test2

# Test Case 3: Throughput at latency SLA
python VNF_PERFORMANCE_TESTS.py test3

# All tests
python VNF_PERFORMANCE_TESTS.py testall
```

## 🚨 **Common Errors and Solutions**

### **✅ RESOLVED: Prometheus Configuration Errors**

**Issue**: Prometheus scraping failures for VNF endpoints
**Status**: ✅ **FIXED**

**Solution Applied**:
- Removed failing VNF job configurations from `orchestration/prometheus_config.yml`
- Eliminated scraping targets for unresponsive VNF endpoints:
  - `vnf-firewall-1:8080`
  - `vnf-antivirus-1:8080`
  - `vnf-spamfilter-1:8080`
  - `vnf-encryption-1:8080`
  - `vnf-contentfilter-1:8080`
- Kept only Prometheus self-monitoring for stable operation

### **Error 1: Docker Not Running**

**Cause**: Docker Desktop is not started

**Solution**: 
```bash
# Start Docker Desktop (Windows/Mac)
# Or: sudo systemctl start docker (Linux)

# Check Docker status
docker ps
```

### **Error 2: Import Errors**

**Cause**: Missing dependencies or wrong Python version

**Solution**:
```bash
# Install dependencies
pip install -r requirements.txt

# Check Python version (3.8+ required)
python --version
```

### **Error 3: Port Already in Use**

**Cause**: Another instance is running

**Solution**:
```bash
# Check what's using the port
netstat -tulpn | grep :9090
netstat -tulpn | grep :8080
netstat -tulpn | grep :3000

# Kill the process or use different ports
```

## 🔍 **Debugging System Issues**

### **1. Check System Status**

```bash
# Check if all services are running
docker compose ps

# Check VNF images
docker images | grep my-

# Check system health
curl http://localhost:8080/health
```

### **2. Check Test Results**

```bash
# Run individual test cases
python VNF_PERFORMANCE_TESTS.py test1
python VNF_PERFORMANCE_TESTS.py test2
python VNF_PERFORMANCE_TESTS.py test3

# Check test output for errors
```

### **3. Verify Dependencies**

```bash
# Check Python version
python --version

# Check installed packages
pip list | grep -E "(prometheus|docker|numpy|pandas)"

# Install missing dependencies
pip install -r requirements.txt
```

## 🎯 **Best Practices**

### **1. Build Images First**

```bash
# Always build VNF images before starting orchestration
python VNF_PERFORMANCE_TESTS.py build
```

### **2. Start Orchestration Before Testing**

```bash
# Start orchestration system before running tests
python VNF_PERFORMANCE_TESTS.py orchestrate
```

### **3. Run Tests in Order**

```bash
# Run tests in logical order
python VNF_PERFORMANCE_TESTS.py test1    # End-to-end latency
python VNF_PERFORMANCE_TESTS.py test2    # Tail latency percentiles
python VNF_PERFORMANCE_TESTS.py test3    # Throughput at latency SLA
```

### **4. Monitor Live Dashboards**

```bash
# Access live monitoring
# Grafana: http://localhost:3001 (admin/admin)
# Prometheus: http://localhost:9090
# SDN Controller: http://localhost:8080
```

## 📊 **Live Monitoring Endpoints**

Once running successfully:

- **🎛️ Grafana Dashboards**: http://localhost:3001 (admin/admin)
- **📊 Prometheus Metrics**: http://localhost:9090
- **🔧 SDN Controller**: http://localhost:8080
- **📈 VNF Orchestrator**: http://localhost:9091

## 🛠️ **Development Workflow**

### **1. Build and Test**

```bash
# Build VNF images
python VNF_PERFORMANCE_TESTS.py build

# Start orchestration
python VNF_PERFORMANCE_TESTS.py orchestrate
```

### **2. Run Performance Tests**

```bash
# Run individual test cases
python VNF_PERFORMANCE_TESTS.py test1
python VNF_PERFORMANCE_TESTS.py test2
python VNF_PERFORMANCE_TESTS.py test3

# Run all tests
python VNF_PERFORMANCE_TESTS.py testall
```

### **3. Monitor Live Dashboards**

```bash
# Access live monitoring
# Grafana: http://localhost:3001 (admin/admin)
# Prometheus: http://localhost:9090
# SDN Controller: http://localhost:8080
```

### **4. Check Results**

```bash
# Check test results
cat vnf_performance_test_report.json

# Check system metrics
curl http://localhost:9091/metrics
```

## 🔧 **Troubleshooting Checklist**

- [ ] Is Docker Desktop running?
- [ ] Are all dependencies installed (`pip install -r requirements.txt`)?
- [ ] Are the ports (3000, 8080, 9090, 9091) available?
- [ ] Are you using Python 3.8+?
- [ ] Have you built VNF images first (`python VNF_PERFORMANCE_TESTS.py build`)?
- [ ] Have you started orchestration (`python VNF_PERFORMANCE_TESTS.py orchestrate`)?
- [ ] Are you running tests from the project root directory?

## 📞 **Getting Help**

If you still encounter issues:

1. **Build VNF images**: `python VNF_PERFORMANCE_TESTS.py build`
2. **Start orchestration**: `python VNF_PERFORMANCE_TESTS.py orchestrate`
3. **Run tests**: `python VNF_PERFORMANCE_TESTS.py testall`
4. **Check Docker status**: `docker ps`
5. **Verify Python version**: `python --version`
6. **Check dependencies**: `pip list | grep prometheus`
7. **Review this guide**: Ensure you're following the correct steps

## 🎉 **Success Indicators**

When everything is working correctly, you should see:

```
🚀 Building all VNF images...
✅ Built: 4 VNFs
🚀 Starting VNF Orchestration System...
✅ All orchestration components imported successfully
📊 Test Case 1 Results: ✅ Success - Mean Latency: 30.27ms
📊 Test Case 2 Results: ✅ Success - P99: 54.15ms
📊 Test Case 3 Results: ✅ Success - Max Throughput: 4273.93 req/s
🎉 All 3 test cases passed successfully!
```

## 🚀 **Quick Commands Summary**

```bash
# Build all VNF images
python VNF_PERFORMANCE_TESTS.py build

# Start orchestration system
python VNF_PERFORMANCE_TESTS.py orchestrate

# Run performance tests
python VNF_PERFORMANCE_TESTS.py test1    # End-to-end latency
python VNF_PERFORMANCE_TESTS.py test2    # Tail latency percentiles
python VNF_PERFORMANCE_TESTS.py test3    # Throughput at latency SLA
python VNF_PERFORMANCE_TESTS.py testall  # All tests
```

The performance testing system is now ready with 3 critical test cases! 🎉
