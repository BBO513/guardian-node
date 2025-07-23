"""
IoT Device Security Protocol Module
Detects and analyzes IoT devices on the network for security vulnerabilities
"""

import socket
import subprocess
import re
import json
import time
import threading
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import concurrent.futures

def get_metadata() -> Dict[str, Any]:
    """Get module metadata"""
    return {
        'name': 'IoT Device Security Analyzer',
        'description': 'Detects and analyzes IoT devices on the network for security vulnerabilities',
        'version': '1.0.0',
        'author': 'Guardian Team',
        'family_friendly': True,
        'supported_protocols': ['http', 'https', 'upnp', 'mdns', 'snmp']
    }

def analyze(target: str = None, **kwargs) -> Dict[str, Any]:
    """
    Analyze IoT devices on the network
    
    Args:
        target: Specific network range to scan (e.g., "192.168.1.0/24")
        **kwargs: Additional parameters
            - scan_ports: List of ports to scan (default: common IoT ports)
            - timeout: Scan timeout in seconds (default: 30)
            - max_threads: Maximum concurrent threads (default: 20)
            - deep_scan: Perform detailed device analysis (default: False)
    
    Returns:
        Analysis results with findings and recommendations
    """
    findings = []
    recommendations = []
    technical_details = {}
    
    try:
        # Determine network range to scan
        if not target:
            target = _detect_local_network()
            if not target:
                return {
                    'status': 'error',
                    'findings': [],
                    'recommendations': ['Unable to detect local network range. Please specify network range manually.'],
                    'technical_details': {'error': 'Network detection failed'}
                }
        
        technical_details['scan_target'] = target
        scan_timeout = kwargs.get('timeout', 30)
        max_threads = kwargs.get('max_threads', 20)
        deep_scan = kwargs.get('deep_scan', False)
        
        # Define IoT-specific ports to scan
        iot_ports = kwargs.get('scan_ports', [
            80, 443,      # Web interfaces
            8080, 8443,   # Alternative web ports
            1900,         # UPnP
            5353,         # mDNS/Bonjour
            161, 162,     # SNMP
            554,          # RTSP (cameras)
            8554,         # Alternative RTSP
            23,           # Telnet (insecure)
            22,           # SSH
            21,           # FTP (insecure)
            1883, 8883,   # MQTT
            5683,         # CoAP
            502,          # Modbus
            47808,        # BACnet
            10001,        # Ubiquiti devices
        ])
        
        # Scan for devices
        print(f"Scanning network {target} for IoT devices...")
        devices = _scan_network_for_devices(target, iot_ports, scan_timeout, max_threads)
        
        if not devices:
            findings.append({
                'severity': 'info',
                'title': 'IoT Device Scan Complete',
                'description': 'No IoT devices detected on the network',
                'recommendation': 'This is good for security! If you have IoT devices, ensure they are properly configured.',
                'technical_info': {'devices_found': 0}
            })
        else:
            # Analyze each detected device
            for device in devices:
                device_findings = _analyze_iot_device(device, deep_scan)
                findings.extend(device_findings)
            
            # Add summary finding
            findings.append({
                'severity': 'info',
                'title': 'IoT Devices Detected',
                'description': f'Found {len(devices)} potential IoT devices on the network',
                'recommendation': 'Review each device for security best practices',
                'technical_info': {
                    'devices_count': len(devices),
                    'device_ips': [d['ip'] for d in devices]
                }
            })
        
        # Generate recommendations based on findings
        recommendations = _generate_iot_recommendations(findings, devices)
        
        # Determine overall status
        status = _determine_iot_status(findings)
        
        technical_details.update({
            'scan_parameters': {
                'target_network': target,
                'ports_scanned': iot_ports,
                'timeout': scan_timeout,
                'max_threads': max_threads,
                'deep_scan': deep_scan
            },
            'devices_found': len(devices),
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
            'recommendations': [f'IoT device analysis failed: {str(e)}'],
            'technical_details': {'error': str(e)}
        }

def _detect_local_network() -> Optional[str]:
    """Detect the local network range"""
    try:
        # Get local IP and subnet
        result = subprocess.run(['ipconfig'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            ip_address = None
            subnet_mask = None
            
            for line in lines:
                if 'IPv4 Address' in line:
                    ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if ip_match:
                        ip_address = ip_match.group(1)
                elif 'Subnet Mask' in line:
                    mask_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if mask_match:
                        subnet_mask = mask_match.group(1)
            
            if ip_address and subnet_mask:
                # Calculate network range
                network_range = _calculate_network_range(ip_address, subnet_mask)
                return network_range
        
        # Fallback to common network ranges
        common_ranges = ['192.168.1.0/24', '192.168.0.0/24', '10.0.0.0/24']
        for range_addr in common_ranges:
            # Test if we can reach the gateway
            gateway_ip = range_addr.split('/')[0][:-1] + '1'  # e.g., 192.168.1.1
            if _is_host_reachable(gateway_ip):
                return range_addr
        
        return None
        
    except Exception:
        return None

def _calculate_network_range(ip: str, subnet_mask: str) -> str:
    """Calculate network range from IP and subnet mask"""
    try:
        ip_parts = [int(x) for x in ip.split('.')]
        mask_parts = [int(x) for x in subnet_mask.split('.')]
        
        # Calculate network address
        network_parts = [ip_parts[i] & mask_parts[i] for i in range(4)]
        network_addr = '.'.join(map(str, network_parts))
        
        # Calculate CIDR notation
        cidr = sum(bin(x).count('1') for x in mask_parts)
        
        return f"{network_addr}/{cidr}"
        
    except Exception:
        return "192.168.1.0/24"  # Default fallback

def _scan_network_for_devices(network_range: str, ports: List[int], timeout: int, max_threads: int) -> List[Dict[str, Any]]:
    """Scan network range for devices with IoT-specific ports"""
    devices = []
    
    try:
        # Parse network range
        if '/' in network_range:
            base_ip, cidr = network_range.split('/')
            cidr = int(cidr)
        else:
            base_ip = network_range
            cidr = 24
        
        # Generate IP addresses to scan
        base_parts = base_ip.split('.')
        if cidr == 24:
            # Scan /24 network (most common)
            ip_base = '.'.join(base_parts[:3])
            ip_addresses = [f"{ip_base}.{i}" for i in range(1, 255)]
        else:
            # For other CIDR ranges, scan a reasonable subset
            ip_base = '.'.join(base_parts[:3])
            ip_addresses = [f"{ip_base}.{i}" for i in range(1, 50)]
        
        # Scan devices with threading
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            future_to_ip = {
                executor.submit(_scan_single_device, ip, ports, timeout): ip 
                for ip in ip_addresses
            }
            
            for future in concurrent.futures.as_completed(future_to_ip, timeout=timeout):
                ip = future_to_ip[future]
                try:
                    device_info = future.result()
                    if device_info:
                        devices.append(device_info)
                except Exception:
                    continue  # Skip failed scans
    
    except Exception as e:
        print(f"Network scan error: {e}")
    
    return devices

def _scan_single_device(ip: str, ports: List[int], timeout: int) -> Optional[Dict[str, Any]]:
    """Scan a single device for IoT-specific ports"""
    try:
        open_ports = []
        device_info = {'ip': ip, 'open_ports': [], 'services': {}}
        
        # Quick ping test first
        if not _is_host_reachable(ip, timeout=2):
            return None
        
        # Scan specific ports
        for port in ports:
            if _is_port_open(ip, port, timeout=2):
                open_ports.append(port)
                
                # Try to identify service
                service_info = _identify_service(ip, port)
                if service_info:
                    device_info['services'][port] = service_info
        
        if open_ports:
            device_info['open_ports'] = open_ports
            device_info['device_type'] = _classify_device_type(open_ports, device_info['services'])
            return device_info
        
        return None
        
    except Exception:
        return None

def _is_host_reachable(ip: str, timeout: int = 3) -> bool:
    """Check if host is reachable"""
    try:
        result = subprocess.run(['ping', '-n', '1', '-w', str(timeout * 1000), ip], 
                              capture_output=True, text=True, timeout=timeout + 2)
        return result.returncode == 0
    except Exception:
        return False

def _is_port_open(ip: str, port: int, timeout: int = 3) -> bool:
    """Check if a specific port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def _identify_service(ip: str, port: int) -> Optional[Dict[str, Any]]:
    """Try to identify the service running on a port"""
    try:
        service_info = {'port': port, 'protocol': 'unknown'}
        
        # Common IoT service identification
        if port in [80, 8080]:
            service_info['protocol'] = 'http'
            service_info['description'] = 'Web interface'
        elif port in [443, 8443]:
            service_info['protocol'] = 'https'
            service_info['description'] = 'Secure web interface'
        elif port == 1900:
            service_info['protocol'] = 'upnp'
            service_info['description'] = 'UPnP service'
        elif port == 5353:
            service_info['protocol'] = 'mdns'
            service_info['description'] = 'mDNS/Bonjour'
        elif port in [161, 162]:
            service_info['protocol'] = 'snmp'
            service_info['description'] = 'SNMP management'
        elif port in [554, 8554]:
            service_info['protocol'] = 'rtsp'
            service_info['description'] = 'Video streaming (camera)'
        elif port == 23:
            service_info['protocol'] = 'telnet'
            service_info['description'] = 'Telnet (insecure)'
        elif port == 22:
            service_info['protocol'] = 'ssh'
            service_info['description'] = 'SSH'
        elif port in [1883, 8883]:
            service_info['protocol'] = 'mqtt'
            service_info['description'] = 'MQTT messaging'
        
        return service_info
        
    except Exception:
        return None

def _classify_device_type(open_ports: List[int], services: Dict[int, Dict]) -> str:
    """Classify device type based on open ports and services"""
    
    # Camera indicators
    if 554 in open_ports or 8554 in open_ports:
        return 'IP Camera'
    
    # Router/Gateway indicators
    if 1900 in open_ports and (80 in open_ports or 443 in open_ports):
        return 'Router/Gateway'
    
    # Smart home hub indicators
    if 1883 in open_ports or 8883 in open_ports:
        return 'Smart Home Hub'
    
    # Network device with SNMP
    if 161 in open_ports:
        return 'Network Device'
    
    # Web-enabled device
    if 80 in open_ports or 443 in open_ports:
        return 'Web-enabled IoT Device'
    
    # Generic IoT device
    if len(open_ports) > 0:
        return 'IoT Device'
    
    return 'Unknown Device'

def _analyze_iot_device(device: Dict[str, Any], deep_scan: bool = False) -> List[Dict[str, Any]]:
    """Analyze a single IoT device for security issues"""
    findings = []
    
    try:
        ip = device['ip']
        open_ports = device.get('open_ports', [])
        services = device.get('services', {})
        device_type = device.get('device_type', 'Unknown Device')
        
        # Check for insecure protocols
        insecure_ports = [21, 23]  # FTP, Telnet
        for port in insecure_ports:
            if port in open_ports:
                protocol_name = 'FTP' if port == 21 else 'Telnet'
                findings.append({
                    'severity': 'high',
                    'title': f'Insecure Protocol: {protocol_name}',
                    'description': f'{device_type} at {ip} is using insecure {protocol_name} protocol',
                    'recommendation': f'Disable {protocol_name} and use secure alternatives like SFTP or SSH',
                    'technical_info': {
                        'device_ip': ip,
                        'device_type': device_type,
                        'insecure_port': port,
                        'protocol': protocol_name
                    }
                })
        
        # Check for default web interfaces
        web_ports = [80, 443, 8080, 8443]
        for port in web_ports:
            if port in open_ports:
                findings.append({
                    'severity': 'medium',
                    'title': f'Web Interface Detected',
                    'description': f'{device_type} at {ip} has a web interface on port {port}',
                    'recommendation': 'Ensure the web interface uses strong passwords and is updated regularly',
                    'technical_info': {
                        'device_ip': ip,
                        'device_type': device_type,
                        'web_port': port
                    }
                })
        
        # Check for UPnP (potential security risk)
        if 1900 in open_ports:
            findings.append({
                'severity': 'medium',
                'title': 'UPnP Service Active',
                'description': f'{device_type} at {ip} has UPnP service running',
                'recommendation': 'Consider disabling UPnP if not needed, as it can pose security risks',
                'technical_info': {
                    'device_ip': ip,
                    'device_type': device_type,
                    'service': 'UPnP'
                }
            })
        
        # Check for SNMP (management protocol)
        if 161 in open_ports:
            findings.append({
                'severity': 'medium',
                'title': 'SNMP Management Active',
                'description': f'{device_type} at {ip} has SNMP management enabled',
                'recommendation': 'Ensure SNMP uses strong community strings and consider SNMPv3',
                'technical_info': {
                    'device_ip': ip,
                    'device_type': device_type,
                    'service': 'SNMP'
                }
            })
        
        # Device-specific recommendations
        if device_type == 'IP Camera':
            findings.append({
                'severity': 'info',
                'title': 'IP Camera Security',
                'description': f'IP Camera detected at {ip}',
                'recommendation': 'Change default passwords, enable encryption, and regularly update firmware',
                'technical_info': {
                    'device_ip': ip,
                    'device_type': device_type,
                    'security_focus': 'camera_security'
                }
            })
        
        # General IoT device finding
        findings.append({
            'severity': 'info',
            'title': f'IoT Device: {device_type}',
            'description': f'Detected {device_type} at {ip} with {len(open_ports)} open ports',
            'recommendation': 'Ensure this device is properly secured and regularly updated',
            'technical_info': {
                'device_ip': ip,
                'device_type': device_type,
                'open_ports': open_ports,
                'services': services
            }
        })
    
    except Exception as e:
        findings.append({
            'severity': 'low',
            'title': 'Device Analysis Error',
            'description': f'Unable to fully analyze device: {str(e)}',
            'recommendation': 'Manually review this device for security best practices',
            'technical_info': {'error': str(e), 'device': device}
        })
    
    return findings

def _generate_iot_recommendations(findings: List[Dict[str, Any]], devices: List[Dict[str, Any]]) -> List[str]:
    """Generate IoT security recommendations"""
    recommendations = []
    
    # Extract specific recommendations from findings
    for finding in findings:
        if 'recommendation' in finding:
            recommendations.append(finding['recommendation'])
    
    # Add general IoT security recommendations
    general_recommendations = [
        'Change all default passwords on IoT devices',
        'Regularly update IoT device firmware',
        'Use a separate network (VLAN) for IoT devices',
        'Disable unnecessary services and ports on IoT devices',
        'Monitor IoT device network traffic for anomalies',
        'Use strong, unique passwords for each IoT device',
        'Enable encryption on IoT devices when available',
        'Regularly audit connected IoT devices',
        'Consider using a firewall to restrict IoT device access',
        'Keep an inventory of all IoT devices on your network'
    ]
    
    # Add general recommendations that aren't already covered
    for rec in general_recommendations:
        if not any(rec.lower() in existing.lower() for existing in recommendations):
            recommendations.append(rec)
    
    return recommendations[:15]  # Limit to top 15 recommendations

def _determine_iot_status(findings: List[Dict[str, Any]]) -> str:
    """Determine overall IoT security status"""
    if not findings:
        return 'secure'
    
    # Count findings by severity
    critical_count = 0
    high_count = 0
    medium_count = 0
    
    for finding in findings:
        severity = finding.get('severity', 'info').lower()
        if severity == 'critical':
            critical_count += 1
        elif severity == 'high':
            high_count += 1
        elif severity == 'medium':
            medium_count += 1
    
    # Determine status based on severity counts
    if critical_count > 0 or high_count >= 2:
        return 'critical'
    elif high_count > 0 or medium_count >= 3:
        return 'warning'
    elif medium_count > 0:
        return 'warning'
    
    return 'secure'