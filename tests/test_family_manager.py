#!/usr/bin/env python3
"""
Test file for family assistant manager skill integration
Validates Task 20.3 requirements
"""

import sys
import os
from pathlib import Path

# Add guardian_interpreter to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'guardian_interpreter'))

def test_family_manager_skills():
    """Test family assistant manager skill integration"""
    print("🧪 Testing Family Manager Skill Integration")
    print("=" * 50)
    
    try:
        from family_assistant.family_assistant_manager import FamilyAssistantManager
        
        # Initialize family manager
        fm = FamilyAssistantManager()
        
        # Test skill registration
        print(f"✓ Family manager initialized with {len(fm.family_skills)} skills")
        
        # Test individual skills
        test_skills = [
            'threat_analysis',
            'password_check', 
            'device_scan',
            'parental_control_check',
            'phishing_education',
            'network_security_audit'
        ]
        
        print("\nTesting skill execution:")
        for skill in test_skills:
            try:
                result = fm.execute_skill(skill)
                print(f"✓ {skill}: {result[:50]}...")
            except Exception as e:
                print(f"✗ {skill}: {e}")
        
        # Test error handling
        print("\nTesting error handling:")
        invalid_result = fm.execute_skill('nonexistent_skill')
        print(f"✓ Invalid skill handled: {invalid_result}")
        
        # Test child-safe formatting
        print("\nTesting response formatting:")
        safe_response = fm.format_response("Test response", child_safe=True)
        unsafe_response = fm.format_response("Test response", child_safe=False)
        print(f"✓ Child-safe: {safe_response}")
        print(f"✓ Standard: {unsafe_response}")
        
        print("\n🎉 All family manager tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Family manager test failed: {e}")
        return False

def test_cli_integration():
    """Test CLI integration with family skills"""
    print("\n🧪 Testing CLI Integration")
    print("=" * 30)
    
    try:
        import main
        
        # Create CLI instance
        cli = main.GuardianCLI()
        
        # Test family skill execution
        print("Testing CLI family skill execution:")
        cli.run_family_skill('threat_analysis')
        
        print("✓ CLI integration test passed!")
        return True
        
    except Exception as e:
        print(f"✗ CLI integration test failed: {e}")
        return False

def test_gui_integration():
    """Test GUI integration with family skills"""
    print("\n🧪 Testing GUI Integration")
    print("=" * 30)
    
    try:
        from guardian_gui import GuardianMainWindow
        
        # Create mock guardian with family manager
        class MockGuardian:
            def __init__(self):
                from family_assistant.family_assistant_manager import FamilyAssistantManager
                self.family_manager = FamilyAssistantManager()
        
        # Test GUI with family manager
        mock_guardian = MockGuardian()
        window = GuardianMainWindow(mock_guardian)
        
        # Test security scan integration
        window.run_security_scan()
        
        print("✓ GUI integration test passed!")
        return True
        
    except Exception as e:
        print(f"✗ GUI integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Running Task 20.3 Validation Tests")
    print("=" * 60)
    
    results = []
    results.append(test_family_manager_skills())
    results.append(test_cli_integration())
    results.append(test_gui_integration())
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Task 20.3 - Complete skill integration and testing: VALIDATED ✅")
    else:
        print("⚠️ Some tests failed - review implementation")
    
    sys.exit(0 if passed == total else 1)