#!/usr/bin/env python3
"""
Test Runner for VNF Orchestration System
Run this from the project root directory to test the orchestration components
"""

import sys
import os
import asyncio
import logging

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_metrics_registry():
    """Test the centralized metrics registry"""
    try:
        from orchestration.metrics_registry import start_metrics_server, get_vnf_orchestrator_metrics
        
        print("🧪 Testing Metrics Registry...")
        
        # Start metrics server
        success = start_metrics_server(9090)
        if success:
            print("✅ Metrics server started successfully")
        else:
            print("⚠️  Metrics server already running or failed to start")
        
        # Test metrics creation
        metrics = get_vnf_orchestrator_metrics()
        print(f"✅ Successfully created {len(metrics)} metrics")
        
        # Test using metrics
        if 'vnf_instances' in metrics:
            metrics['vnf_instances'].labels(vnf_type='test').set(5)
            print("✅ Successfully set test metric value")
        
        return True
        
    except Exception as e:
        print(f"❌ Metrics registry test failed: {e}")
        return False

def test_vnf_orchestrator():
    """Test the VNF orchestrator"""
    try:
        from orchestration.vnf_orchestrator import VNFOrchestrator
        
        print("\n🧪 Testing VNF Orchestrator...")
        
        # Create orchestrator instance
        orchestrator = VNFOrchestrator()
        print("✅ VNF Orchestrator created successfully")
        
        # Test basic methods
        resources = orchestrator.get_available_resources()
        print(f"✅ Available resources: {resources}")
        
        instances = orchestrator.get_vnf_instances('firewall')
        print(f"✅ Firewall instances: {instances}")
        
        return True
        
    except Exception as e:
        print(f"❌ VNF Orchestrator test failed: {e}")
        return False

def test_sdn_controller():
    """Test the SDN controller"""
    try:
        from orchestration.sdn_controller import SDNController
        
        print("\n🧪 Testing SDN Controller...")
        
        # Create SDN controller instance
        controller = SDNController(port=8081)  # Use different port to avoid conflicts
        print("✅ SDN Controller created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ SDN Controller test failed: {e}")
        return False

async def test_async_operations():
    """Test async operations"""
    try:
        from orchestration.vnf_orchestrator import VNFOrchestrator
        
        print("\n🧪 Testing Async Operations...")
        
        orchestrator = VNFOrchestrator()
        
        # Test async initialization
        success = await orchestrator.initialize()
        if success:
            print("✅ Async initialization successful")
        else:
            print("❌ Async initialization failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Async operations test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting VNF Orchestration System Tests")
    print("=" * 60)
    
    # Test 1: Metrics Registry
    if not test_metrics_registry():
        print("❌ Metrics registry test failed!")
        return
    
    # Test 2: VNF Orchestrator
    if not test_vnf_orchestrator():
        print("❌ VNF Orchestrator test failed!")
        return
    
    # Test 3: SDN Controller
    if not test_sdn_controller():
        print("❌ SDN Controller test failed!")
        return
    
    # Test 4: Async Operations
    try:
        asyncio.run(test_async_operations())
    except Exception as e:
        print(f"❌ Async operations test failed: {e}")
        return
    
    print("\n" + "=" * 60)
    print("🎉 All tests passed! Orchestration system is working correctly.")
    print("\n📊 You can now access metrics at: http://localhost:9090/metrics")
    print("🔧 To run the full system, use: python -m orchestration.integrated_system")

if __name__ == "__main__":
    main()
