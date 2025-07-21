#!/usr/bin/env python3
"""
Health check script for Guardian Node Family Assistant
Provides HTTP endpoint for Docker health checks
"""

import os
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('health_check')

# Import Guardian components if available
try:
    from guardian_interpreter.llm_loader import get_llm_loader
    from guardian_interpreter.llm_integration import create_llm
    from guardian_interpreter.resource_monitor import ResourceMonitor
    LLM_AVAILABLE = True
except ImportError:
    logger.warning("Guardian components not available, using minimal health check")
    LLM_AVAILABLE = False

class HealthStatus:
    """Health status information for Guardian Node"""
    
    def __init__(self):
        self.resource_monitor = None
        self.llm_loader = None
        
        # Initialize components
        try:
            if 'ResourceMonitor' in globals():
                self.resource_monitor = ResourceMonitor()
            
            if 'get_llm_loader' in globals():
                self.llm_loader = get_llm_loader()
        except Exception as e:
            logger.error(f"Error initializing health components: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current health status"""
        status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': os.environ.get('GUARDIAN_VERSION', '1.0.0'),
            'mode': os.environ.get('GUARDIAN_MODE', 'standard')
        }
        
        # Add system resources
        try:
            if self.resource_monitor:
                stats = self.resource_monitor.get_current_stats()
                status['resources'] = {
                    'cpu_percent': stats.get('cpu_percent', 0),
                    'memory_percent': stats.get('memory_percent', 0),
                    'temperature_c': stats.get('temperature_c', 0)
                }
            else:
                # Basic resource info without ResourceMonitor
                import psutil
                status['resources'] = {
                    'cpu_percent': psutil.cpu_percent(),
                    'memory_percent': psutil.virtual_memory().percent
                }
        except Exception as e:
            logger.warning(f"Error getting resource stats: {e}")
            status['resources'] = {'error': str(e)}
        
        # Add LLM status
        try:
            if self.llm_loader:
                models = self.llm_loader.get_available_models()
                status['llm'] = {
                    'available_models': len(models),
                    'current_model': self.llm_loader.get_current_model(),
                    'models': [m.name for m in models]
                }
        except Exception as e:
            logger.warning(f"Error getting LLM status: {e}")
            status['llm'] = {'error': str(e)}
        
        return status

class HealthCheckHandler(BaseHTTPRequestHandler):
    """HTTP handler for health check endpoints"""
    
    def __init__(self, *args, **kwargs):
        self.health_status = HealthStatus()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health':
            self._handle_health()
        elif self.path == '/metrics':
            self._handle_metrics()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def _handle_health(self):
        """Handle health check endpoint"""
        status = self.health_status.get_status()
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(status).encode())
    
    def _handle_metrics(self):
        """Handle Prometheus metrics endpoint"""
        status = self.health_status.get_status()
        
        # Convert status to Prometheus format
        metrics = []
        
        # Basic metrics
        metrics.append(f'guardian_up 1')
        
        # Resource metrics
        if 'resources' in status:
            resources = status['resources']
            metrics.append(f'guardian_cpu_percent {resources.get("cpu_percent", 0)}')
            metrics.append(f'guardian_memory_percent {resources.get("memory_percent", 0)}')
            if 'temperature_c' in resources:
                metrics.append(f'guardian_temperature_celsius {resources.get("temperature_c", 0)}')
        
        # LLM metrics
        if 'llm' in status:
            llm = status['llm']
            metrics.append(f'guardian_llm_models_available {llm.get("available_models", 0)}')
            metrics.append(f'guardian_llm_model_loaded {1 if llm.get("current_model") else 0}')
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write('\n'.join(metrics).encode())

def run_server(port=8080):
    """Run the health check server"""
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    logger.info(f"Starting health check server on port {port}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Stopping health check server")
        server.server_close()

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.environ.get('GUARDIAN_HEALTH_PORT', '8080'))
    run_server(port)