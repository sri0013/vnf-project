#!/usr/bin/env python3
"""
Antivirus VNF - Content-based virus detection
Scans email content for virus signatures and malicious patterns
"""

import time
import hashlib
import threading
from datetime import datetime

class AntivirusVNF:
    def __init__(self):
        # Mock virus signatures (MD5 hashes of known malicious content)
        self.virus_signatures = {
            # Empty file hash (common in some attacks)
            "d41d8cd98f00b204e9800998ecf8427e": "Empty file virus",
            
            # Simple test virus signatures
            "5d41402abc4b2a76b9719d911017c592": "Test virus 'hello'",
            "098f6bcd4621d373cade4e832627b4f6": "Test virus 'test'",
            
            # Common malicious patterns (simplified)
            "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3": "Malicious script pattern",
            "40bd001563085fc35165329ea1ff5c5ecbdbbeef": "Suspicious executable pattern"
        }
        
        # Suspicious patterns in content
        self.suspicious_patterns = [
            r'<script.*?>.*?</script>',  # JavaScript tags
            r'javascript:',              # JavaScript protocol
            r'vbscript:',                # VBScript protocol
            r'<iframe.*?>',              # IFrame tags
            r'<object.*?>',              # Object tags
            r'<embed.*?>',               # Embed tags
            r'<applet.*?>',              # Applet tags
            r'<form.*?>',                # Form tags (potential phishing)
            r'password.*?=.*?',          # Password fields
            r'credit.*?card.*?number',   # Credit card patterns
        ]
        
        # Statistics tracking
        self.stats = {
            'files_scanned': 0,
            'viruses_detected': 0,
            'suspicious_content': 0,
            'clean_files': 0
        }
        
    def log(self, message):
        """Log antivirus activities with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[ANTIVIRUS {timestamp}] {message}")
        
    def scan_content(self, content, filename="unknown"):
        """
        Scan content for viruses and suspicious patterns
        
        Args:
            content (str): Content to scan
            filename (str): Name of the file being scanned
            
        Returns:
            dict: Scan results with status and details
        """
        self.stats['files_scanned'] += 1
        
        # Generate MD5 hash of content
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        
        # Check for virus signatures
        if content_hash in self.virus_signatures:
            self.stats['viruses_detected'] += 1
            virus_name = self.virus_signatures[content_hash]
            self.log(f"🦠 VIRUS DETECTED! File: {filename}")
            self.log(f"   Hash: {content_hash}")
            self.log(f"   Virus: {virus_name}")
            self.log(f"   Action: QUARANTINED")
            return {
                'status': 'infected',
                'virus_name': virus_name,
                'hash': content_hash,
                'action': 'quarantined'
            }
        
        # Check for suspicious patterns
        import re
        suspicious_found = []
        for pattern in self.suspicious_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                suspicious_found.append(pattern)
        
        if suspicious_found:
            self.stats['suspicious_content'] += 1
            self.log(f"⚠️  SUSPICIOUS CONTENT DETECTED! File: {filename}")
            self.log(f"   Patterns: {suspicious_found}")
            self.log(f"   Action: FLAGGED FOR REVIEW")
            return {
                'status': 'suspicious',
                'patterns': suspicious_found,
                'action': 'flagged'
            }
        
        # Content is clean
        self.stats['clean_files'] += 1
        self.log(f"✅ Content CLEAN. File: {filename}")
        self.log(f"   Hash: {content_hash}")
        return {
            'status': 'clean',
            'hash': content_hash,
            'action': 'allowed'
        }
    
    def scan_email_attachment(self, attachment_data, filename):
        """
        Scan email attachment for viruses
        
        Args:
            attachment_data (bytes): Raw attachment data
            filename (str): Attachment filename
            
        Returns:
            dict: Scan results
        """
        # Convert bytes to string for scanning (simplified)
        content = attachment_data.decode('utf-8', errors='ignore')
        return self.scan_content(content, filename)
    
    def get_statistics(self):
        """Return current antivirus statistics"""
        total = self.stats['files_scanned']
        if total == 0:
            return {
                'total_scanned': 0,
                'viruses_detected': 0,
                'suspicious_content': 0,
                'clean_files': 0,
                'detection_rate': 0.0
            }
        
        detection_rate = ((self.stats['viruses_detected'] + self.stats['suspicious_content']) / total) * 100
        
        return {
            'total_scanned': total,
            'viruses_detected': self.stats['viruses_detected'],
            'suspicious_content': self.stats['suspicious_content'],
            'clean_files': self.stats['clean_files'],
            'detection_rate': detection_rate
        }
    
    def simulate_email_scanning(self):
        """Simulate email content scanning for demonstration"""
        import random
        
        # Test email contents
        test_emails = [
            # Clean emails
            ("Meeting tomorrow", "Let's meet at 2 PM tomorrow for the project discussion."),
            ("Invoice #12345", "Please find attached invoice for services rendered."),
            ("Weekly report", "Here is the weekly progress report for your review."),
            
            # Suspicious emails
            ("Click here to win!", "<script>alert('You won!')</script> Click here to claim your prize!"),
            ("Password reset", "<form action='http://fake.com'>Enter your password: <input type='password'></form>"),
            ("Important document", "<iframe src='http://malicious.com'></iframe> Check this document."),
            
            # Virus-infected emails (using known hashes)
            ("Test virus", "hello"),  # Will trigger virus detection
            ("Empty file", ""),       # Will trigger virus detection
            ("Test content", "test"), # Will trigger virus detection
        ]
        
        for subject, content in test_emails:
            self.log(f"📧 Scanning email: '{subject[:30]}...'")
            result = self.scan_content(content, f"email_{subject[:10]}")
            
            if result['status'] == 'infected':
                self.log(f"🚫 Email BLOCKED due to virus")
            elif result['status'] == 'suspicious':
                self.log(f"⚠️  Email FLAGGED for review")
            else:
                self.log(f"✅ Email PASSED antivirus scan")
            
            time.sleep(3)  # Simulate processing time
    
    def start_service(self):
        """Start the antivirus VNF service"""
        self.log("🛡️  Antivirus VNF Started - Scanning Email Content")
        self.log(f"📋 Configuration:")
        self.log(f"   Virus Signatures: {len(self.virus_signatures)} patterns")
        self.log(f"   Suspicious Patterns: {len(self.suspicious_patterns)} rules")
        self.log(f"   Scanning: Email content and attachments")
        
        # Start statistics reporting thread
        def report_stats():
            while True:
                time.sleep(30)  # Report every 30 seconds
                stats = self.get_statistics()
                self.log(f"📊 Statistics: {stats['total_scanned']} files scanned, "
                        f"{stats['viruses_detected']} viruses, {stats['detection_rate']:.1f}% detection rate")
        
        stats_thread = threading.Thread(target=report_stats, daemon=True)
        stats_thread.start()
        
        # Main scanning loop
        try:
            while True:
                self.simulate_email_scanning()
                time.sleep(6)  # Wait before next simulation cycle
                
        except KeyboardInterrupt:
            self.log("🛑 Antivirus VNF Shutting Down...")
            final_stats = self.get_statistics()
            self.log(f"📈 Final Statistics: {final_stats}")

if __name__ == "__main__":
    antivirus = AntivirusVNF()
    antivirus.start_service()
