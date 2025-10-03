#!/usr/bin/env python3
"""
VNF Metrics Exporter - Works with VNF_PERFORMANCE_TESTS.py
Exports proper Prometheus metrics for Grafana dashboards
"""
import time
import math
import random
import threading
from flask import Flask, Response
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
import psutil  # noqa: F401 - reserved for future system metrics
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Prometheus metrics - matching the dashboard JSON files
vnf_instances_total = Gauge('vnf_instances_total', 'Total VNF instances', ['vnf_type'])
vnf_cpu_usage_seconds_total = Counter('vnf_cpu_usage_seconds_total', 'CPU usage by VNF', ['vnf_type', 'instance'])
vnf_memory_usage_bytes = Gauge('vnf_memory_usage_bytes', 'Memory usage by VNF', ['vnf_type', 'instance'])
vnf_network_throughput_bytes_total = Counter('vnf_network_throughput_bytes_total', 'Network throughput', ['vnf_type', 'direction'])

# SFC Performance metrics
sfc_e2e_latency_seconds = Histogram('sfc_e2e_latency_seconds', 'End-to-end latency', buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0])
sfc_current_latency_seconds = Histogram('sfc_current_latency_seconds', 'Current latency measurements', buckets=[0.01, 0.05, 0.1, 0.5, 1.0])
sfc_throughput_bytes_total = Counter('sfc_throughput_bytes_total', 'SFC throughput', ['chain_id'])
sfc_chain_status = Gauge('sfc_chain_status', 'SFC chain status', ['chain_id'])
sfc_sla_violations_total = Counter('sfc_sla_violations_total', 'SLA violations')

# DRL Agent metrics
drl_training_loss = Gauge('drl_training_loss', 'DRL training loss')
drl_episode_reward = Gauge('drl_episode_reward', 'DRL episode reward')
drl_epsilon_value = Gauge('drl_epsilon_value', 'DRL epsilon value')
drl_resource_efficiency_ratio = Gauge('drl_resource_efficiency_ratio', 'DRL resource efficiency')
drl_sfc_satisfaction_rate = Gauge('drl_sfc_satisfaction_rate', 'DRL SFC satisfaction rate')
drl_action_distribution = Gauge('drl_action_distribution', 'DRL action distribution', ['action'])

# ARIMA metrics
arima_historical_data = Gauge('arima_historical_data', 'ARIMA historical data')
arima_forecast = Gauge('arima_forecast', 'ARIMA forecast')
arima_forecast_upper_ci = Gauge('arima_forecast_upper_ci', 'ARIMA upper confidence interval')
arima_forecast_lower_ci = Gauge('arima_forecast_lower_ci', 'ARIMA lower confidence interval')
arima_mae = Gauge('arima_mae', 'ARIMA Mean Absolute Error')
arima_rmse = Gauge('arima_rmse', 'ARIMA Root Mean Square Error')
arima_mape = Gauge('arima_mape', 'ARIMA Mean Absolute Percentage Error')
arima_r_squared = Gauge('arima_r_squared', 'ARIMA R-squared')
arima_aic = Gauge('arima_aic', 'ARIMA AIC')
arima_bic = Gauge('arima_bic', 'ARIMA BIC')

# Latency improvement metrics
latency_improvement_percentage = Gauge('latency_improvement_percentage', 'Latency improvement percentage')
latency_component_breakdown = Gauge('latency_component_breakdown', 'Latency component breakdown', ['component'])
throughput_at_100ms_sla = Gauge('throughput_at_100ms_sla', 'Throughput at 100ms SLA')

def simulate_vnf_metrics() -> None:
    """Simulate realistic VNF metrics for remote surgery applications"""
    vnf_types = ['firewall', 'encryption', 'spamfilter', 'contentfiltering']

    for vnf_type in vnf_types:
        # Instance counts
        instance_count = random.randint(2, 4)
        vnf_instances_total.labels(vnf_type=vnf_type).set(instance_count)

        # CPU and memory usage per instance
        for i in range(instance_count):
            instance_name = f"{vnf_type}-{i}"
            cpu_usage_seconds = random.uniform(0.1, 0.8)  # seconds to add
            memory_usage = random.uniform(100, 800) * 1024 * 1024  # 100-800 MB

            vnf_cpu_usage_seconds_total.labels(vnf_type=vnf_type, instance=instance_name).inc(cpu_usage_seconds)
            vnf_memory_usage_bytes.labels(vnf_type=vnf_type, instance=instance_name).set(memory_usage)

            # Network throughput
            rx_bytes = random.uniform(1000, 50000)  # 1KB - 50KB/s
            tx_bytes = random.uniform(1000, 45000)  # 1KB - 45KB/s
            vnf_network_throughput_bytes_total.labels(vnf_type=vnf_type, direction='rx').inc(rx_bytes)
            vnf_network_throughput_bytes_total.labels(vnf_type=vnf_type, direction='tx').inc(tx_bytes)

