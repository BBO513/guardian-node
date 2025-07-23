#!/usr/bin/env python3
"""
Test suite for Home Network Protocol Modules
Tests router security, WiFi security, and IoT device analysis modules
"""

import unittest
import tempfile
import os
import shutil
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Import the protocol modules
import sys
sys.path.append('protocols')

from protocols import router_security_protocol
from protocols import wifi_security_protocol
from protocols import iot_security_protocol

class TestRouterSecurityProtocol(unittest.TestCase):
    """Test cases for Router Security Protocol"""
    
    def test_get_metadata(self):
        """Test router security protocol metadata"""
        metadata = router_security_protocol.get_metadata()
        
        self.assertEqual(metadata['name'], 'Router Security Analyzer')
        self.assertTrue(metadata['family_friendly'])
        self.assertIn('http', metadata['supported_protocols'])
        self.assertIn('https', metadata['supported_protocols'])
    
    @patch('protocols.router_security_protocol._detect_router_ip')
    @patch('protocols.router_security_protocol._is_router_reachable')
    def test_analyze_with_auto_detect(self, mock_reachable, mock_detect):
        """Test router analysis with auto-detection"""
        mock_detect.return_value = '192.168.1.1'
        mock_reachable.return_value = True
        
        with patch.multiple('protocols.router_security_protocol',
                          _check_default_passwords=Mock(return_value=[]),
                          _check_wifi_encryption=Mock(return_value=[]),
                          _check_open_ports=Mock(return_value=[]),
                          _check_firmware_info=Mock(return_value=[]),
                          _check_upnp_security=Mock(return_value=[])):
            
            result = router_security_protocol.analyze()
            
            self.assertEqual(result['status'], 'secure')
            self.assertIn('technical_details', result)
            self.assertEqual(result['technical_details']['router_ip'], '192.168.1.1')
    
    @patch('protocols.router_security_protocol._is_router_reachable')
    def test_analyze_unreachable_router(self, mock_reachable):
        """Test router analysis with unreachable router"""
        mock_reachable.return_value = False
        
        result = router_security_protocol.analyze(target='192.168.1.1')
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('Unable to reach router', result['recommendations'][0])
    
    def test_determine_router_status(self):
        """Test router status determination"""
        # Test secure status
        status = router_security_protocol._determine_router_status([])
        self.assertEqual(status, 'secure')
        
        # Test critical status
        critical_finding = [{'severity': 'critical', 'title': 'Test'}]
        status = router_security_protocol._determine_router_status(critical_finding)
        self.assertEqual(status, 'critical')
        
        # Test warning status
        medium_findings = [{'severity': 'medium', 'title': 'Test'}]
        status = router_security_protocol._determine_router_status(medium_findings)
        self.assertEqual(status, 'warning')
    
    @patch('subprocess.run')
    def test_detect_router_ip_windows(self, mock_run):
        """Test router IP detection on Windows"""
        # Mock ipconfig output
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = """
Windows IP Configuration

Ethernet adapter Ethernet:
   Default Gateway . . . . . . . . . : 192.168.1.1
"""
        
        router_ip = router_security_protocol._detect_router_ip()
        self.assertEqual(router_ip, '192.168.1.1')
    
    def test_generate_router_recommendations(self):
        """Test router recommendation generation"""
        findings = [
            {'recommendation': 'Change default password'},
            {'recommendation': 'Update firmware'}
        ]
        
        recommendations = router_security_protocol._generate_router_recommendations(findings)
        
        self.assertIn('Change default password', recommendations)
        self.assertIn('Update firmware', recommendations)
        self.assertGreater(len(recommendations), 2)  # Should include general recommendations

