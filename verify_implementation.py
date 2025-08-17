#!/usr/bin/env python3
"""
Verification script for Mail Server VNF Implementation
Shows the current status of the implementation
"""

import subprocess
import sys

def check_docker_images():
    """Check if required Docker images exist"""
    print("🔍 Checking Docker images...")
    
    required_images = [
        'my-firewall-vnf',
        'my-antivirus-vnf', 
        'my-spamfilter-vnf',
        'my-encryption-vnf',
        'my-contentfilter-vnf',
        'my-mail-vnf'
    ]
    
    missing_images = []
    found_images = []
    
    for image in required_images:
        try:
            result = subprocess.run(['docker', 'images', '-q', image], 
                                  capture_output=True, text=True)
            if result.stdout.strip():
                found_images.append(image)
                print(f"  ✅ {image}")
            else:
                missing_images.append(image)
                print(f"  ❌ {image}")
        except Exception as e:
            missing_images.append(image)
            print(f"  ❌ {image} (Error: {e})")
    
    return found_images, missing_images

def check_docker_status():
    """Check if Docker is running"""
    print("🔍 Checking Docker status...")
    
    try:
        result = subprocess.run(['docker', 'ps'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ Docker is running")
            return True
        else:
            print("  ❌ Docker is not responding")
            return False
    except Exception as e:
        print(f"  ❌ Docker error: {e}")
        return False

def test_mail_server():
    """Test mail server functionality"""
    print("🔍 Testing mail server...")
    
    # Test if image exists
    try:
        result = subprocess.run(['docker', 'images', '-q', 'my-mail-vnf'], 
                              capture_output=True, text=True)
        if not result.stdout.strip():
            print("  ❌ Mail server image not found")
            return False
    except Exception as e:
        print(f"  ❌ Error checking mail image: {e}")
        return False
    
    # Test running container
    try:
        result = subprocess.run(['docker', 'run', '-d', '--name', 'vnf-mail-verify', 
                               '-p', '2525:2525', 'my-mail-vnf'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ Mail server container started successfully")
            
            # Test port connectivity
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('localhost', 2525))
            sock.close()
            
            if result == 0:
                print("  ✅ SMTP port 2525 is accessible")
                
                # Clean up
                subprocess.run(['docker', 'rm', '-f', 'vnf-mail-verify'], 
                             capture_output=True, text=True)
                return True
            else:
                print("  ❌ SMTP port 2525 is not accessible")
                subprocess.run(['docker', 'rm', '-f', 'vnf-mail-verify'], 
                             capture_output=True, text=True)
                return False
        else:
            print(f"  ❌ Failed to start mail server: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ❌ Error testing mail server: {e}")
        return False

def main():
    """Main verification function"""
    print("🚀 Mail Server VNF Implementation Verification")
    print("=" * 50)
    
    # Check Docker status
    if not check_docker_status():
        print("\n❌ Docker is not running. Please start Docker Desktop first.")
        return
    
    print()
    
    # Check Docker images
    found_images, missing_images = check_docker_images()
    
    print()
    
    # Test mail server specifically
    mail_server_working = test_mail_server()
    
    print("\n" + "=" * 50)
    print("📋 Implementation Summary:")
    print(f"  • Docker Status: {'✅ Running' if check_docker_status() else '❌ Not Running'}")
    print(f"  • VNF Images: {len(found_images)}/{len(found_images) + len(missing_images)} found")
    print(f"  • Mail Server: {'✅ Working' if mail_server_working else '❌ Not Working'}")
    
    if missing_images:
        print(f"\n⚠️  Missing images: {', '.join(missing_images)}")
        print("💡 Build missing images using: ./build_vnf_images.ps1")
    
    if mail_server_working:
        print("\n✅ Mail Server VNF Implementation is COMPLETE and WORKING!")
        print("💡 You can now run the SFC topology: sudo python3 scripts/sfc_topology.py")
    else:
        print("\n❌ Mail Server VNF needs attention")
        print("💡 Check the error messages above and fix any issues")

if __name__ == '__main__':
    main()
