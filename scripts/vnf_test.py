#!/usr/bin/env python3
"""
VNF Test Script - Simple orchestration test for Service Function Chain
Tests individual VNFs and the complete SFC chain
"""

import subprocess
import time
import sys
import json
from datetime import datetime

class VNFTestOrchestrator:
    def __init__(self):
        self.vnf_images = {
            'firewall': 'my-firewall-vnf',
            'antivirus': 'my-antivirus-vnf',
            'spamfilter': 'my-spamfilter-vnf',
            'encryption': 'my-encryption-vnf',
            'contentfilter': 'my-contentfilter-vnf'
        }
        
        self.vnf_containers = {
            'firewall': 'vnf-firewall',
            'antivirus': 'vnf-antivirus',
            'spamfilter': 'vnf-spamfilter',
            'encryption': 'vnf-encryption',
            'contentfilter': 'vnf-contentfilter'
        }
        
        self.test_results = {}
        
    def log(self, message):
        """Log test activities with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[VNF_TEST {timestamp}] {message}")
        
    def check_docker_images(self):
        """Check if all required Docker images exist"""
        self.log("🔍 Checking Docker images...")
        missing_images = []
        
        for vnf_name, image_name in self.vnf_images.items():
            try:
                result = subprocess.run(['docker', 'images', '-q', image_name], 
                                      capture_output=True, text=True)
                if not result.stdout.strip():
                    missing_images.append(image_name)
                else:
                    self.log(f"✅ {vnf_name}: {image_name}")
            except Exception as e:
                self.log(f"❌ Error checking {image_name}: {e}")
                missing_images.append(image_name)
        
        if missing_images:
            self.log(f"❌ Missing images: {missing_images}")
            self.log("Please build the missing images first:")
            for image in missing_images:
                vnf_name = image.replace('my-', '').replace('-vnf', '')
                self.log(f"  cd {vnf_name} && docker build -t {image} .")
            return False
        
        self.log("✅ All Docker images found")
        return True
    
    def cleanup_containers(self):
        """Stop and remove existing VNF containers"""
        self.log("🧹 Cleaning up existing containers...")
        
        for vnf_name, container_name in self.vnf_containers.items():
            try:
                # Stop container if running
                subprocess.run(['docker', 'stop', container_name], 
                             capture_output=True, text=True)
                # Remove container
                subprocess.run(['docker', 'rm', container_name], 
                             capture_output=True, text=True)
                self.log(f"Cleaned up {container_name}")
            except Exception as e:
                self.log(f"Error cleaning up {container_name}: {e}")
    
    def start_vnf(self, vnf_name):
        """Start a specific VNF container"""
        image_name = self.vnf_images[vnf_name]
        container_name = self.vnf_containers[vnf_name]
        
        try:
            self.log(f"🚀 Starting {vnf_name} VNF...")
            result = subprocess.run([
                'docker', 'run', '-d', 
                '--name', container_name,
                '--network', 'bridge',
                image_name
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log(f"✅ {vnf_name} VNF started successfully")
                return True
            else:
                self.log(f"❌ Failed to start {vnf_name} VNF: {result.stderr}")
                return False
        except Exception as e:
            self.log(f"❌ Error starting {vnf_name} VNF: {e}")
            return False
    
    def stop_vnf(self, vnf_name):
        """Stop a specific VNF container"""
        container_name = self.vnf_containers[vnf_name]
        
        try:
            self.log(f"🛑 Stopping {vnf_name} VNF...")
            subprocess.run(['docker', 'stop', container_name], 
                         capture_output=True, text=True)
            subprocess.run(['docker', 'rm', container_name], 
                         capture_output=True, text=True)
            self.log(f"✅ {vnf_name} VNF stopped and removed")
            return True
        except Exception as e:
            self.log(f"❌ Error stopping {vnf_name} VNF: {e}")
            return False
    
    def get_vnf_logs(self, vnf_name, lines=10):
        """Get logs from a specific VNF container"""
        container_name = self.vnf_containers[vnf_name]
        
        try:
            result = subprocess.run([
                'docker', 'logs', '--tail', str(lines), container_name
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error getting logs: {result.stderr}"
        except Exception as e:
            return f"Error getting logs: {e}"
    
    def test_individual_vnf(self, vnf_name):
        """Test a single VNF in isolation"""
        self.log(f"🧪 Testing {vnf_name} VNF individually...")
        
        # Start the VNF
        if not self.start_vnf(vnf_name):
            return False
        
        # Wait for VNF to initialize
        time.sleep(5)
        
        # Get initial logs
        initial_logs = self.get_vnf_logs(vnf_name, 5)
        self.log(f"📋 Initial logs for {vnf_name}:")
        print(initial_logs)
        
        # Let it run for a bit
        time.sleep(10)
        
        # Get runtime logs
        runtime_logs = self.get_vnf_logs(vnf_name, 10)
        self.log(f"📋 Runtime logs for {vnf_name}:")
        print(runtime_logs)
        
        # Stop the VNF
        self.stop_vnf(vnf_name)
        
        # Check if logs contain expected patterns
        success_indicators = {
            'firewall': ['Firewall VNF Started', 'ALLOWED', 'BLOCKED'],
            'antivirus': ['Antivirus VNF Started', 'Content CLEAN', 'VIRUS DETECTED'],
            'spamfilter': ['Spam Filter VNF Started', 'Email PASSED', 'SPAM DETECTED'],
            'encryption': ['Encryption Gateway VNF Started', 'Email ENCRYPTED', 'Email DECRYPTED'],
            'contentfilter': ['Content Filtering VNF Started', 'Content APPROVED', 'CONTENT BLOCKED']
        }
        
        indicators = success_indicators.get(vnf_name, [])
        success = any(indicator in runtime_logs for indicator in indicators)
        
        if success:
            self.log(f"✅ {vnf_name} VNF test PASSED")
        else:
            self.log(f"❌ {vnf_name} VNF test FAILED")
        
        return success
    
    def test_sfc_chain(self):
        """Test the complete Service Function Chain"""
        self.log("🔗 Testing complete SFC chain...")
        
        # Start all VNFs in sequence
        started_vnfs = []
        for vnf_name in self.vnf_images.keys():
            if self.start_vnf(vnf_name):
                started_vnfs.append(vnf_name)
                time.sleep(3)  # Wait between starts
            else:
                self.log(f"❌ Failed to start {vnf_name}, stopping test")
                self.cleanup_all_vnfs()
                return False
        
        self.log(f"✅ Started {len(started_vnfs)} VNFs: {started_vnfs}")
        
        # Let the chain run for a while
        self.log("⏳ Running SFC chain for 30 seconds...")
        time.sleep(30)
        
        # Collect logs from all VNFs
        chain_logs = {}
        for vnf_name in started_vnfs:
            logs = self.get_vnf_logs(vnf_name, 15)
            chain_logs[vnf_name] = logs
            self.log(f"📋 {vnf_name} logs:")
            print(logs)
            print("-" * 50)
        
        # Check if all VNFs are processing
        all_processing = True
        for vnf_name, logs in chain_logs.items():
            if not logs or "VNF Started" not in logs:
                all_processing = False
                self.log(f"❌ {vnf_name} not processing correctly")
        
        if all_processing:
            self.log("✅ SFC chain test PASSED - All VNFs processing")
        else:
            self.log("❌ SFC chain test FAILED - Some VNFs not processing")
        
        # Cleanup
        self.cleanup_all_vnfs()
        return all_processing
    
    def cleanup_all_vnfs(self):
        """Stop and remove all VNF containers"""
        self.log("🧹 Cleaning up all VNF containers...")
        
        for vnf_name in self.vnf_images.keys():
            self.stop_vnf(vnf_name)
    
    def run_comprehensive_test(self):
        """Run comprehensive VNF testing"""
        self.log("🚀 Starting comprehensive VNF testing...")
        
        # Check prerequisites
        if not self.check_docker_images():
            self.log("❌ Cannot proceed without Docker images")
            return False
        
        # Cleanup any existing containers
        self.cleanup_containers()
        
        # Test individual VNFs
        self.log("\n" + "="*60)
        self.log("🧪 PHASE 1: Individual VNF Testing")
        self.log("="*60)
        
        individual_results = {}
        for vnf_name in self.vnf_images.keys():
            individual_results[vnf_name] = self.test_individual_vnf(vnf_name)
            time.sleep(2)
        
        # Test complete SFC chain
        self.log("\n" + "="*60)
        self.log("🔗 PHASE 2: Complete SFC Chain Testing")
        self.log("="*60)
        
        sfc_result = self.test_sfc_chain()
        
        # Generate test report
        self.log("\n" + "="*60)
        self.log("📊 TEST RESULTS SUMMARY")
        self.log("="*60)
        
        passed_individual = sum(individual_results.values())
        total_individual = len(individual_results)
        
        self.log(f"Individual VNF Tests: {passed_individual}/{total_individual} passed")
        for vnf_name, result in individual_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            self.log(f"  {vnf_name}: {status}")
        
        sfc_status = "✅ PASSED" if sfc_result else "❌ FAILED"
        self.log(f"SFC Chain Test: {sfc_status}")
        
        overall_success = all(individual_results.values()) and sfc_result
        overall_status = "✅ ALL TESTS PASSED" if overall_success else "❌ SOME TESTS FAILED"
        self.log(f"\nOverall Result: {overall_status}")
        
        return overall_success
    
    def interactive_mode(self):
        """Run interactive VNF testing mode"""
        self.log("🎮 Starting interactive VNF testing mode...")
        
        while True:
            print("\n" + "="*50)
            print("VNF Test Orchestrator - Interactive Mode")
            print("="*50)
            print("1. Check Docker images")
            print("2. Test individual VNF")
            print("3. Test complete SFC chain")
            print("4. View VNF logs")
            print("5. Cleanup containers")
            print("6. Run comprehensive test")
            print("7. Exit")
            print("-"*50)
            
            choice = input("Enter your choice (1-7): ").strip()
            
            if choice == '1':
                self.check_docker_images()
                
            elif choice == '2':
                print("\nAvailable VNFs:")
                for i, vnf_name in enumerate(self.vnf_images.keys(), 1):
                    print(f"  {i}. {vnf_name}")
                
                try:
                    vnf_choice = int(input("Select VNF to test (1-5): ")) - 1
                    vnf_names = list(self.vnf_images.keys())
                    if 0 <= vnf_choice < len(vnf_names):
                        self.test_individual_vnf(vnf_names[vnf_choice])
                    else:
                        self.log("❌ Invalid choice")
                except ValueError:
                    self.log("❌ Invalid input")
                    
            elif choice == '3':
                self.test_sfc_chain()
                
            elif choice == '4':
                print("\nAvailable VNFs:")
                for i, vnf_name in enumerate(self.vnf_images.keys(), 1):
                    print(f"  {i}. {vnf_name}")
                
                try:
                    vnf_choice = int(input("Select VNF to view logs (1-5): ")) - 1
                    vnf_names = list(self.vnf_images.keys())
                    if 0 <= vnf_choice < len(vnf_names):
                        vnf_name = vnf_names[vnf_choice]
                        logs = self.get_vnf_logs(vnf_name, 20)
                        self.log(f"📋 Logs for {vnf_name}:")
                        print(logs)
                    else:
                        self.log("❌ Invalid choice")
                except ValueError:
                    self.log("❌ Invalid input")
                    
            elif choice == '5':
                self.cleanup_containers()
                
            elif choice == '6':
                self.run_comprehensive_test()
                
            elif choice == '7':
                self.log("👋 Exiting interactive mode...")
                break
                
            else:
                self.log("❌ Invalid choice, please try again")

def main():
    """Main function"""
    print("🚀 VNF Service Function Chain Test Orchestrator")
    print("Email Security SFC: Firewall → Antivirus → Spam Filter → Encryption → Content Filter")
    
    orchestrator = VNFTestOrchestrator()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--comprehensive':
            # Run comprehensive test
            success = orchestrator.run_comprehensive_test()
            sys.exit(0 if success else 1)
        elif sys.argv[1] == '--interactive':
            # Run interactive mode
            orchestrator.interactive_mode()
        else:
            print("Usage:")
            print("  python vnf_test.py --comprehensive  # Run comprehensive test")
            print("  python vnf_test.py --interactive    # Run interactive mode")
            print("  python vnf_test.py                  # Show this help")
    else:
        # Default: show help and run comprehensive test
        print("\nRunning comprehensive test by default...")
        print("Use --interactive for interactive mode")
        print("Use --comprehensive for comprehensive test only")
        print("-" * 50)
        
        success = orchestrator.run_comprehensive_test()
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
