#!/usr/bin/env python3
"""
VNF System Startup Script
Integrates with existing VNF_PERFORMANCE_TESTS.py system
"""
import subprocess
import time
import sys
import requests
import os

def start_metrics_exporter() -> bool:
    """Start the VNF metrics exporter"""
    print("🚀 Starting VNF Metrics Exporter...")
    try:
        subprocess.Popen([sys.executable, 'vnf_metrics_exporter.py'])
        time.sleep(3)  # Give it time to start

        # Check if it's running
        try:
            response = requests.get('http://localhost:9091/health', timeout=5)
            if response.status_code == 200:
                print("✅ VNF Metrics Exporter is running on port 9091")
                return True
        except requests.exceptions.RequestException:
            pass

        print("❌ Failed to start VNF Metrics Exporter")
        return False
    except Exception as e:  # noqa: BLE001 - broad for startup script UX
        print(f"❌ Error starting metrics exporter: {e}")
        return False

def start_prometheus() -> bool:
    """Start Prometheus with fixed configuration"""
    print("🚀 Starting Prometheus...")
    try:
        if os.path.exists('prometheus_fixed.yml'):
            cmd = ['prometheus', '--config.file=prometheus_fixed.yml',
                  '--storage.tsdb.path=./prometheus_data',
                  '--web.console.libraries=/etc/prometheus/console_libraries',
                  '--web.console.templates=/etc/prometheus/consoles',
                  '--storage.tsdb.retention.time=200h',
                  '--web.enable-lifecycle']
            subprocess.Popen(cmd)
            time.sleep(5)

            # Check if Prometheus is running
            try:
                response = requests.get('http://localhost:9090/-/healthy', timeout=10)
                if response.status_code == 200:
                    print("✅ Prometheus is running on port 9090")
                    return True
            except requests.exceptions.RequestException:
                pass

        print("❌ Failed to start Prometheus (make sure it's installed)")
        print("💡 You can also use Docker: docker run -p 9090:9090 -v %cd%/prometheus_fixed.yml:/etc/prometheus/prometheus.yml prom/prometheus")
        return False
    except Exception as e:  # noqa: BLE001
        print(f"❌ Error starting Prometheus: {e}")
        return False

def check_grafana() -> bool:
    """Check if Grafana is running on port 3001"""
    try:
        response = requests.get('http://localhost:3001/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ Grafana is running on port 3001")
            return True
    except requests.exceptions.RequestException:
        pass

    print("❌ Grafana not detected on port 3001")
    print("💡 Start Grafana: docker run -p 3001:3000 grafana/grafana")
    return False

def wait_for_services() -> bool:
    """Wait for all services to be ready"""
    print("⏳ Waiting for services to be ready...")
    max_wait = 30
    start_time = time.time()

    while time.time() - start_time < max_wait:
        try:
            # Check metrics exporter
            metrics_response = requests.get('http://localhost:9091/metrics', timeout=2)
            if metrics_response.status_code == 200:
                print("✅ All services are ready!")
                return True
        except requests.exceptions.RequestException:
            pass

        time.sleep(2)
        print(".", end="", flush=True)

    print("\n⏰ Timeout waiting for services")
    return False

def main() -> None:
    """Main startup function"""
    print("🎯 VNF System Integration Startup")
    print("=" * 50)

    # Step 1: Start metrics exporter
    if not start_metrics_exporter():
        print("❌ Cannot continue without metrics exporter")
        sys.exit(1)

    # Step 2: Check/start Prometheus
    start_prometheus()

    # Step 3: Check Grafana
    check_grafana()

    # Step 4: Wait for everything to be ready
    if wait_for_services():
        print("\n🎉 VNF Monitoring System is ready!")
        print("\n📊 Access Points:")
        print("   • VNF Metrics: http://localhost:9091/metrics")
        print("   • Prometheus: http://localhost:9090")
        print("   • Grafana: http://localhost:3001 (admin/admin)")
        print("\n🚀 Now you can run your VNF_PERFORMANCE_TESTS.py commands:")
        print("   • python VNF_PERFORMANCE_TESTS.py orchestrate")
        print("   • python VNF_PERFORMANCE_TESTS.py testall")
    else:
        print("\n❌ System not fully ready, but you can still try running tests")

if __name__ == '__main__':
    main()