def simulate_sfc_metrics() -> None:
    """Simulate SFC performance metrics for surgical applications"""
    # Critical: Remote surgery requires <100ms latency
    base_latency = random.uniform(0.015, 0.085)  # 15-85ms base latency

    # Add occasional latency spikes (network congestion simulation)
    if random.random() < 0.05:  # 5% chance of spike
        latency = random.uniform(0.1, 0.15)  # 100-150ms spike
        sfc_sla_violations_total.inc()
    else:
        latency = base_latency

    # Record latency measurements
    sfc_e2e_latency_seconds.observe(latency)
    sfc_current_latency_seconds.observe(latency)

    # SFC chain status (simulate 3 active chains)
    for chain_id in ['chain-1', 'chain-2', 'chain-3']:
        status = 1 if random.random() > 0.02 else 0  # 98% uptime
        sfc_chain_status.labels(chain_id=chain_id).set(status)

        # Throughput per chain
        throughput = random.uniform(1000, 5000)  # 1KB - 5KB/s per chain
        sfc_throughput_bytes_total.labels(chain_id=chain_id).inc(throughput)

def simulate_drl_metrics() -> None:
    """Simulate DRL agent metrics for intelligent VNF placement"""
    # Training progress simulation
    episode = time.time() % 1000  # Simulate episode progression
    loss = max(0.1, 2.0 - (episode / 500))  # Decreasing loss over time
    reward = min(100, episode / 10)  # Increasing reward over time
    epsilon = max(0.01, 0.9 - (episode / 1000))  # Epsilon decay

    drl_training_loss.set(loss)
    drl_episode_reward.set(reward)
    drl_epsilon_value.set(epsilon)

    # Efficiency metrics
    efficiency = min(0.95, 0.6 + (episode / 2000))  # Improving efficiency
    satisfaction = min(0.98, 0.7 + (episode / 1500))  # Improving satisfaction

    drl_resource_efficiency_ratio.set(efficiency)
    drl_sfc_satisfaction_rate.set(satisfaction)

    # Action distribution (for surgery: scale_up, scale_down, migrate, maintain)
    actions = ['scale_up', 'scale_down', 'migrate', 'maintain']
    action_weights = [0.2, 0.15, 0.25, 0.4]  # Favor maintain for stability

    for action, weight in zip(actions, action_weights):
        value = weight * random.uniform(0.8, 1.2)  # Add some randomness
        drl_action_distribution.labels(action=action).set(value)

def simulate_arima_metrics() -> None:
    """Simulate ARIMA forecasting metrics for predictive scaling"""
    # Historical data simulation (load pattern)
    historical = 50 + 20 * math.sin(time.time() / 100) + random.uniform(-5, 5)

    # Forecast with confidence intervals
    forecast = historical + random.uniform(-2, 2)
    upper_ci = forecast + random.uniform(5, 10)
    lower_ci = forecast - random.uniform(5, 10)

    arima_historical_data.set(historical)
    arima_forecast.set(forecast)
    arima_forecast_upper_ci.set(upper_ci)
    arima_forecast_lower_ci.set(lower_ci)

    # Model quality metrics
    arima_mae.set(random.uniform(2, 5))  # Mean Absolute Error
    arima_rmse.set(random.uniform(3, 7))  # Root Mean Square Error
    arima_mape.set(random.uniform(5, 15))  # Mean Absolute Percentage Error
    arima_r_squared.set(random.uniform(0.85, 0.98))  # R-squared (good fit)
    arima_aic.set(random.uniform(100, 200))  # AIC
    arima_bic.set(random.uniform(110, 220))  # BIC

def simulate_latency_improvement() -> None:
    """Simulate latency improvement metrics"""
    # Show improvement over time
    baseline_latency_ms = 140  # ms
    current_p95_ms = random.uniform(80, 120)  # Current P95 latency
    improvement = ((baseline_latency_ms - current_p95_ms) / baseline_latency_ms) * 100

    latency_improvement_percentage.set(improvement)

    # Component breakdown
    components = ['processing', 'network', 'queuing', 'serialization']
    component_latencies_ms = [25, 15, 8, 5]  # ms

    for component, latency_ms in zip(components, component_latencies_ms):
        latency_component_breakdown.labels(component=component).set(latency_ms / 1000)  # seconds

    # Throughput at 100ms SLA
    throughput_bytes_per_s = random.uniform(2_000_000, 4_000_000)  # ~2-4 MB/s
    throughput_at_100ms_sla.set(throughput_bytes_per_s)

def update_metrics() -> None:
    """Update all metrics continuously"""
    while True:
        try:
            simulate_vnf_metrics()
            simulate_sfc_metrics()
            simulate_drl_metrics()
            simulate_arima_metrics()
            simulate_latency_improvement()
            time.sleep(5)  # Update every 5 seconds
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
            time.sleep(5)

@app.route('/health')
def health():
    return {'status': 'healthy', 'timestamp': time.time()}

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route('/')
def root():
    return {
        'service': 'VNF Metrics Exporter',
        'status': 'running',
        'endpoints': {
            'health': '/health',
            'metrics': '/metrics'
        }
    }

if __name__ == '__main__':
    # Start metrics update thread
    metrics_thread = threading.Thread(target=update_metrics, daemon=True)
    metrics_thread.start()

    logger.info("Starting VNF Metrics Exporter on port 9091")
    app.run(host='0.0.0.0', port=9091, debug=False)


