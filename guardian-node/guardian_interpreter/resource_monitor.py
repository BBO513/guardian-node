"""
Production-grade Raspberry Pi Resource and Thermal Monitor Module
Provides continuous monitoring of CPU, memory, disk usage, and temperature
with automatic throttling and GUI integration for Guardian Node
"""

import psutil
import threading
import time
import os
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime

class ResourceMonitor:
    """
    Production-grade resource and thermal monitoring for Raspberry Pi
    Provides continuous monitoring with automatic throttling and alerts
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.monitoring = False
        self.monitor_thread = None
        self.stats_history = []
        self.max_history = 100  # Keep last 100 readings
        
        # Default thresholds
        self.cpu_threshold = 90
        self.memory_threshold = 90
        self.temp_threshold = 75
        self.disk_threshold = 90
        
        # Callbacks
        self.log_callback = None
        self.gui_update_callback = None
        self.throttle_callback = None
        
    def get_temp(self) -> Optional[float]:
        """
        Get CPU temperature from Raspberry Pi thermal zone
        Returns temperature in Celsius or None if unavailable
        """
        try:
            # Primary method for Raspberry Pi
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                return int(f.read()) / 1000.0
        except Exception:
            try:
                # Alternative method using vcgencmd (if available)
                import subprocess
                result = subprocess.run(['vcgencmd', 'measure_temp'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    temp_str = result.stdout.strip()
                    # Extract temperature from "temp=XX.X'C" format
                    temp_value = temp_str.split('=')[1].split("'")[0]
                    return float(temp_value)
            except Exception:
                pass
            
            try:
                # Fallback for other systems
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        if entries:
                            return entries[0].current
            except Exception:
                pass
                
        return None
    
    def get_resource_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system resource status
        Returns dictionary with CPU, memory, disk usage and temperature
        """
        try:
            # Get CPU usage (1 second interval for accuracy)
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Get memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)
            
            # Get disk usage for root partition
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_free_gb = disk.free / (1024**3)
            
            # Get temperature
            temperature = self.get_temp()
            
            # Get additional system info
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            # Get load average (Unix systems)
            load_avg = None
            try:
                load_avg = os.getloadavg()
            except (OSError, AttributeError):
                pass
            
            stats = {
                "timestamp": datetime.now().isoformat(),
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count(),
                    "load_avg": load_avg
                },
                "memory": {
                    "percent": memory_percent,
                    "total_gb": memory.total / (1024**3),
                    "available_gb": memory_available_gb,
                    "used_gb": memory.used / (1024**3)
                },
                "disk": {
                    "percent": disk_percent,
                    "total_gb": disk.total / (1024**3),
                    "free_gb": disk_free_gb,
                    "used_gb": disk.used / (1024**3)
                },
                "temperature": {
                    "celsius": temperature,
                    "fahrenheit": (temperature * 9/5 + 32) if temperature else None
                },
                "system": {
                    "uptime_hours": uptime.total_seconds() / 3600,
                    "boot_time": boot_time.isoformat()
                }
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting resource status: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "cpu": {"percent": 0},
                "memory": {"percent": 0},
                "disk": {"percent": 0},
                "temperature": {"celsius": None}
            }
    
    def get_status_level(self, stats: Dict[str, Any]) -> str:
        """
        Determine overall system status level based on thresholds
        Returns: 'normal', 'warning', 'critical'
        """
        cpu_pct = stats.get("cpu", {}).get("percent", 0)
        mem_pct = stats.get("memory", {}).get("percent", 0)
        disk_pct = stats.get("disk", {}).get("percent", 0)
        temp = stats.get("temperature", {}).get("celsius")
        
        # Critical conditions
        if (cpu_pct > self.cpu_threshold or 
            mem_pct > self.memory_threshold or 
            disk_pct > self.disk_threshold or
            (temp and temp > self.temp_threshold)):
            return 'critical'
        
        # Warning conditions (80% of thresholds)
        warning_cpu = self.cpu_threshold * 0.8
        warning_mem = self.memory_threshold * 0.8
        warning_disk = self.disk_threshold * 0.8
        warning_temp = self.temp_threshold * 0.8
        
        if (cpu_pct > warning_cpu or 
            mem_pct > warning_mem or 
            disk_pct > warning_disk or
            (temp and temp > warning_temp)):
            return 'warning'
        
        return 'normal'
    
    def check_thresholds(self, stats: Dict[str, Any]) -> None:
        """
        Check resource thresholds and trigger alerts/throttling
        """
        cpu_pct = stats.get("cpu", {}).get("percent", 0)
        mem_pct = stats.get("memory", {}).get("percent", 0)
        disk_pct = stats.get("disk", {}).get("percent", 0)
        temp = stats.get("temperature", {}).get("celsius")
        
        alerts = []
        
        # Temperature alerts (highest priority)
        if temp and temp > self.temp_threshold:
            alert = {
                "type": "temperature",
                "level": "critical",
                "message": f"High temperature: {temp:.1f}°C (threshold: {self.temp_threshold}°C)",
                "value": temp,
                "threshold": self.temp_threshold
            }
            alerts.append(alert)
            self.logger.warning(alert["message"])
            
            # Trigger throttling for temperature
            if self.throttle_callback:
                self.throttle_callback("temperature", temp, self.temp_threshold)
        
        # CPU alerts
        if cpu_pct > self.cpu_threshold:
            alert = {
                "type": "cpu",
                "level": "critical",
                "message": f"High CPU usage: {cpu_pct:.1f}% (threshold: {self.cpu_threshold}%)",
                "value": cpu_pct,
                "threshold": self.cpu_threshold
            }
            alerts.append(alert)
            self.logger.warning(alert["message"])
            
            if self.throttle_callback:
                self.throttle_callback("cpu", cpu_pct, self.cpu_threshold)
        
        # Memory alerts
        if mem_pct > self.memory_threshold:
            alert = {
                "type": "memory",
                "level": "critical",
                "message": f"High memory usage: {mem_pct:.1f}% (threshold: {self.memory_threshold}%)",
                "value": mem_pct,
                "threshold": self.memory_threshold
            }
            alerts.append(alert)
            self.logger.warning(alert["message"])
            
            if self.throttle_callback:
                self.throttle_callback("memory", mem_pct, self.memory_threshold)
        
        # Disk alerts
        if disk_pct > self.disk_threshold:
            alert = {
                "type": "disk",
                "level": "critical",
                "message": f"High disk usage: {disk_pct:.1f}% (threshold: {self.disk_threshold}%)",
                "value": disk_pct,
                "threshold": self.disk_threshold
            }
            alerts.append(alert)
            self.logger.warning(alert["message"])
        
        # Log alerts if callback provided
        if alerts and self.log_callback:
            self.log_callback({"alerts": alerts, "stats": stats})
    
    def monitor_loop(self, check_interval: int = 10) -> None:
        """
        Main monitoring loop - runs in separate thread
        """
        self.logger.info(f"Resource monitoring started (interval: {check_interval}s)")
        
        while self.monitoring:
            try:
                # Get current resource status
                stats = self.get_resource_status()
                
                # Add to history
                self.stats_history.append(stats)
                if len(self.stats_history) > self.max_history:
                    self.stats_history.pop(0)
                
                # Check thresholds and trigger alerts
                self.check_thresholds(stats)
                
                # Call logging callback
                if self.log_callback:
                    self.log_callback(stats)
                
                # Call GUI update callback
                if self.gui_update_callback:
                    status_level = self.get_status_level(stats)
                    self.gui_update_callback(stats, status_level)
                
                # Wait for next check
                time.sleep(check_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(check_interval)
        
        self.logger.info("Resource monitoring stopped")
    
    def start_monitoring(self, 
                        log_callback: Optional[Callable] = None,
                        gui_update_callback: Optional[Callable] = None,
                        throttle_callback: Optional[Callable] = None,
                        check_interval: int = 10,
                        cpu_threshold: int = 90,
                        memory_threshold: int = 90,
                        temp_threshold: int = 75,
                        disk_threshold: int = 90) -> None:
        """
        Start resource monitoring with specified callbacks and thresholds
        
        Args:
            log_callback: Function to call for logging stats
            gui_update_callback: Function to call for GUI updates
            throttle_callback: Function to call when throttling is needed
            check_interval: Seconds between checks
            cpu_threshold: CPU usage threshold (%)
            memory_threshold: Memory usage threshold (%)
            temp_threshold: Temperature threshold (°C)
            disk_threshold: Disk usage threshold (%)
        """
        if self.monitoring:
            self.logger.warning("Monitoring already running")
            return
        
        # Set callbacks and thresholds
        self.log_callback = log_callback
        self.gui_update_callback = gui_update_callback
        self.throttle_callback = throttle_callback
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.temp_threshold = temp_threshold
        self.disk_threshold = disk_threshold
        
        # Start monitoring
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self.monitor_loop, 
            args=(check_interval,), 
            daemon=True
        )
        self.monitor_thread.start()
        
        self.logger.info("Resource monitoring thread started")
    
    def stop_monitoring(self) -> None:
        """Stop resource monitoring"""
        if not self.monitoring:
            return
        
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        self.logger.info("Resource monitoring stopped")
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current resource statistics"""
        return self.get_resource_status()
    
    def get_stats_history(self, limit: int = 50) -> list:
        """Get recent statistics history"""
        return self.stats_history[-limit:] if self.stats_history else []
    
    def get_average_stats(self, minutes: int = 5) -> Dict[str, Any]:
        """Get average statistics over specified time period"""
        if not self.stats_history:
            return {}
        
        # Calculate how many readings to include (assuming 10s intervals)
        readings_count = min(len(self.stats_history), (minutes * 60) // 10)
        recent_stats = self.stats_history[-readings_count:]
        
        if not recent_stats:
            return {}
        
        # Calculate averages
        cpu_avg = sum(s.get("cpu", {}).get("percent", 0) for s in recent_stats) / len(recent_stats)
        mem_avg = sum(s.get("memory", {}).get("percent", 0) for s in recent_stats) / len(recent_stats)
        disk_avg = sum(s.get("disk", {}).get("percent", 0) for s in recent_stats) / len(recent_stats)
        
        temps = [s.get("temperature", {}).get("celsius") for s in recent_stats if s.get("temperature", {}).get("celsius")]
        temp_avg = sum(temps) / len(temps) if temps else None
        
        return {
            "period_minutes": minutes,
            "readings_count": readings_count,
            "cpu_avg": cpu_avg,
            "memory_avg": mem_avg,
            "disk_avg": disk_avg,
            "temperature_avg": temp_avg
        }


# Convenience functions for backward compatibility
def get_temp() -> Optional[float]:
    """Get CPU temperature - convenience function"""
    monitor = ResourceMonitor()
    return monitor.get_temp()

def get_resource_status() -> Dict[str, Any]:
    """Get resource status - convenience function"""
    monitor = ResourceMonitor()
    return monitor.get_resource_status()

def monitor(log_callback: Callable, 
           gui_update_callback: Optional[Callable] = None, 
           check_interval: int = 10, 
           cpu_th: int = 90, 
           mem_th: int = 90, 
           temp_th: int = 75) -> ResourceMonitor:
    """
    Start monitoring with simple callback interface - convenience function
    Returns ResourceMonitor instance for control
    """
    resource_monitor = ResourceMonitor()
    resource_monitor.start_monitoring(
        log_callback=log_callback,
        gui_update_callback=gui_update_callback,
        check_interval=check_interval,
        cpu_threshold=cpu_th,
        memory_threshold=mem_th,
        temp_threshold=temp_th
    )
    return resource_monitor