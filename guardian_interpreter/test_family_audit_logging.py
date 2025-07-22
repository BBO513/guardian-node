#!/usr/bin/env python3
"""
Test suite for enhanced family audit logging functionality
Tests the AuditLogger class extensions for family features
"""

import unittest
import tempfile
import shutil
import os
import json
import logging
from datetime import datetime
from network_security import AuditLogger

class TestFamilyAuditLogging(unittest.TestCase):
    """Test cases for family audit logging enhancements"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for test logs
        self.test_dir = tempfile.mkdtemp()
        
        # Create test configuration
        self.config = {
            'logging': {
                'log_directory': self.test_dir,
                'level': 'INFO'
            }
        }
        
        # Create test logger
        self.logger = logging.getLogger('TestLogger')
        self.logger.setLevel(logging.INFO)
        
        # Initialize AuditLogger
        self.audit_logger = AuditLogger(self.config, self.logger)
    
    def tearDown(self):
        """Clean up test environment"""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_family_activity_logging(self):
        """Test logging of family activities"""
        family_id = "test_family_001"
        activity_type = "query"
        details = {
            "question": "How can I secure my home WiFi?",
            "user_age_group": "adult",
            "session_id": "session_123"
        }
        
        # Log family activity
        self.audit_logger.log_family_activity(family_id, activity_type, details)
        
        # Verify log was written
        family_log_path = os.path.join(self.test_dir, "family_audit.log")
        self.assertTrue(os.path.exists(family_log_path))
        
        # Read and verify log content
        with open(family_log_path, 'r') as f:
            log_line = f.readline().strip()
            log_record = json.loads(log_line)
        
        self.assertEqual(log_record['family_id'], family_id)
        self.assertEqual(log_record['activity_type'], activity_type)
        self.assertEqual(log_record['details']['question'], details['question'])
        self.assertEqual(log_record['session_id'], details['session_id'])
        self.assertIn('timestamp', log_record)
    
    def test_family_security_event_logging(self):
        """Test logging of family security events"""
        family_id = "test_family_002"
        event_type = "suspicious_activity_detected"
        details = {
            "device_type": "smartphone",
            "threat_level": "medium",
            "action_taken": "notification_sent"
        }
        
        # Log family security event
        self.audit_logger.log_family_security_event(family_id, event_type, details)
        
        # Verify log was written
        family_log_path = os.path.join(self.test_dir, "family_audit.log")
        self.assertTrue(os.path.exists(family_log_path))
        
        # Read and verify log content
        with open(family_log_path, 'r') as f:
            log_line = f.readline().strip()
            log_record = json.loads(log_line)
        
        self.assertEqual(log_record['family_id'], family_id)
        self.assertEqual(log_record['security_event_type'], event_type)
        self.assertEqual(log_record['details']['device_type'], details['device_type'])
        self.assertEqual(log_record['details']['threat_level'], details['threat_level'])
        self.assertIn('timestamp', log_record)
    
    def test_sensitive_data_redaction(self):
        """Test that sensitive data is properly redacted"""
        family_id = "test_family_003"
        activity_type = "profile_update"
        details = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "secret123",
            "phone": "555-1234",
            "device_info": "iPhone 12",
            "api_key": "sk-1234567890abcdef"
        }
        
        # Log family activity with sensitive data
        self.audit_logger.log_family_activity(family_id, activity_type, details)
        
        # Read and verify sensitive data was redacted
        family_log_path = os.path.join(self.test_dir, "family_audit.log")
        with open(family_log_path, 'r') as f:
            log_line = f.readline().strip()
            log_record = json.loads(log_line)
        
        # Check that sensitive fields are redacted
        self.assertEqual(log_record['details']['email'], "***REDACTED***")
        self.assertEqual(log_record['details']['password'], "***REDACTED***")
        self.assertEqual(log_record['details']['phone'], "***REDACTED***")
        self.assertEqual(log_record['details']['api_key'], "***REDACTED***")
        
        # Check that non-sensitive fields are preserved
        self.assertEqual(log_record['details']['device_info'], "iPhone 12")
    
    def test_get_family_logs(self):
        """Test retrieving logs for a specific family"""
        family_id_1 = "test_family_004"
        family_id_2 = "test_family_005"
        
        # Log activities for different families
        self.audit_logger.log_family_activity(family_id_1, "query", {"question": "WiFi security"})
        self.audit_logger.log_family_activity(family_id_2, "query", {"question": "Child safety"})
        self.audit_logger.log_family_activity(family_id_1, "recommendation", {"type": "security_update"})
        
        # Get logs for family_id_1
        family_1_logs = self.audit_logger.get_family_logs(family_id_1)
        
        # Verify correct logs are returned
        self.assertEqual(len(family_1_logs), 2)
        for log in family_1_logs:
            self.assertEqual(log['family_id'], family_id_1)
        
        # Verify activity types
        activity_types = [log['activity_type'] for log in family_1_logs]
        self.assertIn('query', activity_types)
        self.assertIn('recommendation', activity_types)
    
    def test_family_audit_summary(self):
        """Test family audit summary generation"""
        family_id = "test_family_006"
        
        # Log various activities
        self.audit_logger.log_family_activity(family_id, "query", {"question": "Test 1"})
        self.audit_logger.log_family_activity(family_id, "query", {"question": "Test 2"})
        self.audit_logger.log_family_activity(family_id, "recommendation", {"type": "security"})
        self.audit_logger.log_family_security_event(family_id, "threat_detected", {"level": "low"})
        
        # Get summary
        summary = self.audit_logger.get_family_audit_summary(family_id)
        
        # Verify summary statistics
        self.assertEqual(summary['total_family_events'], 4)
        self.assertEqual(summary['activity_types']['query'], 2)
        self.assertEqual(summary['activity_types']['recommendation'], 1)
        self.assertEqual(summary['security_events'], 1)
        self.assertEqual(summary['families_tracked'], 1)
    
    def test_nested_sensitive_data_redaction(self):
        """Test redaction of sensitive data in nested dictionaries"""
        family_id = "test_family_007"
        activity_type = "device_registration"
        details = {
            "device": {
                "name": "Family iPad",
                "owner_email": "parent@example.com",
                "serial": "ABC123456"
            },
            "user": {
                "full_name": "Jane Smith",
                "age": 35,
                "preferences": {
                    "password": "mypassword123"
                }
            }
        }
        
        # Log activity with nested sensitive data
        self.audit_logger.log_family_activity(family_id, activity_type, details)
        
        # Read and verify nested sensitive data was redacted
        family_log_path = os.path.join(self.test_dir, "family_audit.log")
        with open(family_log_path, 'r') as f:
            log_line = f.readline().strip()
            log_record = json.loads(log_line)
        
        # Check nested redaction
        self.assertEqual(log_record['details']['device']['owner_email'], "***REDACTED***")
        self.assertEqual(log_record['details']['user']['full_name'], "***REDACTED***")
        self.assertEqual(log_record['details']['user']['preferences']['password'], "***REDACTED***")
        
        # Check non-sensitive nested fields are preserved
        self.assertEqual(log_record['details']['device']['name'], "Family iPad")
        self.assertEqual(log_record['details']['device']['serial'], "ABC123456")
        self.assertEqual(log_record['details']['user']['age'], 35)
    
    def test_session_id_tracking(self):
        """Test that session IDs are properly tracked"""
        family_id = "test_family_008"
        session_id = "session_abc123"
        
        details_with_session = {
            "question": "How to set parental controls?",
            "session_id": session_id
        }
        
        # Log activity with session ID
        self.audit_logger.log_family_activity(family_id, "query", details_with_session)
        
        # Verify session ID is preserved
        family_log_path = os.path.join(self.test_dir, "family_audit.log")
        with open(family_log_path, 'r') as f:
            log_line = f.readline().strip()
            log_record = json.loads(log_line)
        
        self.assertEqual(log_record['session_id'], session_id)
    
    def test_log_limit_functionality(self):
        """Test that log retrieval respects limit parameter"""
        family_id = "test_family_009"
        
        # Log multiple activities
        for i in range(10):
            self.audit_logger.log_family_activity(
                family_id, 
                "query", 
                {"question": f"Test question {i}"}
            )
        
        # Test different limits
        logs_5 = self.audit_logger.get_family_logs(family_id, limit=5)
        logs_3 = self.audit_logger.get_family_logs(family_id, limit=3)
        
        self.assertEqual(len(logs_5), 5)
        self.assertEqual(len(logs_3), 3)
        
        # Verify we get the most recent logs
        self.assertIn("Test question 9", logs_3[-1]['details']['question'])

if __name__ == '__main__':
    # Run the tests
    unittest.main()