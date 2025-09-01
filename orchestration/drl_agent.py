import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
import random
from collections import deque, namedtuple
from typing import Dict, List, Tuple, Optional
import logging
import json
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActionType(Enum):
    ALLOCATE = "allocate"
    UNINSTALL = "uninstall"
    WAIT = "wait"

@dataclass
class SFCState:
    """State representation for SFC orchestration"""
    dc_resources: Dict[str, float]  # CPU, memory, bandwidth
    installed_vnfs: Dict[str, int]  # VNF type -> count
    sfc_allocations: Dict[str, Dict]  # Chain allocations
    pending_requests: Dict[str, float]  # Request requirements
    current_load: Dict[str, float]  # Current VNF load

@dataclass
class SFCAction:
    """Action representation for SFC orchestration"""
    action_type: ActionType
    vnf_type: str
    instance_id: Optional[str] = None
    priority: int = 5
    parameters: Optional[Dict] = None

class AttentionLayer(nn.Module):
    """Multi-head attention mechanism for state processing"""
    def __init__(self, input_dim: int, num_heads: int = 8, dropout: float = 0.1):
        super().__init__()
        self.num_heads = num_heads
        self.head_dim = input_dim // num_heads
        assert self.head_dim * num_heads == input_dim, "input_dim must be divisible by num_heads"
        
        self.query = nn.Linear(input_dim, input_dim)
        self.key = nn.Linear(input_dim, input_dim)
        self.value = nn.Linear(input_dim, input_dim)
        self.dropout = nn.Dropout(dropout)
        self.output_projection = nn.Linear(input_dim, input_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size, seq_len, _ = x.size()
        
        # Multi-head attention
        Q = self.query(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        K = self.key(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        V = self.value(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        
        # Attention scores
        scores = torch.matmul(Q, K.transpose(-2, -1)) / np.sqrt(self.head_dim)
        attention_weights = F.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)
        
        # Apply attention
        context = torch.matmul(attention_weights, V)
        context = context.transpose(1, 2).contiguous().view(batch_size, seq_len, -1)
        
        return self.output_projection(context)

class DQNNetwork(nn.Module):
    """Deep Q-Network with attention mechanism"""
    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int = 256):
        super().__init__()
        
        # State processing layers
        self.state_encoder = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )
        
        # Attention layer for processing state relationships
        self.attention = AttentionLayer(hidden_dim)
        
        # Dueling DQN architecture
        self.value_stream = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1)
        )
        
        self.advantage_stream = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, action_dim)
        )
        
    def forward(self, state: torch.Tensor) -> torch.Tensor:
        # Encode state
        encoded = self.state_encoder(state)
        
        # Apply attention (reshape for attention layer)
        batch_size = encoded.size(0)
        encoded = encoded.unsqueeze(1)  # Add sequence dimension
        attended = self.attention(encoded)
        attended = attended.squeeze(1)  # Remove sequence dimension
        
        # Dueling DQN
        value = self.value_stream(attended)
        advantage = self.advantage_stream(attended)
        
        # Combine value and advantage
        q_values = value + advantage - advantage.mean(dim=1, keepdim=True)
        
        return q_values

class PrioritizedReplayBuffer:
    """Prioritized experience replay buffer"""
    def __init__(self, capacity: int = 10000, alpha: float = 0.6, beta: float = 0.4):
        self.capacity = capacity
        self.alpha = alpha
        self.beta = beta
        self.buffer = deque(maxlen=capacity)
        self.priorities = deque(maxlen=capacity)
        self.eps = 1e-6
        
    def add(self, experience: Tuple, priority: float = None):
        if priority is None:
            priority = max(self.priorities) if self.priorities else 1.0
        
        self.buffer.append(experience)
        self.priorities.append(priority)
        
    def sample(self, batch_size: int) -> Tuple[List, List[int], List[float]]:
        if len(self.buffer) < batch_size:
            return list(self.buffer), [1.0] * len(self.buffer), [1.0] * len(self.buffer)
        
        # Calculate sampling probabilities
        priorities = np.array(self.priorities)
        probs = priorities ** self.alpha
        probs /= probs.sum()
        
        # Sample indices
        indices = np.random.choice(len(self.buffer), batch_size, p=probs)
        experiences = [self.buffer[idx] for idx in indices]
        
        # Calculate importance sampling weights
        weights = (len(self.buffer) * probs[indices]) ** (-self.beta)
        weights /= weights.max()
        
        return experiences, indices, weights
    
    def update_priorities(self, indices: List[int], priorities: List[float]):
        for idx, priority in zip(indices, priorities):
            if idx < len(self.priorities):
                self.priorities[idx] = priority + self.eps

