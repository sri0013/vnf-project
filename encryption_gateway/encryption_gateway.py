#!/usr/bin/env python3
"""
Encryption Gateway VNF - Email encryption and decryption
Provides data confidentiality for email communications
"""

import time
import base64
import hashlib
import threading
from datetime import datetime
from prometheus_client import start_http_server, Counter, Histogram

class EncryptionGatewayVNF:
    def __init__(self):
        # Encryption configuration
        self.encryption_key = "VNF_SECRET_KEY_2024_SFC_PROJECT"
        self.algorithm = "AES-256"  # Simulated algorithm name
        
        # Key management (simplified)
        self.key_rotation_interval = 3600  # 1 hour in seconds
        self.last_key_rotation = time.time()
        
        # Statistics tracking
        self.stats = {
            'emails_encrypted': 0,
            'emails_decrypted': 0,
            'encryption_errors': 0,
            'decryption_errors': 0,
            'total_processed': 0
        }

        # Prometheus metrics
        self.emails_processed_total = Counter(
            'encryption_emails_processed_total',
            'Total emails processed by encryption gateway',
            ['action']  # encrypt_success, decrypt_success, encrypt_error, decrypt_error
        )
        self.processing_seconds = Histogram(
            'encryption_processing_seconds',
            'Time spent processing emails'
        )

        # Start metrics server
        start_http_server(8080)
        self.log("📈 Prometheus metrics server started on port 8080")
        
    def log(self, message):
        """Log encryption activities with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[ENCRYPTION {timestamp}] {message}")
        
    def simple_encrypt(self, content):
        """
        Simple XOR encryption for demonstration
        In production, use proper cryptographic libraries like cryptography
        
        Args:
            content (str): Content to encrypt
            
        Returns:
            str: Base64 encoded encrypted content
        """
        try:
            encrypted = ""
            for i, char in enumerate(content):
                # XOR with key character (cycling through key)
                key_char = self.encryption_key[i % len(self.encryption_key)]
                encrypted += chr(ord(char) ^ ord(key_char))
            
            # Encode to base64 for safe transmission
            return base64.b64encode(encrypted.encode('utf-8')).decode('utf-8')
            
        except Exception as e:
            self.log(f"❌ Encryption error: {e}")
            self.stats['encryption_errors'] += 1
            return None
    
    def simple_decrypt(self, encrypted_content):
        """
        Simple XOR decryption for demonstration
        
        Args:
            encrypted_content (str): Base64 encoded encrypted content
            
        Returns:
            str: Decrypted content or None if error
        """
        try:
            # Decode from base64
            decoded = base64.b64decode(encrypted_content.encode('utf-8')).decode('utf-8')
            
            decrypted = ""
            for i, char in enumerate(decoded):
                # XOR with key character (cycling through key)
                key_char = self.encryption_key[i % len(self.encryption_key)]
                decrypted += chr(ord(char) ^ ord(key_char))
            
            return decrypted
            
        except Exception as e:
            self.log(f"❌ Decryption error: {e}")
            self.stats['decryption_errors'] += 1
            return None
    
    def process_email(self, content, direction="encrypt", email_id="unknown"):
        """
        Process email for encryption or decryption
        
        Args:
            content (str): Email content
            direction (str): 'encrypt' or 'decrypt'
            email_id (str): Email identifier for logging
            
        Returns:
            dict: Processing results
        """
        start = time.time()
        self.stats['total_processed'] += 1
        
        if direction == "encrypt":
            self.log(f"🔐 Encrypting email: {email_id}")
            encrypted = self.simple_encrypt(content)
            
            if encrypted:
                self.stats['emails_encrypted'] += 1
                self.emails_processed_total.labels(action='encrypt_success').inc()
                self.processing_seconds.observe(time.time() - start)
                self.log(f"✅ Email ENCRYPTED successfully")
                self.log(f"   Original: {content[:30]}...")
                self.log(f"   Encrypted: {encrypted[:30]}...")
                return {
                    'status': 'success',
                    'action': 'encrypted',
                    'original_length': len(content),
                    'encrypted_length': len(encrypted),
                    'result': encrypted
                }
            else:
                self.emails_processed_total.labels(action='encrypt_error').inc()
                self.processing_seconds.observe(time.time() - start)
                self.log(f"❌ Email encryption FAILED")
                return {
                    'status': 'error',
                    'action': 'encrypt_failed',
                    'error': 'Encryption failed'
                }
                
        elif direction == "decrypt":
            self.log(f"🔓 Decrypting email: {email_id}")
            decrypted = self.simple_decrypt(content)
            
            if decrypted:
                self.stats['emails_decrypted'] += 1
                self.emails_processed_total.labels(action='decrypt_success').inc()
                self.processing_seconds.observe(time.time() - start)
                self.log(f"✅ Email DECRYPTED successfully")
                self.log(f"   Encrypted: {content[:30]}...")
                self.log(f"   Decrypted: {decrypted[:30]}...")
                return {
                    'status': 'success',
                    'action': 'decrypted',
                    'encrypted_length': len(content),
                    'decrypted_length': len(decrypted),
                    'result': decrypted
                }
            else:
                self.emails_processed_total.labels(action='decrypt_error').inc()
                self.processing_seconds.observe(time.time() - start)
                self.log(f"❌ Email decryption FAILED")
                return {
                    'status': 'error',
                    'action': 'decrypt_failed',
                    'error': 'Decryption failed'
                }
        
        else:
            self.log(f"❌ Invalid direction: {direction}")
            return {
                'status': 'error',
                'action': 'invalid_direction',
                'error': f'Invalid direction: {direction}'
            }
    
    def rotate_encryption_key(self):
        """Rotate encryption key for security"""
        import secrets
        import string
        
        # Generate new key
        alphabet = string.ascii_letters + string.digits
        new_key = ''.join(secrets.choice(alphabet) for i in range(32))
        
        self.encryption_key = new_key
        self.last_key_rotation = time.time()
        self.log(f"🔄 Encryption key rotated: {new_key[:10]}...")
    
    def get_statistics(self):
        """Return current encryption statistics"""
        return {
            'total_processed': self.stats['total_processed'],
            'emails_encrypted': self.stats['emails_encrypted'],
            'emails_decrypted': self.stats['emails_decrypted'],
            'encryption_errors': self.stats['encryption_errors'],
            'decryption_errors': self.stats['decryption_errors'],
            'success_rate': ((self.stats['emails_encrypted'] + self.stats['emails_decrypted']) / 
                           max(1, self.stats['total_processed'])) * 100
        }
    
    def simulate_email_processing(self):
        """Simulate email encryption/decryption for demonstration"""
        import random
        
        # Test email contents
        test_emails = [
            "Confidential business proposal for Q4 2024",
            "Personal message to friend about weekend plans",
            "Financial transaction details and account information",
            "Sensitive project data and strategic planning",
            "Private communication between executives",
            "Contract negotiations and legal documents",
            "Employee performance review and feedback",
            "Customer data and privacy information"
        ]
        
        for i, content in enumerate(test_emails):
            email_id = f"email_{i+1:03d}"
            
            # Simulate encryption
            self.log(f"📧 Processing: {email_id}")
            encrypt_result = self.process_email(content, "encrypt", email_id)
            
            if encrypt_result['status'] == 'success':
                encrypted_content = encrypt_result['result']
                
                # Simulate decryption
                time.sleep(2)  # Simulate processing delay
                decrypt_result = self.process_email(encrypted_content, "decrypt", email_id)
                
                if decrypt_result['status'] == 'success':
                    decrypted_content = decrypt_result['result']
                    if decrypted_content == content:
                        self.log(f"✅ Round-trip encryption/decryption successful")
                    else:
                        self.log(f"❌ Round-trip encryption/decryption failed")
            
            time.sleep(4)  # Wait before next email
    
    def start_service(self):
        """Start the encryption gateway VNF service"""
        self.log("🔐 Encryption Gateway VNF Started - Processing Email Encryption")
        self.log(f"📋 Configuration:")
        self.log(f"   Algorithm: {self.algorithm}")
        self.log(f"   Key Rotation: Every {self.key_rotation_interval} seconds")
        self.log(f"   Processing: Email encryption and decryption")
        
        # Start key rotation thread
        def key_rotation():
            while True:
                time.sleep(self.key_rotation_interval)
                self.rotate_encryption_key()
        
        rotation_thread = threading.Thread(target=key_rotation, daemon=True)
        rotation_thread.start()
        
        # Start statistics reporting thread
        def report_stats():
            while True:
                time.sleep(30)  # Report every 30 seconds
                stats = self.get_statistics()
                self.log(f"📊 Statistics: {stats['total_processed']} emails, "
                        f"{stats['success_rate']:.1f}% success rate")
        
        stats_thread = threading.Thread(target=report_stats, daemon=True)
        stats_thread.start()
        
        # Main processing loop
        try:
            while True:
                self.simulate_email_processing()
                time.sleep(8)  # Wait before next simulation cycle
                
        except KeyboardInterrupt:
            self.log("🛑 Encryption Gateway VNF Shutting Down...")
            final_stats = self.get_statistics()
            self.log(f"📈 Final Statistics: {final_stats}")

if __name__ == "__main__":
    encryption_gateway = EncryptionGatewayVNF()
    encryption_gateway.start_service()
