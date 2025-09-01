#!/usr/bin/env python3
"""
VNF Service Function Chain Orchestrator
Implements intelligent scaling with ARIMA forecasting and rolling updates
"""

import time
import json
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import schedule

import docker
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import requests
import yaml

# Import centralized metrics registry - handle both relative and absolute imports
try:
    # Try relative import first (when run as module)
    from .metrics_registry import get_vnf_orchestrator_metrics, start_metrics_server
except ImportError:
    try:
        # Fallback to absolute import (when run standalone)
        from orchestration.metrics_registry import get_vnf_orchestrator_metrics, start_metrics_server
    except ImportError:
        # Final fallback - direct import (for testing)
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from metrics_registry import get_vnf_orchestrator_metrics, start_metrics_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VNFOrchestrator:
    """Advanced VNF Orchestrator with ARIMA forecasting and rolling updates"""
    
    def __init__(self, config_file: str = "orchestration_config.yml"):
        self.config = self._load_config(config_file)
        self.docker_client = docker.from_env()
        
        # VNF instances tracking
        self.vnf_instances = {
            'firewall': [],
            'antivirus': [],
            'spamfilter': [],
            'encryption': [],
            'contentfilter': []
        }
        
        # Metrics storage for ARIMA forecasting
        self.metrics_history = {
            'firewall': {'cpu': [], 'memory': [], 'latency': []},
            'antivirus': {'cpu': [], 'memory': [], 'latency': []},
            'spamfilter': {'cpu': [], 'memory': [], 'latency': []},
            'encryption': {'cpu': [], 'memory': [], 'latency': []},
            'contentfilter': {'cpu': [], 'memory': [], 'latency': []}
        }
        
        # Scaling thresholds
        self.scaling_thresholds = self.config.get('scaling_thresholds', {
            'cpu_upper': 80,
            'cpu_lower': 30,
            'memory_upper': 85,
            'memory_lower': 40,
            'latency_upper': 1000,
            'latency_lower': 200
        })
        
        # Get metrics from centralized registry
        self.metrics = get_vnf_orchestrator_metrics()
        
        # Start centralized Prometheus metrics server
        start_metrics_server(9090)
        
        logger.info("VNF Orchestrator initialized successfully")
    
    def log(self, message: str):
        """Simple logging method for compatibility"""
        logger.info(message)
    
    async def initialize(self):
        """Initialize the VNF Orchestrator asynchronously"""
        logger.info("VNF Orchestrator initializing...")
        
        try:
            # Initialize Docker client
            self.docker_client = docker.from_env()
            logger.info("Docker client initialized")
            
            # Initialize VNF instances tracking
            for vnf_type in self.vnf_instances:
                self.vnf_instances[vnf_type] = []
            logger.info("VNF instances tracking initialized")
            
            # Initialize metrics history
            for vnf_type in self.metrics_history:
                for metric in self.metrics_history[vnf_type]:
                    self.metrics_history[vnf_type][metric] = []
            logger.info("Metrics history initialized")
            
            # Prometheus metrics are managed by centralized registry
            logger.info("Prometheus metrics initialized")
            
            logger.info("VNF Orchestrator initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during initialization: {e}")
            return False
    
    def _load_config(self, config_file: str) -> dict:
        """Load configuration from YAML file"""
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_file} not found, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> dict:
        """Get default configuration"""
        return {
            'vnf_types': ['firewall', 'antivirus', 'spamfilter', 'encryption', 'contentfilter'],
            'min_instances': 1,
            'max_instances': 5,
            'scaling_thresholds': {
                'cpu_upper': 80,
                'cpu_lower': 30,
                'memory_upper': 85,
                'memory_lower': 40,
                'latency_upper': 1000,
                'latency_lower': 200
            },
            'forecasting': {
                'window_size': 20,  # Number of data points for ARIMA
                'forecast_steps': 3,  # Number of steps to forecast
                'confidence_threshold': 0.7
            },
            'rolling_update': {
                'health_check_timeout': 30,
                'drain_timeout': 60,
                'grace_period': 10
            }
        }
    

    
    def collect_metrics(self, vnf_type: str, instance_id: str) -> Dict:
        """Collect metrics from a VNF instance"""
        try:
            # Get container stats
            container = self.docker_client.containers.get(instance_id)
            stats = container.stats(stream=False)
            
            # Calculate CPU usage
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
            cpu_usage = (cpu_delta / system_delta) * 100 if system_delta > 0 else 0
            
            # Calculate memory usage
            memory_usage = (stats['memory_stats']['usage'] / stats['memory_stats']['limit']) * 100
            
            # Get custom metrics from VNF (if available)
            try:
                response = requests.get(f"http://{instance_id}:8080/metrics", timeout=5)
                if response.status_code == 200:
                    custom_metrics = response.json()
                    latency = custom_metrics.get('processing_latency', 0)
                    packets_processed = custom_metrics.get('packets_processed', 0)
                else:
                    latency = 0
                    packets_processed = 0
            except:
                latency = 0
                packets_processed = 0
            
            metrics = {
                'cpu': cpu_usage,
                'memory': memory_usage,
                'latency': latency,
                'packets_processed': packets_processed,
                'timestamp': datetime.now()
            }
            
            # Update Prometheus metrics
            self.metrics['vnf_cpu_usage'].labels(vnf_type=vnf_type, instance_id=instance_id).set(cpu_usage)
            self.metrics['vnf_memory_usage'].labels(vnf_type=vnf_type, instance_id=instance_id).set(memory_usage)
            self.metrics['vnf_processing_latency'].labels(vnf_type=vnf_type, instance_id=instance_id).set(latency)
            self.metrics['vnf_packets_processed'].labels(vnf_type=vnf_type, instance_id=instance_id).inc(packets_processed)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting metrics from {instance_id}: {e}")
            return None
    
    def forecast_metrics(self, vnf_type: str, metric_name: str) -> Optional[float]:
        """Forecast metrics using ARIMA model"""
        try:
            history = self.metrics_history[vnf_type][metric_name]
            if len(history) < self.config['forecasting']['window_size']:
                return None
            
            # Prepare data for ARIMA
            data = pd.Series(history[-self.config['forecasting']['window_size']:])
            
            # Fit ARIMA model (1,1,1) - can be optimized based on data characteristics
            model = ARIMA(data, order=(1, 1, 1))
            fitted_model = model.fit()
            
            # Forecast next value
            forecast = fitted_model.forecast(steps=1)
            forecasted_value = forecast[0]
            
            # Calculate forecast accuracy (if we have actual values to compare)
            if len(history) > self.config['forecasting']['window_size']:
                actual = history[-1]
                accuracy = 1 - abs(forecasted_value - actual) / actual if actual > 0 else 1
                self.metrics['forecast_accuracy'].labels(vnf_type=vnf_type, metric=metric_name).observe(accuracy)
            
            logger.info(f"Forecasted {metric_name} for {vnf_type}: {forecasted_value:.2f}")
            return forecasted_value
            
        except Exception as e:
            logger.error(f"Error forecasting {metric_name} for {vnf_type}: {e}")
            return None
    
    def should_scale_out(self, vnf_type: str) -> bool:
        """Determine if scaling out is needed based on current and forecasted metrics"""
        current_instances = len(self.vnf_instances[vnf_type])
        if current_instances >= self.config['max_instances']:
            return False
        
        # Check current metrics
        current_metrics = self.get_aggregated_metrics(vnf_type)
        if not current_metrics:
            return False
        
        # Check thresholds
        if (current_metrics['cpu'] > self.scaling_thresholds['cpu_upper'] or
            current_metrics['memory'] > self.scaling_thresholds['memory_upper'] or
            current_metrics['latency'] > self.scaling_thresholds['latency_upper']):
            return True
        
        # Check forecasted metrics
        for metric in ['cpu', 'memory', 'latency']:
            forecasted = self.forecast_metrics(vnf_type, metric)
            if forecasted:
                threshold = self.scaling_thresholds[f'{metric}_upper']
                if forecasted > threshold:
                    logger.info(f"Scaling out {vnf_type} due to forecasted {metric}: {forecasted:.2f} > {threshold}")
                    return True
        
        return False
    
    def should_scale_in(self, vnf_type: str) -> bool:
        """Determine if scaling in is needed"""
        current_instances = len(self.vnf_instances[vnf_type])
        if current_instances <= self.config['min_instances']:
            return False
        
        current_metrics = self.get_aggregated_metrics(vnf_type)
        if not current_metrics:
            return False
        
        # Check if all metrics are below lower thresholds
        if (current_metrics['cpu'] < self.scaling_thresholds['cpu_lower'] and
            current_metrics['memory'] < self.scaling_thresholds['memory_lower'] and
            current_metrics['latency'] < self.scaling_thresholds['latency_lower']):
            return True
        
        return False
    
    def get_aggregated_metrics(self, vnf_type: str) -> Optional[Dict]:
        """Get aggregated metrics for a VNF type"""
        if not self.vnf_instances[vnf_type]:
            return None
        
        all_metrics = []
        for instance_id in self.vnf_instances[vnf_type]:
            metrics = self.collect_metrics(vnf_type, instance_id)
            if metrics:
                all_metrics.append(metrics)
        
        if not all_metrics:
            return None
        
        # Calculate averages
        aggregated = {
            'cpu': np.mean([m['cpu'] for m in all_metrics]),
            'memory': np.mean([m['memory'] for m in all_metrics]),
            'latency': np.mean([m['latency'] for m in all_metrics]),
            'packets_processed': sum([m['packets_processed'] for m in all_metrics])
        }
        
        return aggregated
    
    def scale_out(self, vnf_type: str) -> bool:
        """Scale out by adding a new VNF instance with rolling update"""
        try:
            logger.info(f"Scaling out {vnf_type}")
            
            # Create new instance
            new_instance_id = self._create_vnf_instance(vnf_type)
            if not new_instance_id:
                return False
            
            # Wait for health check
            if not self._wait_for_health_check(new_instance_id):
                logger.error(f"Health check failed for new {vnf_type} instance")
                self._remove_vnf_instance(new_instance_id)
                return False
            
            # Add to instances list
            self.vnf_instances[vnf_type].append(new_instance_id)
            self.metrics['vnf_instances'].labels(vnf_type=vnf_type).set(len(self.vnf_instances[vnf_type]))
            self.metrics['scaling_actions'].labels(vnf_type=vnf_type, action='scale_out').inc()
            
            # Update SDN flows (in a real implementation)
            self._update_sdn_flows(vnf_type, 'add', new_instance_id)
            
            logger.info(f"Successfully scaled out {vnf_type}, new instance: {new_instance_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error scaling out {vnf_type}: {e}")
            return False
    
    def scale_in(self, vnf_type: str) -> bool:
        """Scale in by removing a VNF instance with rolling update"""
        try:
            logger.info(f"Scaling in {vnf_type}")
            
            if not self.vnf_instances[vnf_type]:
                return False
            
            # Select instance to remove (least loaded)
            instance_to_remove = self._select_instance_to_remove(vnf_type)
            if not instance_to_remove:
                return False
            
            # Drain connections (in a real implementation)
            self._drain_connections(instance_to_remove)
            
            # Remove from SDN flows
            self._update_sdn_flows(vnf_type, 'remove', instance_to_remove)
            
            # Remove instance
            self._remove_vnf_instance(instance_to_remove)
            self.vnf_instances[vnf_type].remove(instance_to_remove)
            self.metrics['vnf_instances'].labels(vnf_type=vnf_type).set(len(self.vnf_instances[vnf_type]))
            self.metrics['scaling_actions'].labels(vnf_type=vnf_type, action='scale_in').inc()
            
            logger.info(f"Successfully scaled in {vnf_type}, removed instance: {instance_to_remove}")
            return True
            
        except Exception as e:
            logger.error(f"Error scaling in {vnf_type}: {e}")
            return False
    
    def _create_vnf_instance(self, vnf_type: str) -> Optional[str]:
        """Create a new VNF instance"""
        try:
            image_name = f"my-{vnf_type}-vnf"
            container_name = f"{vnf_type}-{int(time.time())}"
            
            container = self.docker_client.containers.run(
                image_name,
                name=container_name,
                detach=True,
                ports={'8080/tcp': None},  # Expose metrics port
                environment={'VNF_TYPE': vnf_type}
            )
            
            return container.id
            
        except Exception as e:
            logger.error(f"Error creating {vnf_type} instance: {e}")
            return None
    
    def _remove_vnf_instance(self, instance_id: str):
        """Remove a VNF instance"""
        try:
            container = self.docker_client.containers.get(instance_id)
            container.stop(timeout=10)
            container.remove()
        except Exception as e:
            logger.error(f"Error removing instance {instance_id}: {e}")
    
    def _wait_for_health_check(self, instance_id: str) -> bool:
        """Wait for health check to pass"""
        timeout = self.config['rolling_update']['health_check_timeout']
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"http://{instance_id}:8080/health", timeout=5)
                if response.status_code == 200:
                    return True
            except:
                pass
            time.sleep(2)
        
        return False
    
    def _select_instance_to_remove(self, vnf_type: str) -> Optional[str]:
        """Select the least loaded instance to remove"""
        if not self.vnf_instances[vnf_type]:
            return None
        
        # Get metrics for all instances
        instance_metrics = {}
        for instance_id in self.vnf_instances[vnf_type]:
            metrics = self.collect_metrics(vnf_type, instance_id)
            if metrics:
                # Calculate load score (weighted average)
                load_score = (metrics['cpu'] * 0.4 + metrics['memory'] * 0.3 + metrics['latency'] * 0.3)
                instance_metrics[instance_id] = load_score
        
        if not instance_metrics:
            return self.vnf_instances[vnf_type][0]  # Remove first if no metrics
        
        # Return instance with lowest load
        return min(instance_metrics, key=instance_metrics.get)
    
    def _drain_connections(self, instance_id: str):
        """Drain connections from an instance"""
        timeout = self.config['rolling_update']['drain_timeout']
        logger.info(f"Draining connections from {instance_id} for {timeout}s")
        time.sleep(timeout)  # In real implementation, this would actively drain connections
    
    def _update_sdn_flows(self, vnf_type: str, action: str, instance_id: str):
        """Update SDN flows (placeholder for real implementation)"""
        logger.info(f"SDN flow update: {action} {instance_id} for {vnf_type}")
        # In a real implementation, this would update OpenFlow rules or similar
    
    def update_metrics_history(self):
        """Update metrics history for all VNF instances"""
        for vnf_type in self.config['vnf_types']:
            for instance_id in self.vnf_instances[vnf_type]:
                metrics = self.collect_metrics(vnf_type, instance_id)
                if metrics:
                    for metric_name in ['cpu', 'memory', 'latency']:
                        self.metrics_history[vnf_type][metric_name].append(metrics[metric_name])
                    
                    # Keep only recent history
                    max_history = self.config['forecasting']['window_size'] * 2
                    for metric_name in ['cpu', 'memory', 'latency']:
                        if len(self.metrics_history[vnf_type][metric_name]) > max_history:
                            self.metrics_history[vnf_type][metric_name] = self.metrics_history[vnf_type][metric_name][-max_history:]
    
    def orchestration_loop(self):
        """Main orchestration loop"""
        logger.info("Starting orchestration loop")
        
        while True:
            try:
                # Update metrics history
                self.update_metrics_history()
                
                # Check each VNF type for scaling needs
                for vnf_type in self.config['vnf_types']:
                    if self.should_scale_out(vnf_type):
                        self.scale_out(vnf_type)
                    elif self.should_scale_in(vnf_type):
                        self.scale_in(vnf_type)
                
                # Sleep before next iteration
                time.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                logger.info("Orchestration loop interrupted")
                break
            except Exception as e:
                logger.error(f"Error in orchestration loop: {e}")
                time.sleep(30)
    
    def start(self):
        """Start the orchestrator"""
        logger.info("Starting VNF Orchestrator")
        
        # Start orchestration loop in a separate thread
        orchestration_thread = threading.Thread(target=self.orchestration_loop, daemon=True)
        orchestration_thread.start()
        
        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down VNF Orchestrator")
    
    # Additional methods needed by integrated_system.py
    def get_available_resources(self) -> Dict[str, float]:
        """Get available system resources"""
        try:
            import psutil
            cpu_available = 100.0 - psutil.cpu_percent()
            memory = psutil.virtual_memory()
            memory_available = 100.0 - memory.percent
            
            return {
                'cpu_available': cpu_available,
                'memory_available': memory_available,
                'cpu_total': psutil.cpu_count(),
                'memory_total': memory.total / (1024**3),  # GB
                'network_bandwidth': 1000.0  # Mbps (assumed)
            }
        except ImportError:
            # Fallback if psutil not available
            return {
                'cpu_available': 80.0,
                'memory_available': 70.0,
                'cpu_total': 8,
                'memory_total': 16.0,
                'network_bandwidth': 1000.0
            }
    
    def get_vnf_instances(self, vnf_type: str) -> List[str]:
        """Get list of VNF instance IDs for a specific type"""
        return self.vnf_instances.get(vnf_type, [])
    
    def get_all_vnf_instances(self) -> List[str]:
        """Get all VNF instance IDs across all types"""
        all_instances = []
        for instances in self.vnf_instances.values():
            all_instances.extend(instances)
        return all_instances
    
    def get_vnf_load(self, vnf_type: str) -> float:
        """Get current load for a VNF type"""
        instances = self.get_vnf_instances(vnf_type)
        if not instances:
            return 0.0
        
        # Calculate average load across all instances
        total_load = 0.0
        valid_instances = 0
        
        for instance_id in instances:
            metrics = self.collect_metrics(vnf_type, instance_id)
            if metrics:
                # Calculate load as weighted average of CPU and memory
                load = (metrics['cpu'] * 0.6 + metrics['memory'] * 0.4) / 100.0
                total_load += load
                valid_instances += 1
        
        return total_load / valid_instances if valid_instances > 0 else 0.0
    
    def get_active_sfcs(self) -> Dict:
        """Get active SFC allocations"""
        # This is a placeholder - in a real implementation, you'd track SFCs
        return {
            'active_chains': len(self.get_all_vnf_instances()),
            'total_bandwidth': 100.0,  # Mbps
            'average_latency': 50.0    # ms
        }
    
    async def allocate_vnf(self, vnf_type: str) -> bool:
        """Allocate a new VNF instance"""
        try:
            return self.scale_out(vnf_type)
        except Exception as e:
            logger.error(f"Error allocating VNF {vnf_type}: {e}")
            return False
    
    async def remove_vnf(self, vnf_type: str, instance_id: str) -> bool:
        """Remove a VNF instance"""
        try:
            if instance_id in self.vnf_instances.get(vnf_type, []):
                self._remove_vnf_instance(instance_id)
                self.vnf_instances[vnf_type].remove(instance_id)
                self.metrics['vnf_instances'].labels(vnf_type=vnf_type).set(len(self.vnf_instances[vnf_type]))
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing VNF {vnf_type} instance {instance_id}: {e}")
            return False
    
    async def create_sfc(self, sfc_config: Dict) -> bool:
        """Create a new Service Function Chain"""
        try:
            chain_id = sfc_config.get('chain_id')
            vnf_sequence = sfc_config.get('vnf_sequence', [])
            
            logger.info(f"Creating SFC {chain_id} with sequence: {vnf_sequence}")
            
            # Allocate VNFs for the chain
            for vnf_type in vnf_sequence:
                success = await self.allocate_vnf(vnf_type)
                if not success:
                    logger.error(f"Failed to allocate VNF {vnf_type} for SFC {chain_id}")
                    return False
            
            logger.info(f"SFC {chain_id} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating SFC: {e}")
            return False
    
    async def scale_out_async(self, vnf_type: str) -> Optional[str]:
        """Async version of scale out"""
        try:
            success = self.scale_out(vnf_type)
            if success:
                # Return the ID of the newly created instance
                instances = self.get_vnf_instances(vnf_type)
                return instances[-1] if instances else None
            return None
        except Exception as e:
            logger.error(f"Error in async scale out: {e}")
            return None
    
    async def scale_in_async(self, vnf_type: str, instance_id: str) -> bool:
        """Async version of scale in"""
        try:
            return await self.remove_vnf(vnf_type, instance_id)
        except Exception as e:
            logger.error(f"Error in async scale in: {e}")
            return False
    
    async def get_available_instance(self, vnf_type: str) -> Optional[str]:
        """Get an available VNF instance of the specified type"""
        instances = self.get_vnf_instances(vnf_type)
        if instances:
            # Return the first available instance
            return instances[0]
        return None

if __name__ == "__main__":
    orchestrator = VNFOrchestrator()
    orchestrator.start()
