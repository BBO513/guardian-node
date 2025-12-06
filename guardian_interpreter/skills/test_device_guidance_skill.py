"""
Unit tests for Device Guidance Skill
Tests the device security guidance functionality for family cybersecurity.
"""

import unittest
import sys
import os

# Add the skills directory to the path
sys.path.append(os.path.dirname(__file__))

from device_guidance_skill import (
    DeviceSecurityDatabase,
    DeviceSecurityFormatter,
    DeviceGuidanceSkill,
    run
)

class TestDeviceSecurityDatabase(unittest.TestCase):
    """Test the DeviceSecurityDatabase class"""
    
    def setUp(self):
        self.db = DeviceSecurityDatabase()
    
    def test_get_device_exact_match(self):
        """Test getting device with exact match"""
        device = self.db.get_device('smartphone')
        self.assertIsNotNone(device)
        self.assertEqual(device['name'], 'Smartphones (iPhone/Android)')
        self.assertIn('security_features', device)
        self.assertIn('age_specific', device)
    
    def test_get_device_common_name(self):
        """Test getting device with common name"""
        device = self.db.get_device('phone')
        self.assertIsNotNone(device)
        self.assertEqual(device['device_id'], 'smartphone')
    
    def test_get_device_not_found(self):
        """Test getting non-existent device"""
        device = self.db.get_device('nonexistent')
        self.assertIsNone(device)
    
    def test_search_devices(self):
        """Test searching for devices"""
        # Search for phone
        results = self.db.search_devices('phone')
        self.assertGreater(len(results), 0)
        
        # Search for computer
        results = self.db.search_devices('computer')
        self.assertGreater(len(results), 0)
        
        # Search for something that doesn't exist
        results = self.db.search_devices('xyznothinghere')
        self.assertEqual(len(results), 0)
    
    def test_device_structure(self):
        """Test that all devices have required structure"""
        for device_id, device_data in self.db.devices.items():
            self.assertIn('name', device_data)
            self.assertIn('common_names', device_data)
            self.assertIn('security_features', device_data)
            self.assertIn('age_specific', device_data)
            
            # Check security features structure
            for feature_id, feature in device_data['security_features'].items():
                self.assertIn('name', feature)
                self.assertIn('description', feature)
                self.assertIn('importance', feature)
                self.assertIn('setup_difficulty', feature)
            
            # Check age-specific structure
            for age_group, recommendations in device_data['age_specific'].items():
                self.assertIsInstance(recommendations, list)
                self.assertGreater(len(recommendations), 0)

class TestDeviceSecurityFormatter(unittest.TestCase):
    """Test the DeviceSecurityFormatter class"""
    
    def setUp(self):
        self.formatter = DeviceSecurityFormatter()
        self.sample_device = {
            'name': 'Test Device',
            'security_features': {
                'feature1': {
                    'name': 'Test Feature',
                    'description': 'A test security feature',
                    'importance': 'critical',
                    'setup_difficulty': 'easy'
                }
            },
            'age_specific': {
                'child': ['Test recommendation for children'],
                'adult': ['Test recommendation for adults']
            }
        }
    
    def test_format_device_overview(self):
        """Test formatting device overview"""
        overview = self.formatter.format_device_overview(self.sample_device)
        
        self.assertIn('Test Device', overview)
        self.assertIn('Test Feature', overview)
        self.assertIn('A test security feature', overview)
        self.assertIn('🔴', overview)  # Critical importance emoji
        self.assertIn('✅', overview)  # Easy difficulty emoji
    
    def test_format_age_specific_guidance_all(self):
        """Test formatting age-specific guidance for all ages"""
        guidance = self.formatter.format_age_specific_guidance(self.sample_device)
        
        self.assertIn('Family-Specific Recommendations', guidance)
        self.assertIn('For Childs:', guidance)
        self.assertIn('For Adults:', guidance)
        self.assertIn('Test recommendation for children', guidance)
        self.assertIn('Test recommendation for adults', guidance)
    
    def test_format_age_specific_guidance_specific(self):
        """Test formatting age-specific guidance for specific age"""
        guidance = self.formatter.format_age_specific_guidance(self.sample_device, 'child')
        
        self.assertIn('For Childs:', guidance)
        self.assertIn('Test recommendation for children', guidance)
        self.assertNotIn('Test recommendation for adults', guidance)
    
    def test_format_quick_setup_guide(self):
        """Test formatting quick setup guide"""
        guide = self.formatter.format_quick_setup_guide(self.sample_device)
        
        self.assertIn('Quick Setup Priority List', guide)
        self.assertIn('1. Test Feature', guide)
        self.assertIn('Easy to set up', guide)

