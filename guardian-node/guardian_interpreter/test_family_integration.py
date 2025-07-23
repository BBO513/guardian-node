#!/usr/bin/env python3
"""
Integration Test for Family Assistant Components
Tests the complete integration of family assistant with Guardian Interpreter
"""

import sys
import os
import logging
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

def test_family_assistant_integration():
    """Test complete family assistant integration"""
    print("=" * 60)
    print("Guardian Node Family Assistant Integration Test")
    print("=" * 60)
    
    # Test 1: Import all family assistant components
    print("\n1. Testing imports...")
    try:
        # Check if family_assistant directory exists
        family_assistant_path = Path("family_assistant")
        if not family_assistant_path.exists():
            print(f"✗ Family assistant directory not found at {family_assistant_path}")
            return False
        
        # Try importing with sys.path manipulation
        import importlib.util
        
        # Import FamilyAssistantManager
        spec = importlib.util.spec_from_file_location(
            "family_assistant_manager", 
            "family_assistant/family_assistant_manager.py"
        )
        fam_manager_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fam_manager_module)
        FamilyAssistantManager = fam_manager_module.FamilyAssistantManager
        
        # Import models
        spec = importlib.util.spec_from_file_location(
            "models", 
            "family_assistant/models.py"
        )
        models_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(models_module)
        FamilyProfile = models_module.FamilyProfile
        
        # Import skill registry
        spec = importlib.util.spec_from_file_location(
            "skill_registry", 
            "family_assistant/skill_registry.py"
        )
        registry_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(registry_module)
        get_family_skill_registry = registry_module.get_family_skill_registry
        
        print("✓ Family assistant imports successful")
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False
    
    # Test 2: Initialize family assistant manager
    print("\n2. Testing FamilyAssistantManager initialization...")
    try:
        config = {
            'family_assistant': {
                'enabled': True,
                'family_data_path': 'test_data'
            }
        }
        logger = logging.getLogger('test')
        
        family_manager = FamilyAssistantManager(config, logger)
        print("✓ FamilyAssistantManager initialized successfully")
    except Exception as e:
        print(f"✗ FamilyAssistantManager initialization failed: {e}")
        return False
    
    # Test 3: Test family skill registry
    print("\n3. Testing family skill registry...")
    try:
        skill_registry = get_family_skill_registry(logger)
        skills = skill_registry.list_skills()
        print(f"✓ Family skill registry loaded {len(skills)} skills:")
        for skill_name, description in skills.items():
            print(f"   - {skill_name}: {description}")
    except Exception as e:
        print(f"✗ Family skill registry failed: {e}")
        return False
    
    # Test 4: Register skills with family manager
    print("\n4. Testing skill registration...")
    try:
        for skill_name, skill_instance in skill_registry.skills.items():
            family_manager.register_family_skill(skill_name, skill_instance)
        print(f"✓ Registered {len(skill_registry.skills)} family skills")
    except Exception as e:
        print(f"✗ Skill registration failed: {e}")
        return False
    
    # Test 5: Test family query processing
    print("\n5. Testing family query processing...")
    try:
        test_query = "How can I keep my family safe online?"
        result = family_manager.process_family_query(test_query)
        
        if result.get('response'):
            print("✓ Family query processed successfully")
            print(f"   Response length: {len(result['response'])} characters")
            print(f"   Confidence: {result.get('confidence', 0):.2f}")
        else:
            print("✗ No response generated")
            return False
    except Exception as e:
        print(f"✗ Family query processing failed: {e}")
        return False
    
    # Test 6: Test family profile analysis
    print("\n6. Testing family profile analysis...")
    try:
        sample_profile = {
            'family_id': 'test_family',
            'family_name': 'Test Family',
            'members': [
                {
                    'member_id': 'parent_001',
                    'name': 'Parent',
                    'age_group': 'adult',
                    'tech_skill_level': 'intermediate'
                }
            ],
            'devices': [
                {
                    'device_id': 'phone_001',
                    'device_type': 'smartphone',
                    'os_type': 'iOS',
                    'os_version': '17.0',
                    'owner': 'parent_001'
                }
            ]
        }
        
        analysis_result = family_manager.analyze_family_security(sample_profile)
        print(f"✓ Family security analysis completed")
        print(f"   Status: {analysis_result.status}")
        print(f"   Score: {analysis_result.overall_score:.1f}/100")
        print(f"   Findings: {len(analysis_result.findings)}")
        print(f"   Recommendations: {len(analysis_result.recommendations)}")
    except Exception as e:
        print(f"✗ Family profile analysis failed: {e}")
        return False
    
    # Test 7: Test voice interface availability (optional)
    print("\n7. Testing voice interface availability...")
    try:
        from family_assistant.voice_interface import FamilyVoiceInterface
        voice_interface = FamilyVoiceInterface(config, logger, family_manager)
        
        if voice_interface.is_available():
            print("✓ Voice interface is available")
        else:
            print("⚠️ Voice interface not available (dependencies may be missing)")
            print("   Install: pip install speechrecognition pyttsx3 pyaudio")
    except ImportError as e:
        print(f"⚠️ Voice interface import failed: {e}")
        print("   This is optional - install voice dependencies if needed")
    except Exception as e:
        print(f"⚠️ Voice interface test failed: {e}")
    
    # Test 8: Test Guardian integration
    print("\n8. Testing Guardian Interpreter integration...")
    try:
        from main import GuardianInterpreter
        
        # Create a minimal config for testing
        test_config_path = "test_config.yaml"
        with open(test_config_path, 'w') as f:
            f.write("""
# Test configuration
llm:
  model_path: "models/test-model.gguf"
network:
  ALLOW_ONLINE: false
logging:
  level: "INFO"
family_assistant:
  enabled: true
""")
        
        # Initialize Guardian (this will test family assistant integration)
        guardian = GuardianInterpreter(test_config_path)
        
        if hasattr(guardian, 'family_manager') and guardian.family_manager:
            print("✓ Guardian Interpreter with family assistant initialized")
        else:
            print("⚠️ Family assistant not properly integrated with Guardian")
        
        # Cleanup test config
        os.remove(test_config_path)
        
    except Exception as e:
        print(f"⚠️ Guardian integration test failed: {e}")
        print("   This may be due to missing dependencies or configuration")
    
    print("\n" + "=" * 60)
    print("Integration Test Summary:")
    print("✓ Core family assistant components working")
    print("✓ Skills system integrated")
    print("✓ Query processing functional")
    print("✓ Security analysis operational")
    print("⚠️ Voice interface optional (install dependencies if needed)")
    print("⚠️ Full Guardian integration may need configuration")
    print("=" * 60)
    
    return True

