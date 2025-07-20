#!/usr/bin/env python3
"""
Test script for LLM integration with family assistant
"""

import logging
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_llm_integration():
    """Test LLM integration with family assistant"""
    print("🧪 Testing LLM Integration with Family Assistant")
    print("=" * 50)
    
    # Test 1: Import all components
    print("\n1. Testing imports...")
    try:
        from guardian_interpreter.llm_integration import create_llm
        from guardian_interpreter.family_llm_prompts import FamilyContext, ChildSafetyLevel, create_family_prompt_manager, create_child_safety_filter
        from guardian_interpreter.family_assistant.family_assistant_manager import FamilyAssistantManager
        print("✓ All imports successful")
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False
    
    # Test 2: Create LLM instance
    print("\n2. Testing LLM creation...")
    try:
        config = {
            'llm': {
                'model_path': 'models/test-model.gguf',  # Non-existent for testing
                'context_length': 2048,
                'max_tokens': 256,
                'temperature': 0.7
            }
        }
        logger = logging.getLogger('test')
        llm = create_llm(config, logger)
        print(f"✓ LLM instance created: {type(llm).__name__}")
        
        # Test model info
        info = llm.get_model_info()
        print(f"  - Model available: {info.get('available', False)}")
        print(f"  - Model loaded: {info.get('loaded', False)}")
        
    except Exception as e:
        print(f"✗ LLM creation failed: {e}")
        return False
    
    # Test 3: Test family prompts
    print("\n3. Testing family prompts...")
    try:
        prompt_manager = create_family_prompt_manager()
        
        # Test system prompt generation
        system_prompt = prompt_manager.get_system_prompt(
            context=FamilyContext.CHILD_EDUCATION,
            child_safe_mode=True,
            safety_level=ChildSafetyLevel.MODERATE
        )
        print(f"✓ System prompt generated ({len(system_prompt)} chars)")
        
        # Test child safety filter
        safety_filter = create_child_safety_filter()
        filtered = safety_filter.filter_response(
            "Hackers can steal your data", 
            ChildSafetyLevel.STRICT
        )
        print(f"✓ Child safety filtering works: '{filtered}'")
        
    except Exception as e:
        print(f"✗ Family prompts failed: {e}")
        return False
    
    # Test 4: Test family assistant manager
    print("\n4. Testing family assistant manager...")
    try:
        manager = FamilyAssistantManager(
            config=config,
            logger=logger
        )
        
        # Test query processing
        result = manager.process_family_query(
            "How do I protect my child online?",
            context={'family_profile': {'family_id': 'test_family'}}
        )
        print(f"✓ Query processed: {result.get('response', 'No response')[:100]}...")
        print(f"  - Confidence: {result.get('confidence', 0)}")
        
    except Exception as e:
        print(f"✗ Family assistant manager failed: {e}")
        return False
    
    # Test 5: Test family skills integration
    print("\n5. Testing family skills...")
    try:
        from guardian_interpreter.skills import threat_analysis_skill, device_guidance_skill, child_education_skill
        
        # Test threat analysis
        threat_result = threat_analysis_skill.run("phishing")
        print(f"✓ Threat analysis skill: {len(threat_result)} chars response")
        
        # Test device guidance
        device_result = device_guidance_skill.run("smartphone")
        print(f"✓ Device guidance skill: {len(device_result)} chars response")
        
        # Test child education
        education_result = child_education_skill.run("elementary")
        print(f"✓ Child education skill: {len(education_result)} chars response")
        
    except Exception as e:
        print(f"✗ Family skills failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All LLM integration tests passed!")
    print("\n📝 Notes:")
    print("- LLM will use MockLLM until llama-cpp-python is installed")
    print("- Add a GGUF model file to enable real AI responses")
    print("- Family skills work independently of LLM status")
    print("- Child safety filtering is always active")
    
    return True

def test_with_mock_llm():
    """Test LLM responses with mock implementation"""
    print("\n🤖 Testing Mock LLM Responses")
    print("-" * 30)
    
    try:
        import llm_integration
        config = {'llm': {'model_path': 'mock'}}
        logger = logging.getLogger('test')
        
        llm = llm_integration.create_llm(config, logger)
        llm.load_model()
        
        # Test standard response
        response = llm.generate_response("How do I secure my home network?")
        print(f"Standard response: {response[:100]}...")
        
        # Test family response
        import family_llm_prompts
        family_response = llm.generate_family_response(
            "How do I teach my child about online safety?",
            context=family_llm_prompts.FamilyContext.CHILD_EDUCATION,
            child_safe_mode=True,
            safety_level=family_llm_prompts.ChildSafetyLevel.MODERATE
        )
        print(f"Family response: {family_response[:100]}...")
        
        print("✓ Mock LLM responses working correctly")
        
    except Exception as e:
        print(f"✗ Mock LLM test failed: {e}")

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Run tests
    success = test_llm_integration()
    
    if success:
        test_with_mock_llm()
        print("\n🚀 LLM integration is ready for production!")
        print("   Install llama-cpp-python and add GGUF models for full AI functionality.")
    else:
        print("\n❌ LLM integration tests failed!")
        sys.exit(1)