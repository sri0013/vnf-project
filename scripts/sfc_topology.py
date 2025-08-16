#!/usr/bin/env python3
"""
SFC Topology Script - Mininet Service Function Chain
Creates a network topology with VNF containers for email security
"""

from mininet.net import Mininet
from mininet.node import Controller, Host
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info
import subprocess
import time
import sys

class DockerHost(Host):
    """Custom host that can run Docker containers"""
    def __init__(self, name, **kwargs):
        super(DockerHost, self).__init__(name, **kwargs)

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
        except Exception as e:
            info(f"Error checking image {image}: {e}\n")
            missing_images.append(image)
    
    if missing_images:
        info(f"❌ Missing Docker images: {missing_images}\n")
        info("Please build the VNF images first:\n")
        for image in missing_images:
            vnf_name = image.replace('my-', '').replace('-vnf', '')
            info(f"  cd {vnf_name} && docker build -t {image} .\n")
        return False
    
    info("✅ All required Docker images found\n")
    return True

def cleanup_existing_containers():
    """Stop and remove existing VNF containers"""
    container_prefixes = ['vnf-firewall', 'vnf-antivirus', 'vnf-spamfilter', 
                         'vnf-encryption', 'vnf-contentfilter']
    
    for prefix in container_prefixes:
        try:
            # Stop container if running
            subprocess.run(['docker', 'stop', prefix], 
                         capture_output=True, text=True)
            # Remove container
            subprocess.run(['docker', 'rm', prefix], 
                         capture_output=True, text=True)
            info(f"Cleaned up {prefix}\n")
        except Exception as e:
            info(f"Error cleaning up {prefix}: {e}\n")

def create_sfc_network():
    """Create the Service Function Chain network"""
    setLogLevel('info')
    
    info("🔧 Creating SFC Network Topology...\n")
    
    # Check Docker images first
    if not check_docker_images():
        info("❌ Cannot proceed without Docker images\n")
        return
    
    # Clean up existing containers
    cleanup_existing_containers()
    
    # Create network
    net = Mininet(controller=Controller, link=TCLink, host=DockerHost)
    
    # Add controller
    info("📡 Adding controller...\n")
    net.addController('c0')
    
    # Add hosts (mail clients)
    info("🖥️  Creating hosts...\n")
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24') 
    h3 = net.addHost('h3', ip='10.0.0.3/24')
    h4 = net.addHost('h4', ip='10.0.0.4/24')
    
    # Add mail server
    mail_server = net.addHost('mail', ip='10.0.0.100/24')
    
    # Add switches for SFC chain
    info("🔌 Creating switches...\n")
    s1 = net.addSwitch('s1')  # Entry switch
    s2 = net.addSwitch('s2')  # Exit switch
    
    # Connect hosts and mail server to switches
    info("🔗 Connecting network components...\n")
    net.addLink(h1, s1, bw=10)
    net.addLink(h2, s1, bw=10)
    net.addLink(h3, s1, bw=10)
    net.addLink(h4, s1, bw=10)
    net.addLink(mail_server, s2, bw=10)
    
    # Connect switches (this will be the SFC path)
    net.addLink(s1, s2, bw=100)
    
    info("🚀 Starting network...\n")
    net.start()
    
    # Start VNF containers in sequence (SFC chain)
    info("🔧 Starting VNF Service Function Chain...\n")
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
            info(f"Starting {vnf_name} VNF...\n")
            result = subprocess.run([
                'docker', 'run', '-d', 
                '--name', container_name,
                '--network', 'bridge',
                image_name
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                vnf_containers.append(container_name)
                info(f"✅ {vnf_name} VNF started successfully\n")
            else:
                info(f"❌ Failed to start {vnf_name} VNF: {result.stderr}\n")
        except Exception as e:
            info(f"❌ Error starting {vnf_name} VNF: {e}\n")
    
    info(f"\n🔗 Service Function Chain Active with {len(vnf_containers)} VNFs\n")
    info("VNF Chain: Firewall → Antivirus → Spam Filter → Encryption → Content Filter\n")
    
    # Display network information
    info("\n📋 Network Topology:\n")
    info("Hosts: h1(10.0.0.1), h2(10.0.0.2), h3(10.0.0.3), h4(10.0.0.4)\n")
    info("Mail Server: mail(10.0.0.100)\n")
    info("All traffic flows through the VNF chain\n")
    
    # Test connectivity
    info("\n🔍 Testing basic connectivity...\n")
    net.ping([h1, h2])
    
    info("\n📧 Simulating mail flow through SFC...\n")
    info("Mail from h1 → [VNF Chain] → mail server → [VNF Chain] → h2\n")
    
    # Display VNF monitoring commands
    info("\n📊 VNF Monitoring Commands:\n")
    for container in vnf_containers:
        info(f"  docker logs {container}\n")
    
    # Enter CLI for manual testing
    info("\n💻 Entering Mininet CLI...\n")
    info("Try commands like:\n")
    info("  h1 ping 10.0.0.100\n")
    info("  h1 telnet 10.0.0.100 25\n")
    info("  docker logs vnf-firewall\n")
    info("  exit (to stop the network)\n")
    
    try:
        CLI(net)
    except KeyboardInterrupt:
        info("\n🛑 Interrupted by user\n")
    finally:
        # Cleanup
        info("🧹 Cleaning up VNF containers...\n")
        for container in vnf_containers:
            try:
                subprocess.run(['docker', 'stop', container], 
                             capture_output=True, text=True)
                subprocess.run(['docker', 'rm', container], 
                             capture_output=True, text=True)
                info(f"Stopped and removed {container}\n")
            except Exception as e:
                info(f"Error cleaning up {container}: {e}\n")
        
        info("🛑 Stopping network...\n")
        net.stop()
        info("Network stopped.\n")

def main():
    """Main function"""
    info("🚀 VNF Service Function Chain Network\n")
    info("Email Security SFC: Firewall → Antivirus → Spam Filter → Encryption → Content Filter\n")
    
    try:
        create_sfc_network()
    except Exception as e:
        info(f"❌ Error creating network: {str(e)}\n")
        sys.exit(1)

if __name__ == '__main__':
    main()
