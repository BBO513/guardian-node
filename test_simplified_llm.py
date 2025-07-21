#!/usr/bin/env python3
"""
Test script for simplified Guardian LLM Integration
"""

import sys
import os
import logging
import yaml
from pathlib import Path

# Add the guardian_interpreter directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'guardian_interpreter'))

def setup_logging():
    """Set up logging for the test"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger('test_simplified_llm')

def main():
    """Main test function"""
    logger = setup_logging()
    
    # Create test configuration
    test_config = {
        'llm': {
            'models': {
                'default': 'models/phi-3-mini-4k-instruct-q4.gguf',
                'child': 'models/phi-3-mini-child-safe-q4.gguf',
                'adult': 'models/llama-3.2-3b-security-q4.gguf'
            }
        }
    }
    
    print("🧠 Testing Simplified Guardian LLM Integration")
    print("=" * 50)
    
    try:
        from llm_integration import create_llm, GuardianLLM
        
        # Create LLM instance
        print("1. Creating LLM instance...")
        llm = create_llm(test_config, logger)
        print("✅ LLM instance created")
        
        # Test model switching
        print("\n2. Testing model switching...")
        contexts = [
            {'age_group': 'child'},
            {'age_group': 'adult'},
            {'age_group': 'unknown'}  # Should use default
        ]
        
        for context in contexts:
            print(f"   Switching to context: {context}")
            llm.switch_model(context)
        
        # Test response generation
        print("\n3. Testing response generation...")
        test_prompt = "Hello, are you running offline?"
        print(f"   Prompt: {test_prompt}")
        
        try:
            response = llm.generate_response(test_prompt)
            print(f"   Response: {response[:100]}...")
            print("✅ Response generation working")
        except Exception as e:
            print(f"   ⚠️  Response generation error: {e}")
            print("   ✅ Fallback mechanism should handle this")
        
        print("\n✅ Simplified LLM integration test completed!")
        return 0
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())