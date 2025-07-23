"""
LAN Scanner Skill for Guardian Interpreter
Scans the local network for active devices and open ports.
Useful for network discovery and security assessment.
"""

import subprocess
import socket
import ipaddress
import threading
from concurrent.futures import ThreadPoolExecutor
import time

def run(*args, **kwargs):
    """
    Scan the local network for active devices.
    
    Args:
        args[0]: Network range (e.g., "192.168.1.0/24") - optional, defaults to auto-detect
        args[1]: Scan type ("ping", "port", "full") - optional, defaults to "ping"
    
    Returns:
        str: Scan results
    """
    # Parse arguments
    network_range = args[0] if args else None
    scan_type = args[1] if len(args) > 1 else "ping"
    
    if not network_range:
        network_range = _detect_local_network()
        if not network_range:
            return "Error: Could not detect local network range"
    
    try:
        network = ipaddress.IPv4Network(network_range, strict=False)
    except ValueError as e:
        return f"Error: Invalid network range '{network_range}': {e}"
    
    print(f"Scanning network: {network_range}")
    print(f"Scan type: {scan_type}")
    print("This may take a moment...")
    
    start_time = time.time()
    
    if scan_type == "ping":
        results = _ping_scan(network)
    elif scan_type == "port":
        results = _port_scan(network)
    elif scan_type == "full":
        results = _full_scan(network)
    else:
        return f"Error: Unknown scan type '{scan_type}'. Use: ping, port, or full"
    
    end_time = time.time()
    scan_duration = end_time - start_time
    
    # Format results
    output = f"LAN Scan Results ({scan_duration:.2f}s)\n"
    output += "=" * 40 + "\n"
    output += f"Network: {network_range}\n"
    output += f"Scan Type: {scan_type}\n"
    output += f"Active Hosts: {len(results)}\n\n"
    
    for host_info in results:
        output += f"Host: {host_info['ip']}\n"
        if 'hostname' in host_info:
            output += f"  Hostname: {host_info['hostname']}\n"
        if 'ports' in host_info:
            output += f"  Open Ports: {', '.join(map(str, host_info['ports']))}\n"
        output += "\n"
    
    return output

def _detect_local_network():
    """Auto-detect the local network range"""
    try:
        # Get default gateway
        result = subprocess.run(['ip', 'route', 'show', 'default'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'default via' in line:
                    parts = line.split()
                    gateway_ip = parts[2]
                    # Assume /24 network
                    network_parts = gateway_ip.split('.')
                    network_parts[-1] = '0'
                    network_base = '.'.join(network_parts)
                    return f"{network_base}/24"
    except Exception:
        pass
    
    # Fallback to common ranges
    return "192.168.1.0/24"

def _ping_scan(network):
    """Perform ping scan to find active hosts"""
    active_hosts = []
    
    def ping_host(ip):
        try:
            result = subprocess.run(['ping', '-c', '1', '-W', '1', str(ip)], 
                                  capture_output=True, timeout=3)
            if result.returncode == 0:
                host_info = {'ip': str(ip)}
                # Try to get hostname
                try:
                    hostname = socket.gethostbyaddr(str(ip))[0]
                    host_info['hostname'] = hostname
                except:
                    pass
                return host_info
        except Exception:
            pass
        return None
    
    # Use threading for faster scanning
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(ping_host, ip) for ip in network.hosts()]
        for future in futures:
            result = future.result()
            if result:
                active_hosts.append(result)
    
    return active_hosts

def _port_scan(network):
    """Perform port scan on common ports"""
    common_ports = [22, 23, 53, 80, 135, 139, 443, 445, 993, 995, 1723, 3389, 5900, 8080]
    active_hosts = []
    
    def scan_host_ports(ip):
        open_ports = []
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((str(ip), port))
                if result == 0:
                    open_ports.append(port)
                sock.close()
            except Exception:
                pass
        
        if open_ports:
            host_info = {'ip': str(ip), 'ports': open_ports}
            # Try to get hostname
            try:
                hostname = socket.gethostbyaddr(str(ip))[0]
                host_info['hostname'] = hostname
            except:
                pass
            return host_info
        return None
    
    # Use threading for faster scanning
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(scan_host_ports, ip) for ip in network.hosts()]
        for future in futures:
            result = future.result()
            if result:
                active_hosts.append(result)
    
    return active_hosts

def _full_scan(network):
    """Perform both ping and port scan"""
    # First do ping scan to find active hosts
    active_hosts = _ping_scan(network)
    
    # Then do port scan on active hosts
    common_ports = [22, 23, 53, 80, 135, 139, 443, 445, 993, 995, 1723, 3389, 5900, 8080]
    
    def scan_ports(host_info):
        ip = host_info['ip']
        open_ports = []
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip, port))
                if result == 0:
                    open_ports.append(port)
                sock.close()
            except Exception:
                pass
        
        if open_ports:
            host_info['ports'] = open_ports
        return host_info
    
    # Add port information to active hosts
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(scan_ports, host) for host in active_hosts]
        enhanced_hosts = [future.result() for future in futures]
    
    return enhanced_hosts

# Skill metadata
__doc__ = "LAN network scanner for device discovery and port scanning"
__version__ = "1.0.0"
__author__ = "Blackbox Matrix"

