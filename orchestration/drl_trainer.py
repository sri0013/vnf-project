import asyncio
import time
import json
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from drl_agent import DRLAgent, SFCState, SFCAction, ActionType
from vnf_orchestrator import VNFOrchestrator
from sdn_controller import SDNController

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TrainingConfig:
    """Configuration for DRL training"""
    episodes: int = 20
    max_steps_per_episode: int = 100
    training_updates: int = 350
    save_interval: int = 50
    eval_interval: int = 10
    model_save_path: str = "models/drl_vnf_agent.pth"
    results_save_path: str = "results/training_results.json"
    
    # DRL parameters
    learning_rate: float = 0.001
    gamma: float = 0.99
    epsilon: float = 1.0
    epsilon_min: float = 0.01
    epsilon_decay: float = 0.995
    batch_size: int = 32
    replay_capacity: int = 10000
    target_update_freq: int = 100
    
    # State/Action dimensions
    state_dim: int = 50
    action_dim: int = 13  # 6 allocate + 6 uninstall + 1 wait

class SFCEnvironment:
    """Environment wrapper for SFC orchestration"""
    
    def __init__(self, orchestrator: VNFOrchestrator, sdn_controller: SDNController):
        self.orchestrator = orchestrator
        self.sdn_controller = sdn_controller
        self.vnf_types = ['firewall', 'antivirus', 'spamfilter', 'encryption_gateway', 'content_filtering', 'mail']
        
    def get_state(self) -> SFCState:
        """Get current environment state"""
        # Get DC resources
        dc_resources = self.orchestrator.get_available_resources()
        
        # Get installed VNFs
        installed_vnfs = {}
        for vnf_type in self.vnf_types:
            instances = self.orchestrator.get_vnf_instances(vnf_type)
            installed_vnfs[vnf_type] = len(instances)
        
        # Get SFC allocations
        sfc_allocations = self.orchestrator.get_active_sfcs()
        
        # Get pending requests (simulated)
        pending_requests = self._simulate_pending_requests()
        
        # Get current load
        current_load = {}
        for vnf_type in self.vnf_types:
            load = self.orchestrator.get_vnf_load(vnf_type)
            current_load[vnf_type] = load
        
        return SFCState(
            dc_resources=dc_resources,
            installed_vnfs=installed_vnfs,
            sfc_allocations=sfc_allocations,
            pending_requests=pending_requests,
            current_load=current_load
        )
    
    def _simulate_pending_requests(self) -> Dict[str, float]:
        """Simulate pending SFC requests"""
        return {
            'request_count': np.random.poisson(3),  # Average 3 requests
            'bandwidth_requirements': np.random.uniform(10, 50),  # 10-50 Mbps
            'latency_constraints': np.random.uniform(100, 500)  # 100-500ms
        }
    
    def execute_action(self, action: SFCAction) -> Dict:
        """Execute action and return result"""
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
                success = self.orchestrator.allocate_vnf(action.vnf_type)
                if success:
                    result['sfc_satisfied'] = True
                    result['resource_efficiency'] = self._calculate_resource_efficiency()
                else:
                    result['action_invalid'] = True
                    
            elif action.action_type == ActionType.UNINSTALL:
                instances = self.orchestrator.get_vnf_instances(action.vnf_type)
                if instances:
                    # Check if uninstallation is necessary
                    load = self.orchestrator.get_vnf_load(action.vnf_type)
                    if load < 0.3:  # Low load threshold
                        self.orchestrator.remove_vnf(action.vnf_type, instances[0])
                        result['resource_efficiency'] = self._calculate_resource_efficiency()
                    else:
                        result['unnecessary'] = True
                else:
                    result['action_invalid'] = True
                    
            elif action.action_type == ActionType.WAIT:
                # No action taken, just wait
                pass
                
        except Exception as e:
            logger.error(f"Error executing action {action}: {e}")
            result['action_invalid'] = True
        
        # Check for SLA violations
        result['sla_violation'] = self._check_sla_violations()
        
        return result
    
    def _calculate_resource_efficiency(self) -> float:
        """Calculate resource efficiency score"""
        resources = self.orchestrator.get_available_resources()
        total_cpu = resources.get('cpu_total', 8)
        total_memory = resources.get('memory_total', 16)
        
        used_cpu = total_cpu - resources.get('cpu_available', 0)
        used_memory = total_memory - resources.get('memory_available', 0)
        
        cpu_efficiency = used_cpu / total_cpu
        memory_efficiency = used_memory / total_memory
        
        return (cpu_efficiency + memory_efficiency) / 2
    
    def _check_sla_violations(self) -> bool:
        """Check for SLA violations"""
        # Simulate SLA checking
        return np.random.random() < 0.1  # 10% chance of violation
    
    def reset(self):
        """Reset environment to initial state"""
        # Remove all VNFs
        for vnf_type in self.vnf_types:
            instances = self.orchestrator.get_vnf_instances(vnf_type)
            for instance in instances:
                self.orchestrator.remove_vnf(vnf_type, instance)
        
        # Clear flow rules
        self.sdn_controller.clear_all_flows()
        
        logger.info("Environment reset completed")

