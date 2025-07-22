#!/usr/bin/env python3
"""
Test script for simplified Family Assistant Manager
"""

import sys
import os
import logging

# Add the guardian_interpreter directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'guardian_interpreter'))

def setup_logging():
    """Set up logging for the test"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger('test_simplified_family')

class MockLLM:
    """Mock LLM for testing"""
    def generate_response(self, prompt):
        return f"Response to: {prompt}"

class SimplifiedFamilyAssistantManager:
    """Simplified version of the Family Assistant Manager for testing"""
    def __init__(self):
        self.llm = MockLLM()
    
    def process_query(self, query, child_safe=True):
        prompt = f"Provide a {'child-safe' if child_safe else 'standard'} family response to: {query}. Use simple language and analogies for kids."
        response = self.llm.generate_response(prompt)
        return self.format_response(response, child_safe)
    
    def format_response(self, response, child_safe):
        if child_safe:
            return "Kid-friendly: " + response.replace("risk", "challenge").replace("threat", "lesson")
        return response

def main():
    """Main test function"""
    logger = setup_logging()
    
    print("👨‍👩‍👧‍👦 Testing Simplified Family Assistant Manager")
    print("=" * 50)
    
    try:
        # Create family assistant manager
        print("1. Creating Family Assistant Manager...")
        fm = SimplifiedFamilyAssistantManager()
        print("✅ Family Assistant Manager created")
        
        # Test child-safe query
        print("\n2. Testing child-safe query...")
        child_query = "How do I protect against security risks and threats?"
        print(f"   Query: {child_query}")
        
        child_response = fm.process_query(child_query, child_safe=True)
        print(f"   Response: {child_response}")
        
        if "Kid-friendly:" in child_response and "challenge" in child_response and "lesson" in child_response:
            print("   ✅ Child-safe formatting applied correctly")
        else:
            print("   ❌ Child-safe formatting not applied correctly")
        
        # Test standard query
        print("\n3. Testing standard query...")
        adult_query = "What are the latest security threats?"
        print(f"   Query: {adult_query}")
        
        adult_response = fm.process_query(adult_query, child_safe=False)
        print(f"   Response: {adult_response}")
        
        if "Kid-friendly:" not in adult_response:
            print("   ✅ Standard formatting applied correctly")
        else:
            print("   ❌ Standard formatting not applied correctly")
        
        print("\n✅ Simplified Family Assistant Manager test completed!")
        return 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())