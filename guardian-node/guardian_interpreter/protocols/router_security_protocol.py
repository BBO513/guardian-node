"""
Router Security Analysis Protocol Module
Analyzes router security configuration and provides family-friendly recommendations
"""

import socket
import subprocess
import re
import requests
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

def get_metadata() -> Dict[str, Any]:
    """Get module metadata"""
    return {
        'name': 'Router Security Analyzer',
        'description': 'Analyzes home router security settings and configuration',
        'version': '1.0.0',
        'author': 'Guardian Team',
        'family_friendly': True,
        'supported_protocols': ['http', 'https', 'snmp', 'upnp']
    }

def analyze(target: str = None, **kwargs) -> Dict[str, Any]:
    """
    Analyze router security configuration
    
    Args:
        target: Router IP address (optional, will auto-detect if not provided)
        **kwargs: Additional parameters
            - check_firmware: Check for firmware updates (default: True)
            - check_passwords: Check for default passwords (default: True)
            - check_encryption: Check WiFi encryption (default: True)
            - check_ports: Check for open ports (default: True)
    
    Returns:
        Analysis results with findings and recommendations
    """
    findings = []
    recommendations = []
    technical_details = {}
    
    try:
        # Auto-detect router IP if not provided
        if not target:
            target = _detect_router_ip()
            if not target:
                return {
                    'status': 'error',
                    'findings': [],
                    'recommendations': ['Unable to detect router IP address. Please specify the router IP manually.'],
                    'technical_details': {'error': 'Router IP detection failed'}
                }
        
        technical_details['router_ip'] = target
        
        # Check if router is reachable
        if not _is_router_reachable(target):
            return {
                'status': 'error',
                'findings': [],
                'recommendations': [f'Unable to reach router at {target}. Please check the IP address and network connection.'],
                'technical_details': {'error': f'Router {target} not reachable'}
            }
        
        # Perform security checks
        if kwargs.get('check_passwords', True):
            password_findings = _check_default_passwords(target)
            findings.extend(password_findings)
        
        if kwargs.get('check_encryption', True):
            encryption_findings = _check_wifi_encryption(target)
            findings.extend(encryption_findings)
        
        if kwargs.get('check_ports', True):
            port_findings = _check_open_ports(target)
            findings.extend(port_findings)
        
        if kwargs.get('check_firmware', True):
            firmware_findings = _check_firmware_info(target)
            findings.extend(firmware_findings)
        
        # Check for UPnP vulnerabilities
        upnp_findings = _check_upnp_security(target)
        findings.extend(upnp_findings)
        
        # Generate recommendations based on findings
        recommendations = _generate_router_recommendations(findings)
        
        # Determine overall status
        status = _determine_router_status(findings)
        
        technical_details.update({
            'checks_performed': {
                'default_passwords': kwargs.get('check_passwords', True),
                'wifi_encryption': kwargs.get('check_encryption', True),
                'open_ports': kwargs.get('check_ports', True),
                'firmware_check': kwargs.get('check_firmware', True),
                'upnp_check': True
            },
            'analysis_timestamp': datetime.now().isoformat()
        })
        
        return {
            'status': status,
            'findings': findings,
            'recommendations': recommendations,
            'technical_details': technical_details
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'findings': [],
            'recommendations': [f'Router security analysis failed: {str(e)}'],
            'technical_details': {'error': str(e)}
        }

