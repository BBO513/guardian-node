#!/usr/bin/env python3
"""
Simple test script for parental control protocol module
"""

import sys
import os
sys.path.append('guardian_interpreter')

from protocols.parental_control_protocol import get_metadata, analyze

def test_basic_functionality():
    """Test basic functionality of the parental control protocol"""
    print("Testing Parental Control Protocol Module")
    print("=" * 50)
    
    # Test metadata
    print("1. Testing metadata...")
    metadata = get_metadata()
    print(f"   Module name: {metadata['name']}")
    print(f"   Version: {metadata['version']}")
    print(f"   Supported protocols: {metadata['supported_protocols']}")
    print("   ✓ Metadata test passed")
    
    # Test basic analysis
    print("\n2. Testing basic analysis...")
    result = analyze(
        target='test_device',
        check_content_filtering=True,
        check_device_monitoring=False,
        check_time_restrictions=False,
        check_social_media=False
    )
    
    print(f"   Status: {result['status']}")
    print(f"   Findings count: {len(result['findings'])}")
    print(f"   Recommendations count: {len(result['recommendations'])}")
    print("   ✓ Basic analysis test passed")
    
    # Test full analysis
    print("\n3. Testing full analysis...")
    full_result = analyze(target='test_device')
    
    print(f"   Status: {full_result['status']}")
    print(f"   Findings count: {len(full_result['findings'])}")
    print(f"   Recommendations count: {len(full_result['recommendations'])}")
    print("   ✓ Full analysis test passed")
    
    print("\n" + "=" * 50)
    print("All tests passed successfully!")
    
    return True

if __name__ == "__main__":
    try:
        test_basic_functionality()
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)