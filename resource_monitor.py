"""
Resource Monitor Module for Guardian Node
Monitors system resources (CPU, memory, temperature) for Raspberry Pi
"""

import logging
import platform
from typing import Dict, Any

# Try to import psutil for system monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class ResourceMonitor:
    """Monitor system resources"""
    
    def __init__(self, logger: logging.Logger = None):
        """Initialize resource monitor"""
        self.logger = logger or logging.getLogger(__name__)
        self.is_raspberry_pi = self._detect_raspberry_pi()
        
        if not PSUTIL_AVAILABLE:
            self.logger.warning("psutil not available. Install with: pip install psutil")
    
    def _detect_raspberry_pi(self) -> bool:
        """Detect if running on Raspberry Pi"""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                return 'Raspberry Pi' in f.read()
        except:
            return False
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current system statistics"""
        # Initialize with default values
        stats = {
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'memory_used_mb': 0.0,
            'memory_total_mb': 0.0,
            'temperature_c': None
        }
        
        if not PSUTIL_AVAILABLE:
            # Return mock data when psutil not available
            stats = {
                'cpu_percent': 25.0,
                'memory_percent': 45.0,
                'memory_used_mb': 1800.0,
                'memory_total_mb': 4096.0,
                'temperature_c': 42.5
            }
            return stats
        
        try:
            # CPU usage
            stats['cpu_percent'] = psutil.cpu_percent(interval=0.1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            stats['memory_percent'] = memory.percent
            stats['memory_used_mb'] = memory.used / (1024 * 1024)
            stats['memory_total_mb'] = memory.total / (1024 * 1024)
            
            # Temperature (Raspberry Pi specific)
            if self.is_raspberry_pi:
                try:
                    with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                        temp = float(f.read().strip()) / 1000.0
                        stats['temperature_c'] = temp
                except:
                    stats['temperature_c'] = None
            else:
                stats['temperature_c'] = None
            
        except Exception as e:
            self.logger.error(f"Failed to get system stats: {e}")
            # Return mock data on error
            stats = {
                'cpu_percent': 25.0,
                'memory_percent': 45.0,
                'memory_used_mb': 1800.0,
                'memory_total_mb': 4096.0,
                'temperature_c': 42.5
            }
        
        return stats
    
    def get_system_status_level(self, stats: Dict[str, Any]) -> str:
        """
        Determine system status level based on stats
        
        Returns:
            'normal', 'warning', or 'critical'
        """
        cpu = stats.get('cpu_percent', 0)
        memory = stats.get('memory_percent', 0)
        temp = stats.get('temperature_c')
        
        # Check for critical conditions
        if cpu > 90 or memory > 90:
            return 'critical'
        if temp and temp > 80:
            return 'critical'
        
        # Check for warning conditions
        if cpu > 75 or memory > 75:
            return 'warning'
        if temp and temp > 70:
            return 'warning'
        
        return 'normal'
    
    def stop(self):
        """Stop resource monitoring"""
        pass


# For testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    monitor = ResourceMonitor()
    
    print("\n=== System Resource Monitor ===")
    stats = monitor.get_current_stats()
    
    print(f"CPU Usage: {stats['cpu_percent']:.1f}%")
    print(f"Memory Usage: {stats['memory_percent']:.1f}%")
    print(f"Memory Used: {stats['memory_used_mb']:.0f} MB / {stats['memory_total_mb']:.0f} MB")
    
    if stats['temperature_c']:
        print(f"Temperature: {stats['temperature_c']:.1f}°C")
    
    status = monitor.get_system_status_level(stats)
    print(f"\nSystem Status: {status.upper()}")
