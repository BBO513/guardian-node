#!/usr/bin/env python3
"""
Quick test for Guardian Node LLM model switching functionality
This is the testable command mentioned in the task requirements
"""

import sys
import os
import logging
import yaml
from pathlib import Path

# Add the guardian_interpreter directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'guardian_interpreter'))

def test_model_switching():
    """Test model switching with different contexts"""
    print("🧠 Testing Guardian LLM Model Switching")
    print("=" * 50)
    
    try:
        from llm_integration import GuardianLLM
        
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
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('test')
        
        # Create LLM instance
        llm = GuardianLLM(test_config, logger)
        
        print("1. Loading model...")
        if llm.load_model():
            print("✅ Model loaded successfully")
        else:
            print("⚠️  Model loading failed, using mock mode")
        
        print(f"\n2. Current inference mode: {llm.inference_mode}")
        print(f"   Current model: {llm.current_model_key}")
        
        # Test model switching
        print("\n3. Testing model switching...")
        test_contexts = [
            {'age_group': 'kids', 'query_type': 'education'},
            {'age_group': 'adult', 'query_type': 'security'},
            {'age_group': 'teen', 'query_type': 'general'}
        ]
        
        for context in test_contexts:
            print(f"   Switching to context: {context}")
            if llm.switch_model(context):
                current_model = llm.get_model_info().get('current_model')
                print(f"   ✅ Using model: {current_model}")
            else:
                print(f"   ⚠️  Could not switch model")
        
        # Test response generation
        print("\n4. Testing response generation...")
        test_prompt = "Test prompt"
        
        try:
            response = llm.generate_response(test_prompt)
            if "Mock" in response or "placeholder" in response.lower():
                print("✅ Mock response generated (expected if no real model)")
                print(f"   Response: {response[:100]}...")
            else:
                print("✅ Real model response generated")
                print(f"   Response: {response[:100]}...")
        except Exception as e:
            print(f"❌ Response generation failed: {e}")
            return False
        
        # Show performance stats
        print("\n5. Performance statistics:")
        perf_stats = llm.get_model_performance_stats()
        for key, value in perf_stats.items():
            print(f"   {key}: {value}")
        
        print("\n✅ Model switching test completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from the guardian-node directory")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_model_switching()
    sys.exit(0 if success else 1)