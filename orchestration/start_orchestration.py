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

def get_compose_cmd():
    """Return the preferred docker compose command as a list, trying v2 first, then v1.
    Example: ['docker', 'compose'] or ['docker-compose']
    """
    # Try docker compose (v2)
    try:
        result = subprocess.run(['docker', 'compose', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            return ['docker', 'compose']
    except FileNotFoundError:
        pass
    # Fallback to docker-compose (v1)
    try:
        result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            return ['docker-compose']
    except FileNotFoundError:
        pass
    return None

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

def start_orchestration_stack(compose_cmd):
    """Start the complete orchestration stack"""
    log("Starting orchestration stack with Docker Compose...")
    
    result = subprocess.run(compose_cmd + ['up', '-d'])
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

def show_status(compose_cmd):
    """Show status of all services"""
    log("Checking service status...")
    
    result = subprocess.run(compose_cmd + ['ps'], capture_output=True, text=True)
    if result.returncode == 0:
        print("\n" + result.stdout)
    
    log("Service URLs:")
    print("  📊 Prometheus: http://localhost:9090")
    print("  🎛️  SDN Controller: http://localhost:8080")
    print("  🤖 VNF Orchestrator: http://localhost:9091")
    print("  📈 Grafana: http://localhost:3000 (admin/admin)")

def show_monitoring_commands(compose_cmd):
    """Show useful monitoring commands"""
    compose_str = ' '.join(compose_cmd)
    log("Useful monitoring commands:")
    print("\n📊 Check VNF metrics:")
    print("  curl http://localhost:9091/metrics")
    
    print("\n🎛️  Check SDN flows:")
    print("  curl http://localhost:8080/flows")
    
    print("\n🤖 Check VNF instances:")
    print("  curl http://localhost:8080/vnf/firewall/instances")
    
    print("\n📈 View logs:")
    print(f"  {compose_str} logs -f vnf-orchestrator")
    print(f"  {compose_str} logs -f sdn-controller")
    
    print("\n🔄 Check scaling actions:")
    print("  curl http://localhost:9091/metrics | grep scaling_actions")

def stop_orchestration_stack(compose_cmd):
    """Stop the orchestration stack"""
    log("Stopping orchestration stack...")
    
    result = subprocess.run(compose_cmd + ['down'])
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
    
    compose_cmd = get_compose_cmd()
    if not compose_cmd:
        log("❌ Docker Compose (v2 or v1) is not installed")
        sys.exit(1)
    
    log("✅ Prerequisites check passed")
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'stop':
            stop_orchestration_stack(compose_cmd)
            return
        elif command == 'status':
            show_status(compose_cmd)
            return
        elif command == 'monitor':
            show_monitoring_commands(compose_cmd)
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
    if not start_orchestration_stack(compose_cmd):
        sys.exit(1)
    
    # Wait for services
    wait_for_services()
    
    # Show status
    show_status(compose_cmd)
    
    # Show monitoring commands
    show_monitoring_commands(compose_cmd)
    
    log("🎉 Orchestration stack is ready!")
    log("Press Ctrl+C to stop the stack")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log("Shutting down...")
        stop_orchestration_stack(compose_cmd)

if __name__ == "__main__":
    main()
