#!/usr/bin/env python3
"""
Universal Test Script for VNF Orchestration System
This script can be run from anywhere to test the system
"""

import os
import sys
import subprocess

def find_project_root():
    """Find the vnf-project root directory"""
    current_dir = os.path.abspath(os.getcwd())
    
    while current_dir != os.path.dirname(current_dir):
        if os.path.exists(os.path.join(current_dir, 'orchestration', '__init__.py')):
            return current_dir
        current_dir = os.path.dirname(current_dir)
    
    return None

def main():
    """Main test function"""
    print("🧪 VNF Orchestration System Test")
    print("=" * 40)
    
    # Find project root
    project_root = find_project_root()
    if not project_root:
        print("❌ Error: Could not find vnf-project root directory")
        print("   Current directory:", os.getcwd())
        sys.exit(1)
    
    print(f"✅ Found project root: {project_root}")
    
    # Change to project root
    os.chdir(project_root)
    print(f"📁 Changed to: {os.getcwd()}")
    
    # Test 1: Basic import
    print("\n🧪 Test 1: Basic Import")
    try:
        result = subprocess.run([
            sys.executable, '-c', 
            'from orchestration.vnf_orchestrator import VNFOrchestrator; print("✅ VNF Orchestrator imported")'
        ], capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            print("✅ Import test passed")
        else:
            print(f"❌ Import test failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Import test error: {e}")
        return False
    
    # Test 2: Metrics registry
    print("\n🧪 Test 2: Metrics Registry")
    try:
        result = subprocess.run([
            sys.executable, '-c', 
            'from orchestration.metrics_registry import start_metrics_server; print("✅ Metrics registry imported")'
        ], capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            print("✅ Metrics registry test passed")
        else:
            print(f"❌ Metrics registry test failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Metrics registry test error: {e}")
        return False
    
    # Test 3: SDN Controller
    print("\n🧪 Test 3: SDN Controller")
    try:
        result = subprocess.run([
            sys.executable, '-c', 
            'from orchestration.sdn_controller import SDNController; print("✅ SDN Controller imported")'
        ], capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            print("✅ SDN Controller test passed")
        else:
            print(f"❌ SDN Controller test failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ SDN Controller test error: {e}")
        return False
    
    print("\n" + "=" * 40)
    print("🎉 All tests passed! System is ready to run.")
    print("\n🚀 To run the system, use:")
    print("   python launch_orchestration.py")
    print("   OR")
    print("   python -m orchestration.integrated_system")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
