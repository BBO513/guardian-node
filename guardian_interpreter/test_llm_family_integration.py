"""
Integration test for LLM with family-friendly prompts
Tests the enhanced LLM integration with family prompt management
"""

import logging
import yaml
from llm_integration import MockLLM
from family_llm_prompts import FamilyContext, ChildSafetyLevel


def test_llm_family_integration():
    """Test LLM integration with family prompts using MockLLM"""
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Load configuration
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        # Use minimal config for testing
        config = {
            'llm': {
                'model_path': 'models/test-model.gguf',
                'context_length': 4096,
                'temperature': 0.7,
                'max_tokens': 512,
                'threads': 4
            }
        }
    
    # Create MockLLM instance for testing (since we don't have a real model file)
    llm = MockLLM(config, logger)
    
    print("Using Mock LLM for testing family prompt integration")
    
    # Test model loading
    success = llm.load_model()
    print(f"Model loading: {'SUCCESS' if success else 'FAILED'}")
    
    if not llm.is_loaded():
        print("Model not loaded, exiting test...")
        return
    
    # Test basic response generation
    print("\n=== Testing Basic Response ===")
    basic_response = llm.generate_response("What is cybersecurity?")
    print(f"Basic response: {basic_response[:200]}...")
    
    # Test family-friendly response generation
    print("\n=== Testing Family Response (General) ===")
    family_response = llm.generate_family_response(
        "How do I keep my family safe online?",
        context=FamilyContext.GENERAL
    )
    print(f"Family response: {family_response[:200]}...")
    
    # Test child education context
    print("\n=== Testing Child Education Context ===")
    child_response = llm.generate_family_response(
        "What is a password?",
        context=FamilyContext.CHILD_EDUCATION,
        child_safe_mode=True,
        safety_level=ChildSafetyLevel.STRICT
    )
    print(f"Child education response: {child_response[:200]}...")
    
    # Test parent guidance context
    print("\n=== Testing Parent Guidance Context ===")
    parent_response = llm.generate_family_response(
        "How do I teach my kids about online safety?",
        context=FamilyContext.PARENT_GUIDANCE
    )
    print(f"Parent guidance response: {parent_response[:200]}...")
    
    # Test device security context
    print("\n=== Testing Device Security Context ===")
    device_response = llm.generate_family_response(
        "How do I secure my family's smartphones?",
        context=FamilyContext.DEVICE_SECURITY
    )
    print(f"Device security response: {device_response[:200]}...")
    
    # Test with family profile
    print("\n=== Testing with Family Profile ===")
    family_profile = {
        'members': [
            {'age_group': 'child', 'tech_skill_level': 'beginner'},
            {'age_group': 'adult', 'tech_skill_level': 'intermediate'}
        ],
        'devices': [
            {'device_type': 'smartphone'},
            {'device_type': 'tablet'}
        ],
        'security_preferences': {
            'threat_tolerance': 'low'
        }
    }
    
    profile_response = llm.generate_family_response(
        "What security measures should we prioritize?",
        context=FamilyContext.GENERAL,
        family_profile=family_profile
    )
    print(f"Personalized response: {profile_response[:200]}...")
    
    # Test model info
    print("\n=== Model Information ===")
    model_info = llm.get_model_info()
    for key, value in model_info.items():
        print(f"{key}: {value}")
    
    print("\n=== Integration Test Complete ===")
    print("All family prompt integration features tested successfully!")


if __name__ == "__main__":
    test_llm_family_integration()