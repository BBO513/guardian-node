"""
System Information Skill for Guardian Interpreter
Provides detailed information about the system, network interfaces, and Guardian status.
"""

import os
import platform
import subprocess
import socket
import psutil
from datetime import datetime

def run(*args, **kwargs):
    """
    Gather and display system information.
    
    Args:
        args[0]: Info type ("basic", "network", "full") - optional, defaults to "basic"
    
    Returns:
        str: System information report
    """
    info_type = args[0] if args else "basic"
    
    if info_type == "basic":
        return _get_basic_info()
    elif info_type == "network":
        return _get_network_info()
    elif info_type == "full":
        return _get_full_info()
    else:
        return f"Error: Unknown info type '{info_type}'. Use: basic, network, or full"

def _get_basic_info():
    """Get basic system information"""
    info = "Guardian System Information\n"
    info += "=" * 30 + "\n\n"
    
    # System basics
    info += f"Hostname: {socket.gethostname()}\n"
    info += f"Platform: {platform.platform()}\n"
    info += f"Architecture: {platform.architecture()[0]}\n"
    info += f"Processor: {platform.processor()}\n"
    info += f"Python Version: {platform.python_version()}\n"
    
    # System resources
    try:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        info += f"\nSystem Resources:\n"
        info += f"  Memory: {memory.used // (1024**3):.1f}GB / {memory.total // (1024**3):.1f}GB ({memory.percent:.1f}%)\n"
        info += f"  Disk: {disk.used // (1024**3):.1f}GB / {disk.total // (1024**3):.1f}GB ({(disk.used/disk.total)*100:.1f}%)\n"
        info += f"  CPU Usage: {psutil.cpu_percent(interval=1):.1f}%\n"
    except Exception as e:
        info += f"\nResource info unavailable: {e}\n"
    
    # Network basics
    try:
        local_ip = _get_local_ip()
        info += f"\nNetwork:\n"
        info += f"  Local IP: {local_ip}\n"
        info += f"  Internet: {'Connected' if _check_internet() else 'Disconnected'}\n"
    except Exception as e:
        info += f"\nNetwork info unavailable: {e}\n"
    
    return info

def _get_network_info():
    """Get detailed network information"""
    info = "Network Information\n"
    info += "=" * 20 + "\n\n"
    
    # Network interfaces
    try:
        interfaces = psutil.net_if_addrs()
        info += "Network Interfaces:\n"
        for interface, addresses in interfaces.items():
            info += f"\n{interface}:\n"
            for addr in addresses:
                if addr.family == socket.AF_INET:  # IPv4
                    info += f"  IPv4: {addr.address}\n"
                    if addr.netmask:
                        info += f"  Netmask: {addr.netmask}\n"
                elif addr.family == socket.AF_INET6:  # IPv6
                    info += f"  IPv6: {addr.address}\n"
    except Exception as e:
        info += f"Interface info unavailable: {e}\n"
    
    # Network statistics
    try:
        net_stats = psutil.net_io_counters()
        info += f"\nNetwork Statistics:\n"
        info += f"  Bytes Sent: {net_stats.bytes_sent // (1024**2):.1f} MB\n"
        info += f"  Bytes Received: {net_stats.bytes_recv // (1024**2):.1f} MB\n"
        info += f"  Packets Sent: {net_stats.packets_sent}\n"
        info += f"  Packets Received: {net_stats.packets_recv}\n"
    except Exception as e:
        info += f"Network stats unavailable: {e}\n"
    
    # Routing information
    try:
        result = subprocess.run(['ip', 'route'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            info += f"\nRouting Table:\n"
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    info += f"  {line}\n"
    except Exception:
        info += "\nRouting info unavailable\n"
    
    return info

def _get_full_info():
    """Get comprehensive system information"""
    info = "Full System Report\n"
    info += "=" * 20 + "\n\n"
    
    # Combine basic and network info
    info += _get_basic_info() + "\n\n"
    info += _get_network_info() + "\n\n"
    
    # Process information
    try:
        processes = len(psutil.pids())
        info += f"Running Processes: {processes}\n\n"
    except Exception:
        pass
    
    # Boot time
    try:
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        info += f"System Boot Time: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        uptime = datetime.now() - boot_time
        info += f"System Uptime: {uptime.days} days, {uptime.seconds//3600} hours\n\n"
    except Exception:
        pass
    
    # Guardian-specific info
    info += "Guardian Status:\n"
    info += f"  Working Directory: {os.getcwd()}\n"
    info += f"  Process ID: {os.getpid()}\n"
    info += f"  User: {os.getenv('USER', 'unknown')}\n"
    
    return info

def _get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "Unknown"

def _check_internet():
    """Check if internet connection is available"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

# Skill metadata
__doc__ = "System information and status reporting"
__version__ = "1.0.0"
__author__ = "Blackbox Matrix"