class DRLAgent:
    """Deep Reinforcement Learning Agent for VNF Orchestration"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # State and action dimensions
        self.state_dim = config.get('state_dim', 50)
        self.action_dim = config.get('action_dim', 20)
        
        # Neural Networks
        self.q_network = DQNNetwork(self.state_dim, self.action_dim).to(self.device)
        self.target_network = DQNNetwork(self.state_dim, self.action_dim).to(self.device)
        self.target_network.load_state_dict(self.q_network.state_dict())
        
        # Optimizer
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=config.get('learning_rate', 0.001))
        
        # Experience replay
        self.replay_buffer = PrioritizedReplayBuffer(
            capacity=config.get('replay_capacity', 10000)
        )
        
        # Training parameters
        self.gamma = config.get('gamma', 0.99)
        self.epsilon = config.get('epsilon', 1.0)
        self.epsilon_min = config.get('epsilon_min', 0.01)
        self.epsilon_decay = config.get('epsilon_decay', 0.995)
        self.target_update_freq = config.get('target_update_freq', 100)
        self.batch_size = config.get('batch_size', 32)
        
        # Training state
        self.training_step = 0
        self.episode_rewards = []
        self.losses = []
        
        # VNF types and actions mapping
        self.vnf_types = ['firewall', 'antivirus', 'spamfilter', 'encryption_gateway', 'content_filtering', 'mail']
        self.action_mapping = self._create_action_mapping()
        
    def _create_action_mapping(self) -> Dict[int, SFCAction]:
        """Create mapping from action indices to SFCAction objects"""
        mapping = {}
        action_idx = 0
        
        # Allocate actions for each VNF type
        for vnf_type in self.vnf_types:
            mapping[action_idx] = SFCAction(ActionType.ALLOCATE, vnf_type)
            action_idx += 1
            
        # Uninstall actions for each VNF type
        for vnf_type in self.vnf_types:
            mapping[action_idx] = SFCAction(ActionType.UNINSTALL, vnf_type)
            action_idx += 1
            
        # Wait action
        mapping[action_idx] = SFCAction(ActionType.WAIT, "none")
        
        return mapping
    
    def state_to_tensor(self, state: SFCState) -> torch.Tensor:
        """Convert SFCState to tensor representation"""
        # Flatten state into a single vector
        state_vector = []
        
        # DC resources
        state_vector.extend([
            state.dc_resources.get('cpu_available', 0.0),
            state.dc_resources.get('memory_available', 0.0),
            state.dc_resources.get('network_bandwidth', 0.0)
        ])
        
        # Installed VNFs
        for vnf_type in self.vnf_types:
            state_vector.append(state.installed_vnfs.get(vnf_type, 0))
        
        # SFC allocations (simplified)
        sfc_count = len(state.sfc_allocations)
        state_vector.append(sfc_count)
        
        # Pending requests
        state_vector.extend([
            state.pending_requests.get('request_count', 0.0),
            state.pending_requests.get('bandwidth_requirements', 0.0),
            state.pending_requests.get('latency_constraints', 0.0)
        ])
        
        # Current load
        for vnf_type in self.vnf_types:
            state_vector.append(state.current_load.get(vnf_type, 0.0))
        
        # Pad to state_dim
        while len(state_vector) < self.state_dim:
            state_vector.append(0.0)
        
        return torch.FloatTensor(state_vector[:self.state_dim]).unsqueeze(0).to(self.device)
    
    def select_action(self, state: SFCState, training: bool = True) -> SFCAction:
        """Select action using epsilon-greedy policy"""
        if training and random.random() < self.epsilon:
            # Random action
            action_idx = random.randint(0, self.action_dim - 1)
        else:
            # Greedy action
            state_tensor = self.state_to_tensor(state)
            with torch.no_grad():
                q_values = self.q_network(state_tensor)
                action_idx = q_values.argmax().item()
        
        return self.action_mapping.get(action_idx, SFCAction(ActionType.WAIT, "none"))
    
    def calculate_reward(self, action: SFCAction, state: SFCState, result: Dict) -> float:
        """Calculate reward based on action outcome"""
        reward = 0.0
        
        # SFC satisfaction reward
        if result.get('sfc_satisfied', False):
            reward += 2.0
        
        # Penalty for dropped SFCs
        if result.get('sfc_dropped', False):
            reward -= 1.5
        
        # Penalty for invalid actions
        if result.get('action_invalid', False):
            reward -= 1.0
        
        # Penalty for unnecessary uninstallations
        if action.action_type == ActionType.UNINSTALL and result.get('unnecessary', False):
            reward -= 0.5
        
        # Bonus for efficient resource usage
        if result.get('resource_efficiency', 0.0) > 0.8:
            reward += 0.3
        
        # Penalty for SLA violations
        if result.get('sla_violation', False):
            reward -= 0.8
        
        # Small penalty for wait actions to encourage proactive behavior
        if action.action_type == ActionType.WAIT:
            reward -= 0.1
        
        return reward
    
    def train_step(self) -> float:
        """Perform one training step"""
        if len(self.replay_buffer.buffer) < self.batch_size:
            return 0.0
        
        # Sample batch
        experiences, indices, weights = self.replay_buffer.sample(self.batch_size)
        
        # Unpack experiences
        states, actions, rewards, next_states, dones = zip(*experiences)
        
        # Convert to tensors
        state_batch = torch.cat([self.state_to_tensor(s) for s in states])
        next_state_batch = torch.cat([self.state_to_tensor(s) for s in next_states])
        action_batch = torch.LongTensor([list(self.action_mapping.keys())[list(self.action_mapping.values()).index(a)] for a in actions]).to(self.device)
        reward_batch = torch.FloatTensor(rewards).to(self.device)
        done_batch = torch.BoolTensor(dones).to(self.device)
        weight_batch = torch.FloatTensor(weights).to(self.device)
        
        # Current Q values
        current_q_values = self.q_network(state_batch).gather(1, action_batch.unsqueeze(1))
        
        # Next Q values (double DQN)
        with torch.no_grad():
            next_actions = self.q_network(next_state_batch).argmax(1)
            next_q_values = self.target_network(next_state_batch).gather(1, next_actions.unsqueeze(1))
            target_q_values = reward_batch.unsqueeze(1) + (self.gamma * next_q_values * ~done_batch.unsqueeze(1))
        
        # Compute loss
        loss = F.mse_loss(current_q_values, target_q_values, reduction='none')
        weighted_loss = (loss * weight_batch.unsqueeze(1)).mean()
        
        # Backward pass
        self.optimizer.zero_grad()
        weighted_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.q_network.parameters(), 1.0)
        self.optimizer.step()
        
        # Update priorities
        priorities = loss.detach().cpu().numpy().flatten()
        self.replay_buffer.update_priorities(indices, priorities)
        
        # Update target network
        self.training_step += 1
        if self.training_step % self.target_update_freq == 0:
            self.target_network.load_state_dict(self.q_network.state_dict())
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        return weighted_loss.item()
    
    def save_model(self, filepath: str):
        """Save the trained model"""
        torch.save({
            'q_network_state_dict': self.q_network.state_dict(),
            'target_network_state_dict': self.target_network.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'training_step': self.training_step,
            'episode_rewards': self.episode_rewards,
            'losses': self.losses
        }, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load a trained model"""
        checkpoint = torch.load(filepath, map_location=self.device)
        self.q_network.load_state_dict(checkpoint['q_network_state_dict'])
        self.target_network.load_state_dict(checkpoint['target_network_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint['epsilon']
        self.training_step = checkpoint['training_step']
        self.episode_rewards = checkpoint['episode_rewards']
        self.losses = checkpoint['losses']
        logger.info(f"Model loaded from {filepath}")
    
    def get_stats(self) -> Dict:
        """Get training statistics"""
        return {
            'epsilon': self.epsilon,
            'training_step': self.training_step,
            'replay_buffer_size': len(self.replay_buffer.buffer),
            'episode_rewards': self.episode_rewards[-100:] if self.episode_rewards else [],
            'losses': self.losses[-100:] if self.losses else []
        }
