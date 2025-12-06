# Test Suite for Network Scanner
# Tests network scanning functionality for Guardian Node

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from guardian_interpreter.network_scanner import create_network_scanner, NetworkScanner, MockNetworkScanner


@pytest.fixture
def scanner():
    """Create a network scanner instance for testing"""
    return create_network_scanner()


def test_scanner_initialization(scanner):
    """Test that scanner initializes correctly"""
    assert scanner is not None
    assert hasattr(scanner, 'discover_local_network')
    assert hasattr(scanner, 'scan_host_ports')
    assert hasattr(scanner, 'vulnerability_scan')


def test_scanner_availability(scanner):
    """Test scanner availability check"""
    # Should work with either real or mock implementation
    result = scanner.is_available()
    assert isinstance(result, bool)


def test_check_nmap_binary(scanner):
    """Test Nmap binary detection"""
    result = scanner.check_nmap_binary()
    assert isinstance(result, bool)


def test_discover_local_network(scanner):
    """Test network discovery"""
    # Use a small range for testing
    devices = scanner.discover_local_network("192.168.1.1/32")
    
    assert isinstance(devices, list)
    # Should return at least empty list
    assert devices is not None


def test_scan_host_ports(scanner):
    """Test port scanning"""
    # Scan localhost on common ports
    result = scanner.scan_host_ports("127.0.0.1", "80,443")
    
    assert isinstance(result, dict)
    assert 'host' in result
    assert result['host'] == "127.0.0.1"


def test_vulnerability_scan(scanner):
    """Test vulnerability scanning"""
    # Basic scan on localhost
    result = scanner.vulnerability_scan("127.0.0.1", "basic")
    
    assert isinstance(result, dict)
    assert 'host' in result


def test_quick_network_assessment(scanner):
    """Test quick network assessment"""
    # Assess a single host
    result = scanner.quick_network_assessment("192.168.1.1/32")
    
    assert isinstance(result, dict)
    assert 'network_range' in result
    assert 'recommendations' in result


def test_export_results(scanner):
    """Test results export"""
    test_results = {
        'test': 'data',
        'timestamp': '2025-12-05'
    }
    
    output_file = scanner.export_results(test_results, "test_scan.json")
    
    # Should return path or None
    assert output_file is None or isinstance(output_file, str)


def test_get_scan_summary(scanner):
    """Test scan summary generation"""
    test_results = {
        'host': '192.168.1.1',
        'status': 'up',
        'open_ports': [],
        'total_open_ports': 0
    }
    
    summary = scanner.get_scan_summary(test_results)
    
    assert isinstance(summary, str)
    assert len(summary) > 0


def test_mock_scanner():
    """Test mock scanner implementation"""
    mock = MockNetworkScanner()
    
    assert not mock.is_available()
    assert not mock.check_nmap_binary()
    
    devices = mock.discover_local_network()
    assert isinstance(devices, list)
    
    result = mock.scan_host_ports("127.0.0.1")
    assert isinstance(result, dict)


def test_scanner_error_handling(scanner):
    """Test error handling with invalid inputs"""
    # Invalid network range
    devices = scanner.discover_local_network("invalid")
    assert isinstance(devices, list)
    
    # Invalid host
    result = scanner.scan_host_ports("999.999.999.999")
    assert isinstance(result, dict)


def test_risk_assessment(scanner):
    """Test device risk assessment"""
    # Test with mock port scan results
    port_scan = {
        'status': 'up',
        'open_ports': [
            {'port': 22, 'protocol': 'tcp'},
            {'port': 80, 'protocol': 'tcp'}
        ]
    }
    
    if hasattr(scanner, '_assess_device_risk'):
        risk = scanner._assess_device_risk(port_scan)
        assert risk in ['low', 'medium', 'high', 'unknown']


def test_severity_assessment(scanner):
    """Test vulnerability severity assessment"""
    if hasattr(scanner, '_assess_severity'):
        # Test high severity
        severity = scanner._assess_severity('vuln-test', 'CRITICAL vulnerability detected')
        assert severity == 'high'
        
        # Test medium severity
        severity = scanner._assess_severity('test', 'WARNING: weak configuration')
        assert severity == 'medium'
        
        # Test low severity
        severity = scanner._assess_severity('info', 'Information disclosure')
        assert severity == 'low'


def test_recommendations_generation(scanner):
    """Test security recommendations generation"""
    test_assessments = [
        {
            'device': {'ip': '192.168.1.100'},
            'risk_level': 'high',
            'port_scan': {
                'open_ports': [
                    {'port': 23, 'protocol': 'tcp'}  # Telnet
                ]
            }
        }
    ]
    
    if hasattr(scanner, '_generate_recommendations'):
        recommendations = scanner._generate_recommendations(test_assessments)
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