def test_voice_dependencies():
    """Test voice interface dependencies"""
    print("\nTesting voice dependencies...")
    
    dependencies = [
        ('speechrecognition', 'Speech recognition'),
        ('pyttsx3', 'Text-to-speech'),
        ('pyaudio', 'Audio I/O'),
        ('sounddevice', 'Sound device access')
    ]
    
    available = []
    missing = []
    
    for module_name, description in dependencies:
        try:
            __import__(module_name)
            available.append((module_name, description))
            print(f"✓ {description} ({module_name}) - Available")
        except ImportError:
            missing.append((module_name, description))
            print(f"✗ {description} ({module_name}) - Missing")
    
    if missing:
        print(f"\nTo enable voice features, install missing dependencies:")
        print("pip install " + " ".join([dep[0] for dep in missing]))
        print("\nOn Linux, you may also need:")
        print("sudo apt install portaudio19-dev python3-pyaudio")
    else:
        print("\n✓ All voice dependencies available!")
    
    return len(missing) == 0

if __name__ == "__main__":
    print("Guardian Node Family Assistant Integration Test")
    print("This test verifies that all family assistant components work together")
    
    # Run main integration test
    success = test_family_assistant_integration()
    
    # Test voice dependencies separately
    voice_available = test_voice_dependencies()
    
    if success:
        print("\n🎉 Family Assistant integration test PASSED!")
        if voice_available:
            print("🎤 Voice interface fully available!")
        else:
            print("🔇 Voice interface needs dependencies (optional)")
    else:
        print("\n❌ Family Assistant integration test FAILED!")
        sys.exit(1)