class TestDeviceGuidanceSkill(unittest.TestCase):
    """Test the main DeviceGuidanceSkill class"""
    
    def setUp(self):
        self.skill = DeviceGuidanceSkill()
    
    def test_get_device_guidance_found(self):
        """Test getting guidance for existing device"""
        guidance = self.skill.get_device_guidance('smartphone')
        
        self.assertIsInstance(guidance, str)
        self.assertIn('Smartphones', guidance)
        self.assertIn('Security Guide', guidance)
        self.assertIn('Essential Security Features', guidance)
        self.assertIn('Family-Specific Recommendations', guidance)
        self.assertIn('Quick Setup Priority List', guidance)
    
    def test_get_device_guidance_with_age(self):
        """Test getting guidance with specific age group"""
        guidance = self.skill.get_device_guidance('smartphone', 'child')
        
        self.assertIsInstance(guidance, str)
        self.assertIn('Smartphones', guidance)
        self.assertIn('For Childs:', guidance)
    
    def test_get_device_guidance_not_found(self):
        """Test getting guidance for non-existent device"""
        guidance = self.skill.get_device_guidance('nonexistentdevice')
        
        self.assertIsInstance(guidance, str)
        self.assertIn("couldn't find", guidance)
        self.assertIn('I can help with these device types', guidance)
    
    def test_get_general_device_security(self):
        """Test getting general device security overview"""
        overview = self.skill.get_general_device_security()
        
        self.assertIsInstance(overview, str)
        self.assertIn('Family Device Security Overview', overview)
        self.assertIn('Smartphones', overview)
        self.assertIn('Computers', overview)

class TestRunFunction(unittest.TestCase):
    """Test the main run function"""
    
    def test_run_no_args(self):
        """Test run function with no arguments"""
        result = run()
        self.assertIsInstance(result, str)
        self.assertIn('Family Device Security Overview', result)
    
    def test_run_specific_device(self):
        """Test run function with specific device"""
        result = run('smartphone')
        self.assertIsInstance(result, str)
        self.assertIn('Smartphones', result)
        self.assertIn('Security Guide', result)
    
    def test_run_with_age_keyword(self):
        """Test run function with age keyword in query"""
        result = run('smartphone', 'for', 'child')
        self.assertIsInstance(result, str)
        self.assertIn('Smartphones', result)
    
    def test_run_general_query(self):
        """Test run function with general query"""
        result = run('general', 'overview')
        self.assertIsInstance(result, str)
        self.assertIn('Family Device Security Overview', result)
    
    def test_run_multiple_devices(self):
        """Test run function with query that might match multiple devices"""
        result = run('smart')
        self.assertIsInstance(result, str)
        # Should either find smart home devices or show options
        self.assertTrue(len(result) > 50)
    
    def test_run_error_handling(self):
        """Test run function error handling"""
        # This should not raise an exception
        result = run('some', 'complex', 'query', 'that', 'might', 'cause', 'issues')
        self.assertIsInstance(result, str)
    
    def test_run_with_kwargs(self):
        """Test run function with keyword arguments"""
        result = run('smartphone', age_group='teen')
        self.assertIsInstance(result, str)
        self.assertIn('Smartphones', result)

class TestDeviceTypes(unittest.TestCase):
    """Test that all major device types are covered"""
    
    def setUp(self):
        self.skill = DeviceGuidanceSkill()
    
    def test_smartphone_guidance(self):
        """Test smartphone guidance"""
        result = run('smartphone')
        self.assertIn('Smartphones', result)
        self.assertIn('Screen Lock', result)
    
    def test_tablet_guidance(self):
        """Test tablet guidance"""
        result = run('tablet')
        self.assertIn('Tablets', result)
        self.assertIn('Screen Lock', result)
    
    def test_computer_guidance(self):
        """Test computer guidance"""
        result = run('computer')
        self.assertIn('Computers', result)
        self.assertIn('Antivirus', result)
    
    def test_smart_home_guidance(self):
        """Test smart home guidance"""
        result = run('smart home')
        self.assertIn('Smart Home', result)
        self.assertIn('Default Passwords', result)
    
    def test_router_guidance(self):
        """Test router guidance"""
        result = run('router')
        self.assertIn('Router', result)
        self.assertIn('Admin Password', result)

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)