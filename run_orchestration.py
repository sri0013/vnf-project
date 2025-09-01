#!/usr/bin/env python3
"""
Simple Runner for VNF Orchestration System
This script demonstrates the correct way to run the orchestration system

USAGE:
    cd vnf-project
    python run_orchestration.py
"""

import subprocess
import sys
import os

def main():
    """Run the orchestration system using the correct module approach"""
    
    # Check if we're in the right directory
    if not os.path.exists('orchestration') or not os.path.isdir('orchestration'):
        print("❌ Error: This script must be run from the vnf-project root directory")
        print("   Current directory:", os.getcwd())
        print("   Expected to find 'orchestration/' directory")
        sys.exit(1)
    
    # Check if __init__.py exists
    if not os.path.exists('orchestration/__init__.py'):
        print("❌ Error: orchestration/__init__.py not found")
        print("   Creating it now...")
        try:
            with open('orchestration/__init__.py', 'w') as f:
                f.write('# VNF Orchestration Package\n')
            print("✅ Created orchestration/__init__.py")
        except Exception as e:
            print(f"❌ Failed to create __init__.py: {e}")
            sys.exit(1)
    
    print("🚀 Starting VNF Orchestration System")
    print("=" * 50)
    print("📁 Running from:", os.getcwd())
    print("🔧 Using module execution: python -m orchestration.integrated_system")
    print("=" * 50)
    
    try:
        # Run the orchestration system as a module
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
