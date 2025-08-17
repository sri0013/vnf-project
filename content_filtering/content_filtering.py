#!/usr/bin/env python3
"""
Content Filtering VNF - Data loss prevention and policy enforcement
Detects sensitive data patterns and enforces content policies
"""

import time
import re
import threading
from datetime import datetime
from prometheus_client import start_http_server, Counter, Histogram

class ContentFilteringVNF:
    def __init__(self):
        # Prohibited content patterns (sensitive data detection)
        self.prohibited_patterns = {
            # Credit card patterns
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b': 'Credit card number',
            r'\b\d{4}[-\s]?\d{6}[-\s]?\d{5}\b': 'Credit card number (Amex)',
            
            # Social Security Number patterns
            r'\b\d{3}-\d{2}-\d{4}\b': 'Social Security Number',
            r'\b\d{9}\b': 'SSN (no dashes)',
            
            # Phone number patterns
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b': 'Phone number',
            r'\b\(\d{3}\)\s?\d{3}[-.\s]?\d{4}\b': 'Phone number (parentheses)',
            
            # Email patterns (for bulk email detection)
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b': 'Email address',
            
            # IP address patterns
            r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b': 'IP address',
            
            # Date patterns (for sensitive date detection)
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b': 'Date pattern',
            r'\b\d{4}-\d{2}-\d{2}\b': 'ISO date pattern'
        }
        
        # Blocked keywords and phrases
        self.blocked_keywords = [
            'internal use only',
            'classified',
            'top secret',
            'confidential',
            'proprietary',
            'trade secret',
            'for internal distribution only',
            'not for external use',
            'restricted access',
            'sensitive information',
            'private and confidential',
            'company confidential'
        ]
        
        # File type restrictions
        self.blocked_file_extensions = [
            '.exe', '.bat', '.cmd', '.com', '.pif', '.scr',
            '.vbs', '.js', '.jar', '.msi', '.dll', '.sys'
        ]
        
        # Size limits
        self.max_content_size = 10 * 1024 * 1024  # 10MB
        self.max_attachment_count = 5
        
        # Statistics tracking
        self.stats = {
            'content_scanned': 0,
            'policy_violations': 0,
            'sensitive_data_detected': 0,
            'content_blocked': 0,
            'content_allowed': 0
        }

        # Prometheus metrics
        self.content_scanned_total = Counter(
            'contentfilter_items_scanned_total',
            'Total content items scanned',
            ['status']  # approved, blocked
        )
        self.content_size_bytes = Histogram(
            'contentfilter_content_size_bytes',
            'Size of scanned content (bytes)'
        )
        self.sensitive_data_total = Counter(
            'contentfilter_sensitive_data_total',
            'Total instances where sensitive data was detected'
        )

        # Start metrics server
        start_http_server(8080)
        self.log("📈 Prometheus metrics server started on port 8080")
        
    def log(self, message):
        """Log content filtering activities with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[CONTENT_FILTER {timestamp}] {message}")
        
    def scan_content(self, content, filename="unknown", sender="unknown"):
        """
        Scan content for policy violations and sensitive data
        
        Args:
            content (str): Content to scan
            filename (str): Name of the file being scanned
            sender (str): Sender information
            
        Returns:
            dict: Scan results with violations and actions
        """
        self.stats['content_scanned'] += 1
        violations = []
        sensitive_data = []

        # Observe content size
        self.content_size_bytes.observe(len(content))
        
        # Check 1: Prohibited patterns (sensitive data)
        for pattern, description in self.prohibited_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                sensitive_data.append({
                    'type': description,
                    'count': len(matches),
                    'examples': matches[:3]  # Show first 3 examples
                })
                violations.append(f"Sensitive data detected: {description} ({len(matches)} instances)")
        
        # Check 2: Blocked keywords
        content_lower = content.lower()
        for keyword in self.blocked_keywords:
            if keyword.lower() in content_lower:
                violations.append(f"Blocked keyword: {keyword}")
        
        # Check 3: File size check
        if len(content) > self.max_content_size:
            violations.append(f"Content too large: {len(content)} bytes (max: {self.max_content_size})")
        
        # Check 4: File extension check
        if filename:
            file_ext = filename.lower()
            for ext in self.blocked_file_extensions:
                if file_ext.endswith(ext):
                    violations.append(f"Blocked file type: {ext}")
        
        # Check 5: Content length analysis
        if len(content) < 10:
            violations.append("Content too short (potential spam)")
        
        # Determine action based on violations
        if violations:
            self.stats['policy_violations'] += 1
            self.stats['content_blocked'] += 1
            
            if sensitive_data:
                self.stats['sensitive_data_detected'] += 1
                self.sensitive_data_total.inc()
                self.log(f"🚫 CONTENT BLOCKED - Sensitive Data Detected")
                self.log(f"   File: {filename}")
                self.log(f"   Sender: {sender}")
                self.log(f"   Violations: {violations}")
                self.log(f"   Action: BLOCKED - Data Loss Prevention")
            else:
                self.log(f"🚫 CONTENT BLOCKED - Policy Violation")
                self.log(f"   File: {filename}")
                self.log(f"   Sender: {sender}")
                self.log(f"   Violations: {violations}")
                self.log(f"   Action: BLOCKED")
            
            self.content_scanned_total.labels(status='blocked').inc()
            return {
                'status': 'blocked',
                'violations': violations,
                'sensitive_data': sensitive_data,
                'action': 'blocked',
                'reason': 'Policy violation'
            }
        else:
            self.stats['content_allowed'] += 1
            self.content_scanned_total.labels(status='approved').inc()
            self.log(f"✅ Content APPROVED - No policy violations")
            self.log(f"   File: {filename}")
            self.log(f"   Sender: {sender}")
            self.log(f"   Size: {len(content)} bytes")
            return {
                'status': 'approved',
                'violations': [],
                'sensitive_data': [],
                'action': 'allowed',
                'reason': 'No violations'
            }
    
    def scan_email_attachments(self, attachments):
        """
        Scan email attachments for policy violations
        
        Args:
            attachments (list): List of attachment information
            
        Returns:
            dict: Attachment scan results
        """
        if len(attachments) > self.max_attachment_count:
            return {
                'status': 'blocked',
                'reason': f'Too many attachments: {len(attachments)} (max: {self.max_attachment_count})'
            }
        
        blocked_attachments = []
        for attachment in attachments:
            filename = attachment.get('filename', 'unknown')
            size = attachment.get('size', 0)
            
            # Check file extension
            for ext in self.blocked_file_extensions:
                if filename.lower().endswith(ext):
                    blocked_attachments.append(f"Blocked file type: {filename}")
                    break
            
            # Check file size
            if size > self.max_content_size:
                blocked_attachments.append(f"File too large: {filename} ({size} bytes)")
        
        if blocked_attachments:
            return {
                'status': 'blocked',
                'reason': 'Attachment policy violations',
                'violations': blocked_attachments
            }
        
        return {
            'status': 'approved',
            'reason': 'All attachments compliant'
        }
    
    def get_statistics(self):
        """Return current content filtering statistics"""
        total = self.stats['content_scanned']
        if total == 0:
            return {
                'total_scanned': 0,
                'policy_violations': 0,
                'sensitive_data_detected': 0,
                'content_blocked': 0,
                'content_allowed': 0,
                'block_rate': 0.0
            }
        
        block_rate = (self.stats['content_blocked'] / total) * 100
        
        return {
            'total_scanned': total,
            'policy_violations': self.stats['policy_violations'],
            'sensitive_data_detected': self.stats['sensitive_data_detected'],
            'content_blocked': self.stats['content_blocked'],
            'content_allowed': self.stats['content_allowed'],
            'block_rate': block_rate
        }
    
    def simulate_content_filtering(self):
        """Simulate content filtering for demonstration"""
        import random
        
        # Test content scenarios
        test_contents = [
            # Clean content
            {
                'content': 'Regular business email about project updates and meeting schedules.',
                'filename': 'meeting_notes.txt',
                'sender': 'john@company.com'
            },
            {
                'content': 'Weekly report with progress updates and next steps.',
                'filename': 'weekly_report.pdf',
                'sender': 'manager@corp.com'
            },
            
            # Content with sensitive data
            {
                'content': 'Please process payment with credit card: 4532-1234-5678-9012',
                'filename': 'payment_info.txt',
                'sender': 'finance@company.com'
            },
            {
                'content': 'Employee SSN: 123-45-6789 for tax purposes.',
                'filename': 'employee_data.txt',
                'sender': 'hr@company.com'
            },
            {
                'content': 'Contact me at john.doe@example.com or call 555-123-4567',
                'filename': 'contact_info.txt',
                'sender': 'john@company.com'
            },
            
            # Content with blocked keywords
            {
                'content': 'INTERNAL USE ONLY: Company financial data and projections.',
                'filename': 'financial_data.txt',
                'sender': 'finance@company.com'
            },
            {
                'content': 'This is CONFIDENTIAL information not for external use.',
                'filename': 'confidential.txt',
                'sender': 'executive@company.com'
            },
            
            # Large content
            {
                'content': 'A' * (self.max_content_size + 1000),  # Exceeds size limit
                'filename': 'large_file.txt',
                'sender': 'user@company.com'
            }
        ]
        
        for test_case in test_contents:
            self.log(f"📄 Scanning content: '{test_case['filename']}'")
            result = self.scan_content(
                test_case['content'],
                test_case['filename'],
                test_case['sender']
            )
            
            if result['status'] == 'blocked':
                self.log(f"🚫 Content BLOCKED: {result['reason']}")
            else:
                self.log(f"✅ Content APPROVED")
            
            time.sleep(3)  # Simulate processing time
    
    def start_service(self):
        """Start the content filtering VNF service"""
        self.log("🛡️  Content Filtering VNF Started - Monitoring Content Policy")
        self.log(f"📋 Configuration:")
        self.log(f"   Prohibited Patterns: {len(self.prohibited_patterns)} rules")
        self.log(f"   Blocked Keywords: {len(self.blocked_keywords)} terms")
        self.log(f"   Max Content Size: {self.max_content_size} bytes")
        self.log(f"   Max Attachments: {self.max_attachment_count}")
        self.log(f"   Filtering: Data loss prevention and policy enforcement")
        
        # Start statistics reporting thread
        def report_stats():
            while True:
                time.sleep(30)  # Report every 30 seconds
                stats = self.get_statistics()
                self.log(f"📊 Statistics: {stats['total_scanned']} items scanned, "
                        f"{stats['content_blocked']} blocked ({stats['block_rate']:.1f}%)")
        
        stats_thread = threading.Thread(target=report_stats, daemon=True)
        stats_thread.start()
        
        # Main filtering loop
        try:
            while True:
                self.simulate_content_filtering()
                time.sleep(9)  # Wait before next simulation cycle
                
        except KeyboardInterrupt:
            self.log("🛑 Content Filtering VNF Shutting Down...")
            final_stats = self.get_statistics()
            self.log(f"📈 Final Statistics: {final_stats}")

if __name__ == "__main__":
    content_filter = ContentFilteringVNF()
    content_filter.start_service()
