#!/usr/bin/env python3
"""
Test script for the mail server VNF
Tests SMTP connectivity and basic email functionality
"""

import socket
import time
import subprocess
import sys

def test_smtp_connection(host='10.0.0.100', port=2525):
    """Test SMTP connection to the mail server"""
    print(f"🔍 Testing SMTP connection to {host}:{port}")
    
    try:
        # Create socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, port))
        
        # Read banner
        response = sock.recv(1024).decode('utf-8')
        print(f"✅ Connected! Server banner: {response.strip()}")
        
        # Send HELO command
        sock.send(b"HELO testclient.example.com\r\n")
        response = sock.recv(1024).decode('utf-8')
        print(f"✅ HELO response: {response.strip()}")
        
        # Send QUIT command
        sock.send(b"QUIT\r\n")
        response = sock.recv(1024).decode('utf-8')
        print(f"✅ QUIT response: {response.strip()}")
        
        sock.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def check_mail_container():
    """Check if the mail container is running"""
    print("🔍 Checking mail container status...")
    
    try:
        result = subprocess.run(['docker', 'ps', '--filter', 'name=vnf-mail'], 
                              capture_output=True, text=True)
        
        if 'vnf-mail' in result.stdout:
            print("✅ Mail container is running")
            return True
        else:
            print("❌ Mail container is not running")
            return False
            
    except Exception as e:
        print(f"❌ Error checking container: {e}")
        return False

def show_mail_logs():
    """Show recent mail server logs"""
    print("📋 Recent mail server logs:")
    
    try:
        result = subprocess.run(['docker', 'logs', '--tail', '10', 'vnf-mail'], 
                              capture_output=True, text=True)
        print(result.stdout)
    except Exception as e:
        print(f"❌ Error getting logs: {e}")

def main():
    """Main test function"""
    print("🚀 Mail Server VNF Test")
    print("=" * 40)
    
    # Check if container is running
    if not check_mail_container():
        print("\n💡 To start the mail container, run:")
        print("   docker run -d --name vnf-mail --network bridge my-mail-vnf")
        print("   # Or for local testing with port mapping:")
        print("   docker run -d --name vnf-mail-test -p 2525:2525 my-mail-vnf")
        return
    
    # Show logs
    show_mail_logs()
    
    # Test SMTP connection
    print("\n" + "=" * 40)
    if test_smtp_connection():
        print("\n✅ Mail server test completed successfully!")
        print("\n💡 You can now test from Mininet CLI:")
        print("   mininet> h1 telnet 10.0.0.100 2525")
    else:
        print("\n❌ Mail server test failed!")
        print("💡 Check that the container is running and accessible")
        print("💡 For local testing, try:")
        print("   docker run -d --name vnf-mail-test -p 2525:2525 my-mail-vnf")
        print("   Test-NetConnection -ComputerName localhost -Port 2525")

if __name__ == '__main__':
    main()
