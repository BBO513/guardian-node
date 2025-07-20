"""
Log Tamper Protection Module for Guardian Node
Provides tamper detection and protection for audit logs
"""

import hashlib
import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import threading

logger = logging.getLogger(__name__)

class LogTamperProtector:
    """
    Provides tamper protection for audit logs using hash chains
    """
    
    def __init__(self, log_dir: str = "/logs"):
        """
        Initialize LogTamperProtector
        
        Args:
            log_dir: Directory containing log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        logger.info(f"LogTamperProtector initialized for directory: {log_dir}")
    
    def append_audit_log(self, log_file: str, entry: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Append entry to audit log with tamper protection
        
        Args:
            log_file: Log file name (relative to log_dir)
            entry: Log entry to append
            metadata: Optional metadata for the entry
            
        Returns:
            True if successful
        """
        with self._lock:
            try:
                log_path = self.log_dir / log_file
                
                # Ensure log file directory exists
                log_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Create structured log entry
                timestamp = datetime.utcnow().isoformat() + 'Z'
                structured_entry = {
                    'timestamp': timestamp,
                    'entry': entry,
                    'metadata': metadata or {}
                }
                
                # Append to log file
                with open(log_path, "a", encoding='utf-8') as f:
                    f.write(json.dumps(structured_entry, separators=(',', ':')) + "\n")
                
                # Update hash chain
                self._update_hash_chain(log_path)
                
                logger.debug(f"Appended entry to {log_file}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to append to audit log {log_file}: {e}")
                return False
    
    def _update_hash_chain(self, log_file: Path) -> None:
        """
        Update hash chain for log file
        
        Args:
            log_file: Path to log file
        """
        try:
            hashchain_file = Path(str(log_file) + ".hashchain")
            
            # Calculate hash of entire log file
            with open(log_file, "rb") as f:
                content = f.read()
            
            current_hash = hashlib.sha256(content).hexdigest()
            
            # Get previous hash from chain
            previous_hash = ""
            if hashchain_file.exists():
                with open(hashchain_file, "r") as f:
                    lines = f.read().strip().split('\n')
                    if lines and lines[-1]:
                        try:
                            last_entry = json.loads(lines[-1])
                            previous_hash = last_entry.get('hash', '')
                        except:
                            # Fallback for simple hash format
                            previous_hash = lines[-1]
            
            # Create chain entry
            chain_entry = {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'hash': current_hash,
                'previous_hash': previous_hash,
                'file_size': len(content),
                'entry_count': content.count(b'\n')
            }
            
            # Append to hash chain
            with open(hashchain_file, "a") as f:
                f.write(json.dumps(chain_entry, separators=(',', ':')) + "\n")
            
            # Set restrictive permissions
            os.chmod(hashchain_file, 0o600)
            
        except Exception as e:
            logger.error(f"Failed to update hash chain for {log_file}: {e}")
            raise
    
    def verify_hash_chain(self, log_file: str) -> Dict[str, Any]:
        """
        Verify integrity of log file using hash chain
        
        Args:
            log_file: Log file name (relative to log_dir)
            
        Returns:
            Dictionary with verification results
        """
        try:
            log_path = self.log_dir / log_file
            hashchain_path = Path(str(log_path) + ".hashchain")
            
            result = {
                'file': log_file,
                'verified': False,
                'error': None,
                'details': {}
            }
            
            if not log_path.exists():
                result['error'] = "Log file does not exist"
                return result
            
            if not hashchain_path.exists():
                result['error'] = "Hash chain file does not exist"
                return result
            
            # Calculate current hash of log file
            with open(log_path, "rb") as f:
                content = f.read()
            
            calculated_hash = hashlib.sha256(content).hexdigest()
            
            # Read hash chain
            with open(hashchain_path, "r") as f:
                chain_lines = f.read().strip().split('\n')
            
            if not chain_lines or not chain_lines[-1]:
                result['error'] = "Empty hash chain"
                return result
            
            # Parse last chain entry
            try:
                last_entry = json.loads(chain_lines[-1])
                stored_hash = last_entry['hash']
            except:
                # Fallback for simple hash format
                stored_hash = chain_lines[-1]
            
            # Verify hash matches
            if calculated_hash == stored_hash:
                result['verified'] = True
                result['details'] = {
                    'calculated_hash': calculated_hash,
                    'stored_hash': stored_hash,
                    'file_size': len(content),
                    'chain_entries': len(chain_lines)
                }
            else:
                result['error'] = "Hash mismatch - possible tampering detected"
                result['details'] = {
                    'calculated_hash': calculated_hash,
                    'stored_hash': stored_hash,
                    'file_size': len(content)
                }
            
            logger.debug(f"Verified hash chain for {log_file}: {result['verified']}")
            return result
            
        except Exception as e:
            logger.error(f"Hash chain verification failed for {log_file}: {e}")
            return {
                'file': log_file,
                'verified': False,
                'error': str(e),
                'details': {}
            }
    
    def verify_all_logs(self) -> Dict[str, Any]:
        """
        Verify all log files in the log directory
        
        Returns:
            Dictionary with verification results for all logs
        """
        results = {
            'overall_status': 'verified',
            'verified_count': 0,
            'failed_count': 0,
            'files': {}
        }
        
        try:
            # Find all log files
            log_files = []
            for file_path in self.log_dir.rglob("*.log"):
                relative_path = file_path.relative_to(self.log_dir)
                log_files.append(str(relative_path))
            
            # Verify each log file
            for log_file in log_files:
                verification_result = self.verify_hash_chain(log_file)
                results['files'][log_file] = verification_result
                
                if verification_result['verified']:
                    results['verified_count'] += 1
                else:
                    results['failed_count'] += 1
                    results['overall_status'] = 'failed'
            
            logger.info(f"Verified {results['verified_count']} logs, {results['failed_count']} failed")
            return results
            
        except Exception as e:
            logger.error(f"Failed to verify all logs: {e}")
            results['overall_status'] = 'error'
            results['error'] = str(e)
            return results
    
    def get_log_integrity_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive log integrity report
        
        Returns:
            Detailed integrity report
        """
        try:
            verification_results = self.verify_all_logs()
            
            report = {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'log_directory': str(self.log_dir),
                'overall_status': verification_results['overall_status'],
                'summary': {
                    'total_files': len(verification_results['files']),
                    'verified_files': verification_results['verified_count'],
                    'failed_files': verification_results['failed_count']
                },
                'files': verification_results['files'],
                'recommendations': []
            }
            
            # Add recommendations based on results
            if verification_results['failed_count'] > 0:
                report['recommendations'].append(
                    "CRITICAL: Log tampering detected. Investigate immediately."
                )
                report['recommendations'].append(
                    "Review system access logs and security measures."
                )
            
            if verification_results['verified_count'] == 0:
                report['recommendations'].append(
                    "No verified logs found. Check log tamper protection setup."
                )
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate integrity report: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'error': str(e),
                'status': 'error'
            }
    
    def create_log_backup(self, backup_dir: str) -> Dict[str, Any]:
        """
        Create tamper-protected backup of all logs
        
        Args:
            backup_dir: Directory to store backup
            
        Returns:
            Backup operation results
        """
        try:
            backup_path = Path(backup_dir)
            backup_path.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            backup_name = f"logs_backup_{timestamp}"
            backup_full_path = backup_path / backup_name
            backup_full_path.mkdir(exist_ok=True)
            
            # Copy all log files and hash chains
            import shutil
            copied_files = []
            
            for file_path in self.log_dir.rglob("*"):
                if file_path.is_file():
                    relative_path = file_path.relative_to(self.log_dir)
                    dest_path = backup_full_path / relative_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, dest_path)
                    copied_files.append(str(relative_path))
            
            # Create backup manifest
            manifest = {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'source_directory': str(self.log_dir),
                'backup_directory': str(backup_full_path),
                'files_copied': copied_files,
                'integrity_report': self.get_log_integrity_report()
            }
            
            with open(backup_full_path / "backup_manifest.json", "w") as f:
                json.dump(manifest, f, indent=2)
            
            logger.info(f"Created log backup: {backup_full_path}")
            return {
                'success': True,
                'backup_path': str(backup_full_path),
                'files_copied': len(copied_files),
                'manifest': manifest
            }
            
        except Exception as e:
            logger.error(f"Failed to create log backup: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cleanup_old_chains(self, days_to_keep: int = 30) -> int:
        """
        Clean up old hash chain entries (keep recent ones)
        
        Args:
            days_to_keep: Number of days of chain entries to keep
            
        Returns:
            Number of entries cleaned up
        """
        try:
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            cleaned_count = 0
            
            # Find all hash chain files
            for chain_file in self.log_dir.rglob("*.hashchain"):
                try:
                    with open(chain_file, "r") as f:
                        lines = f.readlines()
                    
                    # Filter lines to keep recent entries
                    kept_lines = []
                    for line in lines:
                        try:
                            entry = json.loads(line.strip())
                            entry_date = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                            if entry_date >= cutoff_date:
                                kept_lines.append(line)
                            else:
                                cleaned_count += 1
                        except:
                            # Keep malformed entries to avoid breaking chain
                            kept_lines.append(line)
                    
                    # Write back filtered entries
                    if len(kept_lines) < len(lines):
                        with open(chain_file, "w") as f:
                            f.writelines(kept_lines)
                
                except Exception as e:
                    logger.warning(f"Failed to clean chain file {chain_file}: {e}")
            
            logger.info(f"Cleaned up {cleaned_count} old hash chain entries")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old chains: {e}")
            return 0


class AuditLogger:
    """
    Enhanced audit logger with tamper protection
    """
    
    def __init__(self, log_dir: str = "/logs/audit"):
        """
        Initialize AuditLogger
        
        Args:
            log_dir: Directory for audit logs
        """
        self.log_dir = Path(log_dir)
        self.tamper_protector = LogTamperProtector(str(self.log_dir.parent))
        logger.info(f"AuditLogger initialized: {log_dir}")
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], 
                          severity: str = "info") -> bool:
        """
        Log security event with tamper protection
        
        Args:
            event_type: Type of security event
            details: Event details
            severity: Event severity (info, warning, error, critical)
            
        Returns:
            True if logged successfully
        """
        try:
            log_entry = {
                'event_type': event_type,
                'severity': severity,
                'details': details,
                'source': 'guardian_node_security'
            }
            
            log_file = f"audit/security_{datetime.utcnow().strftime('%Y%m')}.log"
            return self.tamper_protector.append_audit_log(
                log_file, 
                json.dumps(log_entry, separators=(',', ':')),
                {'category': 'security', 'severity': severity}
            )
            
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
            return False
    
    def log_family_activity(self, activity_type: str, family_id: str, 
                           details: Dict[str, Any]) -> bool:
        """
        Log family activity with privacy protection
        
        Args:
            activity_type: Type of family activity
            family_id: Family identifier (hashed for privacy)
            details: Activity details (sanitized)
            
        Returns:
            True if logged successfully
        """
        try:
            # Hash family ID for privacy
            family_hash = hashlib.sha256(family_id.encode()).hexdigest()[:16]
            
            log_entry = {
                'activity_type': activity_type,
                'family_hash': family_hash,
                'details': details,
                'source': 'guardian_node_family'
            }
            
            log_file = f"audit/family_{datetime.utcnow().strftime('%Y%m')}.log"
            return self.tamper_protector.append_audit_log(
                log_file,
                json.dumps(log_entry, separators=(',', ':')),
                {'category': 'family_activity'}
            )
            
        except Exception as e:
            logger.error(f"Failed to log family activity: {e}")
            return False
    
    def verify_audit_integrity(self) -> Dict[str, Any]:
        """
        Verify integrity of all audit logs
        
        Returns:
            Verification results
        """
        return self.tamper_protector.verify_all_logs()
    
    def get_audit_report(self, days: int = 7) -> Dict[str, Any]:
        """
        Generate audit report for specified period
        
        Args:
            days: Number of days to include in report
            
        Returns:
            Audit report
        """
        try:
            integrity_report = self.verify_audit_integrity()
            
            report = {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'period_days': days,
                'integrity_status': integrity_report['overall_status'],
                'log_files': list(integrity_report['files'].keys()),
                'summary': {
                    'total_log_files': len(integrity_report['files']),
                    'verified_files': integrity_report['verified_count'],
                    'failed_files': integrity_report['failed_count']
                }
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate audit report: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'error': str(e)
            }