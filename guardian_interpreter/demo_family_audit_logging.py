#!/usr/bin/env python3
"""
Demonstration of enhanced family audit logging functionality
Shows how the AuditLogger tracks family activities with privacy protection
"""

import logging
import os
from network_security import AuditLogger

def demo_family_audit_logging():
    """Demonstrate family audit logging capabilities"""
    
    print("🔍 Family Audit Logging Demonstration")
    print("=" * 50)
    
    # Setup configuration
    config = {
        'logging': {
            'log_directory': 'logs',
            'level': 'INFO'
        }
    }
    
    # Create logger
    logger = logging.getLogger('DemoLogger')
    logger.setLevel(logging.INFO)
    
    # Initialize AuditLogger
    audit_logger = AuditLogger(config, logger)
    
    print("✓ AuditLogger initialized with family features")
    
    # Demo 1: Family Activity Logging
    print("\n📝 Demo 1: Family Activity Logging")
    print("-" * 30)
    
    family_activities = [
        {
            'family_id': 'smith_family_001',
            'activity_type': 'query',
            'details': {
                'question': 'How can I secure my home WiFi network?',
                'user_age_group': 'adult',
                'session_id': 'session_001'
            }
        },
        {
            'family_id': 'smith_family_001',
            'activity_type': 'recommendation',
            'details': {
                'recommendation_type': 'wifi_security',
                'priority': 'high',
                'estimated_time': '15 minutes'
            }
        },
        {
            'family_id': 'johnson_family_002',
            'activity_type': 'skill_execution',
            'details': {
                'skill_name': 'child_education_skill',
                'topic': 'online_safety',
                'child_age': 10
            }
        }
    ]
    
    for activity in family_activities:
        audit_logger.log_family_activity(
            activity['family_id'],
            activity['activity_type'],
            activity['details']
        )
        print(f"  ✓ Logged {activity['activity_type']} for {activity['family_id']}")
    
    # Demo 2: Family Security Event Logging
    print("\n🛡️  Demo 2: Family Security Event Logging")
    print("-" * 30)
    
    security_events = [
        {
            'family_id': 'smith_family_001',
            'event_type': 'threat_detected',
            'details': {
                'threat_type': 'suspicious_network_activity',
                'device': 'family_tablet',
                'severity': 'medium',
                'action_taken': 'blocked_and_notified'
            }
        },
        {
            'family_id': 'johnson_family_002',
            'event_type': 'parental_control_violation',
            'details': {
                'child_device': 'kids_phone',
                'violation_type': 'inappropriate_content_attempt',
                'time_of_day': 'evening',
                'parent_notified': True
            }
        }
    ]
    
    for event in security_events:
        audit_logger.log_family_security_event(
            event['family_id'],
            event['event_type'],
            event['details']
        )
        print(f"  ✓ Logged {event['event_type']} for {event['family_id']}")
    
    # Demo 3: Sensitive Data Redaction
    print("\n🔒 Demo 3: Sensitive Data Redaction")
    print("-" * 30)
    
    sensitive_activity = {
        'family_id': 'demo_family_003',
        'activity_type': 'profile_setup',
        'details': {
            'parent_name': 'John Smith',
            'parent_email': 'john.smith@email.com',
            'password': 'mySecretPassword123',
            'phone': '555-123-4567',
            'address': '123 Main St, Anytown, USA',
            'child_name': 'Emma Smith',
            'child_age': 8,
            'device_serial': 'ABC123456789'
        }
    }
    
    audit_logger.log_family_activity(
        sensitive_activity['family_id'],
        sensitive_activity['activity_type'],
        sensitive_activity['details']
    )
    print("  ✓ Logged activity with sensitive data (automatically redacted)")
    
    # Demo 4: Retrieve Family Logs
    print("\n📊 Demo 4: Retrieve Family Logs")
    print("-" * 30)
    
    # Get logs for Smith family
    smith_logs = audit_logger.get_family_logs('smith_family_001')
    print(f"  ✓ Retrieved {len(smith_logs)} logs for Smith family")
    
    for i, log in enumerate(smith_logs, 1):
        event_type = log.get('activity_type') or log.get('security_event_type', 'unknown')
        print(f"    {i}. {event_type} at {log['timestamp'][:19]}")
    
    # Demo 5: Family Audit Summary
    print("\n📈 Demo 5: Family Audit Summary")
    print("-" * 30)
    
    # Get overall summary
    overall_summary = audit_logger.get_family_audit_summary()
    print(f"  ✓ Total family events: {overall_summary['total_family_events']}")
    print(f"  ✓ Families tracked: {overall_summary['families_tracked']}")
    print(f"  ✓ Security events: {overall_summary['security_events']}")
    
    print("\n  Activity breakdown:")
    for activity_type, count in overall_summary['activity_types'].items():
        print(f"    - {activity_type}: {count}")
    
    # Get Smith family specific summary
    smith_summary = audit_logger.get_family_audit_summary('smith_family_001')
    print(f"\n  ✓ Smith family events: {smith_summary['total_family_events']}")
    
    # Demo 6: Show Log Files
    print("\n📁 Demo 6: Log Files Created")
    print("-" * 30)
    
    log_files = [
        'logs/audit.log',
        'logs/family_audit.log'
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            file_size = os.path.getsize(log_file)
            print(f"  ✓ {log_file} ({file_size} bytes)")
        else:
            print(f"  ✗ {log_file} (not found)")
    
    print("\n🎉 Family Audit Logging Demo Complete!")
    print("\nKey Features Demonstrated:")
    print("• Privacy-preserving family activity logging")
    print("• Automatic sensitive data redaction")
    print("• Family-specific security event tracking")
    print("• Separate audit log for family activities")
    print("• Family-specific log retrieval and summaries")
    print("• Session tracking for user interactions")

if __name__ == '__main__':
    demo_family_audit_logging()