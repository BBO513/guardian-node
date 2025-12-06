"""
Smart Home Control Module for Guardian Node
Supports Home Assistant, Zigbee, Tuya, and MQTT devices
All processing is local - no cloud dependencies
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

# Try to import smart home libraries
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False


class SmartHomeControl:
    """
    Local smart home device control
    Supports multiple integration methods
    """
    
    def __init__(self, config: Dict[str, Any] = None, logger: logging.Logger = None):
        """
        Initialize smart home control
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config or {}
        self.logger = logger or logging.getLogger(__name__)
        self.smart_home_config = self.config.get('smart_home', {})
        
        # Device registry
        self.devices = {}
        self.device_states = {}
        
        # Integration clients
        self.ha_client = None
        self.mqtt_client = None
        
        # Determine integration type
        self.integration = self.smart_home_config.get('integration', 'home_assistant')
        
        # Initialize based on integration type
        if self.integration == 'home_assistant':
            self._init_home_assistant()
        elif self.integration == 'mqtt':
            self._init_mqtt()
        elif self.integration == 'mock':
            self._init_mock()
        else:
            self.logger.warning(f"Unknown integration: {self.integration}, using mock mode")
            self._init_mock()
    
    def _init_home_assistant(self):
        """Initialize Home Assistant connection"""
        if not REQUESTS_AVAILABLE:
            self.logger.warning("requests library not available. Install with: pip install requests")
            self._init_mock()
            return
        
        try:
            ha_config = self.smart_home_config.get('home_assistant', {})
            self.ha_url = ha_config.get('url', 'http://homeassistant.local:8123')
            self.ha_token = ha_config.get('token', '')
            
            if not self.ha_token:
                self.logger.warning("Home Assistant token not configured, using mock mode")
                self._init_mock()
                return
            
            # Test connection
            headers = {
                'Authorization': f'Bearer {self.ha_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(f'{self.ha_url}/api/', headers=headers, timeout=5)
            
            if response.status_code == 200:
                self.logger.info("✅ Home Assistant connected")
                self.discover_devices()
            else:
                self.logger.warning(f"Home Assistant connection failed: {response.status_code}")
                self._init_mock()
                
        except Exception as e:
            self.logger.error(f"Failed to connect to Home Assistant: {e}")
            self._init_mock()
    
    def _init_mqtt(self):
        """Initialize MQTT connection"""
        if not MQTT_AVAILABLE:
            self.logger.warning("paho-mqtt not available. Install with: pip install paho-mqtt")
            self._init_mock()
            return
        
        try:
            mqtt_config = self.smart_home_config.get('mqtt', {})
            broker = mqtt_config.get('broker', 'localhost')
            port = mqtt_config.get('port', 1883)
            
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.connect(broker, port, 60)
            self.mqtt_client.loop_start()
            
            self.logger.info("✅ MQTT connected")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to MQTT: {e}")
            self._init_mock()
    
    def _init_mock(self):
        """Initialize mock devices for testing"""
        self.integration = 'mock'
        
        # Create mock devices
        self.devices = {
            'kettle': {
                'name': 'Electric Kettle',
                'type': 'switch',
                'room': 'kitchen',
                'state': 'off'
            },
            'ac': {
                'name': 'Air Conditioner',
                'type': 'climate',
                'room': 'living_room',
                'state': 'off',
                'temperature': 22
            },
            'hot_water': {
                'name': 'Hot Water Heater',
                'type': 'switch',
                'room': 'bathroom',
                'state': 'off'
            },
            'lights_living': {
                'name': 'Living Room Lights',
                'type': 'light',
                'room': 'living_room',
                'state': 'off',
                'brightness': 100
            },
            'lights_bedroom': {
                'name': 'Bedroom Lights',
                'type': 'light',
                'room': 'bedroom',
                'state': 'off',
                'brightness': 100
            }
        }
        
        self.logger.info("✅ Mock smart home initialized with 5 devices")
    
    def is_available(self) -> bool:
        """Check if smart home control is available"""
        return len(self.devices) > 0
    
    def discover_devices(self) -> List[Dict[str, Any]]:
        """
        Discover available smart home devices
        
        Returns:
            List of discovered devices
        """
        if self.integration == 'home_assistant':
            return self._discover_ha_devices()
        elif self.integration == 'mqtt':
            return self._discover_mqtt_devices()
        else:
            # Return mock devices
            return [
                {'id': device_id, **device_info}
                for device_id, device_info in self.devices.items()
            ]
    
    def _discover_ha_devices(self) -> List[Dict[str, Any]]:
        """Discover Home Assistant devices"""
        try:
            headers = {
                'Authorization': f'Bearer {self.ha_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(f'{self.ha_url}/api/states', headers=headers, timeout=5)
            
            if response.status_code == 200:
                states = response.json()
                
                # Filter for controllable devices
                for state in states:
                    entity_id = state['entity_id']
                    domain = entity_id.split('.')[0]
                    
                    if domain in ['switch', 'light', 'climate', 'fan']:
                        self.devices[entity_id] = {
                            'name': state['attributes'].get('friendly_name', entity_id),
                            'type': domain,
                            'state': state['state']
                        }
                
                self.logger.info(f"Discovered {len(self.devices)} Home Assistant devices")
                return list(self.devices.values())
            
        except Exception as e:
            self.logger.error(f"Failed to discover Home Assistant devices: {e}")
        
        return []
    
    def _discover_mqtt_devices(self) -> List[Dict[str, Any]]:
        """Discover MQTT devices"""
        # TODO: Implement MQTT device discovery
        self.logger.info("MQTT device discovery not yet implemented")
        return []
    
    def turn_on(self, device: str) -> Dict[str, Any]:
        """
        Turn on a device
        
        Args:
            device: Device ID or name
            
        Returns:
            Result dictionary with success status
        """
        device_id = self._resolve_device_id(device)
        
        if not device_id:
            return {
                'success': False,
                'error': f"Device '{device}' not found",
                'available_devices': list(self.devices.keys())
            }
        
        try:
            if self.integration == 'home_assistant':
                result = self._ha_turn_on(device_id)
            elif self.integration == 'mqtt':
                result = self._mqtt_turn_on(device_id)
            else:
                result = self._mock_turn_on(device_id)
            
            if result['success']:
                self.logger.info(f"✅ Turned on: {device_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to turn on {device_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'device': device_id
            }
    
    def turn_off(self, device: str) -> Dict[str, Any]:
        """
        Turn off a device
        
        Args:
            device: Device ID or name
            
        Returns:
            Result dictionary with success status
        """
        device_id = self._resolve_device_id(device)
        
        if not device_id:
            return {
                'success': False,
                'error': f"Device '{device}' not found",
                'available_devices': list(self.devices.keys())
            }
        
        try:
            if self.integration == 'home_assistant':
                result = self._ha_turn_off(device_id)
            elif self.integration == 'mqtt':
                result = self._mqtt_turn_off(device_id)
            else:
                result = self._mock_turn_off(device_id)
            
            if result['success']:
                self.logger.info(f"✅ Turned off: {device_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to turn off {device_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'device': device_id
            }
    
    def get_status(self, device: str) -> Dict[str, Any]:
        """
        Get device status
        
        Args:
            device: Device ID or name
            
        Returns:
            Device status dictionary
        """
        device_id = self._resolve_device_id(device)
        
        if not device_id:
            return {
                'success': False,
                'error': f"Device '{device}' not found"
            }
        
        if self.integration == 'home_assistant':
            return self._ha_get_status(device_id)
        elif self.integration == 'mqtt':
            return self._mqtt_get_status(device_id)
        else:
            return self._mock_get_status(device_id)
    
    def set_temperature(self, device: str, temperature: float) -> Dict[str, Any]:
        """
        Set temperature for climate devices
        
        Args:
            device: Device ID or name
            temperature: Target temperature in Celsius
            
        Returns:
            Result dictionary
        """
        device_id = self._resolve_device_id(device)
        
        if not device_id:
            return {
                'success': False,
                'error': f"Device '{device}' not found"
            }
        
        device_info = self.devices.get(device_id, {})
        if device_info.get('type') != 'climate':
            return {
                'success': False,
                'error': f"Device '{device_id}' is not a climate device"
            }
        
        try:
            if self.integration == 'home_assistant':
                result = self._ha_set_temperature(device_id, temperature)
            else:
                result = self._mock_set_temperature(device_id, temperature)
            
            if result['success']:
                self.logger.info(f"✅ Set {device_id} temperature to {temperature}°C")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to set temperature: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _resolve_device_id(self, device: str) -> Optional[str]:
        """
        Resolve device name to device ID
        
        Args:
            device: Device name or ID
            
        Returns:
            Device ID or None if not found
        """
        device_lower = device.lower().replace(' ', '_')
        
        # Check if it's already a device ID
        if device_lower in self.devices:
            return device_lower
        
        # Search by name
        for device_id, device_info in self.devices.items():
            if device_info.get('name', '').lower() == device.lower():
                return device_id
            if device_lower in device_id.lower():
                return device_id
        
        return None
    
    # Home Assistant integration methods
    def _ha_turn_on(self, device_id: str) -> Dict[str, Any]:
        """Turn on device via Home Assistant"""
        try:
            headers = {
                'Authorization': f'Bearer {self.ha_token}',
                'Content-Type': 'application/json'
            }
            
            domain = device_id.split('.')[0]
            data = {'entity_id': device_id}
            
            response = requests.post(
                f'{self.ha_url}/api/services/{domain}/turn_on',
                headers=headers,
                json=data,
                timeout=5
            )
            
            return {
                'success': response.status_code == 200,
                'device': device_id,
                'state': 'on'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _ha_turn_off(self, device_id: str) -> Dict[str, Any]:
        """Turn off device via Home Assistant"""
        try:
            headers = {
                'Authorization': f'Bearer {self.ha_token}',
                'Content-Type': 'application/json'
            }
            
            domain = device_id.split('.')[0]
            data = {'entity_id': device_id}
            
            response = requests.post(
                f'{self.ha_url}/api/services/{domain}/turn_off',
                headers=headers,
                json=data,
                timeout=5
            )
            
            return {
                'success': response.status_code == 200,
                'device': device_id,
                'state': 'off'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _ha_get_status(self, device_id: str) -> Dict[str, Any]:
        """Get device status from Home Assistant"""
        try:
            headers = {
                'Authorization': f'Bearer {self.ha_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f'{self.ha_url}/api/states/{device_id}',
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                state = response.json()
                return {
                    'success': True,
                    'device': device_id,
                    'state': state['state'],
                    'attributes': state.get('attributes', {})
                }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _ha_set_temperature(self, device_id: str, temperature: float) -> Dict[str, Any]:
        """Set temperature via Home Assistant"""
        try:
            headers = {
                'Authorization': f'Bearer {self.ha_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'entity_id': device_id,
                'temperature': temperature
            }
            
            response = requests.post(
                f'{self.ha_url}/api/services/climate/set_temperature',
                headers=headers,
                json=data,
                timeout=5
            )
            
            return {
                'success': response.status_code == 200,
                'device': device_id,
                'temperature': temperature
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # MQTT integration methods
    def _mqtt_turn_on(self, device_id: str) -> Dict[str, Any]:
        """Turn on device via MQTT"""
        # TODO: Implement MQTT control
        return {'success': False, 'error': 'MQTT control not yet implemented'}
    
    def _mqtt_turn_off(self, device_id: str) -> Dict[str, Any]:
        """Turn off device via MQTT"""
        # TODO: Implement MQTT control
        return {'success': False, 'error': 'MQTT control not yet implemented'}
    
    def _mqtt_get_status(self, device_id: str) -> Dict[str, Any]:
        """Get device status via MQTT"""
        # TODO: Implement MQTT status
        return {'success': False, 'error': 'MQTT status not yet implemented'}
    
    # Mock integration methods
    def _mock_turn_on(self, device_id: str) -> Dict[str, Any]:
        """Turn on mock device"""
        if device_id in self.devices:
            self.devices[device_id]['state'] = 'on'
            return {
                'success': True,
                'device': device_id,
                'state': 'on',
                'message': f"Mock: Turned on {self.devices[device_id]['name']}"
            }
        return {'success': False, 'error': 'Device not found'}
    
    def _mock_turn_off(self, device_id: str) -> Dict[str, Any]:
        """Turn off mock device"""
        if device_id in self.devices:
            self.devices[device_id]['state'] = 'off'
            return {
                'success': True,
                'device': device_id,
                'state': 'off',
                'message': f"Mock: Turned off {self.devices[device_id]['name']}"
            }
        return {'success': False, 'error': 'Device not found'}
    
    def _mock_get_status(self, device_id: str) -> Dict[str, Any]:
        """Get mock device status"""
        if device_id in self.devices:
            return {
                'success': True,
                'device': device_id,
                **self.devices[device_id]
            }
        return {'success': False, 'error': 'Device not found'}
    
    def _mock_set_temperature(self, device_id: str, temperature: float) -> Dict[str, Any]:
        """Set mock device temperature"""
        if device_id in self.devices:
            self.devices[device_id]['temperature'] = temperature
            self.devices[device_id]['state'] = 'on'
            return {
                'success': True,
                'device': device_id,
                'temperature': temperature,
                'message': f"Mock: Set {self.devices[device_id]['name']} to {temperature}°C"
            }
        return {'success': False, 'error': 'Device not found'}


def create_smart_home_control(config: Dict[str, Any] = None, logger: logging.Logger = None) -> SmartHomeControl:
    """
    Factory function to create SmartHomeControl instance
    
    Args:
        config: Configuration dictionary
        logger: Logger instance
        
    Returns:
        SmartHomeControl instance
    """
    return SmartHomeControl(config, logger)


# For testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("smart_home_test")
    
    # Test with mock devices
    config = {
        'smart_home': {
            'integration': 'mock'
        }
    }
    
    smart_home = SmartHomeControl(config, logger)
    
    print("\n=== Smart Home Control Test ===")
    
    # Discover devices
    devices = smart_home.discover_devices()
    print(f"\nDiscovered {len(devices)} devices:")
    for device in devices:
        print(f"  - {device['name']} ({device['id']}): {device['state']}")
    
    # Turn on kettle
    print("\n=== Testing Device Control ===")
    result = smart_home.turn_on('kettle')
    print(f"Turn on kettle: {result}")
    
    # Get status
    status = smart_home.get_status('kettle')
    print(f"Kettle status: {status}")
    
    # Turn off kettle
    result = smart_home.turn_off('kettle')
    print(f"Turn off kettle: {result}")
    
    # Set AC temperature
    result = smart_home.set_temperature('ac', 24)
    print(f"Set AC temperature: {result}")
    
    print("\n✅ Smart home control test complete!")
