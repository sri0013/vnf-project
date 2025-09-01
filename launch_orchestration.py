#!/usr/bin/env python3
"""
Universal Launcher for VNF Orchestration System
This script can be run from anywhere and will automatically find and launch the system
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_project_root():
    """Find the vnf-project root directory"""
    current_dir = os.path.abspath(os.getcwd())
    
    # Walk up the directory tree to find the project root
    while current_dir != os.path.dirname(current_dir):  # Stop at filesystem root
        if os.path.exists(os.path.join(current_dir, 'orchestration', '__init__.py')):
            return current_dir
        current_dir = os.path.dirname(current_dir)
    
    return None

def main():
    """Main launcher function"""
    print("🚀 VNF Orchestration System Launcher")
    print("=" * 50)
    
    # Find the project root
    project_root = find_project_root()
    if not project_root:
        print("❌ Error: Could not find vnf-project root directory")
        print("   Make sure you're running this from within the vnf-project directory tree")
        print("   Current directory:", os.getcwd())
        sys.exit(1)
    
    print(f"✅ Found project root: {project_root}")
    
    # Change to the project root
    os.chdir(project_root)
    print(f"📁 Changed to directory: {os.getcwd()}")
    
    # Check if __init__.py exists
    init_file = os.path.join('orchestration', '__init__.py')
    if not os.path.exists(init_file):
        print("⚠️  Creating missing __init__.py file...")
        try:
            with open(init_file, 'w') as f:
                f.write('# VNF Orchestration Package\n')
            print("✅ Created orchestration/__init__.py")
        except Exception as e:
            print(f"❌ Failed to create __init__.py: {e}")
            sys.exit(1)
    
    # Test imports
    print("🧪 Testing imports...")
    try:
        result = subprocess.run([
            sys.executable, '-c', 
            'from orchestration.vnf_orchestrator import VNFOrchestrator; print("✅ Imports work")'
        ], capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            print("✅ Import test passed")
        else:
            print(f"❌ Import test failed: {result.stderr}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Import test error: {e}")
        sys.exit(1)
    
    # Launch the system
    print("\n🚀 Launching VNF Orchestration System...")
    print("=" * 50)
    
    try:
        # Run the integrated system as a module
        result = subprocess.run([
            sys.executable, '-m', 'orchestration.integrated_system'
        ], check=False)
        
        if result.returncode == 0:
            print("\n✅ Orchestration system completed successfully")
        else:
            print(f"\n❌ Orchestration system exited with code: {result.returncode}")
            sys.exit(result.returncode)
            
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except FileNotFoundError:
        print("❌ Error: Could not find Python executable")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
