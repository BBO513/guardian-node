#!/usr/bin/env python3
"""
Guardian Node Health Check Script
Monitors the health and status of Guardian Node services
"""

import json
import sys
import os
import time
import socket
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

class GuardianHealthChecker:
    """Health checker for Guardian Node services"""
    
    def __init__(self):
        self.health_file = "/app/health_status.json"
        self.log_file = "/logs/guardian.log"
        self.config_file = "/app/guardian_interpreter/config.yaml"
        self.data_dir = "/data"
        self.models_dir = "/app/models"
        
    def check_health_status_file(self):
        """Check if health status file exists and is recent"""
        try:
            if not os.path.exists(self.health_file):
                return False, "Health status file not found"
            
            with open(self.health_file, 'r') as f:
                status = json.load(f)
            
            # Check if status is running
            if status.get('status') != 'running':
                return False, f"Service status: {status.get('status', 'unknown')}"
            
            # Check if timestamp is recent (within last 5 minutes)
            timestamp_str = status.get('timestamp')
            if timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                if datetime.now().replace(tzinfo=timestamp.tzinfo) - timestamp > timedelta(minutes=5):
                    return False, "Health status is stale"
            
            return True, "Health status OK"
            
        except Exception as e:
            return False, f"Error reading health status: {e}"
    
    def check_process_running(self):
        """Check if Guardian Node process is running"""
        try:
            # Check for Python processes running Guardian Node
            result = subprocess.run(
                ['pgrep', '-f', 'guardian_interpreter'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                return True, f"Guardian processes running: {', '.join(pids)}"
            else:
                return False, "No Guardian processes found"
                
        except Exception as e:
            return False, f"Error checking processes: {e}"
    
    def check_log_file(self):
        """Check if log file exists and has recent entries"""
        try:
            if not os.path.exists(self.log_file):
                return False, "Log file not found"
            
            # Check if log file has been written to recently
            stat = os.stat(self.log_file)
            last_modified = datetime.fromtimestamp(stat.st_mtime)
            
            if datetime.now() - last_modified > timedelta(minutes=10):
                return False, "Log file not recently updated"
            
            # Check log file size (should not be empty)
            if stat.st_size == 0:
                return False, "Log file is empty"
            
            return True, f"Log file OK (size: {stat.st_size} bytes)"
            
        except Exception as e:
            return False, f"Error checking log file: {e}"
    
    def check_configuration(self):
        """Check if configuration file exists and is valid"""
        try:
            if not os.path.exists(self.config_file):
                return False, "Configuration file not found"
            
            # Try to parse YAML configuration
            import yaml
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # Check for required sections
            required_sections = ['system', 'family_assistant', 'logging']
            for section in required_sections:
                if section not in config:
                    return False, f"Missing configuration section: {section}"
            
            return True, "Configuration OK"
            
        except ImportError:
            return True, "Configuration check skipped (PyYAML not available)"
        except Exception as e:
            return False, f"Error checking configuration: {e}"
    
    def check_data_directory(self):
        """Check if data directory is accessible"""
        try:
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir, exist_ok=True)
            
            # Test write access
            test_file = os.path.join(self.data_dir, '.health_check')
            with open(test_file, 'w') as f:
                f.write(str(time.time()))
            
            os.remove(test_file)
            return True, "Data directory accessible"
            
        except Exception as e:
            return False, f"Error accessing data directory: {e}"
    
    def check_network_ports(self):
        """Check if required network ports are available"""
        ports_to_check = [8080, 8443]
        open_ports = []
        
        for port in ports_to_check:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(1)
                    result = sock.connect_ex(('localhost', port))
                    if result == 0:
                        open_ports.append(port)
            except Exception:
                pass
        
        if open_ports:
            return True, f"Ports accessible: {open_ports}"
        else:
            return False, "No network ports accessible"
    
    def check_disk_space(self):
        """Check available disk space"""
        try:
            import shutil
            
            # Check available space in data directory
            total, used, free = shutil.disk_usage(self.data_dir)
            free_gb = free // (1024**3)
            
            if free_gb < 1:  # Less than 1GB free
                return False, f"Low disk space: {free_gb}GB free"
            
            return True, f"Disk space OK: {free_gb}GB free"
            
        except Exception as e:
            return False, f"Error checking disk space: {e}"
    
    def check_memory_usage(self):
        """Check memory usage"""
        try:
            # Read memory info from /proc/meminfo
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
            
            # Parse memory information
            mem_total = None
            mem_available = None
            
            for line in meminfo.split('\n'):
                if line.startswith('MemTotal:'):
                    mem_total = int(line.split()[1]) * 1024  # Convert KB to bytes
                elif line.startswith('MemAvailable:'):
                    mem_available = int(line.split()[1]) * 1024  # Convert KB to bytes
            
            if mem_total and mem_available:
                mem_used_percent = ((mem_total - mem_available) / mem_total) * 100
                
                if mem_used_percent > 90:  # More than 90% memory used
                    return False, f"High memory usage: {mem_used_percent:.1f}%"
                
                return True, f"Memory usage OK: {mem_used_percent:.1f}%"
            
            return True, "Memory check completed"
            
        except Exception as e:
            return True, f"Memory check skipped: {e}"
    
    def run_comprehensive_check(self):
        """Run all health checks"""
        checks = [
            ("Health Status File", self.check_health_status_file),
            ("Process Running", self.check_process_running),
            ("Log File", self.check_log_file),
            ("Configuration", self.check_configuration),
            ("Data Directory", self.check_data_directory),
            ("Network Ports", self.check_network_ports),
            ("Disk Space", self.check_disk_space),
            ("Memory Usage", self.check_memory_usage),
        ]
        
        results = []
        all_passed = True
        
        print("🏥 Guardian Node Health Check")
        print("=" * 40)
        
        for check_name, check_func in checks:
            try:
                passed, message = check_func()
                status_icon = "✅" if passed else "❌"
                print(f"{status_icon} {check_name}: {message}")
                
                results.append({
                    'check': check_name,
                    'passed': passed,
                    'message': message
                })
                
                if not passed:
                    all_passed = False
                    
            except Exception as e:
                print(f"❌ {check_name}: Error - {e}")
                results.append({
                    'check': check_name,
                    'passed': False,
                    'message': f"Error - {e}"
                })
                all_passed = False
        
        print("=" * 40)
        
        # Summary
        passed_checks = sum(1 for r in results if r['passed'])
        total_checks = len(results)
        
        print(f"📊 Health Check Summary: {passed_checks}/{total_checks} checks passed")
        
        if all_passed:
            print("🟢 Guardian Node is healthy")
            return 0
        else:
            print("🔴 Guardian Node has health issues")
            return 1
    
    def run_quick_check(self):
        """Run quick health check for Docker health check"""
        # Quick checks for container health
        quick_checks = [
            self.check_health_status_file,
            self.check_process_running,
        ]
        
        for check_func in quick_checks:
            try:
                passed, message = check_func()
                if not passed:
                    print(f"Health check failed: {message}")
                    return 1
            except Exception as e:
                print(f"Health check error: {e}")
                return 1
        
        return 0

def main():
    """Main health check function"""
    checker = GuardianHealthChecker()
    
    # Determine check type based on arguments
    if len(sys.argv) > 1 and sys.argv[1] == '--comprehensive':
        exit_code = checker.run_comprehensive_check()
    else:
        # Quick check for Docker health check
        exit_code = checker.run_quick_check()
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()