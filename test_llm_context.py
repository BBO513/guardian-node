#!/usr/bin/env python3
"""
Test Script: LLM Context Usage
Verifies that the LLM properly uses context from RAG memory
"""

import sys
import logging
from pathlib import Path

# Add guardian_interpreter to path
sys.path.insert(0, str(Path(__file__).parent / "guardian_interpreter"))

from memory_vault import create_memory_vault
from llm_integration import create_llm
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_context')


def load_config():
    """Load Guardian Node configuration"""
    config_path = Path(__file__).parent / "guardian_interpreter" / "config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def test_context_usage():
    """Test that LLM properly uses context from memory"""
    
    print("=" * 70)
    print("  LLM Context Usage Test")
    print("=" * 70)
    print()
    
    # Load configuration
    config = load_config()
    
    # Initialize memory vault
    print("1. Initializing Memory Vault...")
    memory = create_memory_vault(data_dir="data/test_context_memory", logger=logger)
    
    if not memory.is_available():
        print("   ⚠️  Memory Vault not available (using mock)")
        print("   Install chromadb and sentence-transformers for full test")
        print()
    else:
        print("   ✅ Memory Vault initialized")
        print()
    
    # Initialize LLM
    print("2. Initializing LLM...")
    llm = create_llm(config, logger)
    
    if not llm.is_loaded():
        print("   ⚠️  LLM not loaded")
        print("   Please ensure model file is available")
        return
    else:
        print("   ✅ LLM loaded")
        print()
    
    # Store test data
    print("3. Storing test family data...")
    memory.store_family_profile(
        name="Sarah",
        role="Child",
        age_group="Child",
        safety_level="strict",
        notes="8 years old, loves iPad games"
    )
    memory.store_device(
        device_name="Sarah's iPad",
        device_type="tablet",
        ip_address="192.168.1.100",
        notes="Educational apps only"
    )
    print("   ✅ Stored: Sarah (Child, strict safety)")
    print("   ✅ Stored: Sarah's iPad (tablet)")
    print()
    
    # Test queries
    test_cases = [
        {
            "query": "How can I keep Sarah safe online?",
            "expected_context": ["Sarah", "child", "strict"],
            "description": "Query about specific family member"
        },
        {
            "query": "What parental controls should I use for the iPad?",
            "expected_context": ["Sarah", "iPad", "tablet"],
            "description": "Query about specific device"
        },
        {
            "query": "What apps are safe for kids?",
            "expected_context": ["Sarah", "child"],
            "description": "General query that should use family context"
        }
    ]
    
    print("4. Testing LLM context usage...")
    print()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['description']}")
        print("-" * 70)
        print(f"Query: {test_case['query']}")
        print()
        
        # Get context from memory
        context = memory.get_enriched_context(test_case['query'])
        
        if context:
            print(f"Retrieved Context:")
            print(f"  {context}")
            print()
        else:
            print("  No context retrieved")
            print()
        
        # Prepare enriched query
        if context:
            enriched_query = (
                f"===== CONTEXT FROM MEMORY =====\n"
                f"{context}\n"
                f"===== END CONTEXT =====\n\n"
                f"User's Question: {test_case['query']}\n\n"
                f"Instructions: Use the context above to provide a personalized response. "
                f"Reference specific names, relationships, and details from the context."
            )
        else:
            enriched_query = test_case['query']
        
        # Generate response
        system_prompt = """You are Noddy, a family cybersecurity assistant with persistent memory.
        
        CRITICAL: You MUST pay close attention to and USE the context provided about family members, devices, and past conversations.
        When context mentions specific names, relationships, or details, incorporate them naturally into your response.
        
        When responding:
        1. FIRST: Check if context mentions specific people, devices, or past discussions
        2. THEN: Use those details naturally in your response (e.g., "Since Sarah is a child with strict safety settings...")
        3. ALWAYS: Personalize advice based on the context provided
        
        Be helpful, clear, and safe. Tailor your responses to the family's specific situation when context is provided."""
        
        response = llm.generate_response(enriched_query, system_prompt)
        
        print(f"LLM Response:")
        print(f"  {response}")
        print()
        
        # Check if response uses expected context
        context_used = any(keyword.lower() in response.lower() 
                          for keyword in test_case['expected_context'])
        
        if context_used:
            print("  ✅ Response uses context (mentions expected keywords)")
        else:
            print("  ⚠️  Response may not be using context effectively")
            print(f"     Expected keywords: {test_case['expected_context']}")
        
        print()
        print("=" * 70)
        print()
    
    # Summary
    print("5. Test Summary")
    print("-" * 70)
    print("The LLM should:")
    print("  ✅ Mention specific names (e.g., 'Sarah')")
    print("  ✅ Reference relationships (e.g., 'child', 'strict safety')")
    print("  ✅ Mention specific devices (e.g., 'iPad')")
    print("  ✅ Provide personalized advice based on context")
    print()
    print("If the LLM is not using context:")
    print("  1. Check that context is being retrieved (should show above)")
    print("  2. Verify system prompt emphasizes context usage")
    print("  3. Ensure prompt formatting is correct for model type")
    print("  4. Try adjusting temperature (lower = more focused)")
    print()
    print("=" * 70)


if __name__ == "__main__":
    try:
        test_context_usage()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