class TestWiFiSecurityProtocol(unittest.TestCase):
    """Test cases for WiFi Security Protocol"""
    
    def test_get_metadata(self):
        """Test WiFi security protocol metadata"""
        metadata = wifi_security_protocol.get_metadata()
        
        self.assertEqual(metadata['name'], 'WiFi Security Analyzer')
        self.assertTrue(metadata['family_friendly'])
        self.assertIn('wifi', metadata['supported_protocols'])
        self.assertIn('wpa', metadata['supported_protocols'])
    
    def test_determine_wifi_security_level(self):
        """Test WiFi security level determination"""
        # Test insecure configurations
        level = wifi_security_protocol._determine_wifi_security_level('Open', 'None')
        self.assertEqual(level, 'insecure')
        
        level = wifi_security_protocol._determine_wifi_security_level('WEP', 'WEP')
        self.assertEqual(level, 'insecure')
        
        # Test weak configuration
        level = wifi_security_protocol._determine_wifi_security_level('WPA', 'TKIP')
        self.assertEqual(level, 'weak')
        
        # Test secure configuration
        level = wifi_security_protocol._determine_wifi_security_level('WPA2', 'AES')
        self.assertEqual(level, 'secure')
        
        level = wifi_security_protocol._determine_wifi_security_level('WPA3', 'AES')
        self.assertEqual(level, 'secure')
    
    @patch('subprocess.run')
    def test_check_current_wifi_security(self, mock_run):
        """Test current WiFi security check"""
        # Mock netsh commands
        mock_run.side_effect = [
            # First call - show profiles
            Mock(returncode=0, stdout="All User Profile : TestNetwork"),
            # Second call - show interfaces
            Mock(returncode=0, stdout="Profile : TestNetwork"),
            # Third call - show profile details
            Mock(returncode=0, stdout="""
Profile TestNetwork on interface Wi-Fi:
Authentication         : WPA2-Personal
Cipher                 : AES
""")
        ]
        
        findings = wifi_security_protocol._check_current_wifi_security()
        
        self.assertGreater(len(findings), 0)
        # Should find secure network
        secure_findings = [f for f in findings if 'secure' in f.get('title', '').lower()]
        self.assertGreater(len(secure_findings), 0)
    
    def test_analyze_wifi_profile_security(self):
        """Test WiFi profile security analysis"""
        profile_info = """
Profile TestNetwork on interface Wi-Fi:
Authentication         : WPA2-Personal
Cipher                 : AES
"""
        
        findings = wifi_security_protocol._analyze_wifi_profile_security(
            'TestNetwork', profile_info, is_current=True
        )
        
        self.assertGreater(len(findings), 0)
        self.assertEqual(findings[0]['severity'], 'info')
        self.assertIn('Secure WiFi Network', findings[0]['title'])
    
    def test_generate_wifi_recommendations(self):
        """Test WiFi recommendation generation"""
        findings = [
            {'recommendation': 'Use WPA3 encryption'},
            {'recommendation': 'Change default passwords'}
        ]
        
        recommendations = wifi_security_protocol._generate_wifi_recommendations(findings)
        
        self.assertIn('Use WPA3 encryption', recommendations)
        self.assertIn('Change default passwords', recommendations)
        self.assertGreater(len(recommendations), 2)  # Should include general recommendations
    
    def test_determine_wifi_status(self):
        """Test WiFi status determination"""
        # Test secure status
        status = wifi_security_protocol._determine_wifi_status([])
        self.assertEqual(status, 'secure')
        
        # Test critical status
        critical_finding = [{'severity': 'critical', 'title': 'Test'}]
        status = wifi_security_protocol._determine_wifi_status(critical_finding)
        self.assertEqual(status, 'critical')
        
        # Test warning status
        medium_findings = [{'severity': 'medium', 'title': 'Test'} for _ in range(3)]
        status = wifi_security_protocol._determine_wifi_status(medium_findings)
        self.assertEqual(status, 'warning')

