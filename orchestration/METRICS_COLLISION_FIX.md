# Prometheus Metrics Collision Fix

## Problem Description

The original VNF orchestrator was experiencing **Prometheus metrics collision errors** because:

1. **Multiple metric registrations**: Each time `VNFOrchestrator` was instantiated, it created new Prometheus metrics with the same names
2. **Duplicate metric definitions**: The same metric names (`vnf_instances_total`, `vnf_cpu_usage`, etc.) were being registered multiple times
3. **Port conflicts**: Multiple Prometheus servers were trying to start on the same port

## Error Message

```
ValueError: Duplicated timeseries in CollectorRegistry: 
Collector already registered for vnf_instances_total
```

## Solution Implemented

### 1. Centralized Metrics Registry (`metrics_registry.py`)

Created a **singleton pattern** metrics registry that:
- ✅ **Prevents duplicate registrations** by tracking existing metrics
- ✅ **Provides consistent metrics** across all components
- ✅ **Manages single Prometheus server** instance
- ✅ **Thread-safe** for concurrent access

### 2. Key Features

```python
# Singleton pattern ensures only one registry exists
class MetricsRegistry:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MetricsRegistry, cls).__new__(cls)
        return cls._instance

# Safe metric creation - returns existing or creates new
def get_or_create_counter(self, name: str, description: str, labels: list = None):
    if name in self._metrics:
        return self._metrics[name]  # Return existing
    
    counter = Counter(name, description, labels or [], registry=self._registry)
    self._metrics[name] = counter   # Store new
    return counter
```

### 3. Usage in VNF Orchestrator

```python
# Before (caused collisions):
from prometheus_client import Gauge, Counter, Histogram

def _init_prometheus_metrics(self):
    self.metrics = {
        'vnf_instances': Gauge('vnf_instances_total', 'Total VNF instances', ['vnf_type']),
        # ... more metrics
    }

# After (collision-free):
from .metrics_registry import get_vnf_orchestrator_metrics

def __init__(self):
    # Get metrics from centralized registry
    self.metrics = get_vnf_orchestrator_metrics()
```

## Benefits

### ✅ **Prevents Collisions**
- No more `ValueError: Duplicated timeseries` errors
- Metrics can be created multiple times safely
- Single source of truth for all metrics

### ✅ **Performance Improvements**
- **Faster startup**: No duplicate metric creation
- **Lower memory usage**: Single metric instances
- **Better monitoring**: Consistent metric names and labels

### ✅ **Maintainability**
- **Centralized management**: All metrics in one place
- **Easy debugging**: Clear metric definitions
- **Scalable**: Easy to add new metrics

## Testing

### Run the Test Script

```bash
cd orchestration
python test_metrics.py
```

This will:
1. ✅ Test metric creation multiple times
2. ✅ Test concurrent access
3. ✅ Verify no collisions occur
4. ✅ Start metrics server on port 9090

### Manual Verification

```bash
# Check metrics endpoint
curl http://localhost:9090/metrics

# Look for these metrics:
# - vnf_instances_total
# - vnf_cpu_usage
# - vnf_memory_usage
# - scaling_actions_total
```

## Migration Guide

### For Existing VNF Components

1. **Replace direct Prometheus imports**:
   ```python
   # Old
   from prometheus_client import Counter, Gauge, Histogram
   
   # New
   from .metrics_registry import get_vnf_metrics
   ```

2. **Use centralized metrics**:
   ```python
   # Old
   self.emails_scanned = Counter('emails_scanned_total', 'Total emails')
   
   # New
   self.metrics = get_vnf_metrics('antivirus')
   self.emails_scanned = self.metrics['emails_scanned_total']
   ```

3. **Remove individual Prometheus servers**:
   ```python
   # Old
   start_http_server(8080)  # Remove this
   
   # New
   # Metrics server is managed centrally
   ```

### For New Components

1. **Import the registry**:
   ```python
   from .metrics_registry import get_vnf_metrics, start_metrics_server
   ```

2. **Get metrics**:
   ```python
   metrics = get_vnf_metrics('your_vnf_type')
   ```

3. **Use metrics**:
   ```python
   metrics['emails_scanned_total'].labels(result='clean').inc()
   ```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Centralized Metrics Registry             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Singleton     │  │  Metric Cache   │  │ Prometheus  │ │
│  │   Pattern       │  │                 │  │   Server    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    VNF Components                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ VNF         │  │ VNF         │  │ VNF                 │ │
│  │ Orchestrator│  │ Antivirus   │  │ Firewall            │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Troubleshooting

### Common Issues

1. **Import Error**: `ModuleNotFoundError: No module named 'metrics_registry'`
   - **Solution**: Ensure you're in the `orchestration` directory
   - **Fix**: Use relative import: `from .metrics_registry import ...`

2. **Port Already in Use**: `OSError: [Errno 98] Address already in use`
   - **Solution**: The registry handles this automatically
   - **Check**: Another process might be using port 9090

3. **Metrics Not Appearing**: Empty `/metrics` endpoint
   - **Solution**: Ensure metrics are being used (set/inc/observe)
   - **Check**: Look for metric creation in logs

### Debug Mode

Enable debug logging to see metric operations:

```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## Future Enhancements

1. **Metric Validation**: Add schema validation for metric definitions
2. **Dynamic Labels**: Support runtime label addition
3. **Metric Aggregation**: Built-in aggregation functions
4. **Export Formats**: Support for other monitoring systems
5. **Health Checks**: Built-in metric health monitoring

## Conclusion

The centralized metrics registry successfully resolves the Prometheus collision issues by:

- **Eliminating duplicate registrations**
- **Providing a single metrics server**
- **Ensuring thread-safe access**
- **Maintaining backward compatibility**

This solution follows Prometheus best practices and provides a robust foundation for VNF monitoring and orchestration.
