#!/usr/bin/env python3
"""
Simplified SFC Topology Script - Docker-based Service Function Chain
Creates VNF containers without requiring Mininet
"""

import subprocess
import time
import sys
from datetime import datetime

def log(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[SFC {timestamp}] {message}")

def check_docker_images():
    """Check if required Docker images exist"""
    required_images = [
        'my-firewall-vnf',
        'my-antivirus-vnf', 
        'my-spamfilter-vnf',
        'my-encryption-vnf',
        'my-contentfilter-vnf'
    ]
    
    missing_images = []
    for image in required_images:
        try:
            result = subprocess.run(['docker', 'images', '-q', image], 
                                  capture_output=True, text=True)
            if not result.stdout.strip():
                missing_images.append(image)
            else:
                log(f"✅ {image}")
        except Exception as e:
            log(f"❌ Error checking {image}: {e}")
            missing_images.append(image)
    
    if missing_images:
        log(f"❌ Missing Docker images: {missing_images}")
        log("Please build the VNF images first:")
        for image in missing_images:
            vnf_name = image.replace('my-', '').replace('-vnf', '')
            log(f"  cd {vnf_name} && docker build -t {image} .")
        return False
    
    log("✅ All required Docker images found")
    return True

def cleanup_containers():
    """Stop and remove existing VNF containers"""
    container_names = ['vnf-firewall', 'vnf-antivirus', 'vnf-spamfilter', 
                      'vnf-encryption', 'vnf-contentfilter']
    
    for container in container_names:
        try:
            subprocess.run(['docker', 'stop', container], capture_output=True)
            subprocess.run(['docker', 'rm', container], capture_output=True)
            log(f"Cleaned up {container}")
        except Exception as e:
            log(f"Error cleaning up {container}: {e}")

def create_sfc_network():
    """Create the Service Function Chain using Docker containers"""
    log("🔧 Creating SFC Network with Docker containers...")
    
    # Check Docker images first
    if not check_docker_images():
        log("❌ Cannot proceed without Docker images")
        return
    
    # Clean up existing containers
    cleanup_containers()
    
    # Start VNF containers in sequence (SFC chain)
    log("🔧 Starting VNF Service Function Chain...")
    vnf_containers = []
    
    vnfs = [
        ('firewall', 'my-firewall-vnf', 'vnf-firewall'),
        ('antivirus', 'my-antivirus-vnf', 'vnf-antivirus'), 
        ('spamfilter', 'my-spamfilter-vnf', 'vnf-spamfilter'),
        ('encryption', 'my-encryption-vnf', 'vnf-encryption'),
        ('contentfilter', 'my-contentfilter-vnf', 'vnf-contentfilter')
    ]
    
    for vnf_name, image_name, container_name in vnfs:
        try:
            log(f"Starting {vnf_name} VNF...")
            result = subprocess.run([
                'docker', 'run', '-d', 
                '--name', container_name,
                '--network', 'bridge',
                image_name
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                vnf_containers.append(container_name)
                log(f"✅ {vnf_name} VNF started successfully")
            else:
                log(f"❌ Failed to start {vnf_name} VNF: {result.stderr}")
        except Exception as e:
            log(f"❌ Error starting {vnf_name} VNF: {e}")
    
    log(f"\n🔗 Service Function Chain Active with {len(vnf_containers)} VNFs")
    log("VNF Chain: Firewall → Antivirus → Spam Filter → Encryption → Content Filter")
    
    # Display monitoring commands
    log("\n📊 VNF Monitoring Commands:")
    for container in vnf_containers:
        log(f"  docker logs {container}")
    
    log("\n💻 SFC Network is running...")
    log("Press Ctrl+C to stop the network")
    
    try:
        # Keep the network running
        while True:
            time.sleep(10)
            log("SFC network running... (Ctrl+C to stop)")
    except KeyboardInterrupt:
        log("\n🛑 Stopping SFC network...")
    finally:
        # Cleanup
        log("🧹 Cleaning up VNF containers...")
        for container in vnf_containers:
            try:
                subprocess.run(['docker', 'stop', container], capture_output=True)
                subprocess.run(['docker', 'rm', container], capture_output=True)
                log(f"Stopped and removed {container}")
            except Exception as e:
                log(f"Error cleaning up {container}: {e}")
        
        log("SFC network stopped.")

def main():
    """Main function"""
    log("🚀 Simplified VNF Service Function Chain Network")
    log("Email Security SFC: Firewall → Antivirus → Spam Filter → Encryption → Content Filter")
    
    try:
        create_sfc_network()
    except Exception as e:
        log(f"❌ Error creating network: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
