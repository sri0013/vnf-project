#!/usr/bin/env python3
"""
SDN Controller for VNF Service Function Chain
Manages flow rules during scaling operations
"""

import json
import logging
import threading
import time
from typing import Dict, List, Optional
from flask import Flask, request, jsonify
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SDNController:
    """SDN Controller for managing VNF flow rules"""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.app = Flask(__name__)
        self.flow_rules = {}
        self.vnf_instances = {}
        self.load_balancer = LoadBalancer()
        
        # Register Flask routes
        self._register_routes()
        
        logger.info(f"SDN Controller initialized on port {port}")
    
    async def initialize(self):
        """Initialize the SDN Controller asynchronously"""
        logger.info("SDN Controller initializing...")
        
        try:
            # Initialize flow rules
            self.flow_rules = {}
            logger.info("Flow rules initialized")
            
            # Initialize VNF instances tracking
            self.vnf_instances = {}
            logger.info("VNF instances tracking initialized")
            
            # Initialize load balancer
            self.load_balancer = LoadBalancer()
            logger.info("Load balancer initialized")
            
            logger.info("SDN Controller initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during initialization: {e}")
            return False
    
    def _register_routes(self):
        """Register Flask routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            return jsonify({'status': 'healthy', 'timestamp': time.time()})
        
        @self.app.route('/flows', methods=['GET'])
        def get_flows():
            return jsonify(self.flow_rules)
        
        @self.app.route('/flows', methods=['POST'])
        def add_flow():
            data = request.json
            flow_id = data.get('flow_id')
            vnf_type = data.get('vnf_type')
            instance_id = data.get('instance_id')
            priority = data.get('priority', 100)
            
            if self._add_flow_rule(flow_id, vnf_type, instance_id, priority):
                return jsonify({'status': 'success', 'flow_id': flow_id})
            else:
                return jsonify({'status': 'error', 'message': 'Failed to add flow rule'}), 400
        
        @self.app.route('/flows/<flow_id>', methods=['DELETE'])
        def remove_flow(flow_id):
            if self._remove_flow_rule(flow_id):
                return jsonify({'status': 'success', 'flow_id': flow_id})
            else:
                return jsonify({'status': 'error', 'message': 'Flow rule not found'}), 404
        
        @self.app.route('/vnf/<vnf_type>/instances', methods=['GET'])
        def get_vnf_instances(vnf_type):
            instances = self.vnf_instances.get(vnf_type, [])
            return jsonify({'vnf_type': vnf_type, 'instances': instances})
        
        @self.app.route('/vnf/<vnf_type>/instances', methods=['POST'])
        def add_vnf_instance(vnf_type):
            data = request.json
            instance_id = data.get('instance_id')
            ip_address = data.get('ip_address')
            port = data.get('port', 8080)
            
            if self._add_vnf_instance(vnf_type, instance_id, ip_address, port):
                return jsonify({'status': 'success', 'instance_id': instance_id})
            else:
                return jsonify({'status': 'error', 'message': 'Failed to add VNF instance'}), 400
        
        @self.app.route('/vnf/<vnf_type>/instances/<instance_id>', methods=['DELETE'])
        def remove_vnf_instance(vnf_type, instance_id):
            if self._remove_vnf_instance(vnf_type, instance_id):
                return jsonify({'status': 'success', 'instance_id': instance_id})
            else:
                return jsonify({'status': 'error', 'message': 'VNF instance not found'}), 404
        
        @self.app.route('/load-balance/<vnf_type>', methods=['GET'])
        def get_next_instance(vnf_type):
            instance = self.load_balancer.get_next_instance(vnf_type, self.vnf_instances.get(vnf_type, []))
            if instance:
                return jsonify({'instance': instance})
            else:
                return jsonify({'error': 'No instances available'}), 404
    
    def _add_flow_rule(self, flow_id: str, vnf_type: str, instance_id: str, priority: int = 100) -> bool:
        """Add a flow rule for VNF routing"""
        try:
            flow_rule = {
                'flow_id': flow_id,
                'vnf_type': vnf_type,
                'instance_id': instance_id,
                'priority': priority,
                'status': 'active',
                'created_at': time.time()
            }
            
            self.flow_rules[flow_id] = flow_rule
            logger.info(f"Added flow rule: {flow_id} -> {vnf_type}:{instance_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding flow rule: {e}")
            return False
    
    async def add_flow_rule(self, flow_rule: Dict) -> bool:
        """Add a flow rule asynchronously"""
        try:
            flow_id = flow_rule.get('flow_id')
            vnf_type = flow_rule.get('vnf_type')
            instance_id = flow_rule.get('instance_id')
            priority = flow_rule.get('priority', 100)
            
            return self._add_flow_rule(flow_id, vnf_type, instance_id, priority)
        except Exception as e:
            logger.error(f"Error adding flow rule: {e}")
            return False
    
    async def remove_flow_rule(self, flow_id: str) -> bool:
        """Remove a flow rule asynchronously"""
        try:
            return self._remove_flow_rule(flow_id)
        except Exception as e:
            logger.error(f"Error removing flow rule: {e}")
            return False
    
    def _remove_flow_rule(self, flow_id: str) -> bool:
        """Remove a flow rule"""
        try:
            if flow_id in self.flow_rules:
                del self.flow_rules[flow_id]
                logger.info(f"Removed flow rule: {flow_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error removing flow rule: {e}")
            return False
    
    def _add_vnf_instance(self, vnf_type: str, instance_id: str, ip_address: str, port: int = 8080) -> bool:
        """Add a VNF instance to the controller"""
        try:
            if vnf_type not in self.vnf_instances:
                self.vnf_instances[vnf_type] = []
            
            instance_info = {
                'instance_id': instance_id,
                'ip_address': ip_address,
                'port': port,
                'status': 'active',
                'added_at': time.time(),
                'health_check': time.time()
            }
            
            self.vnf_instances[vnf_type].append(instance_info)
            logger.info(f"Added VNF instance: {vnf_type}:{instance_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding VNF instance: {e}")
            return False
    
    def _remove_vnf_instance(self, vnf_type: str, instance_id: str) -> bool:
        """Remove a VNF instance from the controller"""
        try:
            if vnf_type in self.vnf_instances:
                instances = self.vnf_instances[vnf_type]
                for i, instance in enumerate(instances):
                    if instance['instance_id'] == instance_id:
                        del instances[i]
                        logger.info(f"Removed VNF instance: {vnf_type}:{instance_id}")
                        return True
            return False
            
        except Exception as e:
            logger.error(f"Error removing VNF instance: {e}")
            return False
    
    def update_flow_rules_for_scaling(self, vnf_type: str, action: str, instance_id: str) -> bool:
        """Update flow rules during scaling operations"""
        try:
            if action == 'add':
                # Add new flow rules for the new instance
                flow_id = f"{vnf_type}-{instance_id}-{int(time.time())}"
                return self._add_flow_rule(flow_id, vnf_type, instance_id, priority=100)
                
            elif action == 'remove':
                # Remove flow rules for the instance being removed
                flows_to_remove = []
                for flow_id, flow_rule in self.flow_rules.items():
                    if (flow_rule['vnf_type'] == vnf_type and 
                        flow_rule['instance_id'] == instance_id):
                        flows_to_remove.append(flow_id)
                
                for flow_id in flows_to_remove:
                    self._remove_flow_rule(flow_id)
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating flow rules for scaling: {e}")
            return False
    
    def get_flow_rules_for_vnf(self, vnf_type: str) -> List[Dict]:
        """Get all flow rules for a specific VNF type"""
        return [flow for flow in self.flow_rules.values() if flow['vnf_type'] == vnf_type]
    
    def health_check_instances(self):
        """Perform health checks on VNF instances"""
        while True:
            try:
                for vnf_type, instances in self.vnf_instances.items():
                    for instance in instances[:]:  # Copy list to avoid modification during iteration
                        if not self._check_instance_health(instance):
                            logger.warning(f"Unhealthy instance detected: {vnf_type}:{instance['instance_id']}")
                            # Mark as unhealthy but don't remove immediately
                            instance['status'] = 'unhealthy'
                        else:
                            instance['status'] = 'active'
                            instance['health_check'] = time.time()
                
                time.sleep(30)  # Health check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in health check: {e}")
                time.sleep(30)
    
    def _check_instance_health(self, instance: Dict) -> bool:
        """Check health of a VNF instance"""
        try:
            url = f"http://{instance['ip_address']}:{instance['port']}/health"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def start(self):
        """Start the SDN controller"""
        logger.info("Starting SDN Controller")
        
        # Start health check thread
        health_thread = threading.Thread(target=self.health_check_instances, daemon=True)
        health_thread.start()
        
        # Start Flask app
        self.app.run(host='0.0.0.0', port=self.port, debug=False)

    def clear_all_flows(self):
        """Clear all flow rules"""
        self.flow_rules.clear()
        logger.info("All flow rules cleared")


class LoadBalancer:
    """Simple load balancer for VNF instances"""
    
    def __init__(self):
        self.current_index = {}
    
    def get_next_instance(self, vnf_type: str, instances: List[Dict]) -> Optional[Dict]:
        """Get next available instance using round-robin"""
        if not instances:
            return None
        
        # Filter only healthy instances
        healthy_instances = [inst for inst in instances if inst.get('status') == 'active']
        if not healthy_instances:
            return None
        
        # Round-robin selection
        if vnf_type not in self.current_index:
            self.current_index[vnf_type] = 0
        
        instance = healthy_instances[self.current_index[vnf_type] % len(healthy_instances)]
        self.current_index[vnf_type] = (self.current_index[vnf_type] + 1) % len(healthy_instances)
        
        return instance


if __name__ == "__main__":
    controller = SDNController()
    controller.start()
