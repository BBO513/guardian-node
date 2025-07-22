#!/usr/bin/env python3
"""
Debug script for parental control protocol module
"""

import sys
import os
sys.path.append('guardian_interpreter')

from protocols.parental_control_protocol import analyze

def debug_analysis():
    """Debug the analysis function"""
    print("Debugging Parental Control Protocol Analysis")
    print("=" * 50)
    
    # Test basic analysis with detailed output
    result = analyze(
        target='test_device',
        check_content_filtering=True,
        check_device_monitoring=False,
        check_time_restrictions=False,
        check_social_media=False
    )
    
    print(f"Status: {result['status']}")
    print(f"Findings: {result['findings']}")
    print(f"Recommendations: {result['recommendations']}")
    print(f"Technical details: {result['technical_details']}")
    
    return result

if __name__ == "__main__":
    try:
        debug_analysis()
    except Exception as e:
        print(f"Debug failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)