"""
Router Checker Skill for Guardian Interpreter
Analyzes router security, configuration, and potential vulnerabilities.
Useful for network security assessment and Guardian Node protection.
"""

import socket
import subprocess
import requests
import re
from urllib.parse import urlparse
import time

def run(*args, **kwargs):
    """
    Check router security and configuration.
    
    Args:
        args[0]: Router IP address - optional, defaults to auto-detect gateway
        args[1]: Check type ("basic", "security", "full") - optional, defaults to "basic"
    
    Returns:
        str: Router analysis results
    """
    router_ip = args[0] if args else None
    check_type = args[1] if len(args) > 1 else "basic"
    
    if not router_ip:
        router_ip = _detect_gateway()
        if not router_ip:
            return "Error: Could not detect router/gateway IP address"
    
    print(f"Checking router: {router_ip}")
    print(f"Check type: {check_type}")
    
    if check_type == "basic":
        results = _basic_check(router_ip)
    elif check_type == "security":
        results = _security_check(router_ip)
    elif check_type == "full":
        results = _full_check(router_ip)
    else:
        return f"Error: Unknown check type '{check_type}'. Use: basic, security, or full"
    
    return results

def _detect_gateway():
    """Auto-detect the default gateway (router) IP"""
    try:
        result = subprocess.run(['ip', 'route', 'show', 'default'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'default via' in line:
                    parts = line.split()
                    return parts[2]
    except Exception:
        pass
    
    # Fallback to common router IPs
    common_gateways = ['192.168.1.1', '192.168.0.1', '10.0.0.1', '172.16.0.1']
    for gateway in common_gateways:
        if _ping_host(gateway):
            return gateway
    
    return None

def _ping_host(ip):
    """Check if host responds to ping"""
    try:
        result = subprocess.run(['ping', '-c', '1', '-W', '1', ip], 
                              capture_output=True, timeout=3)
        return result.returncode == 0
    except Exception:
        return False

def _basic_check(router_ip):
    """Perform basic router connectivity and info check"""
    output = f"Router Basic Check Results\n"
    output += "=" * 30 + "\n"
    output += f"Router IP: {router_ip}\n\n"
    
    # Connectivity test
    if _ping_host(router_ip):
        output += "✓ Router is reachable\n"
    else:
        output += "✗ Router is not reachable\n"
        return output
    
    # Port scan for common router services
    common_ports = [22, 23, 53, 80, 443, 8080, 8443]
    open_ports = []
    
    for port in common_ports:
        if _check_port(router_ip, port):
            open_ports.append(port)
    
    output += f"Open Ports: {', '.join(map(str, open_ports)) if open_ports else 'None detected'}\n"
    
    # Try to identify router type
    router_info = _identify_router(router_ip, open_ports)
    if router_info:
        output += f"Router Type: {router_info}\n"
    
    # DNS check
    dns_working = _check_dns(router_ip)
    output += f"DNS Service: {'Working' if dns_working else 'Not responding'}\n"
    
    return output

def _security_check(router_ip):
    """Perform security-focused router analysis"""
    output = f"Router Security Analysis\n"
    output += "=" * 25 + "\n"
    output += f"Router IP: {router_ip}\n\n"
    
    # Basic connectivity first
    if not _ping_host(router_ip):
        output += "✗ Router is not reachable\n"
        return output
    
    security_issues = []
    
    # Check for insecure services
    insecure_ports = {
        23: "Telnet (unencrypted)",
        80: "HTTP Web Interface (unencrypted)",
        21: "FTP (unencrypted)",
        69: "TFTP (unencrypted)"
    }
    
    output += "Security Assessment:\n"
    for port, description in insecure_ports.items():
        if _check_port(router_ip, port):
            security_issues.append(f"Port {port} open: {description}")
            output += f"⚠️  {description} - Port {port} open\n"
    
    # Check for secure alternatives
    secure_ports = {
        22: "SSH (encrypted)",
        443: "HTTPS Web Interface (encrypted)"
    }
    
    for port, description in secure_ports.items():
        if _check_port(router_ip, port):
            output += f"✓ {description} - Port {port} available\n"
    
    # Check for default credentials (basic attempt)
    if 80 in [p for p in insecure_ports.keys() if _check_port(router_ip, p)]:
        cred_check = _check_default_credentials(router_ip)
        if cred_check:
            security_issues.append("Possible default credentials")
            output += f"⚠️  {cred_check}\n"
    
    # Summary
    output += f"\nSecurity Issues Found: {len(security_issues)}\n"
    if security_issues:
        output += "Recommendations:\n"
        for issue in security_issues:
            output += f"  - Address: {issue}\n"
    else:
        output += "✓ No obvious security issues detected\n"
    
    return output

def _full_check(router_ip):
    """Perform comprehensive router analysis"""
    output = f"Comprehensive Router Analysis\n"
    output += "=" * 32 + "\n\n"
    
    # Combine basic and security checks
    output += _basic_check(router_ip) + "\n\n"
    output += _security_check(router_ip) + "\n\n"
    
    # Additional advanced checks
    output += "Advanced Analysis:\n"
    output += "-" * 18 + "\n"
    
    # Network topology
    topology = _analyze_network_topology(router_ip)
    if topology:
        output += f"Network Topology:\n{topology}\n"
    
    # Performance test
    performance = _test_router_performance(router_ip)
    if performance:
        output += f"Performance:\n{performance}\n"
    
    return output

def _check_port(ip, port, timeout=2):
    """Check if a specific port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def _identify_router(router_ip, open_ports):
    """Try to identify router type/brand"""
    if 80 in open_ports:
        try:
            response = requests.get(f"http://{router_ip}", timeout=5)
            content = response.text.lower()
            
            # Look for common router identifiers
            if 'linksys' in content:
                return "Linksys"
            elif 'netgear' in content:
                return "Netgear"
            elif 'tp-link' in content:
                return "TP-Link"
            elif 'asus' in content:
                return "ASUS"
            elif 'dlink' in content or 'd-link' in content:
                return "D-Link"
            elif 'cisco' in content:
                return "Cisco"
            elif 'ubiquiti' in content:
                return "Ubiquiti"
            
            # Check server header
            server = response.headers.get('Server', '')
            if server:
                return f"Unknown ({server})"
                
        except Exception:
            pass
    
    return "Unknown"

def _check_dns(router_ip):
    """Check if router provides DNS service"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)
        # Send a simple DNS query
        sock.sendto(b'\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07example\x03com\x00\x00\x01\x00\x01', (router_ip, 53))
        data = sock.recv(512)
        sock.close()
        return len(data) > 0
    except Exception:
        return False

def _check_default_credentials(router_ip):
    """Check for common default credentials (basic test)"""
    # This is a very basic check - in practice, this would be more sophisticated
    try:
        response = requests.get(f"http://{router_ip}", timeout=5)
        if response.status_code == 200:
            # Look for login forms or default pages
            content = response.text.lower()
            if 'password' in content and ('admin' in content or 'login' in content):
                return "Web interface accessible - check for default credentials"
    except Exception:
        pass
    return None

def _analyze_network_topology(router_ip):
    """Analyze network topology around the router"""
    try:
        # Get network range
        network_parts = router_ip.split('.')
        network_parts[-1] = '0'
        network_base = '.'.join(network_parts)
        
        # Quick scan for other devices
        active_count = 0
        for i in range(1, 255):
            test_ip = f"{network_base[:-1]}{i}"
            if test_ip != router_ip and _ping_host(test_ip):
                active_count += 1
                if active_count >= 5:  # Limit for performance
                    break
        
        return f"  Network: {network_base}/24\n  Active devices detected: {active_count}+"
    except Exception:
        return None

def _test_router_performance(router_ip):
    """Basic router performance test"""
    try:
        # Ping test for latency
        start_time = time.time()
        if _ping_host(router_ip):
            latency = (time.time() - start_time) * 1000
            return f"  Ping latency: {latency:.1f}ms"
    except Exception:
        pass
    return None

# Skill metadata
__doc__ = "Router security and configuration analysis"
__version__ = "1.0.0"
__author__ = "Blackbox Matrix"

