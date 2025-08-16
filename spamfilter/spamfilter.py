#!/usr/bin/env python3
"""
Spam Filter VNF - Email spam detection and filtering
Uses keyword analysis, domain reputation, and content scoring
"""

import time
import re
import threading
from datetime import datetime

class SpamFilterVNF:
    def __init__(self):
        # Common spam keywords with weights
        self.spam_keywords = {
            # High-weight spam indicators
            'viagra': 15,
            'lottery': 12,
            'winner': 10,
            'congratulations': 8,
            'million dollars': 15,
            'click here': 8,
            'free money': 12,
            'urgent': 6,
            'limited time': 7,
            'act now': 8,
            'exclusive offer': 9,
            'guaranteed': 7,
            'risk-free': 6,
            'no obligation': 5,
            'special promotion': 8,
            'discount': 4,
            'sale': 3,
            'buy now': 8,
            'order now': 7,
            'call now': 6
        }
        
        # Known spam domains
        self.spam_domains = [
            'spammer.com',
            'malicious.net',
            'fake-pharmacy.com',
            'lottery-scam.org',
            'viagra-online.net',
            'free-money-scam.com'
        ]
        
        # Suspicious email patterns
        self.suspicious_patterns = [
            r'\b[A-Z]{10,}\b',  # ALL CAPS words
            r'\$\d+',           # Dollar amounts
            r'\b\d{10,}\b',     # Long numbers
            r'[!]{2,}',         # Multiple exclamation marks
            r'[?]{2,}',         # Multiple question marks
        ]
        
        # Statistics tracking
        self.stats = {
            'emails_processed': 0,
            'spam_detected': 0,
            'legitimate_emails': 0,
            'average_spam_score': 0.0
        }
        
    def log(self, message):
        """Log spam filter activities with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[SPAM_FILTER {timestamp}] {message}")
        
    def check_spam(self, email_subject, sender_email, sender_domain, content):
        """
        Check if email is spam using multiple criteria
        
        Args:
            email_subject (str): Email subject line
            sender_email (str): Sender email address
            sender_domain (str): Sender domain
            content (str): Email content
            
        Returns:
            dict: Spam check results with score and decision
        """
        self.stats['emails_processed'] += 1
        spam_score = 0
        reasons = []
        
        # Check 1: Spam keywords in subject and content
        subject_content = f"{email_subject} {content}".lower()
        for keyword, weight in self.spam_keywords.items():
            if keyword.lower() in subject_content:
                spam_score += weight
                reasons.append(f"Spam keyword: {keyword}")
        
        # Check 2: Sender domain reputation
        if sender_domain in self.spam_domains:
            spam_score += 25
            reasons.append(f"Suspicious domain: {sender_domain}")
        
        # Check 3: Content length analysis
        if len(content) < 20:
            spam_score += 5
            reasons.append("Very short content")
        elif len(content) > 10000:
            spam_score += 3
            reasons.append("Very long content")
        
        # Check 4: Suspicious patterns
        for pattern in self.suspicious_patterns:
            matches = re.findall(pattern, subject_content)
            if matches:
                spam_score += len(matches) * 2
                reasons.append(f"Suspicious pattern: {pattern}")
        
        # Check 5: Subject line analysis
        if len(email_subject) > 100:
            spam_score += 4
            reasons.append("Very long subject")
        
        if email_subject.count('!') > 3:
            spam_score += 6
            reasons.append("Too many exclamation marks")
        
        # Check 6: Email address patterns
        if re.search(r'\d{4,}', sender_email):
            spam_score += 3
            reasons.append("Many numbers in email address")
        
        # Determine spam threshold
        spam_threshold = 20  # Emails with score >= 20 are considered spam
        
        # Update statistics
        if spam_score >= spam_threshold:
            self.stats['spam_detected'] += 1
            self.log(f"🚫 SPAM DETECTED! Score: {spam_score}")
            self.log(f"   Subject: {email_subject[:50]}...")
            self.log(f"   Sender: {sender_email}")
            self.log(f"   Reasons: {reasons}")
            self.log(f"   Action: BLOCKED")
            return {
                'status': 'spam',
                'score': spam_score,
                'reasons': reasons,
                'action': 'blocked'
            }
        else:
            self.stats['legitimate_emails'] += 1
            self.log(f"✅ Email PASSED spam filter")
            self.log(f"   Subject: {email_subject[:50]}...")
            self.log(f"   Sender: {sender_email}")
            self.log(f"   Score: {spam_score}")
            return {
                'status': 'legitimate',
                'score': spam_score,
                'reasons': reasons,
                'action': 'delivered'
            }
    
    def get_statistics(self):
        """Return current spam filter statistics"""
        total = self.stats['emails_processed']
        if total == 0:
            return {
                'total_processed': 0,
                'spam_detected': 0,
                'legitimate_emails': 0,
                'spam_rate': 0.0,
                'average_score': 0.0
            }
        
        spam_rate = (self.stats['spam_detected'] / total) * 100
        avg_score = self.stats['average_spam_score'] / max(1, total)
        
        return {
            'total_processed': total,
            'spam_detected': self.stats['spam_detected'],
            'legitimate_emails': self.stats['legitimate_emails'],
            'spam_rate': spam_rate,
            'average_score': avg_score
        }
    
    def simulate_email_filtering(self):
        """Simulate email filtering for demonstration"""
        import random
        
        # Test email scenarios
        test_emails = [
            # Legitimate emails
            {
                'subject': 'Meeting tomorrow',
                'sender': 'john@company.com',
                'domain': 'company.com',
                'content': 'Let\'s meet at 2 PM tomorrow for the project discussion. Please bring your notes.'
            },
            {
                'subject': 'Invoice #12345',
                'sender': 'billing@vendor.com',
                'domain': 'vendor.com',
                'content': 'Please find attached invoice for services rendered. Payment is due within 30 days.'
            },
            {
                'subject': 'Weekly report',
                'sender': 'manager@corp.com',
                'domain': 'corp.com',
                'content': 'Here is the weekly progress report for your review. Please let me know if you have any questions.'
            },
            
            # Spam emails
            {
                'subject': 'YOU WON THE LOTTERY!!!',
                'sender': 'winner123@lottery-scam.org',
                'domain': 'lottery-scam.org',
                'content': 'CONGRATULATIONS! You have won $1,000,000! Click here to claim your prize NOW!'
            },
            {
                'subject': 'Free viagra - limited time offer',
                'sender': 'pharmacy@fake-pharmacy.com',
                'domain': 'fake-pharmacy.com',
                'content': 'Buy viagra now! Special promotion! Risk-free! Order now!'
            },
            {
                'subject': 'URGENT: Your account needs verification',
                'sender': 'security12345@spammer.com',
                'domain': 'spammer.com',
                'content': 'Your account has been suspended. Click here to verify your information immediately!'
            },
            {
                'subject': 'Exclusive offer - act now!',
                'sender': 'sales@malicious.net',
                'domain': 'malicious.net',
                'content': 'Limited time offer! Buy now! Guaranteed results! No obligation!'
            }
        ]
        
        for email in test_emails:
            self.log(f"📧 Processing email: '{email['subject'][:30]}...'")
            result = self.check_spam(
                email['subject'],
                email['sender'],
                email['domain'],
                email['content']
            )
            
            # Update average score
            self.stats['average_spam_score'] += result['score']
            
            time.sleep(3)  # Simulate processing time
    
    def start_service(self):
        """Start the spam filter VNF service"""
        self.log("🛡️  Spam Filter VNF Started - Filtering Email")
        self.log(f"📋 Configuration:")
        self.log(f"   Spam Keywords: {len(self.spam_keywords)} patterns")
        self.log(f"   Spam Domains: {len(self.spam_domains)} blocked")
        self.log(f"   Spam Threshold: 20 points")
        self.log(f"   Filtering: Subject, content, sender analysis")
        
        # Start statistics reporting thread
        def report_stats():
            while True:
                time.sleep(30)  # Report every 30 seconds
                stats = self.get_statistics()
                self.log(f"📊 Statistics: {stats['total_processed']} emails, "
                        f"{stats['spam_detected']} spam ({stats['spam_rate']:.1f}%)")
        
        stats_thread = threading.Thread(target=report_stats, daemon=True)
        stats_thread.start()
        
        # Main filtering loop
        try:
            while True:
                self.simulate_email_filtering()
                time.sleep(7)  # Wait before next simulation cycle
                
        except KeyboardInterrupt:
            self.log("🛑 Spam Filter VNF Shutting Down...")
            final_stats = self.get_statistics()
            self.log(f"📈 Final Statistics: {final_stats}")

if __name__ == "__main__":
    spam_filter = SpamFilterVNF()
    spam_filter.start_service()
