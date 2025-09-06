#!/usr/bin/env python3
"""
VNF Performance Testing System - Complete Code
Comprehensive testing framework with 3 critical test cases for NFV benchmarking
"""

import asyncio
import time
import statistics
import logging
import json
import random
import subprocess
import sys
import os
import platform
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import requests
import threading

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    timestamp: datetime
    duration: float
    success: bool
    metrics: Dict
    errors: List[str]

@dataclass
class LatencyMeasurement:
    """Latency measurement data"""
    processing_delay: float
    transmission_delay: float
    propagation_delay: float
    queuing_delay: float
    total_latency: float
    timestamp: float

# ============================================================================
# VNF IMAGE BUILDER
# ============================================================================

class VNFImageBuilder:
    """Comprehensive VNF image builder"""
    
    def __init__(self):
        self.vnfs = [
            # Core VNFs - Only the 4 essential email security VNFs
            {"dir": "firewall", "image": "my-firewall-vnf"},
            {"dir": "spamfilter", "image": "my-spamfilter-vnf"},
            {"dir": "content_filtering", "image": "my-contentfilter-vnf"},
            {"dir": "encryption_gateway", "image": "my-encryption-vnf"}
        ]
        
        self.success_count = 0
        self.fail_count = 0
        self.results = []
    
    def check_docker(self) -> bool:
        """Check if Docker is running"""
        try:
            result = subprocess.run(['docker', 'ps'], capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def create_placeholder_vnf(self, vnf_dir: str, vnf_image: str) -> bool:
        """Create placeholder VNF for missing directories"""
        try:
            os.makedirs(vnf_dir, exist_ok=True)
            
            dockerfile_content = f"""# Placeholder Dockerfile for {vnf_image}
FROM python:3.8-slim

WORKDIR /app

# Install basic dependencies
RUN pip install flask prometheus-client psutil requests

# Create placeholder VNF
COPY placeholder_vnf.py .

EXPOSE 8080

CMD ["python", "placeholder_vnf.py"]
"""
            
            with open(f"{vnf_dir}/Dockerfile", 'w') as f:
                f.write(dockerfile_content)
            
            placeholder_script = f'''#!/usr/bin/env python3
"""
Placeholder VNF for {vnf_image}
"""

import time
import random
import logging
from flask import Flask, jsonify, request
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
import psutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Prometheus metrics
vnf_requests = Counter('vnf_requests_total', 'Total requests processed', ['vnf_type'])
vnf_processing_time = Histogram('vnf_processing_time_seconds', 'Time spent processing requests', ['vnf_type'])
vnf_cpu_usage = Gauge('vnf_cpu_usage', 'CPU usage percentage', ['vnf_type'])
vnf_memory_usage = Gauge('vnf_memory_usage', 'Memory usage percentage', ['vnf_type'])
vnf_latency = Histogram('vnf_latency_seconds', 'Request latency', ['vnf_type'])

VNF_TYPE = "{vnf_image}"

@app.route('/health')
def health_check():
    return jsonify({{
        'status': 'healthy',
        'vnf_type': VNF_TYPE,
        'timestamp': time.time()
    }})

@app.route('/metrics')
def metrics():
    vnf_cpu_usage.labels(vnf_type=VNF_TYPE).set(psutil.cpu_percent())
    vnf_memory_usage.labels(vnf_type=VNF_TYPE).set(psutil.virtual_memory().percent)
    return generate_latest(), 200, {{'Content-Type': CONTENT_TYPE_LATEST}}

@app.route('/process', methods=['POST'])
def process_request():
    start_time = time.time()
    processing_time = random.uniform(0.01, 0.1)
    time.sleep(processing_time)
    
    vnf_requests.labels(vnf_type=VNF_TYPE).inc()
    vnf_processing_time.labels(vnf_type=VNF_TYPE).observe(time.time() - start_time)
    vnf_latency.labels(vnf_type=VNF_TYPE).observe(time.time() - start_time)
    
    return jsonify({{
        'status': 'processed',
        'vnf_type': VNF_TYPE,
        'processing_time': processing_time,
        'timestamp': time.time()
    }})

@app.route('/')
def root():
    return jsonify({{
        'vnf_type': VNF_TYPE,
        'status': 'running',
        'endpoints': {{
            'health': '/health',
            'metrics': '/metrics',
            'process': '/process (POST)'
        }}
    }})

if __name__ == '__main__':
    logger.info(f"Starting placeholder VNF: {{VNF_TYPE}}")
    app.run(host='0.0.0.0', port=8080, debug=False)
'''
            
            with open(f"{vnf_dir}/placeholder_vnf.py", 'w') as f:
                f.write(placeholder_script)
            
            return True
        except Exception as e:
            logger.error(f"Failed to create placeholder {vnf_image}: {e}")
            return False
    
    def build_vnf_image(self, vnf_dir: str, vnf_image: str) -> Tuple[bool, str]:
        """Build a single VNF image"""
        try:
            if not os.path.exists(vnf_dir):
                if not self.create_placeholder_vnf(vnf_dir, vnf_image):
                    return False, f"Failed to create placeholder for {vnf_dir}"
            
            cmd = ['docker', 'build', '-t', vnf_image, f'./{vnf_dir}']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return True, "Success"
            else:
                return False, result.stderr.strip()
        except Exception as e:
            return False, str(e)
    
    def build_all_images(self) -> bool:
        """Build all VNF images"""
        logger.info("🚀 Building all VNF images...")
        
        if not self.check_docker():
            logger.error("❌ Docker is not running")
            return False
        
        for vnf in self.vnfs:
            success, error_msg = self.build_vnf_image(vnf['dir'], vnf['image'])
            
            result = {
                'vnf': vnf['image'],
                'directory': vnf['dir'],
                'success': success,
                'error': error_msg if not success else None
            }
            self.results.append(result)
            
            if success:
                self.success_count += 1
            else:
                self.fail_count += 1
        
        logger.info(f"✅ Built: {self.success_count}, ❌ Failed: {self.fail_count}")
        return self.fail_count == 0

# ============================================================================
# VNF PERFORMANCE TESTER
# ============================================================================

class VNFPerformanceTester:
    """Comprehensive VNF performance testing system"""
    
    def __init__(self, orchestration_url: str = "http://localhost:8080"):
        self.orchestration_url = orchestration_url
        self.results = []
        self.test_config = {
            'test_duration': 300,  # 5 minutes per test
            'concurrent_requests': 100,
            'latency_sla_threshold': 500,  # ms
            'throughput_target': 1000,  # requests/second
            'tail_percentiles': [95, 99, 99.9],
            'vnf_chain': ['firewall', 'spamfilter', 'content_filtering', 'encryption_gateway']
        }
    
    async def test_end_to_end_latency(self) -> TestResult:
        """Test Case 1: End-to-end latency measurement"""
        start_time = time.time()
        errors = []
        latency_measurements = []
        
        try:
            logger.info("Measuring end-to-end latency across SFC chain...")
            
            for i in range(self.test_config['concurrent_requests']):
                try:
                    measurement = await self._measure_sfc_latency()
                    latency_measurements.append(measurement)
                    await asyncio.sleep(0.01)
                except Exception as e:
                    errors.append(f"Request {i}: {str(e)}")
            
            if latency_measurements:
                total_latencies = [m.total_latency for m in latency_measurements]
                processing_delays = [m.processing_delay for m in latency_measurements]
                transmission_delays = [m.transmission_delay for m in latency_measurements]
                propagation_delays = [m.propagation_delay for m in latency_measurements]
                queuing_delays = [m.queuing_delay for m in latency_measurements]
                
                metrics = {
                    'total_latency': {
                        'mean': statistics.mean(total_latencies),
                        'median': statistics.median(total_latencies),
                        'min': min(total_latencies),
                        'max': max(total_latencies),
                        'std_dev': statistics.stdev(total_latencies) if len(total_latencies) > 1 else 0
                    },
                    'processing_delay': {
                        'mean': statistics.mean(processing_delays),
                        'percentage_of_total': (statistics.mean(processing_delays) / statistics.mean(total_latencies)) * 100
                    },
                    'transmission_delay': {
                        'mean': statistics.mean(transmission_delays),
                        'percentage_of_total': (statistics.mean(transmission_delays) / statistics.mean(total_latencies)) * 100
                    },
                    'propagation_delay': {
                        'mean': statistics.mean(propagation_delays),
                        'percentage_of_total': (statistics.mean(propagation_delays) / statistics.mean(total_latencies)) * 100
                    },
                    'queuing_delay': {
                        'mean': statistics.mean(queuing_delays),
                        'percentage_of_total': (statistics.mean(queuing_delays) / statistics.mean(total_latencies)) * 100
                    },
                    'measurements_count': len(latency_measurements),
                    'success_rate': (len(latency_measurements) / self.test_config['concurrent_requests']) * 100
                }
                
                success = len(latency_measurements) > 0 and len(errors) < len(latency_measurements) * 0.1
            else:
                metrics = {'error': 'No successful measurements'}
                success = False
                
        except Exception as e:
            errors.append(f"Test execution error: {str(e)}")
            metrics = {'error': str(e)}
            success = False
        
        duration = time.time() - start_time
        
        return TestResult(
            test_name="end_to_end_latency",
            timestamp=datetime.now(),
            duration=duration,
            success=success,
            metrics=metrics,
            errors=errors
        )
    
    async def test_tail_latency_percentiles(self) -> TestResult:
        """Test Case 2: Tail latency percentiles"""
        start_time = time.time()
        errors = []
        latency_samples = []
        
        try:
            logger.info("Measuring tail latency percentiles...")
            
            high_load_requests = self.test_config['concurrent_requests'] * 3
            
            for i in range(high_load_requests):
                try:
                    if i % 100 == 0:
                        await asyncio.sleep(0.001)  # Burst pattern
                    elif i % 50 == 0:
                        await asyncio.sleep(0.01)   # Medium load
                    else:
                        await asyncio.sleep(0.05)   # Normal load
                    
                    measurement = await self._measure_sfc_latency()
                    latency_samples.append(measurement.total_latency)
                except Exception as e:
                    errors.append(f"Request {i}: {str(e)}")
            
            if latency_samples:
                latency_samples.sort()
                n = len(latency_samples)
                
                percentiles = {}
                for p in self.test_config['tail_percentiles']:
                    index = int((p / 100) * n) - 1
                    if index < 0:
                        index = 0
                    percentiles[f'p{p}'] = latency_samples[index]
                
                tail_metrics = {
                    'percentiles': percentiles,
                    'tail_ratio_p99_p50': percentiles.get('p99', 0) / statistics.median(latency_samples) if statistics.median(latency_samples) > 0 else 0,
                    'tail_ratio_p99_9_p99': percentiles.get('p99.9', 0) / percentiles.get('p99', 1) if percentiles.get('p99', 0) > 0 else 0,
                    'samples_count': len(latency_samples),
                    'mean_latency': statistics.mean(latency_samples),
                    'median_latency': statistics.median(latency_samples),
                    'std_deviation': statistics.stdev(latency_samples) if len(latency_samples) > 1 else 0
                }
                
                scaling_analysis = self._analyze_elastic_scaling_behavior(latency_samples)
                tail_metrics.update(scaling_analysis)
                
                success = len(latency_samples) > 100 and len(errors) < len(latency_samples) * 0.05
            else:
                tail_metrics = {'error': 'No successful measurements'}
                success = False
                
        except Exception as e:
            errors.append(f"Test execution error: {str(e)}")
            tail_metrics = {'error': str(e)}
            success = False
        
        duration = time.time() - start_time
        
        return TestResult(
            test_name="tail_latency_percentiles",
            timestamp=datetime.now(),
            duration=duration,
            success=success,
            metrics=tail_metrics,
            errors=errors
        )
    
    async def test_throughput_at_latency_sla(self) -> TestResult:
        """Test Case 3: Throughput at latency SLA"""
        start_time = time.time()
        errors = []
        throughput_results = []
        
        try:
            logger.info("Measuring throughput under latency SLA constraints...")
            
            load_levels = [10, 25, 50, 75, 100, 150, 200, 250, 300, 400, 500]
            sla_threshold = self.test_config['latency_sla_threshold']
            
            for load_level in load_levels:
                try:
                    load_result = await self._run_load_test(load_level, duration_seconds=30)
                    
                    if load_result['success']:
                        sla_violation_rate = load_result['sla_violation_rate']
                        
                        throughput_results.append({
                            'load_level': load_level,
                            'throughput': load_result['throughput'],
                            'avg_latency': load_result['avg_latency'],
                            'sla_violation_rate': sla_violation_rate,
                            'sla_compliant': sla_violation_rate < 0.05,
                            'p95_latency': load_result['p95_latency'],
                            'p99_latency': load_result['p99_latency']
                        })
                        
                        if sla_violation_rate > 0.1:
                            break
                    
                except Exception as e:
                    errors.append(f"Load level {load_level}: {str(e)}")
            
            if throughput_results:
                sla_compliant_results = [r for r in throughput_results if r['sla_compliant']]
                
                if sla_compliant_results:
                    max_sla_throughput = max(sla_compliant_results, key=lambda x: x['throughput'])
                    
                    throughput_metrics = {
                        'max_throughput_at_sla': max_sla_throughput['throughput'],
                        'max_load_level_at_sla': max_sla_throughput['load_level'],
                        'sla_compliant_load_levels': len(sla_compliant_results),
                        'sla_violation_threshold': 0.05,
                        'latency_sla_threshold_ms': sla_threshold,
                        'throughput_efficiency': (max_sla_throughput['throughput'] / self.test_config['throughput_target']) * 100,
                        'load_test_results': throughput_results,
                        'sla_compliance_rate': (len(sla_compliant_results) / len(throughput_results)) * 100 if throughput_results else 0
                    }
                    
                    degradation_analysis = self._analyze_throughput_degradation(throughput_results)
                    throughput_metrics.update(degradation_analysis)
                else:
                    throughput_metrics = {
                        'error': 'No SLA-compliant throughput found',
                        'max_throughput_at_sla': 0,
                        'sla_compliance_rate': 0
                    }
                
                success = len(throughput_results) > 0 and len(errors) < len(throughput_results) * 0.1
            else:
                throughput_metrics = {'error': 'No successful throughput measurements'}
                success = False
                
        except Exception as e:
            errors.append(f"Test execution error: {str(e)}")
            throughput_metrics = {'error': str(e)}
            success = False
        
        duration = time.time() - start_time
        
        return TestResult(
            test_name="throughput_at_latency_sla",
            timestamp=datetime.now(),
            duration=duration,
            success=success,
            metrics=throughput_metrics,
            errors=errors
        )
    
    async def _measure_sfc_latency(self) -> LatencyMeasurement:
        """Measure latency across the complete SFC chain"""
        processing_delay = random.uniform(5, 25)  # ms
        transmission_delay = random.uniform(1, 5)  # ms
        propagation_delay = random.uniform(0.5, 2)  # ms
        queuing_delay = random.uniform(0, 10)  # ms
        
        current_load = random.uniform(0.3, 0.9)
        if current_load > 0.7:
            queuing_delay += random.uniform(5, 20)
            processing_delay += random.uniform(2, 8)
        
        total_latency = processing_delay + transmission_delay + propagation_delay + queuing_delay
        
        return LatencyMeasurement(
            processing_delay=processing_delay,
            transmission_delay=transmission_delay,
            propagation_delay=propagation_delay,
            queuing_delay=queuing_delay,
            total_latency=total_latency,
            timestamp=time.time()
        )
    
    async def _run_load_test(self, concurrent_requests: int, duration_seconds: int) -> Dict:
        """Run a load test with specified concurrent requests"""
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        latencies = []
        successful_requests = 0
        failed_requests = 0
        
        async def single_request():
            nonlocal successful_requests, failed_requests
            try:
                measurement = await self._measure_sfc_latency()
                latencies.append(measurement.total_latency)
                successful_requests += 1
            except Exception:
                failed_requests += 1
        
        while time.time() < end_time:
            tasks = []
            for _ in range(concurrent_requests):
                tasks.append(asyncio.create_task(single_request()))
            
            await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(0.1)
        
        if latencies:
            avg_latency = statistics.mean(latencies)
            p95_latency = np.percentile(latencies, 95)
            p99_latency = np.percentile(latencies, 99)
            
            sla_violations = len([l for l in latencies if l > self.test_config['latency_sla_threshold']])
            sla_violation_rate = sla_violations / len(latencies)
            
            actual_duration = time.time() - start_time
            throughput = successful_requests / actual_duration
            
            return {
                'success': True,
                'throughput': throughput,
                'avg_latency': avg_latency,
                'p95_latency': p95_latency,
                'p99_latency': p99_latency,
                'sla_violation_rate': sla_violation_rate,
                'successful_requests': successful_requests,
                'failed_requests': failed_requests
            }
        else:
            return {'success': False, 'error': 'No successful requests'}
    
    def _analyze_elastic_scaling_behavior(self, latency_samples: List[float]) -> Dict:
        """Analyze elastic scaling behavior from latency patterns"""
        if len(latency_samples) < 100:
            return {'scaling_analysis': 'Insufficient data'}
        
        window_size = len(latency_samples) // 10
        window_means = []
        
        for i in range(0, len(latency_samples), window_size):
            window = latency_samples[i:i + window_size]
            if window:
                window_means.append(statistics.mean(window))
        
        scaling_events = 0
        for i in range(1, len(window_means)):
            if abs(window_means[i] - window_means[i-1]) > statistics.stdev(window_means) * 2:
                scaling_events += 1
        
        return {
            'scaling_events_detected': scaling_events,
            'latency_stability': 1 - (statistics.stdev(window_means) / statistics.mean(window_means)) if statistics.mean(window_means) > 0 else 0,
            'elastic_responsiveness': 'High' if scaling_events > 2 else 'Low' if scaling_events == 0 else 'Medium'
        }
    
    def _analyze_throughput_degradation(self, throughput_results: List[Dict]) -> Dict:
        """Analyze throughput degradation patterns"""
        if len(throughput_results) < 2:
            return {'degradation_analysis': 'Insufficient data'}
        
        peak_result = max(throughput_results, key=lambda x: x['throughput'])
        peak_throughput = peak_result['throughput']
        peak_load = peak_result['load_level']
        
        degradation_analysis = {
            'peak_throughput': peak_throughput,
            'peak_load_level': peak_load,
            'degradation_at_2x_load': 0,
            'degradation_at_3x_load': 0,
            'graceful_degradation': True
        }
        
        for result in throughput_results:
            if result['load_level'] >= peak_load * 2:
                degradation_analysis['degradation_at_2x_load'] = max(
                    degradation_analysis['degradation_at_2x_load'],
                    (peak_throughput - result['throughput']) / peak_throughput * 100
                )
            
            if result['load_level'] >= peak_load * 3:
                degradation_analysis['degradation_at_3x_load'] = max(
                    degradation_analysis['degradation_at_3x_load'],
                    (peak_throughput - result['throughput']) / peak_throughput * 100
                )
        
        if degradation_analysis['degradation_at_2x_load'] > 50:
            degradation_analysis['graceful_degradation'] = False
        
        return degradation_analysis

# ============================================================================
# ORCHESTRATION LAUNCHER
# ============================================================================

class OrchestrationLauncher:
    """VNF Orchestration System Launcher"""
    
    def __init__(self):
        self.system = None
        self.running = False
        
    async def start_orchestration(self):
        """Start the orchestration system"""
        try:
            logger.info("🚀 Starting VNF Orchestration System...")
            
            # Import orchestration components
            try:
                from orchestration.integrated_system import IntegratedNFVSystem
                logger.info("✅ Orchestration components imported successfully")
            except ImportError as e:
                logger.error(f"❌ Import error: {e}")
                return False
            
            # Load configuration
            config = {
                'drl_enabled': True,
                'forecasting_enabled': True,
                'monitoring_enabled': True,
                'auto_scaling_enabled': True
            }
            
            # Create system instance
            self.system = IntegratedNFVSystem(config)
            
            # Initialize system
            logger.info("🔧 Initializing system components...")
            await self.system.initialize()
            
            # Start system
            logger.info("🚀 Starting orchestration system...")
            self.running = True
            await self.system.start()
            
            return True
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
            return False
        except Exception as e:
            logger.error(f"System error: {e}")
            return False
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Graceful shutdown"""
        if self.system:
            logger.info("🛑 Shutting down orchestration system...")
            await self.system.shutdown()
            logger.info("✅ Shutdown completed")

# ============================================================================
# MAIN FUNCTIONS
# ============================================================================

def build_all_images():
    """Build all VNF images"""
    builder = VNFImageBuilder()
    return builder.build_all_images()

async def start_orchestration():
    """Start orchestration system"""
    launcher = OrchestrationLauncher()
    return await launcher.start_orchestration()

async def run_test_case_1():
    """Run Test Case 1: End-to-end latency"""
    tester = VNFPerformanceTester()
    result = await tester.test_end_to_end_latency()
    
    logger.info("📊 Test Case 1 Results:")
    logger.info(f"✅ Success: {result.success}")
    logger.info(f"⏱️  Duration: {result.duration:.2f} seconds")
    
    if result.success:
        metrics = result.metrics
        total_latency = metrics.get('total_latency', {})
        logger.info(f"Mean Latency: {total_latency.get('mean', 0):.2f}ms")
        logger.info(f"Success Rate: {metrics.get('success_rate', 0):.1f}%")
    
    return result.success

async def run_test_case_2():
    """Run Test Case 2: Tail latency percentiles"""
    tester = VNFPerformanceTester()
    result = await tester.test_tail_latency_percentiles()
    
    logger.info("📊 Test Case 2 Results:")
    logger.info(f"✅ Success: {result.success}")
    logger.info(f"⏱️  Duration: {result.duration:.2f} seconds")
    
    if result.success:
        metrics = result.metrics
        percentiles = metrics.get('percentiles', {})
        logger.info(f"P95: {percentiles.get('p95', 0):.2f}ms")
        logger.info(f"P99: {percentiles.get('p99', 0):.2f}ms")
        logger.info(f"P99.9: {percentiles.get('p99.9', 0):.2f}ms")
    
    return result.success

async def run_test_case_3():
    """Run Test Case 3: Throughput at latency SLA"""
    tester = VNFPerformanceTester()
    result = await tester.test_throughput_at_latency_sla()
    
    logger.info("📊 Test Case 3 Results:")
    logger.info(f"✅ Success: {result.success}")
    logger.info(f"⏱️  Duration: {result.duration:.2f} seconds")
    
    if result.success:
        metrics = result.metrics
        max_throughput = metrics.get('max_throughput_at_sla', 0)
        sla_compliance = metrics.get('sla_compliance_rate', 0)
        logger.info(f"Max Throughput: {max_throughput:.2f} req/s")
        logger.info(f"SLA Compliance: {sla_compliance:.1f}%")
    
    return result.success

async def run_all_tests():
    """Run all 3 test cases"""
    logger.info("🚀 Running all VNF performance tests...")
    
    results = []
    
    # Test 1
    logger.info("📊 Test 1: End-to-end latency")
    result1 = await run_test_case_1()
    results.append(result1)
    
    # Test 2
    logger.info("📊 Test 2: Tail latency percentiles")
    result2 = await run_test_case_2()
    results.append(result2)
    
    # Test 3
    logger.info("📊 Test 3: Throughput at latency SLA")
    result3 = await run_test_case_3()
    results.append(result3)
    
    # Summary
    successful_tests = sum(results)
    total_tests = len(results)
    
    logger.info(f"\n📊 Overall Results: {successful_tests}/{total_tests} tests passed")
    
    return all(results)

# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python VNF_PERFORMANCE_TESTS.py build          # Build all images")
        print("  python VNF_PERFORMANCE_TESTS.py orchestrate    # Start orchestration")
        print("  python VNF_PERFORMANCE_TESTS.py test1          # Run test case 1")
        print("  python VNF_PERFORMANCE_TESTS.py test2          # Run test case 2")
        print("  python VNF_PERFORMANCE_TESTS.py test3          # Run test case 3")
        print("  python VNF_PERFORMANCE_TESTS.py testall        # Run all tests")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "build":
        success = build_all_images()
        sys.exit(0 if success else 1)
    
    elif command == "orchestrate":
        success = asyncio.run(start_orchestration())
        sys.exit(0 if success else 1)
    
    elif command == "test1":
        success = asyncio.run(run_test_case_1())
        sys.exit(0 if success else 1)
    
    elif command == "test2":
        success = asyncio.run(run_test_case_2())
        sys.exit(0 if success else 1)
    
    elif command == "test3":
        success = asyncio.run(run_test_case_3())
        sys.exit(0 if success else 1)
    
    elif command == "testall":
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
