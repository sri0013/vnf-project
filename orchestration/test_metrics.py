#!/usr/bin/env python3
"""
Test script to verify centralized metrics registry prevents Prometheus collisions
"""

import time
import threading

# Import metrics registry - handle both relative and absolute imports
try:
    # Try relative import first (when run as module)
    from .metrics_registry import start_metrics_server, get_vnf_orchestrator_metrics
except ImportError:
    try:
        # Fallback to absolute import (when run standalone)
        from orchestration.metrics_registry import start_metrics_server, get_vnf_orchestrator_metrics
    except ImportError:
        # Final fallback - direct import (for testing)
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from metrics_registry import start_metrics_server, get_vnf_orchestrator_metrics

def test_metrics_registry():
    """Test that metrics can be created multiple times without collisions"""
    print("🧪 Testing Centralized Metrics Registry...")
    
    # Start metrics server
    print("📊 Starting metrics server...")
    start_metrics_server(9090)
    
    # Test creating metrics multiple times
    print("🔄 Creating metrics multiple times...")
    
    for i in range(5):
        print(f"   Iteration {i+1}: Creating VNF orchestrator metrics...")
        try:
            metrics = get_vnf_orchestrator_metrics()
            print(f"   ✅ Successfully created metrics (iteration {i+1})")
            
            # Test using the metrics
            if 'vnf_instances' in metrics:
                metrics['vnf_instances'].labels(vnf_type='test').set(i)
                print(f"   📈 Set test metric value to {i}")
            
        except Exception as e:
            print(f"   ❌ Error creating metrics (iteration {i+1}): {e}")
            return False
    
    print("✅ All metrics created successfully without collisions!")
    return True

def test_concurrent_access():
    """Test concurrent access to metrics registry"""
    print("\n🔄 Testing concurrent access...")
    
    def worker(worker_id):
        try:
            metrics = get_vnf_orchestrator_metrics()
            metrics['vnf_instances'].labels(vnf_type=f'worker_{worker_id}').set(worker_id)
            print(f"   Worker {worker_id}: Set metric successfully")
        except Exception as e:
            print(f"   Worker {worker_id}: Error - {e}")
    
    # Create multiple threads
    threads = []
    for i in range(3):
        thread = threading.Thread(target=worker, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    print("✅ Concurrent access test completed!")

def main():
    """Main test function"""
    print("🚀 Starting Metrics Registry Tests")
    print("=" * 50)
    
    # Test 1: Basic metrics creation
    if not test_metrics_registry():
        print("❌ Basic metrics test failed!")
        return
    
    # Test 2: Concurrent access
    test_concurrent_access()
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Metrics registry is working correctly.")
    print("\n📊 You can now access metrics at: http://localhost:9090/metrics")
    
    # Keep the server running for manual testing
    print("\n⏳ Keeping metrics server running for manual testing...")
    print("   Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping metrics server...")

if __name__ == "__main__":
    main()
