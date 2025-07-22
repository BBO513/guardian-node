"""
Network Security Module for Guardian Interpreter
Enhanced network monitoring, blocking, and audit logging.
Ensures privacy-first operation with comprehensive security controls.
"""

import socket
import urllib.parse
import logging
import time
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import threading

class NetworkSecurityManager:
    """
    Manages network security for Guardian Interpreter
    Blocks outbound requests, logs attempts, and provides security monitoring
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger, blocked_logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.blocked_logger = blocked_logger
        self.network_config = config.get('network', {})
        
        # Security state
        self.blocked_attempts = []
        self.allowed_requests = []
        self.security_lock = threading.Lock()
        
        # Initialize security monitoring
        self._setup_security_monitoring()
    
    def _setup_security_monitoring(self):
        """Setup security monitoring and logging"""
        self.logger.info("Network security manager initialized")
        self.logger.info(f"Online mode: {self.network_config.get('ALLOW_ONLINE', False)}")
        
        allowed_domains = self.network_config.get('allowed_domains', [])
        if allowed_domains:
            self.logger.info(f"Allowed domains: {', '.join(allowed_domains)}")
        else:
            self.logger.info("No allowed domains configured")
    
    def is_request_allowed(self, url: str, method: str = "GET") -> bool:
        """
        Check if an outbound request should be allowed
        
        Args:
            url: Target URL
            method: HTTP method
            
        Returns:
            bool: True if request is allowed, False if blocked
        """
        # Check if online mode is enabled
        if not self.network_config.get('ALLOW_ONLINE', False):
            self._log_blocked_request(url, method, "Online mode disabled")
            return False
        
        # Parse URL to check domain
        try:
            parsed_url = urllib.parse.urlparse(url)
            domain = parsed_url.netloc.lower()
            
            # Check allowed domains list
            allowed_domains = self.network_config.get('allowed_domains', [])
            if allowed_domains:
                domain_allowed = any(
                    domain == allowed_domain.lower() or 
                    domain.endswith('.' + allowed_domain.lower())
                    for allowed_domain in allowed_domains
                )
                
                if not domain_allowed:
                    self._log_blocked_request(url, method, f"Domain {domain} not in allowed list")
                    return False
            
            # If we get here, request is allowed
            self._log_allowed_request(url, method)
            return True
            
        except Exception as e:
            self._log_blocked_request(url, method, f"URL parsing error: {e}")
            return False
    
    def _log_blocked_request(self, url: str, method: str, reason: str):
        """Log a blocked network request"""
        with self.security_lock:
            timestamp = time.time()
            blocked_entry = {
                'timestamp': timestamp,
                'url': url,
                'method': method,
                'reason': reason
            }
            
            self.blocked_attempts.append(blocked_entry)
            
            # Keep only recent attempts (last 1000)
            if len(self.blocked_attempts) > 1000:
                self.blocked_attempts = self.blocked_attempts[-1000:]
            
            # Log to both loggers
            log_msg = f"{method} {url} - BLOCKED: {reason}"
            self.blocked_logger.warning(log_msg)
            self.logger.warning(f"BLOCKED REQUEST: {log_msg}")
    
    def _log_allowed_request(self, url: str, method: str):
        """Log an allowed network request"""
        with self.security_lock:
            timestamp = time.time()
            allowed_entry = {
                'timestamp': timestamp,
                'url': url,
                'method': method
            }
            
            self.allowed_requests.append(allowed_entry)
            
            # Keep only recent requests (last 500)
            if len(self.allowed_requests) > 500:
                self.allowed_requests = self.allowed_requests[-500:]
            
            # Log the allowed request
            log_msg = f"{method} {url} - ALLOWED"
            self.logger.info(f"ALLOWED REQUEST: {log_msg}")
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get network security statistics"""
        with self.security_lock:
            return {
                'online_mode': self.network_config.get('ALLOW_ONLINE', False),
                'blocked_attempts': len(self.blocked_attempts),
                'allowed_requests': len(self.allowed_requests),
                'allowed_domains': self.network_config.get('allowed_domains', []),
                'recent_blocked': self.blocked_attempts[-10:] if self.blocked_attempts else [],
                'recent_allowed': self.allowed_requests[-10:] if self.allowed_requests else []
            }
    
    def get_blocked_attempts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent blocked attempts"""
        with self.security_lock:
            return self.blocked_attempts[-limit:] if self.blocked_attempts else []
    
    def get_allowed_requests(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent allowed requests"""
        with self.security_lock:
            return self.allowed_requests[-limit:] if self.allowed_requests else []
    
    def check_network_connectivity(self) -> Dict[str, Any]:
        """Check basic network connectivity without making external requests"""
        results = {
            'local_network': False,
            'gateway_reachable': False,
            'dns_configured': False,
            'interfaces': []
        }
        
        try:
            # Check network interfaces
            import psutil
            interfaces = psutil.net_if_addrs()
            
            for interface, addresses in interfaces.items():
                if interface != 'lo':  # Skip loopback
                    for addr in addresses:
                        if addr.family == socket.AF_INET and not addr.address.startswith('127.'):
                            results['interfaces'].append({
                                'interface': interface,
                                'ip': addr.address,
                                'netmask': addr.netmask
                            })
                            results['local_network'] = True
            
            # Check if we can reach the gateway (without external requests)
            try:
                import subprocess
                result = subprocess.run(['ip', 'route', 'show', 'default'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and 'default via' in result.stdout:
                    results['gateway_reachable'] = True
            except Exception:
                pass
            
            # Check DNS configuration
            try:
                with open('/etc/resolv.conf', 'r') as f:
                    content = f.read()
                    if 'nameserver' in content:
                        results['dns_configured'] = True
            except Exception:
                pass
                
        except Exception as e:
            self.logger.error(f"Network connectivity check failed: {e}")
        
        return results
    
    def enable_online_mode(self, allowed_domains: List[str] = None):
        """
        Enable online mode with optional domain restrictions
        
        Args:
            allowed_domains: List of allowed domains (optional)
        """
        self.network_config['ALLOW_ONLINE'] = True
        
        if allowed_domains:
            self.network_config['allowed_domains'] = allowed_domains
        
        self.logger.warning("ONLINE MODE ENABLED")
        if allowed_domains:
            self.logger.info(f"Allowed domains: {', '.join(allowed_domains)}")
    
    def disable_online_mode(self):
        """Disable online mode (block all outbound requests)"""
        self.network_config['ALLOW_ONLINE'] = False
        self.logger.warning("ONLINE MODE DISABLED - All outbound requests blocked")
    
    def add_allowed_domain(self, domain: str):
        """Add a domain to the allowed list"""
        allowed_domains = self.network_config.get('allowed_domains', [])
        if domain not in allowed_domains:
            allowed_domains.append(domain)
            self.network_config['allowed_domains'] = allowed_domains
            self.logger.info(f"Added allowed domain: {domain}")
    
    def remove_allowed_domain(self, domain: str):
        """Remove a domain from the allowed list"""
        allowed_domains = self.network_config.get('allowed_domains', [])
        if domain in allowed_domains:
            allowed_domains.remove(domain)
            self.network_config['allowed_domains'] = allowed_domains
            self.logger.info(f"Removed allowed domain: {domain}")

class AuditLogger:
    """
    Enhanced audit logging for Guardian Interpreter
    Tracks all user actions, system events, security incidents, and family activities
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.audit_events = []
        self.audit_lock = threading.Lock()
        
        # Family-specific logging
        self.log_dir = config.get('logging', {}).get('log_directory', 'logs')
        os.makedirs(self.log_dir, exist_ok=True)
        self.family_log_file = os.path.join(self.log_dir, "family_audit.log")
        
        # Setup audit logging
        self._setup_audit_logging()
    
    def _setup_audit_logging(self):
        """Setup audit logging system"""
        # Create audit log handler
        audit_handler = logging.FileHandler('logs/audit.log')
        audit_handler.setFormatter(logging.Formatter(
            '%(asctime)s - AUDIT - %(levelname)s - %(message)s'
        ))
        
        self.audit_logger = logging.getLogger('Audit')
        self.audit_logger.addHandler(audit_handler)
        self.audit_logger.setLevel(logging.INFO)
        
        self.log_event('SYSTEM', 'Audit logging initialized')
    
    def log_event(self, category: str, event: str, details: Dict[str, Any] = None):
        """
        Log an audit event
        
        Args:
            category: Event category (USER, SYSTEM, SECURITY, SKILL, LLM)
            event: Event description
            details: Additional event details
        """
        with self.audit_lock:
            timestamp = time.time()
            audit_entry = {
                'timestamp': timestamp,
                'category': category,
                'event': event,
                'details': details or {}
            }
            
            self.audit_events.append(audit_entry)
            
            # Keep only recent events (last 10000)
            if len(self.audit_events) > 10000:
                self.audit_events = self.audit_events[-10000:]
            
            # Log to audit logger
            log_msg = f"[{category}] {event}"
            if details:
                log_msg += f" - Details: {details}"
            
            self.audit_logger.info(log_msg)
    
    def log_user_action(self, action: str, details: Dict[str, Any] = None):
        """Log a user action"""
        self.log_event('USER', action, details)
    
    def log_system_event(self, event: str, details: Dict[str, Any] = None):
        """Log a system event"""
        self.log_event('SYSTEM', event, details)
    
    def log_security_event(self, event: str, details: Dict[str, Any] = None):
        """Log a security event"""
        self.log_event('SECURITY', event, details)
    
    def log_skill_execution(self, skill_name: str, args: List[str], result: str = None):
        """Log skill execution"""
        details = {
            'skill': skill_name,
            'arguments': args,
            'result_length': len(result) if result else 0
        }
        self.log_event('SKILL', f"Executed skill: {skill_name}", details)
    
    def log_llm_interaction(self, prompt: str, response: str = None):
        """Log LLM interaction"""
        details = {
            'prompt_length': len(prompt),
            'response_length': len(response) if response else 0
        }
        self.log_event('LLM', "AI interaction", details)
    
    def get_audit_events(self, category: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent audit events"""
        with self.audit_lock:
            events = self.audit_events
            
            if category:
                events = [e for e in events if e['category'] == category]
            
            return events[-limit:] if events else []
    
    def log_family_activity(self, family_id: str, activity_type: str, details: Dict[str, Any] = None):
        """
        Log family assistant activity with privacy protection
        
        Args:
            family_id: Family identifier
            activity_type: Type of family activity (e.g., 'query', 'recommendation', 'skill_execution')
            details: Activity details (will be redacted for sensitive info)
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            "family_id": family_id,
            "activity_type": activity_type,
            "details": self._redact_sensitive(details or {}),
            "session_id": details.get('session_id') if details else None
        }
        self._write_family_log(record)
        
        # Also log to main audit trail
        self.log_event('FAMILY', f"Family activity: {activity_type}", {
            'family_id': family_id,
            'activity_type': activity_type
        })
    
    def log_family_security_event(self, family_id: str, event_type: str, details: Dict[str, Any] = None):
        """
        Log family-specific security events
        
        Args:
            family_id: Family identifier
            event_type: Type of security event
            details: Event details (will be redacted for sensitive info)
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            "family_id": family_id,
            "security_event_type": event_type,
            "details": self._redact_sensitive(details or {})
        }
        self._write_family_log(record)
        
        # Also log to main audit trail as security event
        self.log_event('SECURITY', f"Family security event: {event_type}", {
            'family_id': family_id,
            'event_type': event_type
        })
    
    def _write_family_log(self, record: Dict[str, Any]):
        """Write record to family-specific audit log"""
        try:
            with open(self.family_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception as e:
            self.logger.error(f"Failed to write family audit log: {e}")
    
    def _redact_sensitive(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove or mask sensitive fields for privacy compliance
        
        Args:
            details: Dictionary that may contain sensitive information
            
        Returns:
            Dictionary with sensitive fields redacted
        """
        if not isinstance(details, dict):
            return details
        
        # List of sensitive field names to redact
        sensitive_fields = {
            "password", "token", "secret", "ssn", "social_security",
            "credit_card", "bank_account", "api_key", "private_key",
            "email", "phone", "address", "full_name", "real_name"
        }
        
        redacted = {}
        for key, value in details.items():
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in sensitive_fields):
                redacted[key] = "***REDACTED***"
            elif isinstance(value, dict):
                redacted[key] = self._redact_sensitive(value)
            else:
                redacted[key] = value
        
        return redacted
    
    def get_family_logs(self, family_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Returns audit logs for a specific family (privacy-respecting)
        
        Args:
            family_id: Family identifier
            limit: Maximum number of logs to return
            
        Returns:
            List of family audit log entries
        """
        logs = []
        if not os.path.exists(self.family_log_file):
            return logs
        
        try:
            with open(self.family_log_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        if record.get("family_id") == family_id:
                            logs.append(record)
                    except json.JSONDecodeError:
                        continue
            
            # Return most recent logs first, limited by the specified limit
            return logs[-limit:] if len(logs) > limit else logs
            
        except Exception as e:
            self.logger.error(f"Failed to read family audit logs: {e}")
            return []
    
    def get_family_audit_summary(self, family_id: str = None) -> Dict[str, Any]:
        """
        Get summary of family audit activities
        
        Args:
            family_id: Optional family ID to filter by
            
        Returns:
            Summary statistics for family audit logs
        """
        if not os.path.exists(self.family_log_file):
            return {
                'total_family_events': 0,
                'activity_types': {},
                'security_events': 0,
                'families_tracked': 0
            }
        
        activity_types = {}
        security_events = 0
        families = set()
        total_events = 0
        
        try:
            with open(self.family_log_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        
                        # Filter by family_id if specified
                        if family_id and record.get("family_id") != family_id:
                            continue
                        
                        total_events += 1
                        families.add(record.get("family_id", "unknown"))
                        
                        # Count activity types
                        activity_type = record.get("activity_type")
                        if activity_type:
                            activity_types[activity_type] = activity_types.get(activity_type, 0) + 1
                        
                        # Count security events
                        if record.get("security_event_type"):
                            security_events += 1
                            
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            self.logger.error(f"Failed to generate family audit summary: {e}")
        
        return {
            'total_family_events': total_events,
            'activity_types': activity_types,
            'security_events': security_events,
            'families_tracked': len(families) if not family_id else 1
        }
    
    def get_audit_summary(self) -> Dict[str, Any]:
        """Get audit summary statistics"""
        with self.audit_lock:
            categories = {}
            for event in self.audit_events:
                cat = event['category']
                categories[cat] = categories.get(cat, 0) + 1
            
            # Include family audit summary
            family_summary = self.get_family_audit_summary()
            
            return {
                'total_events': len(self.audit_events),
                'categories': categories,
                'recent_events': self.audit_events[-10:] if self.audit_events else [],
                'family_audit_summary': family_summary
            }