class TestIoTSecurityProtocol(unittest.TestCase):
    """Test cases for IoT Security Protocol"""
    
    def test_get_metadata(self):
        """Test IoT security protocol metadata"""
        metadata = iot_security_protocol.get_metadata()
        
        self.assertEqual(metadata['name'], 'IoT Device Security Analyzer')
        self.assertTrue(metadata['family_friendly'])
        self.assertIn('http', metadata['supported_protocols'])
        self.assertIn('upnp', metadata['supported_protocols'])
    
    def test_calculate_network_range(self):
        """Test network range calculation"""
        network_range = iot_security_protocol._calculate_network_range('192.168.1.100', '255.255.255.0')
        self.assertEqual(network_range, '192.168.1.0/24')
        
        network_range = iot_security_protocol._calculate_network_range('10.0.0.50', '255.255.0.0')
        self.assertEqual(network_range, '10.0.0.0/16')
    
    def test_classify_device_type(self):
        """Test device type classification"""
        # Test IP Camera
        device_type = iot_security_protocol._classify_device_type([554, 80], {})
        self.assertEqual(device_type, 'IP Camera')
        
        # Test Router/Gateway
        device_type = iot_security_protocol._classify_device_type([1900, 80], {})
        self.assertEqual(device_type, 'Router/Gateway')
        
        # Test Smart Home Hub
        device_type = iot_security_protocol._classify_device_type([1883], {})
        self.assertEqual(device_type, 'Smart Home Hub')
        
        # Test Network Device
        device_type = iot_security_protocol._classify_device_type([161], {})
        self.assertEqual(device_type, 'Network Device')
        
        # Test Web-enabled device
        device_type = iot_security_protocol._classify_device_type([80], {})
        self.assertEqual(device_type, 'Web-enabled IoT Device')
    
    def test_identify_service(self):
        """Test service identification"""
        # Test HTTP service
        service = iot_security_protocol._identify_service('192.168.1.1', 80)
        self.assertEqual(service['protocol'], 'http')
        self.assertEqual(service['description'], 'Web interface')
        
        # Test HTTPS service
        service = iot_security_protocol._identify_service('192.168.1.1', 443)
        self.assertEqual(service['protocol'], 'https')
        self.assertEqual(service['description'], 'Secure web interface')
        
        # Test RTSP service
        service = iot_security_protocol._identify_service('192.168.1.1', 554)
        self.assertEqual(service['protocol'], 'rtsp')
        self.assertEqual(service['description'], 'Video streaming (camera)')
        
        # Test Telnet service
        service = iot_security_protocol._identify_service('192.168.1.1', 23)
        self.assertEqual(service['protocol'], 'telnet')
        self.assertEqual(service['description'], 'Telnet (insecure)')
    
    def test_analyze_iot_device(self):
        """Test IoT device analysis"""
        device = {
            'ip': '192.168.1.100',
            'open_ports': [80, 23, 1900],
            'services': {
                80: {'protocol': 'http', 'description': 'Web interface'},
                23: {'protocol': 'telnet', 'description': 'Telnet (insecure)'},
                1900: {'protocol': 'upnp', 'description': 'UPnP service'}
            },
            'device_type': 'IoT Device'
        }
        
        findings = iot_security_protocol._analyze_iot_device(device)
        
        self.assertGreater(len(findings), 0)
        
        # Should detect insecure Telnet
        telnet_findings = [f for f in findings if 'Telnet' in f.get('title', '')]
        self.assertGreater(len(telnet_findings), 0)
        self.assertEqual(telnet_findings[0]['severity'], 'high')
        
        # Should detect web interface
        web_findings = [f for f in findings if 'Web Interface' in f.get('title', '')]
        self.assertGreater(len(web_findings), 0)
        
        # Should detect UPnP
        upnp_findings = [f for f in findings if 'UPnP' in f.get('title', '')]
        self.assertGreater(len(upnp_findings), 0)
    
    @patch('protocols.iot_security_protocol._detect_local_network')
    @patch('protocols.iot_security_protocol._scan_network_for_devices')
    def test_analyze_with_devices(self, mock_scan, mock_detect):
        """Test IoT analysis with detected devices"""
        mock_detect.return_value = '192.168.1.0/24'
        mock_scan.return_value = [
            {
                'ip': '192.168.1.100',
                'open_ports': [80],
                'services': {80: {'protocol': 'http', 'description': 'Web interface'}},
                'device_type': 'Web-enabled IoT Device'
            }
        ]
        
        result = iot_security_protocol.analyze()
        
        self.assertIn('status', result)
        self.assertGreater(len(result['findings']), 0)
        self.assertIn('IoT Devices Detected', [f['title'] for f in result['findings']])
    
    @patch('protocols.iot_security_protocol._detect_local_network')
    def test_analyze_network_detection_failure(self, mock_detect):
        """Test IoT analysis when network detection fails"""
        mock_detect.return_value = None
        
        result = iot_security_protocol.analyze()
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('Unable to detect local network', result['recommendations'][0])
    
    def test_generate_iot_recommendations(self):
        """Test IoT recommendation generation"""
        findings = [
            {'recommendation': 'Change default passwords'},
            {'recommendation': 'Update firmware'}
        ]
        devices = [{'ip': '192.168.1.100', 'device_type': 'IoT Device'}]
        
        recommendations = iot_security_protocol._generate_iot_recommendations(findings, devices)
        
        self.assertIn('Change default passwords', recommendations)
        self.assertIn('Update firmware', recommendations)
        self.assertGreater(len(recommendations), 2)  # Should include general recommendations
    
    def test_determine_iot_status(self):
        """Test IoT status determination"""
        # Test secure status
        status = iot_security_protocol._determine_iot_status([])
        self.assertEqual(status, 'secure')
        
        # Test critical status with high severity findings
        high_findings = [{'severity': 'high', 'title': 'Test'} for _ in range(2)]
        status = iot_security_protocol._determine_iot_status(high_findings)
        self.assertEqual(status, 'critical')
        
        # Test warning status
        medium_findings = [{'severity': 'medium', 'title': 'Test'} for _ in range(3)]
        status = iot_security_protocol._determine_iot_status(medium_findings)
        self.assertEqual(status, 'warning')

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)