def _detect_router_ip() -> Optional[str]:
    """Detect the default gateway (router) IP address"""
    try:
        # Try to get default gateway on Windows
        result = subprocess.run(['ipconfig'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Default Gateway' in line:
                    # Extract IP address
                    ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if ip_match:
                        return ip_match.group(1)
        
        # Try alternative method using route command
        result = subprocess.run(['route', 'print', '0.0.0.0'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if '0.0.0.0' in line and 'Gateway' not in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        gateway = parts[2]
                        if re.match(r'\d+\.\d+\.\d+\.\d+', gateway):
                            return gateway
        
        # Fallback to common router IPs
        common_ips = ['192.168.1.1', '192.168.0.1', '10.0.0.1', '192.168.1.254']
        for ip in common_ips:
            if _is_router_reachable(ip):
                return ip
        
        return None
        
    except Exception:
        return None

def _is_router_reachable(ip: str) -> bool:
    """Check if router is reachable"""
    try:
        # Try to connect to common router ports
        for port in [80, 443, 8080]:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((ip, port))
            sock.close()
            if result == 0:
                return True
        
        # Try ping as fallback
        result = subprocess.run(['ping', '-n', '1', '-w', '3000', ip], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
        
    except Exception:
        return False

def _check_default_passwords(router_ip: str) -> List[Dict[str, Any]]:
    """Check for default or weak passwords"""
    findings = []
    
    try:
        # Common default credentials for routers
        default_creds = [
            ('admin', 'admin'),
            ('admin', 'password'),
            ('admin', ''),
            ('root', 'admin'),
            ('admin', '1234'),
            ('user', 'user')
        ]
        
        # Try to access router web interface
        for username, password in default_creds:
            try:
                # Try HTTP first
                url = f'http://{router_ip}'
                response = requests.get(url, auth=(username, password), timeout=5)
                
                if response.status_code == 200:
                    findings.append({
                        'severity': 'critical',
                        'title': 'Default Router Credentials',
                        'description': f'Router is using default credentials ({username}/{password or "blank"})',
                        'recommendation': 'Change the router admin password immediately to a strong, unique password',
                        'technical_info': {
                            'url': url,
                            'credentials': f'{username}/{password or "blank"}',
                            'status_code': response.status_code
                        }
                    })
                    break  # Found working credentials, no need to try others
                    
            except requests.exceptions.RequestException:
                continue  # Try next credential pair
        
        # If no default credentials found, it's a good sign
        if not findings:
            findings.append({
                'severity': 'info',
                'title': 'Router Password Security',
                'description': 'Router does not appear to be using common default passwords',
                'recommendation': 'Continue using strong, unique passwords for router access',
                'technical_info': {'default_creds_check': 'passed'}
            })
    
    except Exception as e:
        findings.append({
            'severity': 'low',
            'title': 'Password Check Error',
            'description': f'Unable to check for default passwords: {str(e)}',
            'recommendation': 'Manually verify that your router is not using default passwords',
            'technical_info': {'error': str(e)}
        })
    
    return findings

def _check_wifi_encryption(router_ip: str) -> List[Dict[str, Any]]:
    """Check WiFi encryption settings"""
    findings = []
    
    try:
        # Try to get WiFi information from router
        # This is a simplified check - in practice, this would require
        # router-specific API calls or SNMP queries
        
        # For now, we'll provide general WiFi security guidance
        findings.append({
            'severity': 'info',
            'title': 'WiFi Security Check',
            'description': 'WiFi encryption check requires manual verification',
            'recommendation': 'Ensure your WiFi network uses WPA3 or WPA2 encryption, not WEP or open security',
            'technical_info': {'check_type': 'manual_verification_required'}
        })
        
    except Exception as e:
        findings.append({
            'severity': 'low',
            'title': 'WiFi Encryption Check Error',
            'description': f'Unable to automatically check WiFi encryption: {str(e)}',
            'recommendation': 'Manually check your WiFi settings to ensure WPA3 or WPA2 encryption is enabled',
            'technical_info': {'error': str(e)}
        })
    
    return findings

def _check_open_ports(router_ip: str) -> List[Dict[str, Any]]:
    """Check for unnecessarily open ports"""
    findings = []
    
    try:
        # Common router ports to check
        common_ports = {
            21: 'FTP',
            22: 'SSH',
            23: 'Telnet',
            53: 'DNS',
            80: 'HTTP',
            443: 'HTTPS',
            161: 'SNMP',
            1900: 'UPnP',
            8080: 'HTTP Alt',
            8443: 'HTTPS Alt'
        }
        
        open_ports = []
        potentially_risky_ports = [21, 22, 23, 161]  # FTP, SSH, Telnet, SNMP
        
        for port, service in common_ports.items():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((router_ip, port))
            sock.close()
            
            if result == 0:
                open_ports.append((port, service))
                
                if port in potentially_risky_ports:
                    findings.append({
                        'severity': 'medium',
                        'title': f'Potentially Risky Service: {service}',
                        'description': f'Port {port} ({service}) is open and may pose security risks',
                        'recommendation': f'Consider disabling {service} if not needed, or ensure it uses strong authentication',
                        'technical_info': {'port': port, 'service': service}
                    })
        
        if open_ports:
            port_list = ', '.join([f'{port} ({service})' for port, service in open_ports])
            findings.append({
                'severity': 'info',
                'title': 'Open Router Ports',
                'description': f'Found open ports: {port_list}',
                'recommendation': 'Review open ports and close any that are not needed',
                'technical_info': {'open_ports': open_ports}
            })
        
    except Exception as e:
        findings.append({
            'severity': 'low',
            'title': 'Port Scan Error',
            'description': f'Unable to check open ports: {str(e)}',
            'recommendation': 'Manually review router port settings and close unnecessary ports',
            'technical_info': {'error': str(e)}
        })
    
    return findings

def _check_firmware_info(router_ip: str) -> List[Dict[str, Any]]:
    """Check firmware information"""
    findings = []
    
    try:
        # Try to get router information
        # This would typically require router-specific API calls
        
        findings.append({
            'severity': 'info',
            'title': 'Firmware Update Check',
            'description': 'Firmware version check requires manual verification',
            'recommendation': 'Regularly check for and install router firmware updates from the manufacturer',
            'technical_info': {'check_type': 'manual_verification_required'}
        })
        
    except Exception as e:
        findings.append({
            'severity': 'low',
            'title': 'Firmware Check Error',
            'description': f'Unable to check firmware information: {str(e)}',
            'recommendation': 'Manually check your router admin panel for firmware update options',
            'technical_info': {'error': str(e)}
        })
    
    return findings

def _check_upnp_security(router_ip: str) -> List[Dict[str, Any]]:
    """Check UPnP security settings"""
    findings = []
    
    try:
        # Check if UPnP port is open
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((router_ip, 1900))
        sock.close()
        
        if result == 0:
            findings.append({
                'severity': 'medium',
                'title': 'UPnP Service Detected',
                'description': 'UPnP service is running on the router',
                'recommendation': 'Consider disabling UPnP if not needed, as it can pose security risks',
                'technical_info': {'upnp_port': 1900, 'status': 'open'}
            })
        else:
            findings.append({
                'severity': 'info',
                'title': 'UPnP Security',
                'description': 'UPnP service does not appear to be accessible externally',
                'recommendation': 'Good! Keep UPnP disabled unless specifically needed',
                'technical_info': {'upnp_port': 1900, 'status': 'closed'}
            })
            
    except Exception as e:
        findings.append({
            'severity': 'low',
            'title': 'UPnP Check Error',
            'description': f'Unable to check UPnP status: {str(e)}',
            'recommendation': 'Manually check router settings to ensure UPnP is disabled if not needed',
            'technical_info': {'error': str(e)}
        })
    
    return findings

def _generate_router_recommendations(findings: List[Dict[str, Any]]) -> List[str]:
    """Generate actionable recommendations based on findings"""
    recommendations = []
    
    # Extract recommendations from findings
    for finding in findings:
        if 'recommendation' in finding:
            recommendations.append(finding['recommendation'])
    
    # Add general router security recommendations
    general_recommendations = [
        'Change default router admin username and password',
        'Enable WPA3 or WPA2 encryption for WiFi networks',
        'Regularly update router firmware',
        'Disable WPS (WiFi Protected Setup) if not needed',
        'Use strong, unique WiFi network passwords',
        'Disable remote management unless necessary',
        'Review and close unnecessary open ports',
        'Consider setting up a guest network for visitors'
    ]
    
    # Add general recommendations that aren't already covered
    for rec in general_recommendations:
        if not any(rec.lower() in existing.lower() for existing in recommendations):
            recommendations.append(rec)
    
    return recommendations[:10]  # Limit to top 10 recommendations

def _determine_router_status(findings: List[Dict[str, Any]]) -> str:
    """Determine overall router security status"""
    if not findings:
        return 'secure'
    
    # Check for critical findings
    for finding in findings:
        severity = finding.get('severity', 'info').lower()
        if severity == 'critical':
            return 'critical'
    
    # Check for high/medium severity findings
    medium_high_count = 0
    for finding in findings:
        severity = finding.get('severity', 'info').lower()
        if severity in ['high', 'medium']:
            medium_high_count += 1
    
    if medium_high_count >= 3:
        return 'critical'
    elif medium_high_count >= 1:
        return 'warning'
    
    return 'secure'