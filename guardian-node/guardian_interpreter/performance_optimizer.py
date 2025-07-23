"""
Guardian Node Performance Optimization System
Handles memory/resource management, dynamic LLM model loading/unloading, and response caching
Optimized for Raspberry Pi deployment with family cybersecurity analysis
"""

import threading
import functools
import time
import gc
import hashlib
import json
import logging
from typing import Dict, Any, Optional, Callable, Tuple
from datetime import datetime, timedelta

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

class PerformanceOptimizer:
    """
    Performance optimizer for Guardian Node.
    Handles memory/resource management, dynamic LLM model loading, and response caching.
    Optimized for Raspberry Pi with family cybersecurity focus.
    """
    
    def __init__(self, max_cache_size: int = 128, cache_ttl_hours: int = 24, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        
        # LLM Model Management
        self.model = None
        self.model_loaded = False
        self.model_lock = threading.Lock()
        self.model_name = None
        self.model_load_time = None
        
        # Response Caching System
        self.cache = {}
        self.cache_metadata = {}  # Store timestamps and access counts
        self.cache_order = []  # LRU tracking
        self.max_cache_size = max_cache_size
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        self.cache_lock = threading.Lock()
        
        # Performance Metrics
        self.metrics = {
            'cache_hits': 0,
            'cache_misses': 0,
            'model_loads': 0,
            'model_unloads': 0,
            'memory_cleanups': 0,
            'queries_processed': 0
        }
        
        # Resource Monitoring
        self.resource_monitor_active = False
        self.resource_thresholds = {
            'memory_percent': 85,
            'cpu_percent': 90,
            'temperature_celsius': 75
        }
        
        self.logger.info("Performance Optimizer initialized")
    
    # ---------- Memory & Resource Management ----------
    
    def memory_cleanup(self) -> Dict[str, Any]:
        """Perform comprehensive memory cleanup tasks."""
        try:
            # Record memory before cleanup
            memory_before = self.get_memory_usage()
            
            # Python garbage collection
            collected = gc.collect()
            
            # Clear expired cache entries
            self._cleanup_expired_cache()
            
            # Force memory cleanup for specific libraries if available
            try:
                # Clear any numpy caches if numpy is available
                import numpy as np
                if hasattr(np, 'clear_cache'):
                    np.clear_cache()
            except ImportError:
                pass
            
            # Record memory after cleanup
            memory_after = self.get_memory_usage()
            
            self.metrics['memory_cleanups'] += 1
            
            cleanup_result = {
                'objects_collected': collected,
                'memory_before_mb': memory_before,
                'memory_after_mb': memory_after,
                'memory_freed_mb': memory_before - memory_after if memory_before and memory_after else 0,
                'cache_entries_cleaned': self._get_cache_cleanup_count(),
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Memory cleanup completed: freed {cleanup_result['memory_freed_mb']:.1f}MB, collected {collected} objects")
            return cleanup_result
            
        except Exception as e:
            self.logger.error(f"Memory cleanup error: {e}")
            return {'error': str(e)}
    
    def get_memory_usage(self) -> Optional[float]:
        """Get current memory usage in MB."""
        if not PSUTIL_AVAILABLE:
            return None
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except Exception:
            return None
    
    def monitor_resource_usage(self) -> Dict[str, Any]:
        """Monitor comprehensive system resource usage."""
        try:
            if not PSUTIL_AVAILABLE:
                return {
                    'error': 'psutil not available',
                    'memory_used_mb': None,
                    'cpu_percent': None,
                    'temperature_celsius': None
                }
            
            # Memory information
            memory = psutil.virtual_memory()
            process = psutil.Process()
            process_memory = process.memory_info()
            
            # CPU information
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            
            # Disk information
            disk = psutil.disk_usage('/')
            
            # Temperature (Raspberry Pi specific)
            temperature = self._get_cpu_temperature()
            
            # Network information
            network = psutil.net_io_counters()
            
            resource_info = {
                'timestamp': datetime.now().isoformat(),
                'memory': {
                    'system_total_mb': memory.total / 1024 / 1024,
                    'system_used_mb': memory.used / 1024 / 1024,
                    'system_percent': memory.percent,
                    'process_rss_mb': process_memory.rss / 1024 / 1024,
                    'process_vms_mb': process_memory.vms / 1024 / 1024
                },
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'load_avg': self._get_load_average()
                },
                'disk': {
                    'total_gb': disk.total / 1024 / 1024 / 1024,
                    'used_gb': disk.used / 1024 / 1024 / 1024,
                    'free_gb': disk.free / 1024 / 1024 / 1024,
                    'percent': (disk.used / disk.total) * 100
                },
                'temperature_celsius': temperature,
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv
                },
                'guardian_metrics': self.get_performance_metrics()
            }
            
            # Check if resources are above thresholds
            resource_info['alerts'] = self._check_resource_thresholds(resource_info)
            
            return resource_info
            
        except Exception as e:
            self.logger.error(f"Resource monitoring error: {e}")
            return {'error': str(e)}
    
    def _get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature (Raspberry Pi specific)."""
        try:
            # Try Raspberry Pi thermal zone
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp_millicelsius = int(f.read().strip())
                return temp_millicelsius / 1000.0
        except Exception:
            try:
                # Try vcgencmd if available
                import subprocess
                result = subprocess.run(['vcgencmd', 'measure_temp'], 
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    temp_str = result.stdout.strip()
                    temp_value = temp_str.split('=')[1].split("'")[0]
                    return float(temp_value)
            except Exception:
                pass
        return None
    
    def _get_load_average(self) -> Optional[Tuple[float, float, float]]:
        """Get system load average."""
        try:
            return psutil.getloadavg()
        except (AttributeError, OSError):
            return None
    
    def _check_resource_thresholds(self, resource_info: Dict[str, Any]) -> list:
        """Check if resources exceed thresholds and return alerts."""
        alerts = []
        
        # Memory threshold
        memory_percent = resource_info.get('memory', {}).get('system_percent', 0)
        if memory_percent > self.resource_thresholds['memory_percent']:
            alerts.append({
                'type': 'memory',
                'level': 'warning',
                'message': f'High memory usage: {memory_percent:.1f}%',
                'threshold': self.resource_thresholds['memory_percent']
            })
        
        # CPU threshold
        cpu_percent = resource_info.get('cpu', {}).get('percent', 0)
        if cpu_percent > self.resource_thresholds['cpu_percent']:
            alerts.append({
                'type': 'cpu',
                'level': 'warning',
                'message': f'High CPU usage: {cpu_percent:.1f}%',
                'threshold': self.resource_thresholds['cpu_percent']
            })
        
        # Temperature threshold
        temperature = resource_info.get('temperature_celsius')
        if temperature and temperature > self.resource_thresholds['temperature_celsius']:
            alerts.append({
                'type': 'temperature',
                'level': 'critical',
                'message': f'High temperature: {temperature:.1f}°C',
                'threshold': self.resource_thresholds['temperature_celsius']
            })
        
        return alerts
    
    # ---------- Dynamic LLM Model Loading/Unloading ----------
    
    def load_model(self, model_name: str = "default-llm", model_loader: Optional[Callable] = None) -> bool:
        """Load LLM model into memory with custom loader support."""
        with self.model_lock:
            if self.model_loaded and self.model_name == model_name:
                self.logger.info(f"Model '{model_name}' already loaded")
                return True
            
            try:
                # Unload existing model if different
                if self.model_loaded and self.model_name != model_name:
                    self.unload_model()
                
                self.logger.info(f"Loading LLM model: {model_name}")
                start_time = time.time()
                
                if model_loader:
                    # Use custom model loader
                    self.model = model_loader(model_name)
                else:
                    # Placeholder for actual LLM loading
                    # Replace this with your actual LLM initialization code
                    self.model = f"{model_name} [Guardian LLM Model Loaded]"
                    time.sleep(0.1)  # Simulate loading time
                
                self.model_loaded = True
                self.model_name = model_name
                self.model_load_time = datetime.now()
                self.metrics['model_loads'] += 1
                
                load_time = time.time() - start_time
                self.logger.info(f"LLM Model '{model_name}' loaded successfully in {load_time:.2f}s")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to load model '{model_name}': {e}")
                self.model = None
                self.model_loaded = False
                self.model_name = None
                return False
    
    def unload_model(self) -> bool:
        """Unload LLM model from memory."""
        with self.model_lock:
            if not self.model_loaded:
                self.logger.info("No model to unload")
                return True
            
            try:
                self.logger.info(f"Unloading LLM model: {self.model_name}")
                
                # Custom model cleanup if needed
                if hasattr(self.model, 'cleanup'):
                    self.model.cleanup()
                
                self.model = None
                self.model_loaded = False
                model_name = self.model_name
                self.model_name = None
                self.model_load_time = None
                self.metrics['model_unloads'] += 1
                
                # Perform memory cleanup after unloading
                self.memory_cleanup()
                
                self.logger.info(f"LLM Model '{model_name}' unloaded successfully")
                return True
                
            except Exception as e:
                self.logger.error(f"Error unloading model: {e}")
                return False
    
    def ensure_model(self, model_name: str = "default-llm", model_loader: Optional[Callable] = None) -> bool:
        """Ensure model is loaded before use."""
        if not self.model_loaded:
            return self.load_model(model_name, model_loader)
        return True
    
    def is_model_loaded(self) -> bool:
        """Check if model is currently loaded."""
        return self.model_loaded
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the currently loaded model."""
        with self.model_lock:
            return {
                'loaded': self.model_loaded,
                'model_name': self.model_name,
                'load_time': self.model_load_time.isoformat() if self.model_load_time else None,
                'uptime_minutes': (datetime.now() - self.model_load_time).total_seconds() / 60 if self.model_load_time else 0
            }
    
    # ---------- Response Caching ----------
    
    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate a consistent cache key from function name and arguments."""
        # Create a deterministic string representation
        key_data = {
            'function': func_name,
            'args': args,
            'kwargs': sorted(kwargs.items()) if kwargs else {}
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get_cached_response(self, key: str) -> Optional[Any]:
        """Get response from cache if available and not expired."""
        with self.cache_lock:
            if key not in self.cache:
                self.metrics['cache_misses'] += 1
                return None
            
            # Check if cache entry has expired
            metadata = self.cache_metadata.get(key, {})
            cache_time = metadata.get('timestamp')
            if cache_time and datetime.now() - cache_time > self.cache_ttl:
                # Remove expired entry
                self._remove_cache_entry(key)
                self.metrics['cache_misses'] += 1
                return None
            
            # Update access information
            metadata['last_accessed'] = datetime.now()
            metadata['access_count'] = metadata.get('access_count', 0) + 1
            
            # Move to end to mark as recently used (LRU)
            if key in self.cache_order:
                self.cache_order.remove(key)
            self.cache_order.append(key)
            
            self.metrics['cache_hits'] += 1
            return self.cache[key]
    
    def cache_response(self, key: str, value: Any) -> None:
        """Cache a response with metadata."""
        with self.cache_lock:
            # Remove oldest entries if cache is full
            while len(self.cache_order) >= self.max_cache_size:
                oldest_key = self.cache_order.pop(0)
                self._remove_cache_entry(oldest_key)
            
            # Add new entry
            self.cache[key] = value
            self.cache_metadata[key] = {
                'timestamp': datetime.now(),
                'last_accessed': datetime.now(),
                'access_count': 1,
                'size_bytes': len(str(value))  # Rough size estimate
            }
            self.cache_order.append(key)
    
    def _remove_cache_entry(self, key: str) -> None:
        """Remove a cache entry and its metadata."""
        if key in self.cache:
            del self.cache[key]
        if key in self.cache_metadata:
            del self.cache_metadata[key]
        if key in self.cache_order:
            self.cache_order.remove(key)
    
    def _cleanup_expired_cache(self) -> int:
        """Clean up expired cache entries and return count of removed entries."""
        removed_count = 0
        current_time = datetime.now()
        
        with self.cache_lock:
            expired_keys = []
            for key, metadata in self.cache_metadata.items():
                cache_time = metadata.get('timestamp')
                if cache_time and current_time - cache_time > self.cache_ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                self._remove_cache_entry(key)
                removed_count += 1
        
        if removed_count > 0:
            self.logger.info(f"Cleaned up {removed_count} expired cache entries")
        
        return removed_count
    
    def _get_cache_cleanup_count(self) -> int:
        """Get count of cache entries that would be cleaned up."""
        current_time = datetime.now()
        expired_count = 0
        
        for metadata in self.cache_metadata.values():
            cache_time = metadata.get('timestamp')
            if cache_time and current_time - cache_time > self.cache_ttl:
                expired_count += 1
        
        return expired_count
    
    def clear_cache(self) -> int:
        """Clear the entire response cache and return count of removed entries."""
        with self.cache_lock:
            removed_count = len(self.cache)
            self.cache.clear()
            self.cache_metadata.clear()
            self.cache_order.clear()
        
        self.logger.info(f"Cache cleared: {removed_count} entries removed")
        return removed_count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.cache_lock:
            total_size_bytes = sum(metadata.get('size_bytes', 0) for metadata in self.cache_metadata.values())
            
            return {
                'entries': len(self.cache),
                'max_size': self.max_cache_size,
                'hit_rate': self.metrics['cache_hits'] / (self.metrics['cache_hits'] + self.metrics['cache_misses']) if (self.metrics['cache_hits'] + self.metrics['cache_misses']) > 0 else 0,
                'total_hits': self.metrics['cache_hits'],
                'total_misses': self.metrics['cache_misses'],
                'total_size_bytes': total_size_bytes,
                'ttl_hours': self.cache_ttl.total_seconds() / 3600
            }
    
    # ---------- Decorator for Caching Common Queries ----------
    
    def cached(self, ttl_hours: Optional[int] = None):
        """
        Decorator for caching function results.
        
        Args:
            ttl_hours: Override default TTL for this specific function
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self._generate_cache_key(func.__name__, args, kwargs)
                
                # Try to get from cache
                cached_result = self.get_cached_response(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                start_time = time.time()
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Cache the result
                self.cache_response(cache_key, result)
                
                # Update metrics
                self.metrics['queries_processed'] += 1
                
                self.logger.debug(f"Function {func.__name__} executed in {execution_time:.3f}s and cached")
                return result
            
            return wrapper
        return decorator
    
    # ---------- Performance Metrics ----------
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        return {
            'cache': self.get_cache_stats(),
            'model': self.get_model_info(),
            'counters': self.metrics.copy(),
            'memory_usage_mb': self.get_memory_usage(),
            'uptime_minutes': (datetime.now() - datetime.now()).total_seconds() / 60  # Placeholder
        }
    
    def reset_metrics(self) -> None:
        """Reset performance metrics counters."""
        self.metrics = {
            'cache_hits': 0,
            'cache_misses': 0,
            'model_loads': 0,
            'model_unloads': 0,
            'memory_cleanups': 0,
            'queries_processed': 0
        }
        self.logger.info("Performance metrics reset")
    
    # ---------- Auto-Optimization ----------
    
    def auto_optimize(self) -> Dict[str, Any]:
        """Perform automatic optimization based on current resource usage."""
        optimization_actions = []
        resource_info = self.monitor_resource_usage()
        
        # Check for high memory usage
        memory_percent = resource_info.get('memory', {}).get('system_percent', 0)
        if memory_percent > 80:
            cleanup_result = self.memory_cleanup()
            optimization_actions.append({
                'action': 'memory_cleanup',
                'reason': f'High memory usage: {memory_percent:.1f}%',
                'result': cleanup_result
            })
        
        # Check for high temperature
        temperature = resource_info.get('temperature_celsius')
        if temperature and temperature > 70:
            if self.model_loaded:
                self.unload_model()
                optimization_actions.append({
                    'action': 'model_unload',
                    'reason': f'High temperature: {temperature:.1f}°C',
                    'result': 'Model unloaded to reduce heat'
                })
        
        # Clean up expired cache entries
        expired_cleaned = self._cleanup_expired_cache()
        if expired_cleaned > 0:
            optimization_actions.append({
                'action': 'cache_cleanup',
                'reason': 'Expired cache entries found',
                'result': f'{expired_cleaned} entries removed'
            })
        
        return {
            'timestamp': datetime.now().isoformat(),
            'actions_taken': optimization_actions,
            'resource_info': resource_info
        }


# ================= Guardian Node Integration Examples ================

# Global optimizer instance for Guardian Node
_guardian_optimizer = None

def get_optimizer() -> PerformanceOptimizer:
    """Get the global Guardian Node performance optimizer instance."""
    global _guardian_optimizer
    if _guardian_optimizer is None:
        _guardian_optimizer = PerformanceOptimizer(
            max_cache_size=64,  # Smaller cache for Raspberry Pi
            cache_ttl_hours=24,
            logger=logging.getLogger('GuardianOptimizer')
        )
    return _guardian_optimizer

# Example cached cybersecurity analysis functions
def cached_cybersecurity_advice(query: str) -> str:
    """Example cached cybersecurity advice function."""
    optimizer = get_optimizer()
    
    @optimizer.cached()
    def _get_advice(query: str) -> str:
        # Simulate processing time for cybersecurity analysis
        time.sleep(0.5)
        
        # This would be replaced with actual LLM or analysis logic
        common_responses = {
            'dns filtering': 'Set up family-safe DNS like OpenDNS FamilyShield (208.67.222.123) or Cloudflare for Families (1.1.1.3)',
            'parental controls': 'Enable built-in parental controls: Windows Family Safety, macOS Screen Time, or install Qustodio',
            'wifi security': 'Use WPA3 or WPA2 encryption, change default router passwords, disable WPS',
            'iot security': 'Change default IoT device passwords, use separate network for IoT devices, update firmware regularly'
        }
        
        query_lower = query.lower()
        for key, response in common_responses.items():
            if key in query_lower:
                return f"Guardian Advice: {response}"
        
        return f"Guardian Advice: For '{query}', ensure you follow basic cybersecurity practices: use strong passwords, keep software updated, and be cautious with downloads."
    
    return _get_advice(query)

def cached_protocol_analysis(protocol_name: str, target: str = None) -> Dict[str, Any]:
    """Example cached protocol analysis function."""
    optimizer = get_optimizer()
    
    @optimizer.cached(ttl_hours=6)  # Shorter TTL for protocol analysis
    def _analyze_protocol(protocol_name: str, target: str = None) -> Dict[str, Any]:
        # Simulate protocol analysis processing
        time.sleep(1.0)
        
        return {
            'protocol': protocol_name,
            'target': target,
            'status': 'analyzed',
            'findings': [f'Analysis completed for {protocol_name}'],
            'recommendations': [f'Review {protocol_name} configuration'],
            'timestamp': datetime.now().isoformat()
        }
    
    return _analyze_protocol(protocol_name, target)


if __name__ == "__main__":
    # Example usage and testing
    optimizer = PerformanceOptimizer(max_cache_size=32)
    
    # Test model loading
    optimizer.load_model("guardian-cybersecurity-model")
    print("Model info:", optimizer.get_model_info())
    
    # Test resource monitoring
    print("Resource usage:", optimizer.monitor_resource_usage())
    
    # Test caching
    print("First call:", cached_cybersecurity_advice("How do I set up family DNS filtering?"))
    print("Second call (cached):", cached_cybersecurity_advice("How do I set up family DNS filtering?"))
    
    # Test performance metrics
    print("Performance metrics:", optimizer.get_performance_metrics())
    
    # Test auto-optimization
    print("Auto-optimization:", optimizer.auto_optimize())
    
    # Cleanup
    optimizer.unload_model()
    optimizer.clear_cache()