"""
Unit tests for Parental Control Protocol Module
Tests content filtering, device monitoring, time restrictions, and social media privacy analysis
"""

import unittest
from unittest.mock import patch, MagicMock
import subprocess
import platform
from datetime import datetime
import sys
import os

# Add the guardian_interpreter directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from guardian_interpreter.protocols import parental_control_protocol

class TestParentalControlProtocol(unittest.TestCase):
    """Test cases for Parental Control Protocol module"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_family_profile = {
            'family_id': 'test_family',
            'members': [
                {'name': 'Child1', 'age_group': 'child'},
                {'name': 'Teen1', 'age_group': 'teen'},
                {'name': 'Parent1', 'age_group': 'adult'}
            ]
        }
    
    def test_get_metadata(self):
        """Test module-level get_metadata function"""
        metadata = parental_control_protocol.get_metadata()
        self.assertEqual(metadata['name'], 'Parental Control Protocol')
        self.assertTrue(metadata['family_friendly'])
        self.assertIn('content_filtering', metadata['supported_protocols'])
        self.assertIn('device_monitoring', metadata['supported_protocols'])
        self.assertIn('time_restrictions', metadata['supported_protocols'])
        self.assertIn('social_media_privacy', metadata['supported_protocols'])
        self.assertEqual(metadata['version'], '1.0.0')
        self.assertEqual(metadata['author'], 'Guardian Team')
    
    @patch('guardian_interpreter.protocols.parental_control_protocol._analyze_content_filtering')
    @patch('guardian_interpreter.protocols.parental_control_protocol._analyze_device_monitoring')
    @patch('guardian_interpreter.protocols.parental_control_protocol._analyze_time_restrictions')
    @patch('guardian_interpreter.protocols.parental_control_protocol._analyze_social_media_privacy')
    def test_analyze_all_types(self, mock_social, mock_time, mock_monitoring, mock_content):
        """Test comprehensive analysis of all parental control types"""
        # Mock all analysis functions
        mock_content.return_value = {
            'findings': [{'severity': 'info', 'title': 'Content Finding'}],
            'recommendations': ['Content recommendation'],
            'technical_details': {'content': 'data'}
        }
        mock_monitoring.return_value = {
            'findings': [{'severity': 'medium', 'title': 'Monitoring Finding'}],
            'recommendations': ['Monitoring recommendation'],
            'technical_details': {'monitoring': 'data'}
        }
        mock_time.return_value = {
            'findings': [{'severity': 'low', 'title': 'Time Finding'}],
            'recommendations': ['Time recommendation'],
            'technical_details': {'time': 'data'}
        }
        mock_social.return_value = {
            'findings': [{'severity': 'info', 'title': 'Social Finding'}],
            'recommendations': ['Social recommendation'],
            'technical_details': {'social': 'data'}
        }
        
        result = parental_control_protocol.analyze(target="192.168.1.100", check_type="all")
        
        self.assertIn('status', result)
        self.assertIn('findings', result)
        self.assertIn('recommendations', result)
        self.assertIn('technical_details', result)
        self.assertIsInstance(result['findings'], list)
        self.assertIsInstance(result['recommendations'], list)
        self.assertEqual(len(result['findings']), 4)  # One from each analysis type
        self.assertEqual(len(result['recommendations']), 4)
    
    def test_analyze_content_filtering_only(self):
        """Test content filtering analysis only"""
        with patch('guardian_interpreter.protocols.parental_control_protocol._analyze_content_filtering') as mock_content:
            mock_content.return_value = {
                'findings': [{'severity': 'info', 'title': 'Test Finding'}],
                'recommendations': ['Test recommendation'],
                'technical_details': {'test': 'data'}
            }
            
            result = parental_control_protocol.analyze(check_type="content_filtering")
            
            mock_content.assert_called_once_with({})
            self.assertEqual(len(result['findings']), 1)
            self.assertEqual(len(result['recommendations']), 1)
    
    def test_analyze_device_monitoring_only(self):
        """Test device monitoring analysis only"""
        with patch('guardian_interpreter.protocols.parental_control_protocol._analyze_device_monitoring') as mock_monitoring:
            mock_monitoring.return_value = {
                'findings': [{'severity': 'medium', 'title': 'Monitoring Finding'}],
                'recommendations': ['Monitoring recommendation'],
                'technical_details': {'monitoring': 'data'}
            }
            
            result = parental_control_protocol.analyze(
                check_type="device_monitoring", 
                family_profile=self.sample_family_profile
            )
            
            mock_monitoring.assert_called_once_with(self.sample_family_profile)
            self.assertEqual(len(result['findings']), 1)
    
    def test_analyze_time_restrictions_only(self):
        """Test time restrictions analysis only"""
        with patch('guardian_interpreter.protocols.parental_control_protocol._analyze_time_restrictions') as mock_time:
            mock_time.return_value = {
                'findings': [{'severity': 'low', 'title': 'Time Finding'}],
                'recommendations': ['Time recommendation'],
                'technical_details': {'time': 'data'}
            }
            
            result = parental_control_protocol.analyze(
                check_type="time_restrictions",
                family_profile=self.sample_family_profile
            )
            
            mock_time.assert_called_once_with(self.sample_family_profile)
            self.assertEqual(len(result['findings']), 1)
    
    def test_analyze_social_media_privacy_only(self):
        """Test social media privacy analysis only"""
        with patch('guardian_interpreter.protocols.parental_control_protocol._analyze_social_media_privacy') as mock_social:
            mock_social.return_value = {
                'findings': [{'severity': 'info', 'title': 'Social Finding'}],
                'recommendations': ['Social recommendation'],
                'technical_details': {'social': 'data'}
            }
            
            result = parental_control_protocol.analyze(
                check_type="social_media_privacy",
                family_profile=self.sample_family_profile
            )
            
            mock_social.assert_called_once_with(self.sample_family_profile)
            self.assertEqual(len(result['findings']), 1)
    
    def test_analyze_error_handling(self):
        """Test error handling in analysis"""
        with patch('guardian_interpreter.protocols.parental_control_protocol._analyze_content_filtering') as mock_content:
            mock_content.side_effect = Exception("Test error")
            
            result = parental_control_protocol.analyze(check_type="content_filtering")
            
            self.assertEqual(result['status'], 'error')
            self.assertIn('error', result['technical_details'])
            self.assertTrue(any('Analysis Error' in str(f) for f in result['findings']))
    
    @patch('subprocess.run')
    @patch('platform.system')
    def test_check_dns_filtering_windows(self, mock_platform, mock_subprocess):
        """Test DNS filtering check on Windows"""
        mock_platform.return_value = "Windows"
        mock_subprocess.return_value = MagicMock(
            stdout="Server: 208.67.222.123\nAddress: 208.67.222.123#53",
            returncode=0
        )
        
        result = parental_control_protocol._check_dns_filtering()
        
        self.assertTrue(result['filtered_dns'])
        self.assertEqual(result['service'], 'OpenDNS Family Shield')
        mock_subprocess.assert_called_once()
    
    @patch('subprocess.run')
    @patch('platform.system')
    def test_check_dns_filtering_unix(self, mock_platform, mock_subprocess):
        """Test DNS filtering check on Unix systems"""
        mock_platform.return_value = "Linux"
        mock_subprocess.return_value = MagicMock(
            stdout="185.228.168.168\n185.228.169.168",
            returncode=0
        )
        
        result = parental_control_protocol._check_dns_filtering()
        
        self.assertTrue(result['filtered_dns'])
        self.assertEqual(result['service'], 'CleanBrowsing Family')
    
    @patch('subprocess.run')
    @patch('platform.system')
    def test_check_dns_filtering_no_filter(self, mock_platform, mock_subprocess):
        """Test DNS filtering check when no filtering is detected"""
        mock_platform.return_value = "Linux"
        mock_subprocess.return_value = MagicMock(
            stdout="8.8.8.8\n8.8.4.4",  # Google DNS, no filtering
            returncode=0
        )
        
        result = parental_control_protocol._check_dns_filtering()
        
        self.assertFalse(result['filtered_dns'])
        self.assertIsNone(result['service'])
    
    @patch('subprocess.run')
    @patch('platform.system')
    def test_check_parental_control_software_windows(self, mock_platform, mock_subprocess):
        """Test parental control software detection on Windows"""
        mock_platform.return_value = "Windows"
        mock_subprocess.return_value = MagicMock(
            stdout="qustodio.exe\nnorton.exe\nother.exe",
            returncode=0
        )
        
        result = parental_control_protocol._check_parental_control_software()
        
        self.assertTrue(result['detected'])
        self.assertIn('qustodio', result['software'])
        self.assertIn('norton', result['software'])
    
    @patch('subprocess.run')
    @patch('platform.system')
    def test_check_parental_control_software_unix(self, mock_platform, mock_subprocess):
        """Test parental control software detection on Unix systems"""
        mock_platform.return_value = "Linux"
        mock_subprocess.return_value = MagicMock(
            stdout="qustodio bark circle_home_plus other_process",
            returncode=0
        )
        
        result = parental_control_protocol._check_parental_control_software()
        
        self.assertTrue(result['detected'])
        self.assertIn('qustodio', result['software'])
        self.assertIn('bark', result['software'])
        self.assertIn('circle', result['software'])
    
    @patch('subprocess.run')
    @patch('platform.system')
    def test_detect_monitoring_software(self, mock_platform, mock_subprocess):
        """Test monitoring software detection"""
        mock_platform.return_value = "Linux"
        mock_subprocess.return_value = MagicMock(
            stdout="qustodio bark circle_home_plus other_process",
            returncode=0
        )
        
        result = parental_control_protocol._detect_monitoring_software()
        
        self.assertIn('qustodio', result)
        self.assertIn('bark', result)
        self.assertIn('circle', result)
    
    @patch('subprocess.run')
    @patch('platform.system')
    def test_check_builtin_parental_controls_windows(self, mock_platform, mock_subprocess):
        """Test built-in parental controls check on Windows"""
        mock_platform.return_value = "Windows"
        mock_subprocess.return_value = MagicMock(
            stdout="Microsoft.WindowsFamilyFeatures",
            returncode=0
        )
        
        result = parental_control_protocol._check_builtin_parental_controls()
        
        self.assertTrue(result['enabled'])
        self.assertIn("Windows Family Safety", result['features'])
    
    @patch('subprocess.run')
    @patch('platform.system')
    def test_check_builtin_parental_controls_macos(self, mock_platform, mock_subprocess):
        """Test built-in parental controls check on macOS"""
        mock_platform.return_value = "Darwin"
        mock_subprocess.return_value = MagicMock(
            stdout="screen time settings",
            returncode=0
        )
        
        result = parental_control_protocol._check_builtin_parental_controls()
        
        self.assertTrue(result['enabled'])
        self.assertIn("macOS Screen Time", result['features'])
    
    @patch('subprocess.run')
    @patch('platform.system')
    def test_check_screen_time_controls_macos(self, mock_platform, mock_subprocess):
        """Test screen time controls check on macOS"""
        mock_platform.return_value = "Darwin"
        mock_subprocess.return_value = MagicMock(
            stdout="screen time configuration",
            returncode=0
        )
        
        result = parental_control_protocol._check_screen_time_controls()
        
        self.assertTrue(result['enabled'])
        self.assertIn("macOS Screen Time", result['features'])
    
    @patch('subprocess.run')
    @patch('platform.system')
    def test_check_screen_time_controls_windows(self, mock_platform, mock_subprocess):
        """Test screen time controls check on Windows"""
        mock_platform.return_value = "Windows"
        mock_subprocess.return_value = MagicMock(
            stdout="Microsoft.WindowsFamilyFeatures",
            returncode=0
        )
        
        result = parental_control_protocol._check_screen_time_controls()
        
        self.assertTrue(result['enabled'])
        self.assertIn("Windows Family Features", result['features'])
    
    def test_get_platform_privacy_recommendations(self):
        """Test social media platform privacy recommendations"""
        recommendations = parental_control_protocol._get_platform_privacy_recommendations()
        
        self.assertIn("Instagram", recommendations)
        self.assertIn("TikTok", recommendations)
        self.assertIn("Snapchat", recommendations)
        self.assertIn("YouTube", recommendations)
        self.assertIn("Discord", recommendations)
        self.assertIn("Facebook", recommendations)
        
        # Check that each platform has recommendations
        for platform, recs in recommendations.items():
            self.assertIsInstance(recs, list)
            self.assertGreater(len(recs), 0)
            
        # Check specific recommendations
        self.assertIn("Set account to private", recommendations["Instagram"])
        self.assertIn("Turn on Restricted Mode", recommendations["YouTube"])
        self.assertIn("Enable Ghost Mode in Snap Map", recommendations["Snapchat"])
    
    def test_get_age_appropriate_social_media_guidance(self):
        """Test age-appropriate social media guidance"""
        result = parental_control_protocol._get_age_appropriate_social_media_guidance(
            self.sample_family_profile['members']
        )
        
        self.assertIn('findings', result)
        self.assertIn('recommendations', result)
        self.assertIn('technical_details', result)
        
        # Should have findings for each family member
        self.assertEqual(len(result['findings']), 3)  # Child, Teen, Adult
        
        # Check that recommendations are age-appropriate
        recommendations_text = ' '.join(result['recommendations'])
        self.assertIn('Child1', recommendations_text)
        self.assertIn('Teen1', recommendations_text)
        self.assertIn('Parent1', recommendations_text)
        
        # Check technical details
        self.assertEqual(result['technical_details']['members_analyzed'], 3)
        self.assertIn('child', result['technical_details']['age_groups'])
        self.assertIn('teen', result['technical_details']['age_groups'])
        self.assertIn('adult', result['technical_details']['age_groups'])
    
    def test_determine_overall_status(self):
        """Test overall status determination"""
        # Test secure status
        findings = []
        status = parental_control_protocol._determine_overall_status(findings)
        self.assertEqual(status, "secure")
        
        # Test warning status
        findings = [{'severity': 'medium'}]
        status = parental_control_protocol._determine_overall_status(findings)
        self.assertEqual(status, "warning")
        
        # Test critical status
        findings = [{'severity': 'high'}]
        status = parental_control_protocol._determine_overall_status(findings)
        self.assertEqual(status, "critical")
        
        # Test critical status with critical severity
        findings = [{'severity': 'critical'}]
        status = parental_control_protocol._determine_overall_status(findings)
        self.assertEqual(status, "critical")
        
        # Test warning with low severity
        findings = [{'severity': 'low'}]
        status = parental_control_protocol._determine_overall_status(findings)
        self.assertEqual(status, "warning")
    
    def test_create_finding_helper(self):
        """Test the _create_finding helper method"""
        finding = parental_control_protocol._create_finding(
            severity="medium",
            title="Test Finding",
            description="Test description",
            recommendation="Test recommendation",
            technical_info={"test": "data"}
        )
        
        self.assertEqual(finding['severity'], "medium")
        self.assertEqual(finding['title'], "Test Finding")
        self.assertEqual(finding['description'], "Test description")
        self.assertEqual(finding['recommendation'], "Test recommendation")
        self.assertEqual(finding['technical_info'], {"test": "data"})
        self.assertIn('timestamp', finding)
    
    def test_error_handling_in_subprocess_calls(self):
        """Test error handling in subprocess calls"""
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.side_effect = subprocess.TimeoutExpired('test', 10)
            
            # Should not raise exception, should return safe defaults
            result = parental_control_protocol._check_dns_filtering()
            self.assertFalse(result['filtered_dns'])
            
            result = parental_control_protocol._check_parental_control_software()
            self.assertFalse(result['detected'])

class TestParentalControlProtocolIntegration(unittest.TestCase):
    """Test integration scenarios for parental control protocol"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_family_profile = {
            'family_id': 'test_family',
            'members': [
                {'name': 'Child1', 'age_group': 'child'},
                {'name': 'Teen1', 'age_group': 'teen'},
                {'name': 'Parent1', 'age_group': 'adult'}
            ]
        }
    
    def test_analyze_content_filtering_integration(self):
        """Test content filtering analysis integration"""
        with patch('guardian_interpreter.protocols.parental_control_protocol._check_dns_filtering') as mock_dns, \
             patch('guardian_interpreter.protocols.parental_control_protocol._check_parental_control_software') as mock_software:
            
            mock_dns.return_value = {'filtered_dns': True, 'service': 'OpenDNS Family Shield', 'dns_server': '208.67.222.123'}
            mock_software.return_value = {'detected': True, 'software': ['qustodio']}
            
            result = parental_control_protocol._analyze_content_filtering()
            
            self.assertIn('findings', result)
            self.assertIn('recommendations', result)
            self.assertIn('technical_details', result)
            
            # Should have positive findings for detected filtering
            findings_text = str(result['findings'])
            self.assertIn('DNS Filtering Active', findings_text)
            self.assertIn('Parental Control Software Found', findings_text)
    
    def test_analyze_device_monitoring_integration(self):
        """Test device monitoring analysis integration"""
        with patch('guardian_interpreter.protocols.parental_control_protocol._detect_monitoring_software') as mock_software, \
             patch('guardian_interpreter.protocols.parental_control_protocol._check_builtin_parental_controls') as mock_builtin:
            
            mock_software.return_value = ['qustodio', 'bark']
            mock_builtin.return_value = {'enabled': True, 'features': ['Screen Time']}
            
            result = parental_control_protocol._analyze_device_monitoring(family_profile=self.sample_family_profile)
            
            self.assertIn('findings', result)
            self.assertIn('recommendations', result)
            self.assertIn('technical_details', result)
            
            # Should have positive findings for detected monitoring
            findings_text = str(result['findings'])
            self.assertIn('Device Monitoring Active', findings_text)
            self.assertIn('Built-in Controls Active', findings_text)
    
    def test_analyze_time_restrictions_integration(self):
        """Test time restrictions analysis integration"""
        with patch('guardian_interpreter.protocols.parental_control_protocol._check_screen_time_controls') as mock_screen, \
             patch('guardian_interpreter.protocols.parental_control_protocol._check_bedtime_restrictions') as mock_bedtime, \
             patch('guardian_interpreter.protocols.parental_control_protocol._check_app_time_limits') as mock_apps:
            
            mock_screen.return_value = {'enabled': True, 'features': ['Screen Time']}
            mock_bedtime.return_value = {'configured': True}
            mock_apps.return_value = {'configured': True, 'apps': ['Social Media']}
            
            result = parental_control_protocol._analyze_time_restrictions(family_profile=self.sample_family_profile)
            
            self.assertIn('findings', result)
            self.assertIn('recommendations', result)
            self.assertIn('technical_details', result)
            
            # Should have positive findings for configured restrictions
            findings_text = str(result['findings'])
            self.assertIn('Screen Time Controls Active', findings_text)
            self.assertIn('Bedtime Restrictions Set', findings_text)
            self.assertIn('App Time Limits Set', findings_text)
    
    def test_analyze_social_media_privacy_integration(self):
        """Test social media privacy analysis integration"""
        result = parental_control_protocol._analyze_social_media_privacy(self.sample_family_profile)
        
        self.assertIn('findings', result)
        self.assertIn('recommendations', result)
        self.assertIn('technical_details', result)
        
        # Should have findings for privacy check and age guidance
        self.assertGreater(len(result['findings']), 0)
        
        # Should have platform-specific recommendations
        recommendations_text = ' '.join(result['recommendations'])
        self.assertIn('Instagram:', recommendations_text)
        self.assertIn('TikTok:', recommendations_text)
        self.assertIn('YouTube:', recommendations_text)
        
        # Should have age-appropriate guidance
        self.assertIn('Child1', recommendations_text)
        self.assertIn('Teen1', recommendations_text)

class TestParentalControlProtocolEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def test_empty_family_profile(self):
        """Test analysis with empty family profile"""
        result = parental_control_protocol.analyze(family_profile={})
        
        self.assertIn('status', result)
        self.assertIn('findings', result)
        self.assertIn('recommendations', result)
    
    def test_malformed_family_profile(self):
        """Test analysis with malformed family profile"""
        malformed_profile = {
            'members': [
                {'name': 'Test'},  # Missing age_group
                {'age_group': 'child'}  # Missing name
            ]
        }
        
        result = parental_control_protocol.analyze(family_profile=malformed_profile)
        
        self.assertIn('status', result)
        # Should handle gracefully without crashing
    
    def test_unknown_check_type(self):
        """Test analysis with unknown check type"""
        result = parental_control_protocol.analyze(check_type="unknown_type")
        
        self.assertIn('status', result)
        self.assertIn('findings', result)
        # Should return minimal results without error
        self.assertEqual(len(result['findings']), 0)
        self.assertEqual(len(result['recommendations']), 0)
    
    def test_network_timeout_scenarios(self):
        """Test network timeout scenarios"""
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.side_effect = subprocess.TimeoutExpired('cmd', 10)
            
            # All network-dependent checks should handle timeouts gracefully
            dns_result = parental_control_protocol._check_dns_filtering()
            self.assertFalse(dns_result['filtered_dns'])
            
            software_result = parental_control_protocol._check_parental_control_software()
            self.assertFalse(software_result['detected'])

if __name__ == '__main__':
    unittest.main()