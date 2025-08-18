# VNF Service Function Chain Orchestration Module

## Overview

The orchestration module provides intelligent scaling and health management for VNFs in the Service Function Chain (SFC) using:

- **Threshold-based rules** for quick reaction to traffic changes
- **ARIMA forecasting** for proactive (predictive) scaling
- **Rolling update logic** to maintain uninterrupted service
- **SDN flow management** for zero-downtime scaling

This ensures the SFC adapts to traffic/load changes with minimal resource waste and zero downtime.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Prometheus    │    │ VNF Orchestrator│    │  SDN Controller │
│   (Monitoring)  │◄──►│  (ARIMA + Rules)│◄──►│  (Flow Mgmt)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Grafana     │    │   VNF Instances │    │   Load Balancer │
│  (Visualization)│    │  (Auto Scaling) │    │  (Round Robin)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Components

### 1. VNF Orchestrator (`vnf_orchestrator.py`)
- **ARIMA Forecasting**: Predicts future resource usage using time-series analysis
- **Threshold-based Scaling**: Reacts to current metrics (CPU, memory, latency)
- **Rolling Updates**: Ensures zero downtime during scaling operations
- **Prometheus Integration**: Exports metrics and collects VNF performance data

### 2. SDN Controller (`sdn_controller.py`)
- **Flow Rule Management**: Updates network flows during scaling
- **Load Balancing**: Distributes traffic across VNF instances
- **Health Monitoring**: Continuously checks VNF instance health
- **REST API**: Provides endpoints for orchestration integration

### 3. Prometheus Configuration
- **Metrics Collection**: Gathers VNF performance metrics every 30s
- **Alerting Rules**: Triggers alerts for high resource usage
- **Data Retention**: Stores historical data for ARIMA analysis

## Workflow

### 1. Monitoring (Prometheus)
- Collects per-VNF metrics (CPU, memory, network latency) every 30-60s
- Exposes metrics on HTTP endpoints (`:9090`)
- Stores time-series data for forecasting

### 2. Forecasting (ARIMA Prediction)
- Orchestrator receives time-series metrics from Prometheus
- For each relevant metric:
  - Extracts last N data points (5-10min window)
  - Runs ARIMA model to forecast next data point(s)
  - Helps anticipate imminent traffic spikes or drops

### 3. Rule-Based Decisions
- **Scale Out**: If live or forecasted metric exceeds upper threshold
- **Scale In**: If live or forecasted metric below lower threshold
- **Rolling Update**: Always start healthy new instance before removing old one

### 4. SDN/Flow Update for Zero Downtime
- Update flow rules so new traffic traverses newly added VNFs
- Drain connections from VNFs being removed only after new ones are validated

## Configuration

### Scaling Thresholds
```yaml
scaling_thresholds:
  cpu_upper: 80      # Scale out when CPU > 80%
  cpu_lower: 30      # Scale in when CPU < 30%
  memory_upper: 85   # Scale out when memory > 85%
  memory_lower: 40   # Scale in when memory < 40%
  latency_upper: 1000  # Scale out when latency > 1000ms
  latency_lower: 200   # Scale in when latency < 200ms
```

### ARIMA Forecasting
```yaml
forecasting:
  window_size: 20        # Number of data points for ARIMA model
  forecast_steps: 3      # Number of steps to forecast ahead
  confidence_threshold: 0.7  # Minimum confidence for decisions
```

### Rolling Updates
```yaml
rolling_update:
  health_check_timeout: 30  # Seconds to wait for health check
  drain_timeout: 60         # Seconds to drain connections
  grace_period: 10          # Grace period before termination
```

## Deployment

### Quick Start with Docker Compose
```bash
# Build and start the complete orchestration stack
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f vnf-orchestrator
```

Note:
- The compose service vnf-orchestrator mounts the Docker socket: /var/run/docker.sock:/var/run/docker.sock
- It is configured to run as root (user: root) to avoid permission errors when accessing the Docker daemon.
- On Windows, ensure Docker Desktop uses the Linux backend (WSL2) so the Unix socket is available to Linux containers.

### Manual Deployment
```bash
# 1. Start Prometheus
docker run -d --name prometheus \
  -p 9090:9090 \
  -v $(pwd)/prometheus_config.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus:latest

# 2. Start SDN Controller
docker build -f Dockerfile.sdn -t sdn-controller .
docker run -d --name sdn-controller -p 8080:8080 sdn-controller

# 3. Start VNF Orchestrator
# Build and tag the orchestrator image
docker build -f Dockerfile.orchestrator -t vnf-orchestrator:latest .
# Run it
docker run -d --name vnf-orchestrator \
  -p 9091:9090 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --user root \
  vnf-orchestrator:latest
```

