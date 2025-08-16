#!/usr/bin/env python3
"""
Startup script for VNF Service Function Chain Orchestration
Launches the complete orchestration stack with monitoring
"""

import subprocess
import time
import sys
import os
from datetime import datetime

def log(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[ORCHESTRATION {timestamp}] {message}")

def check_docker():
    """Check if Docker is running"""
    try:
        result = subprocess.run(['docker', 'info'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def check_docker_compose():
    """Check if Docker Compose is available"""
    try:
        result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def build_orchestration_images():
    """Build orchestration Docker images"""
    log("Building orchestration Docker images...")
    
    # Build SDN Controller
    log("Building SDN Controller image...")
    result = subprocess.run([
        'docker', 'build', '-f', 'Dockerfile.sdn', '-t', 'sdn-controller:latest', '.'
    ])
    if result.returncode != 0:
        log("❌ Failed to build SDN Controller image")
        return False
    
    # Build VNF Orchestrator
    log("Building VNF Orchestrator image...")
    result = subprocess.run([
        'docker', 'build', '-f', 'Dockerfile.orchestrator', '-t', 'vnf-orchestrator:latest', '.'
    ])
    if result.returncode != 0:
        log("❌ Failed to build VNF Orchestrator image")
        return False
    
    log("✅ All orchestration images built successfully")
    return True

def start_orchestration_stack():
    """Start the complete orchestration stack"""
    log("Starting orchestration stack with Docker Compose...")
    
    result = subprocess.run(['docker-compose', 'up', '-d'])
    if result.returncode != 0:
        log("❌ Failed to start orchestration stack")
        return False
    
    log("✅ Orchestration stack started successfully")
    return True

def wait_for_services():
    """Wait for services to be ready"""
    log("Waiting for services to be ready...")
    
    services = [
        ('Prometheus', 'http://localhost:9090/api/v1/targets'),
        ('SDN Controller', 'http://localhost:8080/health'),
        ('VNF Orchestrator', 'http://localhost:9091/metrics'),
        ('Grafana', 'http://localhost:3000/api/health')
    ]
    
    import requests
    
    for service_name, url in services:
        log(f"Checking {service_name}...")
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    log(f"✅ {service_name} is ready")
                    break
            except:
                pass
            
            if attempt == max_attempts - 1:
                log(f"⚠️  {service_name} may not be ready yet")
            else:
                time.sleep(2)

def show_status():
    """Show status of all services"""
    log("Checking service status...")
    
    result = subprocess.run(['docker-compose', 'ps'], capture_output=True, text=True)
    if result.returncode == 0:
        print("\n" + result.stdout)
    
    log("Service URLs:")
    print("  📊 Prometheus: http://localhost:9090")
    print("  🎛️  SDN Controller: http://localhost:8080")
    print("  🤖 VNF Orchestrator: http://localhost:9091")
    print("  📈 Grafana: http://localhost:3000 (admin/admin)")

def show_monitoring_commands():
    """Show useful monitoring commands"""
    log("Useful monitoring commands:")
    print("\n📊 Check VNF metrics:")
    print("  curl http://localhost:9091/metrics")
    
    print("\n🎛️  Check SDN flows:")
    print("  curl http://localhost:8080/flows")
    
    print("\n🤖 Check VNF instances:")
    print("  curl http://localhost:8080/vnf/firewall/instances")
    
    print("\n📈 View logs:")
    print("  docker-compose logs -f vnf-orchestrator")
    print("  docker-compose logs -f sdn-controller")
    
    print("\n🔄 Check scaling actions:")
    print("  curl http://localhost:9091/metrics | grep scaling_actions")

def stop_orchestration_stack():
    """Stop the orchestration stack"""
    log("Stopping orchestration stack...")
    
    result = subprocess.run(['docker-compose', 'down'])
    if result.returncode == 0:
        log("✅ Orchestration stack stopped")
    else:
        log("❌ Failed to stop orchestration stack")

def main():
    """Main function"""
    log("🚀 VNF Service Function Chain Orchestration Startup")
    
    # Check prerequisites
    if not check_docker():
        log("❌ Docker is not running or not installed")
        sys.exit(1)
    
    if not check_docker_compose():
        log("❌ Docker Compose is not installed")
        sys.exit(1)
    
    log("✅ Prerequisites check passed")
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'stop':
            stop_orchestration_stack()
            return
        elif command == 'status':
            show_status()
            return
        elif command == 'monitor':
            show_monitoring_commands()
            return
        elif command == 'build':
            build_orchestration_images()
            return
        else:
            log(f"❌ Unknown command: {command}")
            log("Available commands: start, stop, status, monitor, build")
            sys.exit(1)
    
    # Build images
    if not build_orchestration_images():
        sys.exit(1)
    
    # Start stack
    if not start_orchestration_stack():
        sys.exit(1)
    
    # Wait for services
    wait_for_services()
    
    # Show status
    show_status()
    
    # Show monitoring commands
    show_monitoring_commands()
    
    log("🎉 Orchestration stack is ready!")
    log("Press Ctrl+C to stop the stack")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log("Shutting down...")
        stop_orchestration_stack()

if __name__ == "__main__":
    main()
