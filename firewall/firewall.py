#!/usr/bin/env python3
"""
Firewall VNF - Network-level security filtering
Performs IP blocking, port control, and traffic logging
"""

import time
import socket
import threading
from datetime import datetime
from prometheus_client import start_http_server, Counter, Gauge, Histogram

class FirewallVNF:
    def __init__(self):
        # Configuration for firewall rules
        self.blocked_ips = [
            '192.168.1.100',  # Example blocked IP
            '10.0.0.50',      # Another blocked IP
            '172.16.0.10'     # Suspicious IP
        ]
        
        # Allowed ports for email and web traffic
        self.allowed_ports = [
            25,   # SMTP
            80,   # HTTP
            443,  # HTTPS
            993,  # IMAP SSL
            995,  # POP3 SSL
            587,  # SMTP submission
            465   # SMTP SSL
        ]
        
        # Statistics tracking
        self.stats = {
            'packets_processed': 0,
            'packets_blocked': 0,
            'packets_allowed': 0
        }

        # Prometheus metrics
        self.packets_total = Counter(
            'firewall_packets_total',
            'Total packets processed by firewall',
            ['action']  # allowed, blocked
        )
        self.packet_processing_seconds = Histogram(
            'firewall_packet_processing_seconds',
            'Time spent inspecting packets'
        )
        self.blocked_ip_count = Gauge(
            'firewall_blocked_ip_count',
            'Number of configured blocked IPs'
        )
        self.blocked_ip_count.set(len(self.blocked_ips))

        # Start Prometheus metrics server on 8080 (scraped at /metrics)
        start_http_server(8080)
        self.log("📈 Prometheus metrics server started on port 8080")
        
    def log(self, message):
        """Log firewall activities with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[FIREWALL {timestamp}] {message}")
        
    def inspect_packet(self, source_ip, dest_ip, dest_port, protocol="TCP"):
        """
        Inspect incoming packet and apply firewall rules
        
        Args:
            source_ip (str): Source IP address
            dest_ip (str): Destination IP address  
            dest_port (int): Destination port
            protocol (str): Protocol (TCP/UDP)
            
        Returns:
            bool: True if packet is allowed, False if blocked
        """
        start = time.time()
        self.stats['packets_processed'] += 1
        
        # Rule 1: Check if source IP is blocked
        if source_ip in self.blocked_ips:
            self.stats['packets_blocked'] += 1
            self.packets_total.labels(action='blocked').inc()
            self.log(f"🚫 BLOCKED: Traffic from blocked IP {source_ip} to {dest_ip}:{dest_port}")
            self.packet_processing_seconds.observe(time.time() - start)
            return False
        
        # Rule 2: Check if destination port is allowed
        if dest_port not in self.allowed_ports:
            self.stats['packets_blocked'] += 1
            self.packets_total.labels(action='blocked').inc()
            self.log(f"🚫 BLOCKED: Port {dest_port} not allowed for {source_ip} -> {dest_ip}")
            self.packet_processing_seconds.observe(time.time() - start)
            return False
        
        # Rule 3: Check for suspicious patterns (example: high port scanning)
        if dest_port > 1024 and dest_port not in [8080, 8443]:  # Custom ports
            self.log(f"⚠️  WARNING: Non-standard port {dest_port} from {source_ip}")
        
        # Packet passed all rules
        self.stats['packets_allowed'] += 1
        self.packets_total.labels(action='allowed').inc()
        self.log(f"✅ ALLOWED: {source_ip} -> {dest_ip}:{dest_port} ({protocol})")
        self.packet_processing_seconds.observe(time.time() - start)
        return True
    
    def get_statistics(self):
        """Return current firewall statistics"""
        return {
            'total_packets': self.stats['packets_processed'],
            'blocked_packets': self.stats['packets_blocked'],
            'allowed_packets': self.stats['packets_allowed'],
            'block_rate': (self.stats['packets_blocked'] / max(1, self.stats['packets_processed'])) * 100
        }
    
    def simulate_traffic(self):
        """Simulate network traffic for demonstration"""
        import random
        
        # Simulate various traffic patterns
        test_scenarios = [
            # Normal email traffic
            ('10.0.0.1', '10.0.0.100', 25, 'TCP'),
            ('10.0.0.2', '10.0.0.100', 587, 'TCP'),
            ('10.0.0.3', '10.0.0.100', 993, 'TCP'),
            
            # Web traffic
            ('10.0.0.4', '10.0.0.100', 80, 'TCP'),
            ('10.0.0.5', '10.0.0.100', 443, 'TCP'),
            
            # Blocked traffic
            ('192.168.1.100', '10.0.0.100', 25, 'TCP'),  # Blocked IP
            ('10.0.0.6', '10.0.0.100', 22, 'TCP'),       # SSH port not allowed
            ('10.0.0.7', '10.0.0.100', 3389, 'TCP'),     # RDP port not allowed
            
            # Random traffic
            (f'10.0.0.{random.randint(1,50)}', '10.0.0.100', random.choice([25, 80, 443, 8080]), 'TCP')
        ]
        
        for source_ip, dest_ip, dest_port, protocol in test_scenarios:
            self.inspect_packet(source_ip, dest_ip, dest_port, protocol)
            time.sleep(2)  # Simulate processing time
    
    def start_service(self):
        """Start the firewall VNF service"""
        self.log("🔥 Firewall VNF Started - Monitoring Network Traffic")
        self.log(f"📋 Configuration:")
        self.log(f"   Blocked IPs: {self.blocked_ips}")
        self.log(f"   Allowed Ports: {self.allowed_ports}")
        self.log(f"   Monitoring: Email and Web Traffic")
        
        # Start statistics reporting thread
        def report_stats():
            while True:
                time.sleep(30)  # Report every 30 seconds
                stats = self.get_statistics()
                self.log(f"📊 Statistics: {stats['total_packets']} packets, "
                        f"{stats['blocked_packets']} blocked ({stats['block_rate']:.1f}%)")
        
        stats_thread = threading.Thread(target=report_stats, daemon=True)
        stats_thread.start()
        
        # Main traffic processing loop
        try:
            while True:
                self.simulate_traffic()
                time.sleep(5)  # Wait before next simulation cycle
                
        except KeyboardInterrupt:
            self.log("🛑 Firewall VNF Shutting Down...")
            final_stats = self.get_statistics()
            self.log(f"📈 Final Statistics: {final_stats}")

if __name__ == "__main__":
    firewall = FirewallVNF()
    firewall.start_service()
