#!/usr/bin/env python3
"""
Centralized Prometheus Metrics Registry
Prevents metric collisions and provides consistent metrics across all VNF components
"""

import logging
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, start_http_server
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class MetricsRegistry:
    """Centralized metrics registry to prevent duplicate metric registration"""
    
    _instance = None
    _initialized = False
    _registry = None
    _metrics = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MetricsRegistry, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._registry = CollectorRegistry()
            self._metrics = {}
            self._initialized = True
            logger.info("Metrics Registry initialized")
    
    def get_or_create_counter(self, name: str, description: str, labels: list = None) -> Counter:
        """Get existing counter or create new one"""
        if name in self._metrics:
            return self._metrics[name]
        
        counter = Counter(name, description, labels or [], registry=self._registry)
        self._metrics[name] = counter
        logger.debug(f"Created counter metric: {name}")
        return counter
    
    def get_or_create_gauge(self, name: str, description: str, labels: list = None) -> Gauge:
        """Get existing gauge or create new one"""
        if name in self._metrics:
            return self._metrics[name]
        
        gauge = Gauge(name, description, labels or [], registry=self._registry)
        self._metrics[name] = gauge
        logger.debug(f"Created gauge metric: {name}")
        return gauge
    
    def get_or_create_histogram(self, name: str, description: str, labels: list = None) -> Histogram:
        """Get existing histogram or create new one"""
        if name in self._metrics:
            return self._metrics[name]
        
        histogram = Histogram(name, description, labels or [], registry=self._registry)
        self._metrics[name] = histogram
        logger.debug(f"Created histogram metric: {name}")
        return histogram
    
    def get_metric(self, name: str):
        """Get existing metric by name"""
        return self._metrics.get(name)
    
    def get_registry(self) -> CollectorRegistry:
        """Get the underlying Prometheus registry"""
        return self._registry
    
    def start_server(self, port: int = 9090, addr: str = '0.0.0.0') -> bool:
        """Start Prometheus metrics server"""
        try:
            start_http_server(port, addr, registry=self._registry)
            logger.info(f"Prometheus metrics server started on {addr}:{port}")
            return True
        except OSError as e:
            if "Address already in use" in str(e):
                logger.info(f"Prometheus metrics server already running on {addr}:{port}")
                return True
            else:
                logger.error(f"Failed to start Prometheus server: {e}")
                return False

# Global metrics registry instance
metrics_registry = MetricsRegistry()

# Pre-defined metrics for VNF Orchestrator
def get_vnf_orchestrator_metrics():
    """Get all VNF Orchestrator metrics"""
    return {
        'vnf_instances': metrics_registry.get_or_create_gauge(
            'vnf_instances_total', 
            'Total VNF instances', 
            ['vnf_type']
        ),
        'vnf_cpu_usage': metrics_registry.get_or_create_gauge(
            'vnf_cpu_usage', 
            'CPU usage per VNF instance', 
            ['vnf_type', 'instance_id']
        ),
        'vnf_memory_usage': metrics_registry.get_or_create_gauge(
            'vnf_memory_usage', 
            'Memory usage per VNF instance', 
            ['vnf_type', 'instance_id']
        ),
        'vnf_processing_latency': metrics_registry.get_or_create_gauge(
            'vnf_processing_latency', 
            'Processing latency per VNF instance', 
            ['vnf_type', 'instance_id']
        ),
        'vnf_packets_processed': metrics_registry.get_or_create_counter(
            'vnf_packets_processed', 
            'Packets processed per VNF instance', 
            ['vnf_type', 'instance_id']
        ),
        'scaling_actions': metrics_registry.get_or_create_counter(
            'scaling_actions_total', 
            'Total scaling actions', 
            ['vnf_type', 'action']
        ),
        'forecast_accuracy': metrics_registry.get_or_create_histogram(
            'forecast_accuracy', 
            'ARIMA forecast accuracy', 
            ['vnf_type', 'metric']
        )
    }

# Pre-defined metrics for VNFs
def get_vnf_metrics(vnf_type: str):
    """Get metrics for a specific VNF type"""
    return {
        'emails_scanned_total': metrics_registry.get_or_create_counter(
            f'{vnf_type}_emails_scanned_total',
            f'Total items scanned by {vnf_type}',
            ['result']
        ),
        'scan_duration_seconds': metrics_registry.get_or_create_histogram(
            f'{vnf_type}_scan_duration_seconds',
            f'Time spent scanning content by {vnf_type}'
        ),
        'processing_latency': metrics_registry.get_or_create_gauge(
            f'{vnf_type}_processing_latency',
            f'Processing latency for {vnf_type}',
            ['instance_id']
        ),
        'packets_processed': metrics_registry.get_or_create_counter(
            f'{vnf_type}_packets_processed',
            f'Packets processed by {vnf_type}',
            ['instance_id']
        )
    }

# Start the centralized metrics server
def start_metrics_server(port: int = 9090) -> bool:
    """Start the centralized Prometheus metrics server"""
    return metrics_registry.start_server(port)
