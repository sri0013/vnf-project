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
import sys

class DockerHost(Host):
    """Custom host that can run Docker containers"""
    def __init__(self, name, **kwargs):
        super(DockerHost, self).__init__(name, **kwargs)

def check_docker_images():
    """Check if required Docker images exist"""
    required_images = [
        'my-firewall-vnf',
        'my-spamfilter-vnf',
        'my-encryption-vnf',
        'my-contentfilter-vnf'
    ]
    missing = []
    for img in required_images:
        result = subprocess.run(['docker','images','-q', img],
                                capture_output=True, text=True)
        if not result.stdout.strip():
            missing.append(img)
    if missing:
        info(f"❌ Missing Docker images: {missing}\n")
        info("Build them with:\n")
        for img in missing:
            name = img.replace('my-','').replace('-vnf','')
            info(f"  cd {name} && docker build -t {img} .\n")
        return False
    info("✅ All required Docker images found\n")
    return True

def cleanup_containers():
    names = ['vnf-firewall','vnf-spamfilter','vnf-encryption','vnf-contentfilter']
    for n in names:
        subprocess.run(['docker','stop',n], capture_output=True)
        subprocess.run(['docker','rm',n], capture_output=True)
        info(f"Cleaned up {n}\n")

def create_sfc_network():
    setLogLevel('info')
    info("🔧 Creating SFC Network Topology...\n")

    if not check_docker_images():
        return

    cleanup_containers()

    net = Mininet(controller=Controller, link=TCLink, host=DockerHost)
    info("📡 Adding controller...\n")
    net.addController('c0')

    info("🖥️  Creating hosts...\n")
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    h3 = net.addHost('h3', ip='10.0.0.3/24')
    h4 = net.addHost('h4', ip='10.0.0.4/24')
    # Removed dedicated mail host for text-only chain demo

    info("🔌 Creating switches...\n")
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')

    info("🔗 Linking hosts and switches...\n")
    for h in (h1,h2,h3,h4):
        net.addLink(h, s1, bw=10)
    # Mail host link removed
    net.addLink(s1, s2, bw=100)

    info("🚀 Starting network...\n")
    net.start()

    info("🔧 Starting VNF containers...\n")
    vnf_containers = []
    vnfs = [
        ('firewall',    'my-firewall-vnf',    'vnf-firewall'),
        ('spamfilter',  'my-spamfilter-vnf',  'vnf-spamfilter'),
        ('encryption',  'my-encryption-vnf',  'vnf-encryption'),
        ('contentfilter','my-contentfilter-vnf','vnf-contentfilter')
    ]
    for name,img,cont in vnfs:
        info(f"Starting {name}...\n")
        mode = 'bridge'
        res = subprocess.run([
            'docker','run','-d','--name',cont,
            '--network',mode,img
        ], capture_output=True, text=True)
        if res.returncode==0:
            vnf_containers.append(cont)
            info(f"✅ {name} started\n")
        else:
            info(f"❌ {name} failed: {res.stderr}\n")

    info("\n🔍 Testing basic connectivity\n")
    net.ping([h1,h2,h3,h4])

    # SMTP debug server removed for text-only chain demo

    info("\n💻 Entering CLI\n")
    CLI(net)

    info("🧹 Cleaning up...\n")
    for c in vnf_containers:
        subprocess.run(['docker','stop',c], capture_output=True)
        subprocess.run(['docker','rm',c], capture_output=True)
        info(f"Removed {c}\n")
    net.stop()
    info("Network stopped\n")

def main():
    info("🚀 Starting SFC Network\n")
    try:
        create_sfc_network()
    except Exception as e:
        info(f"❌ Error: {e}\n")
        sys.exit(1)

if __name__=='__main__':
    main()
