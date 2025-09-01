#!/usr/bin/env python3
"""
Startup Script for VNF Orchestration System
Run this from the project root directory to start the complete orchestration system
"""

import sys
import os
import asyncio
import logging
import signal
import time

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
shutdown_requested = False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global shutdown_requested
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_requested = True

async def start_orchestration_system():
    """Start the complete orchestration system"""
    try:
        logger.info("🚀 Starting VNF Orchestration System...")
        
        # Import orchestration components
        from orchestration.vnf_orchestrator import VNFOrchestrator
        from orchestration.sdn_controller import SDNController
        from orchestration.sfc_orchestrator import SFCOrchestrator
        from orchestration.drl_agent import DRLAgent
        from orchestration.enhanced_arima import EnhancedARIMAForecaster
        
        logger.info("✅ All orchestration components imported successfully")
        
        # Initialize components
        logger.info("🔧 Initializing orchestration components...")
        
        # Initialize VNF Orchestrator
        vnf_orchestrator = VNFOrchestrator()
        await vnf_orchestrator.initialize()
        logger.info("✅ VNF Orchestrator initialized")
        
        # Initialize SDN Controller
        sdn_controller = SDNController(port=8080)
        await sdn_controller.initialize()
        logger.info("✅ SDN Controller initialized")
        
        # Initialize SFC Orchestrator
        sfc_orchestrator = SFCOrchestrator(vnf_orchestrator, sdn_controller)
        logger.info("✅ SFC Orchestrator initialized")
        
        # Initialize DRL Agent
        drl_agent = DRLAgent()
        logger.info("✅ DRL Agent initialized")
        
        # Initialize ARIMA Forecaster
        arima_forecaster = EnhancedARIMAForecaster()
        logger.info("✅ ARIMA Forecaster initialized")
        
        logger.info("🎉 All components initialized successfully!")
        logger.info("📊 Metrics available at: http://localhost:9090/metrics")
        logger.info("🌐 SDN Controller at: http://localhost:8080")
        
        # Keep system running until shutdown requested
        while not shutdown_requested:
            try:
                # Simulate some orchestration activity
                await asyncio.sleep(10)
                
                # Log system status
                resources = vnf_orchestrator.get_available_resources()
                logger.info(f"System Status - CPU: {resources['cpu_available']:.1f}%, "
                          f"Memory: {resources['memory_available']:.1f}%")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in orchestration loop: {e}")
                await asyncio.sleep(5)
        
        logger.info("🛑 Shutting down orchestration system...")
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Make sure you're running from the project root directory")
        logger.error("Try: python start_orchestration.py")
        return False
    except Exception as e:
        logger.error(f"Failed to start orchestration system: {e}")
        return False
    
    return True

def main():
    """Main startup function"""
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🚀 VNF Service Function Chain Orchestration System")
    print("=" * 60)
    print("🔧 Starting intelligent orchestration with DRL+ARIMA...")
    print("📊 Prometheus metrics will be available at: http://localhost:9090/metrics")
    print("🌐 SDN Controller will be available at: http://localhost:8080")
    print("⏹️  Press Ctrl+C to stop the system gracefully")
    print("=" * 60)
    
    try:
        # Run the orchestration system
        success = asyncio.run(start_orchestration_system())
        
        if success:
            print("\n✅ Orchestration system started successfully!")
        else:
            print("\n❌ Failed to start orchestration system!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
    
    print("\n👋 Orchestration system shutdown complete")

if __name__ == "__main__":
    main()
