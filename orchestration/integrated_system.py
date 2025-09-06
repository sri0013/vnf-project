#!/usr/bin/env python3
"""
Integrated VNF Service Function Chain System
Main entry point for the complete orchestration system
"""

import sys
import os
import asyncio
import logging
import signal
import json
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor

# Add the project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import orchestration components with proper error handling
try:
    from orchestration.vnf_orchestrator import VNFOrchestrator
    from orchestration.sdn_controller import SDNController
    from orchestration.sfc_orchestrator import SFCOrchestrator
    from orchestration.drl_agent import DRLAgent, SFCState, SFCAction, ActionType
    from orchestration.enhanced_arima import EnhancedARIMAForecaster
    from orchestration.grafana_dashboards import GrafanaDashboardGenerator
    logger.info("✅ All orchestration components imported successfully")
except ImportError as e:
    logger.error(f"❌ Import error: {e}")
    logger.error("Make sure you're running from the project root directory")
    logger.error("Try: python -m orchestration.integrated_system")
    sys.exit(1)

class IntegratedNFVSystem:
    """Complete integrated NFV system with DRL and forecasting"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.running = False
        self.shutdown_event = asyncio.Event()
        
        # Initialize components
        self.orchestrator = VNFOrchestrator()
        self.sdn_controller = SDNController()
        self.drl_agent = None
        self.arima_forecaster = None
        
        # Metrics and monitoring
        self.metrics = {
            'sfc_requests': 0,
            'sfc_satisfied': 0,
            'sfc_dropped': 0,
            'resource_efficiency': 0.0,
            'average_latency': 0.0,
            'drl_episodes': 0,
            'forecast_accuracy': 0.0
        }
        
        # Configuration
        self.drl_enabled = self.config.get('drl_enabled', True)
        self.forecasting_enabled = self.config.get('forecasting_enabled', True)
        self.monitoring_enabled = self.config.get('monitoring_enabled', True)
        self.auto_scaling_enabled = self.config.get('auto_scaling_enabled', True)
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    async def initialize(self):
        """Initialize all system components"""
        logger.info("Initializing Integrated NFV System...")
        
        try:
            # Initialize VNF Orchestrator
            await self.orchestrator.initialize()
            logger.info("VNF Orchestrator initialized")
            
            # Initialize SDN Controller
            await self.sdn_controller.initialize()
            logger.info("SDN Controller initialized")
            
            # Initialize DRL Agent
            if self.drl_enabled:
                drl_config = {
                    'state_dim': 50,
                    'action_dim': 13,
                    'learning_rate': 0.001,
                    'gamma': 0.99,
                    'epsilon': 1.0,
                    'epsilon_min': 0.01,
                    'epsilon_decay': 0.995,
                    'batch_size': 32,
                    'replay_capacity': 10000,
                    'target_update_freq': 100
                }
                self.drl_agent = DRLAgent(drl_config)
                logger.info("DRL Agent initialized")
            
            # Initialize ARIMA Forecaster
            if self.forecasting_enabled:
                arima_config = {
                    'min_history_length': 20,
                    'forecast_horizon': 12,
                    'confidence_level': 0.95,
                    'auto_optimize': True
                }
                self.arima_forecaster = EnhancedARIMAForecaster(arima_config)
                logger.info("ARIMA Forecaster initialized")
            
            # Generate Grafana dashboards
            if self.monitoring_enabled:
                dashboard_generator = GrafanaDashboardGenerator()
                dashboard_generator.generate_all_dashboards()
                logger.info("Grafana dashboards generated")
            
            logger.info("System initialization completed successfully")
            
        except Exception as e:
            logger.error(f"Error during initialization: {e}")
            raise
    
    async def start(self):
        """Start the integrated system"""
        logger.info("Starting Integrated NFV System...")
        self.running = True
        
        # Start background tasks
        tasks = []
        
        if self.drl_enabled:
            tasks.append(asyncio.create_task(self._drl_learning_loop()))
        
        if self.forecasting_enabled:
            tasks.append(asyncio.create_task(self._forecasting_loop()))
        
        if self.auto_scaling_enabled:
            tasks.append(asyncio.create_task(self._auto_scaling_loop()))
        
        tasks.append(asyncio.create_task(self._monitoring_loop()))
        tasks.append(asyncio.create_task(self._sfc_request_simulation()))
        
        # Wait for shutdown signal
        await self.shutdown_event.wait()
        
        # Cancel all tasks
        for task in tasks:
            task.cancel()
        
        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("System shutdown completed")
    
    async def _drl_learning_loop(self):
        """DRL agent learning loop"""
        logger.info("Starting DRL learning loop")
        
        while self.running and not self.shutdown_event.is_set():
            try:
                # Get current system state
                state = self._get_system_state()
                
                # Select action using DRL agent
                action = self.drl_agent.select_action(state, training=True)
                
                # Execute action
                result = await self._execute_drl_action(action)
                
                # Calculate reward
                reward = self.drl_agent.calculate_reward(action, state, result)
                
                # Get next state
                next_state = self._get_system_state()
                
                # Store experience
                done = False  # Continuous learning
                self.drl_agent.replay_buffer.add((state, action, reward, next_state, done))
                
                # Train agent
                loss = self.drl_agent.train_step()
                if loss > 0:
                    self.metrics['drl_episodes'] += 1
                
                # Log progress
                if self.metrics['drl_episodes'] % 100 == 0:
                    logger.info(f"DRL Training - Episodes: {self.metrics['drl_episodes']}, "
                              f"Loss: {loss:.4f}, Epsilon: {self.drl_agent.epsilon:.3f}")
                
                await asyncio.sleep(1)  # Training interval
                
            except Exception as e:
                logger.error(f"Error in DRL learning loop: {e}")
                await asyncio.sleep(5)
    
    async def _forecasting_loop(self):
        """ARIMA forecasting loop"""
        logger.info("Starting ARIMA forecasting loop")
        
        while self.running and not self.shutdown_event.is_set():
            try:
                # Collect current metrics
                current_load = self._get_current_load()
                self.arima_forecaster.add_data_point(current_load)
                
                # Generate forecast if enough data
                if len(self.arima_forecaster.history) >= self.arima_forecaster.min_history_length:
                    forecast_result = self.arima_forecaster.forecast(steps=6)
                    
                    # Get scaling recommendations
                    recommendations = self.arima_forecaster.get_scaling_recommendations(
                        current_load=current_load, threshold=0.8
                    )
                    
                    # Log forecast results
                    logger.info(f"ARIMA Forecast - Action: {recommendations['action']}, "
                              f"Reason: {recommendations['reason']}")
                    
                    # Update forecast accuracy metric
                    if forecast_result.accuracy_metrics:
                        self.metrics['forecast_accuracy'] = forecast_result.accuracy_metrics.get('r_squared', 0.0)
                
                await asyncio.sleep(30)  # Forecast interval
                
            except Exception as e:
                logger.error(f"Error in forecasting loop: {e}")
                await asyncio.sleep(60)
    
    async def _auto_scaling_loop(self):
        """Auto-scaling loop based on forecasts and DRL decisions"""
        logger.info("Starting auto-scaling loop")
        
        while self.running and not self.shutdown_event.is_set():
            try:
                # Get current resource utilization
                resources = self.orchestrator.get_available_resources()
                current_load = self._get_current_load()
                
                # Check if scaling is needed
                scaling_action = await self._determine_scaling_action(current_load, resources)
                
                if scaling_action:
                    await self._execute_scaling_action(scaling_action)
                
                await asyncio.sleep(60)  # Scaling check interval
                
            except Exception as e:
                logger.error(f"Error in auto-scaling loop: {e}")
                await asyncio.sleep(120)
    
    async def _monitoring_loop(self):
        """System monitoring loop"""
        logger.info("Starting monitoring loop")
        
        while self.running and not self.shutdown_event.is_set():
            try:
                # Update system metrics
                self._update_system_metrics()
                
                # Log system status
                logger.info(f"System Status - SFC Requests: {self.metrics['sfc_requests']}, "
                          f"Satisfied: {self.metrics['sfc_satisfied']}, "
                          f"Efficiency: {self.metrics['resource_efficiency']:.3f}")
                
                await asyncio.sleep(10)  # Monitoring interval
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(30)
    
    async def _sfc_request_simulation(self):
        """Simulate SFC requests for testing"""
        logger.info("Starting SFC request simulation")
        
        while self.running and not self.shutdown_event.is_set():
            try:
                # Simulate SFC request
                await self._simulate_sfc_request()
                
                await asyncio.sleep(30)  # Request interval
                
            except Exception as e:
                logger.error(f"Error in SFC request simulation: {e}")
                await asyncio.sleep(60)
    
    def _get_system_state(self) -> SFCState:
        """Get current system state for DRL agent"""
        # Get DC resources
        dc_resources = self.orchestrator.get_available_resources()
        
        # Get installed VNFs
        installed_vnfs = {}
        vnf_types = ['firewall', 'spamfilter', 'contentfilter', 'encryption']
        for vnf_type in vnf_types:
            instances = self.orchestrator.get_vnf_instances(vnf_type)
            installed_vnfs[vnf_type] = len(instances)
        
        # Get SFC allocations
        sfc_allocations = self.orchestrator.get_active_sfcs()
        
        # Get pending requests (simulated)
        pending_requests = {
            'request_count': self.metrics['sfc_requests'],
            'bandwidth_requirements': 50.0,  # Simulated
            'latency_constraints': 500.0  # Simulated
        }
        
        # Get current load
        current_load = {}
        for vnf_type in vnf_types:
            load = self.orchestrator.get_vnf_load(vnf_type)
            current_load[vnf_type] = load
        
        return SFCState(
            dc_resources=dc_resources,
            installed_vnfs=installed_vnfs,
            sfc_allocations=sfc_allocations,
            pending_requests=pending_requests,
            current_load=current_load
        )
    
    async def _execute_drl_action(self, action: SFCAction) -> Dict:
        """Execute DRL action and return result"""
        result = {
            'sfc_satisfied': False,
            'sfc_dropped': False,
            'action_invalid': False,
            'unnecessary': False,
            'resource_efficiency': 0.0,
            'sla_violation': False
        }
        
        try:
            if action.action_type == ActionType.ALLOCATE:
                success = await self.orchestrator.allocate_vnf(action.vnf_type)
                if success:
                    result['sfc_satisfied'] = True
                    result['resource_efficiency'] = self._calculate_resource_efficiency()
                else:
                    result['action_invalid'] = True
                    
            elif action.action_type == ActionType.UNINSTALL:
                instances = self.orchestrator.get_vnf_instances(action.vnf_type)
                if instances:
                    load = self.orchestrator.get_vnf_load(action.vnf_type)
                    if load < 0.3:
                        await self.orchestrator.remove_vnf(action.vnf_type, instances[0])
                        result['resource_efficiency'] = self._calculate_resource_efficiency()
                    else:
                        result['unnecessary'] = True
                else:
                    result['action_invalid'] = True
                    
        except Exception as e:
            logger.error(f"Error executing DRL action: {e}")
            result['action_invalid'] = True
        
        return result
    
    async def _determine_scaling_action(self, current_load: float, resources: Dict) -> Optional[Dict]:
        """Determine if scaling action is needed"""
        scaling_action = None
        
        # Check resource thresholds
        cpu_available = resources.get('cpu_available', 0)
        memory_available = resources.get('memory_available', 0)
        
        if current_load > 0.8 and cpu_available > 1.0 and memory_available > 2.0:
            # Scale out
            scaling_action = {
                'action': 'scale_out',
                'vnf_type': self._select_vnf_for_scaling(),
                'reason': f'High load detected: {current_load:.3f}'
            }
        elif current_load < 0.3 and len(self.orchestrator.get_all_vnf_instances()) > 1:
            # Scale in
            scaling_action = {
                'action': 'scale_in',
                'vnf_type': self._select_vnf_for_removal(),
                'reason': f'Low load detected: {current_load:.3f}'
            }
        
        return scaling_action
    
    async def _execute_scaling_action(self, scaling_action: Dict):
        """Execute scaling action"""
        try:
            if scaling_action['action'] == 'scale_out':
                success = await self.orchestrator.allocate_vnf(scaling_action['vnf_type'])
                if success:
                    logger.info(f"Scaled out {scaling_action['vnf_type']}: {scaling_action['reason']}")
                else:
                    logger.warning(f"Failed to scale out {scaling_action['vnf_type']}")
                    
            elif scaling_action['action'] == 'scale_in':
                instances = self.orchestrator.get_vnf_instances(scaling_action['vnf_type'])
                if instances:
                    await self.orchestrator.remove_vnf(scaling_action['vnf_type'], instances[0])
                    logger.info(f"Scaled in {scaling_action['vnf_type']}: {scaling_action['reason']}")
                    
        except Exception as e:
            logger.error(f"Error executing scaling action: {e}")
    
    async def _simulate_sfc_request(self):
        """Simulate SFC request for testing"""
        self.metrics['sfc_requests'] += 1
        
        # Simulate SFC creation
        sfc_config = {
            'chain_id': f'sfc_{self.metrics["sfc_requests"]}',
            'vnf_sequence': ['firewall', 'spamfilter', 'contentfilter', 'encryption'],
            'bandwidth': 50,
            'latency_constraint': 500
        }
        
        try:
            success = await self.orchestrator.create_sfc(sfc_config)
            if success:
                self.metrics['sfc_satisfied'] += 1
                logger.info(f"SFC {sfc_config['chain_id']} created successfully")
            else:
                self.metrics['sfc_dropped'] += 1
                logger.warning(f"SFC {sfc_config['chain_id']} creation failed")
                
        except Exception as e:
            logger.error(f"Error creating SFC: {e}")
            self.metrics['sfc_dropped'] += 1
    
    def _get_current_load(self) -> float:
        """Get current system load"""
        resources = self.orchestrator.get_available_resources()
        total_cpu = resources.get('cpu_total', 8)
        total_memory = resources.get('memory_total', 16)
        
        used_cpu = total_cpu - resources.get('cpu_available', 0)
        used_memory = total_memory - resources.get('memory_available', 0)
        
        cpu_load = used_cpu / total_cpu
        memory_load = used_memory / total_memory
        
        return (cpu_load + memory_load) / 2
    
    def _calculate_resource_efficiency(self) -> float:
        """Calculate resource efficiency"""
        return self._get_current_load()
    
    def _select_vnf_for_scaling(self) -> str:
        """Select VNF type for scaling out"""
        vnf_types = ['firewall', 'spamfilter', 'contentfilter', 'encryption']
        
        # Find VNF with highest load
        max_load = 0
        selected_vnf = vnf_types[0]
        
        for vnf_type in vnf_types:
            load = self.orchestrator.get_vnf_load(vnf_type)
            if load > max_load:
                max_load = load
                selected_vnf = vnf_type
        
        return selected_vnf
    
    def _select_vnf_for_removal(self) -> str:
        """Select VNF type for scaling in"""
        vnf_types = ['firewall', 'spamfilter', 'contentfilter', 'encryption']
        
        # Find VNF with lowest load
        min_load = float('inf')
        selected_vnf = vnf_types[0]
        
        for vnf_type in vnf_types:
            instances = self.orchestrator.get_vnf_instances(vnf_type)
            if len(instances) > 1:  # Only consider if multiple instances exist
                load = self.orchestrator.get_vnf_load(vnf_type)
                if load < min_load:
                    min_load = load
                    selected_vnf = vnf_type
        
        return selected_vnf
    
    def _update_system_metrics(self):
        """Update system metrics"""
        self.metrics['resource_efficiency'] = self._calculate_resource_efficiency()
        
        # Calculate average latency (simulated)
        if self.metrics['sfc_satisfied'] > 0:
            self.metrics['average_latency'] = 100 + (self.metrics['resource_efficiency'] * 200)
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("Initiating system shutdown...")
        self.running = False
        self.shutdown_event.set()
        
        # Save DRL model
        if self.drl_agent:
            self.drl_agent.save_model('models/drl_vnf_agent_final.pth')
        
        # Save system metrics
        with open('system_metrics.json', 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        logger.info("System shutdown completed")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, initiating shutdown...")
    asyncio.create_task(system.shutdown())

async def main():
    """Main function"""
    global system
    
    # Load configuration
    config = {
        'drl_enabled': True,
        'forecasting_enabled': True,
        'monitoring_enabled': True,
        'auto_scaling_enabled': True
    }
    
    # Create system instance
    system = IntegratedNFVSystem(config)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize system
        await system.initialize()
        
        # Start system
        await system.start()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"System error: {e}")
    finally:
        await system.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
