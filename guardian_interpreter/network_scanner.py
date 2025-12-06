# Network Scanner Module for Guardian Node
# Provides network visibility, device discovery, and security scanning capabilities
# Uses Nmap for comprehensive network analysis

import os
import sys
import logging
import json
import subprocess
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

try:
    import nmap
    NMAP_AVAILABLE = True
except ImportError:
    NMAP_AVAILABLE = False
    nmap = None

try:
    from scapy.all import ARP, Ether, srp, conf
    SCAPY_AVAILABLE = True
    # Disable scapy warnings
    conf.verb = 0
except ImportError:
    SCAPY_AVAILABLE = False


class NetworkScanner:
    """
    Network scanning and security assessment for Guardian Node
    Provides device discovery, port scanning, and vulnerability detection
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger('guardian.network_scanner')
        self.nm = None
        self.scan_results = []
        
        # Initialize Nmap if available
        if NMAP_AVAILABLE:
            try:
                self.nm = nmap.PortScanner()
                self.logger.info("Nmap scanner initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize Nmap: {e}")
                self.nm = None
        else:
            self.logger.warning("python-nmap not available. Install with: pip install python-nmap")
    
    def is_available(self) -> bool:
        """Check if network scanning is available"""
        return NMAP_AVAILABLE and self.nm is not None
    
    def check_nmap_binary(self) -> bool:
        """Check if Nmap binary is installed on the system"""
        try:
            result = subprocess.run(['nmap', '--version'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            if result.returncode == 0:
                self.logger.info(f"Nmap binary found: {result.stdout.split()[2]}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            self.logger.error(f"Nmap binary not found: {e}")
        return False
    
    def discover_local_network(self, network_range: str = "192.168.1.0/24") -> List[Dict[str, Any]]:
        """
        Discover devices on the local network using ARP scan
        
        Args:
            network_range: Network range to scan (CIDR notation)
        
        Returns:
            List of discovered devices with IP and MAC addresses
        """
        devices = []
        
        # Try Scapy first (faster for simple discovery)
        if SCAPY_AVAILABLE:
            try:
                self.logger.info(f"Scanning network: {network_range} (using Scapy)")
                arp = ARP(pdst=network_range)
                ether = Ether(dst="ff:ff:ff:ff:ff:ff")
                packet = ether/arp
                
                result = srp(packet, timeout=3, verbose=0)[0]
                
                for sent, received in result:
                    devices.append({
                        'ip': received.psrc,
                        'mac': received.hwsrc,
                        'status': 'up',
                        'method': 'scapy_arp',
                        'timestamp': datetime.now().isoformat()
                    })
                
                self.logger.info(f"Discovered {len(devices)} devices using Scapy")
                return devices
                
            except Exception as e:
                self.logger.error(f"Scapy scan failed: {e}")
        
        # Fallback to Nmap
        if self.is_available():
            try:
                self.logger.info(f"Scanning network: {network_range} (using Nmap)")
                self.nm.scan(hosts=network_range, arguments='-sn')  # Ping scan
                
                for host in self.nm.all_hosts():
                    if self.nm[host].state() == 'up':
                        mac = self.nm[host]['addresses'].get('mac', 'Unknown')
                        vendor = self.nm[host].get('vendor', {}).get(mac, 'Unknown')
                        
                        devices.append({
                            'ip': host,
                            'mac': mac,
                            'vendor': vendor,
                            'status': 'up',
                            'method': 'nmap_ping',
                            'timestamp': datetime.now().isoformat()
                        })
                
                self.logger.info(f"Discovered {len(devices)} devices using Nmap")
                return devices
                
            except Exception as e:
                self.logger.error(f"Nmap scan failed: {e}")
        
        self.logger.warning("No scanning method available")
        return devices
    
    def scan_host_ports(self, host: str, port_range: str = "1-1000") -> Dict[str, Any]:
        """
        Scan ports on a specific host
        
        Args:
            host: IP address or hostname to scan
            port_range: Port range to scan (e.g., "1-1000" or "22,80,443")
        
        Returns:
            Dictionary with scan results
        """
        if not self.is_available():
            return {
                'error': 'Nmap not available',
                'host': host,
                'status': 'unavailable'
            }
        
        try:
            self.logger.info(f"Scanning ports on {host}: {port_range}")
            self.nm.scan(host, port_range, arguments='-sV')  # Service version detection
            
            if host not in self.nm.all_hosts():
                return {
                    'host': host,
                    'status': 'down',
                    'timestamp': datetime.now().isoformat()
                }
            
            host_info = self.nm[host]
            open_ports = []
            
            for proto in host_info.all_protocols():
                ports = host_info[proto].keys()
                for port in ports:
                    port_info = host_info[proto][port]
                    if port_info['state'] == 'open':
                        open_ports.append({
                            'port': port,
                            'protocol': proto,
                            'state': port_info['state'],
                            'service': port_info.get('name', 'unknown'),
                            'version': port_info.get('version', 'unknown'),
                            'product': port_info.get('product', 'unknown')
                        })
            
            result = {
                'host': host,
                'status': host_info.state(),
                'hostname': host_info.hostname(),
                'open_ports': open_ports,
                'total_open_ports': len(open_ports),
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Found {len(open_ports)} open ports on {host}")
            return result
            
        except Exception as e:
            self.logger.error(f"Port scan failed for {host}: {e}")
            return {
                'error': str(e),
                'host': host,
                'status': 'error'
            }
    
    def vulnerability_scan(self, host: str, scan_type: str = "basic") -> Dict[str, Any]:
        """
        Perform vulnerability scanning using Nmap NSE scripts
        
        Args:
            host: IP address or hostname to scan
            scan_type: Type of scan ("basic", "vuln", "full")
        
        Returns:
            Dictionary with vulnerability scan results
        """
        if not self.is_available():
            return {
                'error': 'Nmap not available',
                'host': host,
                'status': 'unavailable'
            }
        
        # Define NSE script arguments based on scan type
        nse_scripts = {
            'basic': 'default,safe',
            'vuln': 'vuln',
            'full': 'vuln,exploit,auth'
        }
        
        script_arg = nse_scripts.get(scan_type, 'default')
        
        try:
            self.logger.info(f"Running vulnerability scan on {host} (type: {scan_type})")
            self.nm.scan(host, arguments=f'-sV --script={script_arg}')
            
            if host not in self.nm.all_hosts():
                return {
                    'host': host,
                    'status': 'down',
                    'timestamp': datetime.now().isoformat()
                }
            
            host_info = self.nm[host]
            vulnerabilities = []
            
            # Extract script results
            for proto in host_info.all_protocols():
                ports = host_info[proto].keys()
                for port in ports:
                    port_info = host_info[proto][port]
                    if 'script' in port_info:
                        for script_name, script_output in port_info['script'].items():
                            vulnerabilities.append({
                                'port': port,
                                'protocol': proto,
                                'script': script_name,
                                'output': script_output,
                                'severity': self._assess_severity(script_name, script_output)
                            })
            
            result = {
                'host': host,
                'status': host_info.state(),
                'scan_type': scan_type,
                'vulnerabilities': vulnerabilities,
                'total_findings': len(vulnerabilities),
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Found {len(vulnerabilities)} potential issues on {host}")
            return result
            
        except Exception as e:
            self.logger.error(f"Vulnerability scan failed for {host}: {e}")
            return {
                'error': str(e),
                'host': host,
                'status': 'error'
            }
    
    def _assess_severity(self, script_name: str, output: str) -> str:
        """Assess severity of vulnerability based on script name and output"""
        output_lower = output.lower()
        
        # High severity indicators
        if any(keyword in output_lower for keyword in ['critical', 'exploit', 'vulnerable', 'cve-']):
            return 'high'
        
        # Medium severity indicators
        if any(keyword in output_lower for keyword in ['warning', 'weak', 'outdated', 'deprecated']):
            return 'medium'
        
        # Low severity or informational
        return 'low'
    
    def quick_network_assessment(self, network_range: str = "192.168.1.0/24") -> Dict[str, Any]:
        """
        Perform a quick network security assessment
        
        Args:
            network_range: Network range to assess
        
        Returns:
            Comprehensive assessment report
        """
        self.logger.info(f"Starting quick network assessment: {network_range}")
        
        # Discover devices
        devices = self.discover_local_network(network_range)
        
        # Assess each device (limited scan for speed)
        device_assessments = []
        for device in devices[:10]:  # Limit to first 10 devices
            ip = device['ip']
            self.logger.info(f"Assessing device: {ip}")
            
            # Quick port scan (common ports only)
            port_scan = self.scan_host_ports(ip, "22,80,443,445,3389,8080")
            
            device_assessments.append({
                'device': device,
                'port_scan': port_scan,
                'risk_level': self._assess_device_risk(port_scan)
            })
        
        # Generate summary
        summary = {
            'network_range': network_range,
            'total_devices': len(devices),
            'assessed_devices': len(device_assessments),
            'devices': device_assessments,
            'timestamp': datetime.now().isoformat(),
            'recommendations': self._generate_recommendations(device_assessments)
        }
        
        self.logger.info(f"Assessment complete: {len(devices)} devices found")
        return summary
    
    def _assess_device_risk(self, port_scan: Dict[str, Any]) -> str:
        """Assess risk level of a device based on open ports"""
        if 'error' in port_scan or port_scan.get('status') != 'up':
            return 'unknown'
        
        open_ports = port_scan.get('open_ports', [])
        
        # High risk ports
        high_risk_ports = [23, 445, 3389, 5900]  # Telnet, SMB, RDP, VNC
        if any(p['port'] in high_risk_ports for p in open_ports):
            return 'high'
        
        # Medium risk: many open ports
        if len(open_ports) > 5:
            return 'medium'
        
        # Low risk: few common ports
        return 'low'
    
    def _generate_recommendations(self, assessments: List[Dict[str, Any]]) -> List[str]:
        """Generate security recommendations based on assessment"""
        recommendations = []
        
        high_risk_count = sum(1 for a in assessments if a.get('risk_level') == 'high')
        if high_risk_count > 0:
            recommendations.append(
                f"⚠️ {high_risk_count} high-risk device(s) detected. "
                "Review open ports and disable unnecessary services."
            )
        
        # Check for common vulnerabilities
        for assessment in assessments:
            open_ports = assessment.get('port_scan', {}).get('open_ports', [])
            for port_info in open_ports:
                if port_info['port'] == 23:
                    recommendations.append(
                        f"🔒 Telnet (port 23) detected on {assessment['device']['ip']}. "
                        "Use SSH instead for secure remote access."
                    )
                if port_info['port'] == 445:
                    recommendations.append(
                        f"🔒 SMB (port 445) detected on {assessment['device']['ip']}. "
                        "Ensure SMB is properly secured and updated."
                    )
        
        if not recommendations:
            recommendations.append("✅ No immediate security concerns detected.")
        
        return recommendations
    
    def export_results(self, results: Dict[str, Any], output_file: str = "scan_results.json"):
        """Export scan results to JSON file"""
        try:
            output_path = Path("data/scans") / output_file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            self.logger.info(f"Results exported to {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Failed to export results: {e}")
            return None
    
    def get_scan_summary(self, results: Dict[str, Any]) -> str:
        """Generate human-readable summary of scan results"""
        if 'error' in results:
            return f"❌ Scan failed: {results['error']}"
        
        if 'total_devices' in results:
            # Network assessment summary
            summary = f"📊 Network Assessment Summary\n"
            summary += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            summary += f"Network: {results['network_range']}\n"
            summary += f"Devices Found: {results['total_devices']}\n"
            summary += f"Assessed: {results['assessed_devices']}\n\n"
            
            # Risk breakdown
            risk_counts = {'high': 0, 'medium': 0, 'low': 0, 'unknown': 0}
            for device in results.get('devices', []):
                risk = device.get('risk_level', 'unknown')
                risk_counts[risk] += 1
            
            summary += f"Risk Levels:\n"
            summary += f"  🔴 High: {risk_counts['high']}\n"
            summary += f"  🟡 Medium: {risk_counts['medium']}\n"
            summary += f"  🟢 Low: {risk_counts['low']}\n\n"
            
            # Recommendations
            summary += f"Recommendations:\n"
            for rec in results.get('recommendations', []):
                summary += f"  {rec}\n"
            
            return summary
        
        elif 'open_ports' in results:
            # Port scan summary
            summary = f"📊 Port Scan Summary\n"
            summary += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            summary += f"Host: {results['host']}\n"
            summary += f"Status: {results['status']}\n"
            summary += f"Open Ports: {results['total_open_ports']}\n\n"
            
            if results['total_open_ports'] > 0:
                summary += f"Services:\n"
                for port in results['open_ports']:
                    summary += f"  {port['port']}/{port['protocol']}: {port['service']}\n"
            
            return summary
        
        return "📊 Scan completed. Check detailed results."


class MockNetworkScanner:
    """Mock scanner for when Nmap is not available"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger('guardian.network_scanner')
        self.logger.warning("Using MockNetworkScanner - install nmap and python-nmap for real scanning")
    
    def is_available(self) -> bool:
        return False
    
    def check_nmap_binary(self) -> bool:
        return False
    
    def discover_local_network(self, network_range: str = "192.168.1.0/24") -> List[Dict[str, Any]]:
        return [{
            'ip': '192.168.1.1',
            'mac': '00:00:00:00:00:00',
            'status': 'up',
            'method': 'mock',
            'note': 'Install nmap for real scanning'
        }]
    
    def scan_host_ports(self, host: str, port_range: str = "1-1000") -> Dict[str, Any]:
        return {
            'host': host,
            'status': 'mock',
            'note': 'Install nmap for real scanning'
        }
    
    def vulnerability_scan(self, host: str, scan_type: str = "basic") -> Dict[str, Any]:
        return {
            'host': host,
            'status': 'mock',
            'note': 'Install nmap for real scanning'
        }
    
    def quick_network_assessment(self, network_range: str = "192.168.1.0/24") -> Dict[str, Any]:
        return {
            'network_range': network_range,
            'status': 'mock',
            'note': 'Install nmap and python-nmap for real scanning',
            'recommendations': ['Install nmap: apt-get install nmap', 'Install python-nmap: pip install python-nmap']
        }
    
    def export_results(self, results: Dict[str, Any], output_file: str = "scan_results.json"):
        return None
    
    def get_scan_summary(self, results: Dict[str, Any]) -> str:
        return "⚠️ Mock scanner active. Install nmap and python-nmap for real network scanning."


def create_network_scanner(logger: Optional[logging.Logger] = None) -> NetworkScanner:
    """Factory function to create appropriate scanner implementation"""
    if NMAP_AVAILABLE:
        scanner = NetworkScanner(logger)
        if scanner.check_nmap_binary():
            return scanner
    
    return MockNetworkScanner(logger)
