#!/usr/bin/env python3
"""
Test suite for Protocol Manager
Tests protocol module loading, execution, and family-friendly reporting
"""

import unittest
import tempfile
import os
import shutil
import logging
from unittest.mock import Mock, patch
from datetime import datetime

from protocol_manager import ProtocolManager, ProtocolAnalysisResult, ProtocolModule

class TestProtocolManager(unittest.TestCase):
    """Test cases for Protocol Manager"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for test protocols
        self.test_dir = tempfile.mkdtemp()
        self.protocols_dir = os.path.join(self.test_dir, 'protocols')
        os.makedirs(self.protocols_dir)
        
        # Mock logger
        self.mock_logger = Mock(spec=logging.Logger)
        self.mock_audit_logger = Mock()
        
        # Test configuration
        self.config = {
            'protocol_modules': {
                'enabled': True,
                'modules_directory': self.protocols_dir,
                'family_friendly_mode': True,
                'max_analysis_results': 100
            }
        }
        
        # Create protocol manager
        self.protocol_manager = ProtocolManager(
            self.config, 
            self.mock_logger, 
            self.mock_audit_logger
        )
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def create_test_protocol_module(self, name, status='secure', findings=None, recommendations=None):
        """Create a test protocol module file"""
        findings = findings or []
        recommendations = recommendations or []
        
        module_content = f'''
def get_metadata():
    return {{
        'name': '{name}',
        'description': 'Test protocol module for {name}',
        'version': '1.0.0',
        'author': 'Test Author',
        'family_friendly': True,
        'supported_protocols': ['{name.lower()}']
    }}

def analyze(target=None, **kwargs):
    import time
    time.sleep(0.001)  # Small delay to ensure execution_time > 0
    return {{
        'status': '{status}',
        'findings': {findings},
        'recommendations': {recommendations},
        'technical_details': {{'target': target, 'kwargs': kwargs}}
    }}
'''
        
        module_path = os.path.join(self.protocols_dir, f'{name.lower()}_protocol.py')
        with open(module_path, 'w') as f:
            f.write(module_content)
        
        return module_path
    
    def test_protocol_manager_initialization(self):
        """Test protocol manager initialization"""
        self.assertIsNotNone(self.protocol_manager)
        self.assertEqual(self.protocol_manager.family_mode, True)
        self.assertEqual(len(self.protocol_manager.protocol_modules), 0)
        self.assertEqual(len(self.protocol_manager.analysis_results), 0)
    
    def test_load_protocol_modules(self):
        """Test loading protocol modules"""
        # Create test modules
        self.create_test_protocol_module('TestProtocol1')
        self.create_test_protocol_module('TestProtocol2')
        
        # Load modules
        loaded_count = self.protocol_manager.load_protocol_modules()
        
        # Verify loading
        self.assertEqual(loaded_count, 2)
        self.assertEqual(len(self.protocol_manager.protocol_modules), 2)
        self.assertIn('testprotocol1_protocol', self.protocol_manager.protocol_modules)
        self.assertIn('testprotocol2_protocol', self.protocol_manager.protocol_modules)
    
    def test_list_protocol_modules(self):
        """Test listing protocol modules"""
        # Create and load test module
        self.create_test_protocol_module('TestProtocol')
        self.protocol_manager.load_protocol_modules()
        
        # List modules
        modules = self.protocol_manager.list_protocol_modules()
        
        # Verify listing
        self.assertEqual(len(modules), 1)
        self.assertEqual(modules[0]['name'], 'TestProtocol')
        self.assertEqual(modules[0]['description'], 'Test protocol module for TestProtocol')
        self.assertTrue(modules[0]['family_friendly'])
    
    def test_run_protocol_analysis_success(self):
        """Test successful protocol analysis"""
        # Create test module with findings
        findings = [
            {'severity': 'medium', 'title': 'Test Finding', 'description': 'Test description'}
        ]
        recommendations = ['Test recommendation']
        
        self.create_test_protocol_module(
            'TestProtocol', 
            status='warning', 
            findings=findings, 
            recommendations=recommendations
        )
        self.protocol_manager.load_protocol_modules()
        
        # Run analysis
        result = self.protocol_manager.run_protocol_analysis(
            'testprotocol_protocol', 
            target='192.168.1.1'
        )
        
        # Verify result
        self.assertIsNotNone(result)
        self.assertEqual(result.protocol_name, 'testprotocol_protocol')
        self.assertEqual(result.status, 'warning')
        self.assertEqual(len(result.findings), 1)
        self.assertEqual(len(result.recommendations), 1)
        self.assertIn('Test recommendation', result.recommendations)
        self.assertIsInstance(result.timestamp, datetime)
        self.assertGreater(result.execution_time, 0)
    
    def test_run_protocol_analysis_nonexistent_module(self):
        """Test running analysis on non-existent module"""
        result = self.protocol_manager.run_protocol_analysis('nonexistent_module')
        
        # Verify failure
        self.assertIsNone(result)
        self.mock_logger.error.assert_called()
    
    def test_family_friendly_summary_generation(self):
        """Test family-friendly summary generation"""
        # Test secure status
        summary = self.protocol_manager._generate_family_friendly_summary(
            'TestProtocol', 'secure', [], []
        )
        self.assertIn('Great news', summary)
        self.assertIn('looks good', summary)
        
        # Test warning status with findings
        findings = [{'severity': 'medium', 'description': 'Test finding'}]
        recommendations = ['Test recommendation']
        summary = self.protocol_manager._generate_family_friendly_summary(
            'TestProtocol', 'warning', findings, recommendations
        )
        self.assertIn('could be improved', summary)
        self.assertIn('1 item to review', summary)
        self.assertIn('1 recommendation', summary)
        
        # Test critical status
        summary = self.protocol_manager._generate_family_friendly_summary(
            'TestProtocol', 'critical', [], []
        )
        self.assertIn('serious security issues', summary)
        self.assertIn('need attention', summary)
    
    def test_format_family_friendly_report(self):
        """Test family-friendly report formatting"""
        # Create test result
        result = ProtocolAnalysisResult(
            protocol_name='TestProtocol',
            status='warning',
            findings=[{'severity': 'medium', 'description': 'Test finding'}],
            recommendations=['Test recommendation'],
            family_friendly_summary='Test summary',
            technical_details={'test': 'data'},
            timestamp=datetime.now(),
            execution_time=1.5
        )
        
        # Format report
        report = self.protocol_manager._format_family_friendly_report(result, detailed=True)
        
        # Verify report content
        self.assertIn('Testprotocol Security Check', report)
        self.assertIn('WARNING', report)
        self.assertIn('Test summary', report)
        self.assertIn('What You Can Do', report)
        self.assertIn('Test recommendation', report)
        self.assertIn('Detailed Findings', report)
        self.assertIn('Test finding', report)
    
    def test_format_technical_report(self):
        """Test technical report formatting"""
        # Disable family mode
        self.protocol_manager.family_mode = False
        
        # Create test result
        result = ProtocolAnalysisResult(
            protocol_name='TestProtocol',
            status='warning',
            findings=[{'severity': 'medium', 'description': 'Test finding'}],
            recommendations=['Test recommendation'],
            family_friendly_summary='Test summary',
            technical_details={'test': 'data'},
            timestamp=datetime.now(),
            execution_time=1.5
        )
        
        # Format report
        report = self.protocol_manager._format_technical_report(result, detailed=True)
        
        # Verify report content
        self.assertIn('Protocol Analysis Report: TestProtocol', report)
        self.assertIn('Status: warning', report)
        self.assertIn('Execution Time: 1.50s', report)
        self.assertIn('Findings:', report)
        self.assertIn('Recommendations:', report)
        self.assertIn('Technical Details:', report)
    
    def test_get_analysis_results(self):
        """Test getting analysis results"""
        # Create and run test analysis
        self.create_test_protocol_module('TestProtocol')
        self.protocol_manager.load_protocol_modules()
        
        result1 = self.protocol_manager.run_protocol_analysis('testprotocol_protocol')
        result2 = self.protocol_manager.run_protocol_analysis('testprotocol_protocol')
        
        # Get all results
        all_results = self.protocol_manager.get_analysis_results()
        self.assertEqual(len(all_results), 2)
        
        # Get results for specific module
        module_results = self.protocol_manager.get_analysis_results('testprotocol_protocol')
        self.assertEqual(len(module_results), 2)
        
        # Get limited results
        limited_results = self.protocol_manager.get_analysis_results(limit=1)
        self.assertEqual(len(limited_results), 1)
    
    def test_get_protocol_summary(self):
        """Test getting protocol summary"""
        # Create and load test modules
        self.create_test_protocol_module('TestProtocol1')
        self.create_test_protocol_module('TestProtocol2')
        self.protocol_manager.load_protocol_modules()
        
        # Run some analyses
        self.protocol_manager.run_protocol_analysis('testprotocol1_protocol')
        self.protocol_manager.run_protocol_analysis('testprotocol2_protocol')
        
        # Get summary
        summary = self.protocol_manager.get_protocol_summary()
        
        # Verify summary
        self.assertEqual(summary['modules_loaded'], 2)
        self.assertEqual(summary['total_analyses'], 2)
        self.assertIn('status_breakdown', summary)
        self.assertIn('recent_results', summary)
        self.assertTrue(summary['family_friendly_mode'])
    
    def test_enable_disable_family_mode(self):
        """Test enabling and disabling family mode"""
        # Test enabling family mode
        self.protocol_manager.disable_family_mode()
        self.assertFalse(self.protocol_manager.family_mode)
        
        self.protocol_manager.enable_family_mode()
        self.assertTrue(self.protocol_manager.family_mode)
        
        # Verify logging calls
        self.mock_logger.info.assert_called()
        self.mock_audit_logger.log_system_event.assert_called()
    
    def test_protocol_module_with_error(self):
        """Test protocol module that raises an error"""
        # Create module that raises an error
        module_content = '''
def get_metadata():
    return {
        'name': 'ErrorProtocol',
        'description': 'Protocol that raises an error',
        'version': '1.0.0',
        'author': 'Test Author',
        'family_friendly': True,
        'supported_protocols': ['error']
    }

def analyze(target=None, **kwargs):
    raise Exception("Test error")
'''
        
        module_path = os.path.join(self.protocols_dir, 'error_protocol.py')
        with open(module_path, 'w') as f:
            f.write(module_content)
        
        # Load and run module
        self.protocol_manager.load_protocol_modules()
        result = self.protocol_manager.run_protocol_analysis('error_protocol')
        
        # Verify error handling
        self.assertIsNotNone(result)
        self.assertEqual(result.status, 'error')
        self.assertIn('Test error', result.technical_details['error'])
        self.assertIn('Unable to complete', result.family_friendly_summary)

if __name__ == '__main__':
    unittest.main()