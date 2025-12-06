#!/usr/bin/env python3
"""
Test script for Guardian Node LLM Integration
Tests both Docker Model Runner and direct GGUF loading approaches
"""

import sys
import os
import logging
import yaml
from pathlib import Path

# Add the guardian_interpreter directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'guardian_interpreter'))

try:
    from guardian_interpreter.llm_integration import create_llm
except ImportError as e:
    print(f"Error importing LLM integration: {e}")
    sys.exit(1)

def setup_logging():
    """Set up logging for the test"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger('test_llm')

def load_config():
    """Load the Guardian configuration"""
    config_path = Path(__file__).parent / 'guardian_interpreter' / 'config.yaml'
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def test_llm_loading(logger, config):
    """Test LLM loading with different backends and multiple models"""
    print("🧠 Testing Guardian LLM Integration")
    print("=" * 50)
    
    # Create LLM instance
    llm = create_llm(config, logger)
    
    # Test model loading
    print("\n1. Testing model loading...")
    if llm.load_model():
        print("✅ Model loaded successfully")
    else:
        print("❌ Model loading failed")
        return False
    
    # Get model info
    print("\n2. Model information:")
    model_info = llm.get_model_info()
    for key, value in model_info.items():
        if key == 'performance_stats' and isinstance(value, dict):
            print(f"   {key}:")
            for model_key, stats in value.items():
                print(f"     {model_key}: {stats}")
        else:
            print(f"   {key}: {value}")
    
    # Test model switching if in direct mode
    if model_info.get('inference_mode') == 'direct':
        print("\n3. Testing model switching...")
        test_contexts = [
            {'age_group': 'child', 'query_type': 'education'},
            {'age_group': 'adult', 'query_type': 'security'},
            {'age_group': 'teen', 'query_type': 'general'}
        ]
        
        for context in test_contexts:
            if llm.switch_model(context):
                current_model = llm.get_model_info().get('current_model')
                print(f"   ✅ Switched to model for {context}: {current_model}")
            else:
                print(f"   ⚠️  Could not switch model for {context}")
    
    return True

def test_basic_inference(logger, config):
    """Test basic inference capabilities with context switching"""
    print("\n4. Testing basic inference...")
    
    llm = create_llm(config, logger)
    if not llm.load_model():
        print("❌ Cannot test inference - model not loaded")
        return False
    
    # Test basic response
    test_prompts = [
        ("Hello, can you confirm you are running offline?", {'age_group': 'adult', 'query_type': 'general'}),
        ("How can I stay safe online?", {'age_group': 'child', 'query_type': 'education'}),
        ("What are the latest cybersecurity threats?", {'age_group': 'adult', 'query_type': 'security'})
    ]
    
    for prompt, context in test_prompts:
        print(f"   Testing with context {context}")
        print(f"   Prompt: {prompt}")
        
        try:
            # Switch model based on context
            llm.switch_model(context)
            
            response = llm.generate_response(prompt)
            print(f"   Response: {response[:150]}...")
            print("   ✅ Inference successful")
        except Exception as e:
            print(f"   ❌ Inference failed: {e}")
            return False
    
    # Test performance stats
    perf_stats = llm.get_model_performance_stats()
    print(f"\n   Performance Summary:")
    print(f"   Current model: {perf_stats.get('current_model')}")
    print(f"   Loaded models: {perf_stats.get('loaded_models')}")
    print(f"   Fallback attempts: {perf_stats.get('fallback_attempts')}")
    
    print("✅ Basic inference working with context switching")
    return True

def test_family_features(logger, config):
    """Test family-friendly features with model switching"""
    print("\n5. Testing family-friendly features...")
    
    llm = create_llm(config, logger)
    if not llm.load_model():
        print("❌ Cannot test family features - model not loaded")
        return False
    
    # Test family responses with different contexts
    family_test_cases = [
        ("How can I help my child stay safe online?", {'age_group': 'child', 'query_type': 'education'}),
        ("What should I know about social media privacy?", {'age_group': 'teen', 'query_type': 'education'}),
        ("Explain phishing attacks in simple terms", {'age_group': 'child', 'query_type': 'education'})
    ]
    
    for prompt, context in family_test_cases:
        print(f"   Testing family prompt with context {context}")
        print(f"   Prompt: {prompt}")
        
        try:
            # Switch to appropriate model for context
            llm.switch_model(context)
            
            # Import family context if available
            try:
                from family_llm_prompts import FamilyContext, ChildSafetyLevel
                
                # Map context to family context
                family_context = FamilyContext.PARENT_GUIDANCE
                if context['age_group'] == 'child':
                    family_context = FamilyContext.CHILD_EDUCATION
                
                response = llm.generate_family_response(
                    prompt,
                    context=family_context,
                    child_safe_mode=True,
                    safety_level=ChildSafetyLevel.STANDARD
                )
                print(f"   Family response: {response[:150]}...")
                print("   ✅ Family features working with context switching")
                
            except ImportError:
                # Fall back to regular response
                response = llm.generate_response(prompt)
                print(f"   Response (no family prompts): {response[:150]}...")
                print("   ⚠️  Family prompts not available, using standard response")
                
        except Exception as e:
            print(f"   ❌ Family features failed for context {context}: {e}")
            return False
    
    print("✅ Family features working")
    return True

def test_docker_model_runner_connection():
    """Test connection to Docker Model Runner if available"""
    print("\n5. Testing Docker Model Runner connection...")
    
    try:
        import requests
        response = requests.get('http://localhost:8080/health', timeout=5)
        if response.status_code == 200:
            print("✅ Docker Model Runner is available")
            return True
        else:
            print(f"⚠️  Docker Model Runner responded with status: {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print("⚠️  Docker Model Runner not available (this is OK)")
        return False
    except ImportError:
        print("⚠️  Requests library not available for testing Docker connection")
        return False

def main():
    """Main test function"""
    logger = setup_logging()
    config = load_config()
    
    if not config:
        print("❌ Failed to load configuration")
        sys.exit(1)
    
    print("🛡️  Guardian Node LLM Integration Test")
    print("=" * 50)
    
    # Run tests
    tests_passed = 0
    total_tests = 6
    
    # Test 1: Docker Model Runner connection
    if test_docker_model_runner_connection():
        tests_passed += 1
    
    # Test 2: LLM loading
    if test_llm_loading(logger, config):
        tests_passed += 1
        
        # Test 3: Basic inference (only if loading worked)
        if test_basic_inference(logger, config):
            tests_passed += 1
        
        # Test 4: Family features (only if loading worked)
        if test_family_features(logger, config):
            tests_passed += 1
    else:
        print("⚠️  Skipping inference tests due to loading failure")
    
    # Test 6: Configuration validation
    print("\n6. Testing configuration...")
    llm_config = config.get('llm', {})
    if llm_config:
        print("✅ LLM configuration found")
        
        # Test multiple model configuration
        models_config = llm_config.get('models', {})
        if models_config:
            print(f"   ✅ Multiple model configuration found: {list(models_config.keys())}")
        else:
            print("   ⚠️  Using legacy single model configuration")
        
        tests_passed += 1
    else:
        print("❌ LLM configuration missing")
    
    # Summary
    print("\n" + "=" * 50)
    print(f"Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! LLM integration is working correctly.")
        return 0
    elif tests_passed >= 3:
        print("⚠️  Most tests passed. Some features may need configuration.")
        return 0
    else:
        print("❌ Multiple tests failed. Please check your configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