class DRLTrainer:
    """DRL training pipeline for VNF orchestration"""
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.results = {
            'episode_rewards': [],
            'episode_lengths': [],
            'losses': [],
            'epsilon_values': [],
            'resource_efficiency': [],
            'sfc_satisfaction_rate': []
        }
        
        # Create directories
        Path(self.config.model_save_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.config.results_save_path).parent.mkdir(parents=True, exist_ok=True)
        
    async def train(self, agent: DRLAgent, environment: SFCEnvironment):
        """Main training loop"""
        logger.info(f"Starting DRL training for {self.config.episodes} episodes")
        
        for episode in range(self.config.episodes):
            logger.info(f"Episode {episode + 1}/{self.config.episodes}")
            
            # Reset environment
            environment.reset()
            
            episode_reward = 0
            episode_length = 0
            sfc_satisfied_count = 0
            total_actions = 0
            
            # Episode loop
            for step in range(self.config.max_steps_per_episode):
                # Get current state
                state = environment.get_state()
                
                # Select action
                action = agent.select_action(state, training=True)
                
                # Execute action
                result = environment.execute_action(action)
                
                # Calculate reward
                reward = agent.calculate_reward(action, state, result)
                episode_reward += reward
                
                # Get next state
                next_state = environment.get_state()
                
                # Store experience
                done = step == self.config.max_steps_per_episode - 1
                agent.replay_buffer.add((state, action, reward, next_state, done))
                
                # Train agent
                loss = agent.train_step()
                if loss > 0:
                    agent.losses.append(loss)
                
                # Update statistics
                episode_length += 1
                total_actions += 1
                if result['sfc_satisfied']:
                    sfc_satisfied_count += 1
                
                # Log progress
                if step % 10 == 0:
                    logger.info(f"Step {step}: Action={action.action_type.value}, "
                              f"VNF={action.vnf_type}, Reward={reward:.3f}")
                
                # Check if episode should end early
                if self._should_end_episode(state, result):
                    break
            
            # Episode completed
            agent.episode_rewards.append(episode_reward)
            
            # Calculate metrics
            resource_efficiency = environment._calculate_resource_efficiency()
            sfc_satisfaction_rate = sfc_satisfied_count / max(total_actions, 1)
            
            # Store results
            self.results['episode_rewards'].append(episode_reward)
            self.results['episode_lengths'].append(episode_length)
            self.results['epsilon_values'].append(agent.epsilon)
            self.results['resource_efficiency'].append(resource_efficiency)
            self.results['sfc_satisfaction_rate'].append(sfc_satisfaction_rate)
            
            logger.info(f"Episode {episode + 1} completed:")
            logger.info(f"  Total Reward: {episode_reward:.3f}")
            logger.info(f"  Episode Length: {episode_length}")
            logger.info(f"  Resource Efficiency: {resource_efficiency:.3f}")
            logger.info(f"  SFC Satisfaction Rate: {sfc_satisfaction_rate:.3f}")
            logger.info(f"  Epsilon: {agent.epsilon:.3f}")
            
            # Save model periodically
            if (episode + 1) % self.config.save_interval == 0:
                agent.save_model(self.config.model_save_path)
                self.save_results()
            
            # Evaluation
            if (episode + 1) % self.config.eval_interval == 0:
                await self.evaluate(agent, environment)
            
            # Small delay between episodes
            await asyncio.sleep(0.1)
        
        # Training completed
        logger.info("Training completed!")
        agent.save_model(self.config.model_save_path)
        self.save_results()
        self.plot_results()
    
    def _should_end_episode(self, state: SFCState, result: Dict) -> bool:
        """Determine if episode should end early"""
        # End if too many invalid actions
        if result.get('action_invalid', False):
            return True
        
        # End if SLA violation
        if result.get('sla_violation', False):
            return True
        
        # End if no resources available
        if state.dc_resources.get('cpu_available', 0) < 0.1:
            return True
        
        return False
    
    async def evaluate(self, agent: DRLAgent, environment: SFCEnvironment):
        """Evaluate agent performance"""
        logger.info("Starting evaluation...")
        
        # Set agent to evaluation mode
        original_epsilon = agent.epsilon
        agent.epsilon = 0.0  # No exploration during evaluation
        
        eval_rewards = []
        eval_satisfaction_rates = []
        
        for _ in range(5):  # 5 evaluation episodes
            environment.reset()
            episode_reward = 0
            sfc_satisfied_count = 0
            total_actions = 0
            
            for step in range(50):  # Shorter evaluation episodes
                state = environment.get_state()
                action = agent.select_action(state, training=False)
                result = environment.execute_action(action)
                reward = agent.calculate_reward(action, state, result)
                
                episode_reward += reward
                total_actions += 1
                if result['sfc_satisfied']:
                    sfc_satisfied_count += 1
                
                if step > 10 and self._should_end_episode(state, result):
                    break
            
            eval_rewards.append(episode_reward)
            satisfaction_rate = sfc_satisfied_count / max(total_actions, 1)
            eval_satisfaction_rates.append(satisfaction_rate)
        
        # Restore epsilon
        agent.epsilon = original_epsilon
        
        avg_reward = np.mean(eval_rewards)
        avg_satisfaction = np.mean(eval_satisfaction_rates)
        
        logger.info(f"Evaluation Results:")
        logger.info(f"  Average Reward: {avg_reward:.3f}")
        logger.info(f"  Average SFC Satisfaction: {avg_satisfaction:.3f}")
    
    def save_results(self):
        """Save training results to file"""
        with open(self.config.results_save_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"Results saved to {self.config.results_save_path}")
    
    def plot_results(self):
        """Plot training results"""
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        # Episode rewards
        axes[0, 0].plot(self.results['episode_rewards'])
        axes[0, 0].set_title('Episode Rewards')
        axes[0, 0].set_xlabel('Episode')
        axes[0, 0].set_ylabel('Reward')
        
        # Episode lengths
        axes[0, 1].plot(self.results['episode_lengths'])
        axes[0, 1].set_title('Episode Lengths')
        axes[0, 1].set_xlabel('Episode')
        axes[0, 1].set_ylabel('Steps')
        
        # Epsilon values
        axes[0, 2].plot(self.results['epsilon_values'])
        axes[0, 2].set_title('Epsilon Decay')
        axes[0, 2].set_xlabel('Episode')
        axes[0, 2].set_ylabel('Epsilon')
        
        # Resource efficiency
        axes[1, 0].plot(self.results['resource_efficiency'])
        axes[1, 0].set_title('Resource Efficiency')
        axes[1, 0].set_xlabel('Episode')
        axes[1, 0].set_ylabel('Efficiency')
        
        # SFC satisfaction rate
        axes[1, 1].plot(self.results['sfc_satisfaction_rate'])
        axes[1, 1].set_title('SFC Satisfaction Rate')
        axes[1, 1].set_xlabel('Episode')
        axes[1, 1].set_ylabel('Satisfaction Rate')
        
        # Losses (if available)
        if agent.losses:
            axes[1, 2].plot(agent.losses)
            axes[1, 2].set_title('Training Loss')
            axes[1, 2].set_xlabel('Training Step')
            axes[1, 2].set_ylabel('Loss')
        
        plt.tight_layout()
        plt.savefig('results/training_plots.png', dpi=300, bbox_inches='tight')
        logger.info("Training plots saved to results/training_plots.png")

async def main():
    """Main training function"""
    # Load configuration
    config = TrainingConfig()
    
    # Initialize components
    orchestrator = VNFOrchestrator()
    sdn_controller = SDNController()
    
    # Create environment
    environment = SFCEnvironment(orchestrator, sdn_controller)
    
    # Create DRL agent
    agent_config = {
        'state_dim': config.state_dim,
        'action_dim': config.action_dim,
        'learning_rate': config.learning_rate,
        'gamma': config.gamma,
        'epsilon': config.epsilon,
        'epsilon_min': config.epsilon_min,
        'epsilon_decay': config.epsilon_decay,
        'batch_size': config.batch_size,
        'replay_capacity': config.replay_capacity,
        'target_update_freq': config.target_update_freq
    }
    
    agent = DRLAgent(agent_config)
    
    # Create trainer
    trainer = DRLTrainer(config)
    
    # Start training
    await trainer.train(agent, environment)
    
    logger.info("DRL training completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
