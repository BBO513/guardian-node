#!/usr/bin/env python3
"""
Test script for Guardian LLM Loader Integration
Tests the enhanced model discovery and management capabilities
"""

import sys
import os
import logging
from pathlib import Path

# Add the guardian_interpreter directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'guardian_interpreter'))

def test_llm_loader_standalone():
    """Test the LLM loader as a standalone component"""
    print("🔍 Testing Guardian LLM Loader (Standalone)")
    print("=" * 50)
    
    try:
        from llm_loader import GuardianLLMLoader, get_llm_loader, initialize_llm
        
        # Test standalone loader
        print("1. Creating LLM Loader...")
        loader = GuardianLLMLoader()
        print("✅ LLM Loader created successfully")
        
        # Test model discovery
        print("\n2. Testing model discovery...")
        available_models = loader.get_available_models()
        print(f"   Discovered {len(available_models)} models")
        
        for model in available_models:
            print(f"   - {model.name}: {model.size_mb:.1f} MB (loaded: {model.loaded})")
        
        # Test model recommendations
        print("\n3. Testing model recommendations...")
        recommendations = loader.get_model_recommendations()
        print(f"   Generated {len(recommendations)} recommendations:")
        for rec in recommendations:
            print(f"   - {rec}")
        
        # Test benchmarking
        print("\n4. Testing model benchmarking...")
        if available_models:
            benchmark_results = loader.benchmark_all_models()
            print(f"   Benchmarked {len(benchmark_results)} models")
            
            for result in benchmark_results[:2]:  # Show first 2 results
                print(f"   - {result['model_name']}: {result['tokens_per_second']} tokens/sec")
        else:
            print("   No models available for benchmarking")
        
        # Test global instance
        print("\n5. Testing global loader instance...")
        global_loader = get_llm_loader()
        if global_loader:
            print("✅ Global loader instance working")
            print(f"   Current model: {global_loader.get_current_model()}")
        
        # Test initialization
        print("\n6. Testing LLM initialization...")
        init_success = initialize_llm()
        print(f"   Initialization {'successful' if init_success else 'failed'}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_llm_integration_with_loader():
    """Test the integration of LLM loader with existing LLM integration"""
    print("\n🔗 Testing LLM Integration with Enhanced Loader")
    print("=" * 50)
    
    try:
        from llm_integration import create_llm
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('test')
        
        # Create test configuration
        test_config = {
            'llm': {
                'models': {
                    'default': {
                        'path': 'models/phi-3-mini-4k-instruct-q4.gguf',
                        'context_length': 4096,
                        'threads': 4,
                        'temperature': 0.7,
                        'max_tokens': 512,
                        'age_groups': ['adult', 'teen', 'child'],
                        'contexts': ['general', 'security', 'education']
                    }
                }
            }
        }
        
        print("1. Creating enhanced LLM integration...")
        llm = create_llm(test_config, logger)
        print("✅ Enhanced LLM integration created")
        
        print("\n2. Loading models with enhanced discovery...")
        if llm.load_model():
            print("✅ Model loading successful")
        else:
            print("⚠️  Model loading failed (expected if no models present)")
        
        print("\n3. Getting enhanced model information...")
        model_info = llm.get_model_info()
        
        # Display key information
        print(f"   LLM Loader Available: {model_info.get('llm_loader_available', False)}")
        print(f"   Inference Mode: {model_info.get('inference_mode', 'unknown')}")
        print(f"   Current Model: {model_info.get('current_model', 'none')}")
        
        # Show discovered models if available
        discovered_models = model_info.get('discovered_models', [])
        if discovered_models:
            print(f"\n   Discovered Models ({len(discovered_models)}):")
            for model in discovered_models:
                print(f"   - {model['name']}: {model['size_mb']:.1f} MB")
        
        # Show recommendations if available
        recommendations = model_info.get('model_recommendations', [])
        if recommendations:
            print(f"\n   Model Recommendations:")
            for rec in recommendations:
                print(f"   - {rec}")
        
        print("\n4. Testing response generation...")
        test_prompt = "Test prompt for enhanced LLM"
        try:
            response = llm.generate_response(test_prompt)
            print(f"   Response: {response[:100]}...")
            print("✅ Response generation working")
        except Exception as e:
            print(f"   ⚠️  Response generation error: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_variables():
    """Test environment variable configuration"""
    print("\n🌍 Testing Environment Variable Configuration")
    print("=" * 50)
    
    # Test default values
    print("1. Testing default environment values...")
    
    # Set some test environment variables
    os.environ['GUARDIAN_MODELS_DIR'] = './models'
    os.environ['GUARDIAN_MAX_MEMORY_MB'] = '4096'
    
    try:
        from llm_loader import GuardianLLMLoader
        
        loader = GuardianLLMLoader()
        print(f"   Models directory: {loader.models_dir}")
        print(f"   Max memory: {loader.max_memory_mb} MB")
        print(f"   Default model path: {loader.default_model_path}")
        
        print("✅ Environment variable configuration working")
        return True
        
    except Exception as e:
        print(f"❌ Environment test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🛡️  Guardian Node LLM Loader Integration Test")
    print("=" * 60)
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Standalone LLM loader
    if test_llm_loader_standalone():
        tests_passed += 1
    
    # Test 2: Integration with existing LLM system
    if test_llm_integration_with_loader():
        tests_passed += 1
    
    # Test 3: Environment variable configuration
    if test_environment_variables():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Enhanced LLM loader integration is working correctly.")
        return 0
    elif tests_passed >= 2:
        print("⚠️  Most tests passed. Some features may need configuration.")
        return 0
    else:
        print("❌ Multiple tests failed. Please check your configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())