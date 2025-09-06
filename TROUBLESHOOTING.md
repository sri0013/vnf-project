# VNF Performance Testing System - Troubleshooting Guide

## 🚨 **Common Issues and Solutions**

### **Issue 1: Docker Not Running**

**Symptoms**: Error when building VNF images or starting orchestration

**Root Cause**: Docker Desktop is not started

**Solutions**:
```bash
# Start Docker Desktop (Windows/Mac)
# Or: sudo systemctl start docker (Linux)

# Check Docker status
docker ps

# Build VNF images
python VNF_PERFORMANCE_TESTS.py build
```

### **Issue 2: Import Errors**

**Symptoms**: Python can't import orchestration components

**Root Cause**: Missing dependencies or wrong Python version

**Solutions**:
```bash
# Install dependencies
pip install -r requirements.txt

# Check Python version (3.8+ required)
python --version

# Run performance tests
python VNF_PERFORMANCE_TESTS.py testall
```

### **Issue 3: Port Already in Use**

**Symptoms**: Error starting monitoring services

**Root Cause**: Another instance is running or port is occupied

**Solutions**:
```bash
# Check what's using the ports
netstat -tulpn | grep :9090
netstat -tulpn | grep :8080
netstat -tulpn | grep :3000
netstat -tulpn | grep :9091

# Kill processes using the ports
sudo kill -9 <PID>

# Or restart Docker services
docker compose down
docker compose up -d
```

### **Issue 4: Test Failures**

**Symptoms**: Performance tests fail or return errors

**Root Cause**: VNF images not built or orchestration not started

**Solutions**:
```bash
# Build VNF images first
python VNF_PERFORMANCE_TESTS.py build

# Start orchestration system
python VNF_PERFORMANCE_TESTS.py orchestrate

# Run tests
python VNF_PERFORMANCE_TESTS.py testall
```

### **Issue 5: Missing Dependencies**

**Symptoms**: ImportError for specific packages

**Root Cause**: Dependencies not installed

**Solutions**:
```bash
# Install all dependencies
pip install -r requirements.txt

# Install specific packages
pip install prometheus-client docker pandas numpy statsmodels flask psutil

# Check installed packages
pip list
```

## 🔧 **Step-by-Step Troubleshooting**

### **Step 1: Quick Diagnosis**

```bash
# Check Python version
python --version

# Check Docker status
docker ps

# Check current directory
pwd
ls -la
```

### **Step 2: Build VNF Images**

```bash
# Build all VNF images
python VNF_PERFORMANCE_TESTS.py build

# Check if images were created
docker images | grep my-
```

### **Step 3: Start Orchestration**

```bash
# Start orchestration system
python VNF_PERFORMANCE_TESTS.py orchestrate

# Check if services are running
docker compose ps
```

### **Step 4: Run Performance Tests**

```bash
# Run all tests
python VNF_PERFORMANCE_TESTS.py testall

# Or run individual tests
python VNF_PERFORMANCE_TESTS.py test1
python VNF_PERFORMANCE_TESTS.py test2
python VNF_PERFORMANCE_TESTS.py test3
```

## 🧪 **Testing Commands**

### **Build VNF Images**
```bash
# Build all VNF images
python VNF_PERFORMANCE_TESTS.py build
```

### **Start Orchestration**
```bash
# Start orchestration system
python VNF_PERFORMANCE_TESTS.py orchestrate
```

### **Run Performance Tests**
```bash
# Run all tests
python VNF_PERFORMANCE_TESTS.py testall

# Run individual test cases
python VNF_PERFORMANCE_TESTS.py test1    # End-to-end latency
python VNF_PERFORMANCE_TESTS.py test2    # Tail latency percentiles
python VNF_PERFORMANCE_TESTS.py test3    # Throughput at latency SLA
```

### **Check System Status**
```bash
# Check Docker containers
docker compose ps

# Check VNF images
docker images | grep my-

# Check system health
curl http://localhost:8080/health
```

## 🚀 **Universal Solutions**

### **Solution 1: Complete System Setup**

```bash
# Build VNF images
python VNF_PERFORMANCE_TESTS.py build

# Start orchestration
python VNF_PERFORMANCE_TESTS.py orchestrate

# Run all tests
python VNF_PERFORMANCE_TESTS.py testall
```

**What it does**:
- ✅ Builds 4 core VNF Docker images (Firewall, Spam Filter, Content Filter, TLS/Encryption)
- ✅ Starts integrated orchestration system
- ✅ Runs all 3 critical test cases
- ✅ Provides comprehensive results

### **Solution 2: Individual Test Cases**

```bash
# Test Case 1: End-to-end latency
python VNF_PERFORMANCE_TESTS.py test1

# Test Case 2: Tail latency percentiles
python VNF_PERFORMANCE_TESTS.py test2

# Test Case 3: Throughput at latency SLA
python VNF_PERFORMANCE_TESTS.py test3
```

### **Solution 3: Live Monitoring**

```bash
# Access live dashboards
# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090
# SDN Controller: http://localhost:8080
# VNF Orchestrator: http://localhost:9091
```

## 🔍 **Debugging Commands**

### **Check System Status**
```bash
# Check Docker containers
docker compose ps

# Check VNF images
docker images | grep my-

# Check system health
curl http://localhost:8080/health
curl http://localhost:9090/api/v1/targets
```

### **Check Test Results**
```bash
# Run individual test cases
python VNF_PERFORMANCE_TESTS.py test1
python VNF_PERFORMANCE_TESTS.py test2
python VNF_PERFORMANCE_TESTS.py test3

# Check test output for errors
```

### **Check Dependencies**
```bash
# Check Python version
python --version

# Check installed packages
pip list | grep -E "(prometheus|docker|numpy|pandas|flask|psutil)"

# Install missing dependencies
pip install -r requirements.txt
```

## 📋 **Troubleshooting Checklist**

- [ ] Is Docker Desktop running?
- [ ] Are all dependencies installed (`pip install -r requirements.txt`)?
- [ ] Are you using Python 3.8+?
- [ ] Have you built VNF images first (`python VNF_PERFORMANCE_TESTS.py build`)?
- [ ] Have you started orchestration (`python VNF_PERFORMANCE_TESTS.py orchestrate`)?
- [ ] Are the required ports (3000, 8080, 9090, 9091) available?
- [ ] Are you running tests from the project root directory?

## 🆘 **Getting Help**

If you still encounter issues:

1. **Build VNF images**: `python VNF_PERFORMANCE_TESTS.py build`
2. **Start orchestration**: `python VNF_PERFORMANCE_TESTS.py orchestrate`
3. **Run tests**: `python VNF_PERFORMANCE_TESTS.py testall`
4. **Check Docker status**: `docker ps`
5. **Verify Python version**: `python --version`
6. **Check dependencies**: `pip list | grep prometheus`
7. **Review this guide**: Ensure you've tried all solutions

## 🎯 **Quick Fix Summary**

| **Problem** | **Quick Fix** |
|-------------|---------------|
| Docker not running | Start Docker Desktop |
| Import errors | `pip install -r requirements.txt` |
| Port conflicts | Kill processes or restart Docker |
| Test failures | Build images and start orchestration first |
| Missing deps | `pip install -r requirements.txt` |

---

**Remember**: Always build VNF images first, then start orchestration, then run tests! 🚀
