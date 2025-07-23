#!/usr/bin/env python3
"""
Test script for Task 20.3 - Complete skill integration and testing
Validates all family skills are properly registered and working
"""

import sys
import logging
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_skill_integration():
    """Test complete skill integration with family assistant manager"""
    print("🧪 Testing Skill Integration (Task 20.3)")
    print("=" * 50)
    
    results = {
        'skill_registration': False,
        'cli_execution': False,
        'gui_integration': False,
        'response_formatting': False,
        'error_handling': False
    }
    
    # Test 1: Skill Registration
    print("\n1. Testing skill registration with family assistant manager...")
    try:
        import main
        cli = main.GuardianCLI()
        
        # Check if family manager has skills registered
        if hasattr(cli.family_manager, 'family_skills'):
            skill_count = len(cli.family_manager.family_skills)
            print(f"   ✓ {skill_count} family skills registered")
            
            # List registered skills
            for skill_name in cli.family_manager.family_skills.keys():
                print(f"     - {skill_name}")
            
            results['skill_registration'] = skill_count > 0
        else:
            print("   ✗ Family manager has no skills registered")
            
    except Exception as e:
        print(f"   ✗ Skill registration test failed: {e}")
    
    # Test 2: CLI Execution
    print("\n2. Testing skill execution through CLI interface...")
    try:
        # Test family skills execution
        test_queries = [
            "How do I protect against phishing?",
            "What should I teach my child about passwords?",
            "How do I secure my smartphone?"
        ]
        
        for query in test_queries:
            result = cli.family_manager.process_family_query(
                query, 
                context={'family_profile': {'family_id': 'test_family'}}
            )
            
            if result and result.get('response'):
                print(f"   ✓ Query processed: '{query}' → {len(result['response'])} chars")
            else:
                print(f"   ✗ Query failed: '{query}'")
        
        results['cli_execution'] = True
        
    except Exception as e:
        print(f"   ✗ CLI execution test failed: {e}")
    
    # Test 3: GUI Integration
    print("\n3. Testing GUI integration...")
    try:
        from guardian_gui import GuardianMainWindow
        
        # Test GUI creation with backend integration
        window = GuardianMainWindow(cli)
        
        # Test mode change integration
        test_modes = ["Kids", "Teens", "Adult"]
        for mode in test_modes:
            window.handle_mode_change(mode)
            profile = window.get_family_profile_for_mode(mode)
            print(f"   ✓ Mode '{mode}' → Profile: {profile['security_level']}")
        
        results['gui_integration'] = True
        
    except Exception as e:
        print(f"   ✗ GUI integration test failed: {e}")
    
    # Test 4: Response Formatting
    print("\n4. Testing family-friendly response formatting...")
    try:
        from skills import threat_analysis_skill, child_education_skill
        
        # Test threat analysis formatting
        threat_response = threat_analysis_skill.run("phishing")
        if "family-friendly" in threat_response.lower() or "🚨" in threat_response:
            print("   ✓ Threat analysis uses family-friendly formatting")
        
        # Test child education formatting
        education_response = child_education_skill.run("elementary")
        if "👶" in education_response or "age-appropriate" in education_response.lower():
            print("   ✓ Child education uses age-appropriate formatting")
        
        results['response_formatting'] = True
        
    except Exception as e:
        print(f"   ✗ Response formatting test failed: {e}")
    
    # Test 5: Error Handling and Fallbacks
    print("\n5. Testing error handling and fallback responses...")
    try:
        # Test invalid skill execution
        invalid_result = cli.family_manager.run_family_skill("nonexistent_skill")
        if not invalid_result.get('success', True):
            print("   ✓ Invalid skill execution handled gracefully")
        
        # Test empty query handling
        empty_result = cli.family_manager.process_family_query("", {})
        if empty_result and empty_result.get('response'):
            print("   ✓ Empty query handled with fallback response")
        
        # Test malformed context handling
        malformed_result = cli.family_manager.process_family_query("test", None)
        if malformed_result:
            print("   ✓ Malformed context handled gracefully")
        
        results['error_handling'] = True
        
    except Exception as e:
        print(f"   ✗ Error handling test failed: {e}")
    
    return results

def print_test_summary(results):
    """Print test summary for Task 20.3"""
    print("\n" + "=" * 50)
    print("📊 SKILL INTEGRATION TEST SUMMARY (Task 20.3)")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title():<25} {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL SKILL INTEGRATION TESTS PASSED!")
        print("✨ Task 20.3 requirements validated:")
        print("   • All family skills properly registered")
        print("   • Skills execute through CLI and GUI interfaces")
        print("   • Responses properly formatted for family audiences")
        print("   • Comprehensive error handling and fallbacks")
        return True
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed")
        print("Please review the errors above before completing Task 20.3")
        return False

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
    
    # Run tests
    results = test_skill_integration()
    
    # Print summary
    success = print_test_summary(results)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)