## Monitoring and Visualization

### Prometheus Metrics
- **VNF Instances**: `vnf_instances_total`
- **CPU Usage**: `vnf_cpu_usage`
- **Memory Usage**: `vnf_memory_usage`
- **Processing Latency**: `vnf_processing_latency`
- **Scaling Actions**: `scaling_actions_total`
- **Forecast Accuracy**: `forecast_accuracy`

### Grafana Dashboards
Access Grafana at `http://localhost:3000` (admin/admin) to view:
- VNF performance metrics
- Scaling history
- Forecast accuracy
- Resource utilization trends

### API Endpoints

#### SDN Controller (`:8080`)
- `GET /health` - Health check
- `GET /flows` - List all flow rules
- `POST /flows` - Add flow rule
- `DELETE /flows/{flow_id}` - Remove flow rule
- `GET /vnf/{vnf_type}/instances` - List VNF instances
- `GET /load-balance/{vnf_type}` - Get next instance for load balancing

#### VNF Orchestrator (`:9091`)
- `GET /metrics` - Prometheus metrics
- `GET /health` - Health check

## Scaling Examples

### Automatic Scale Out
```python
# When CPU > 80% or forecasted CPU > 80%
if current_cpu > 80 or forecasted_cpu > 80:
    orchestrator.scale_out('firewall')
```

### Automatic Scale In
```python
# When all metrics below lower thresholds
if (cpu < 30 and memory < 40 and latency < 200):
    orchestrator.scale_in('firewall')
```

### Rolling Update Process
```python
# 1. Create new instance
new_instance = create_vnf_instance('firewall')

# 2. Health check
if health_check(new_instance):
    # 3. Update SDN flows
    update_flows('add', new_instance)
    
    # 4. Add to load balancer
    add_to_load_balancer(new_instance)
    
    # 5. Drain old instance
    drain_connections(old_instance)
    
    # 6. Remove old instance
    remove_instance(old_instance)
```

## Troubleshooting

### Common Issues

1. **ARIMA Forecasting Errors**
   - Ensure sufficient historical data (minimum 20 data points)
   - Check for data quality issues
   - Verify time-series data is stationary

2. **Scaling Failures**
   - Check Docker daemon connectivity
   - Verify VNF image availability
   - Monitor health check timeouts

3. **SDN Flow Update Issues**
   - Verify SDN controller connectivity
   - Check network configuration
   - Monitor flow rule conflicts

### Debug Commands
```bash
# Check orchestrator logs
docker logs vnf-orchestrator

# Check SDN controller logs
docker logs sdn-controller

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check VNF metrics
curl http://localhost:9091/metrics

# Check SDN controller health
curl http://localhost:8080/health
```

### Troubleshooting: KeyError 'ContainerConfig' for vnf-orchestrator
If you see KeyError: 'ContainerConfig' during compose up:
1) Clean old containers/images and rebuild orchestrator only
   - docker compose -f orchestration/docker-compose.yml down
   - docker rm -f vnf-orchestrator 2>$null
   - docker rmi -f vnf-orchestrator:latest 2>$null
   - docker images | Select-String orchestrator | ForEach-Object { $_.ToString().Split()[2] } | ForEach-Object { docker rmi -f $_ }
2) Build without cache and start only orchestrator
   - docker compose -f orchestration/docker-compose.yml build --no-cache vnf-orchestrator
   - docker compose -f orchestration/docker-compose.yml up vnf-orchestrator
3) Ensure compose service uses only build: (no image:) while debugging (already configured here).

## Performance Optimization

### ARIMA Model Tuning
- Adjust `window_size` based on traffic patterns
- Optimize ARIMA parameters (p,d,q) for your data
- Use seasonal ARIMA for periodic patterns

### Scaling Sensitivity
- Fine-tune thresholds based on workload characteristics
- Use different thresholds for different VNF types
- Implement hysteresis to prevent rapid scaling oscillations

### Resource Management
- Set appropriate min/max instance limits
- Monitor resource overhead of orchestration components
- Implement resource quotas and limits

## Security Considerations

- **Network Isolation**: Use dedicated Docker networks
- **API Security**: Implement authentication for SDN controller
- **Metrics Security**: Secure Prometheus endpoints
- **Container Security**: Use non-root users and security scanning

## Future Enhancements

- **Machine Learning**: Advanced prediction models
- **Multi-Cloud**: Support for hybrid deployments
- **Policy Engine**: Declarative scaling policies
- **Cost Optimization**: Resource cost-aware scaling
- **Integration**: Kubernetes and other orchestration platforms
