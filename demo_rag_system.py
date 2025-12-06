#!/usr/bin/env python3
"""
Demo Script: RAG (Retrieval-Augmented Generation) System for Guardian Node
Demonstrates persistent memory functionality across sessions
"""

import sys
import logging
from pathlib import Path

# Add guardian_interpreter to path
sys.path.insert(0, str(Path(__file__).parent / "guardian_interpreter"))

from memory_vault import create_memory_vault

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('guardian.demo')


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_family_profiles(memory):
    """Demonstrate storing and retrieving family profiles"""
    print_section("DEMO 1: Family Profiles")
    
    # Store family members
    family_members = [
        ("Alex", "Parent", "Adult", "standard", "Guardian and primary user"),
        ("Sarah", "Child", "Child", "strict", "8 years old, loves iPad games"),
        ("Tom", "Teen", "Teen", "moderate", "15 years old, interested in coding"),
        ("Emma", "Parent", "Adult", "standard", "Co-guardian, works from home")
    ]
    
    print("\n📝 Storing family profiles...")
    for name, role, age_group, safety_level, notes in family_members:
        memory.store_family_profile(
            name=name,
            role=role,
            age_group=age_group,
            safety_level=safety_level,
            notes=notes
        )
        print(f"  ✅ Added: {name} ({role}, {age_group})")
    
    # Retrieve all profiles
    print("\n📋 Retrieving all family profiles...")
    profiles = memory.get_all_family_profiles()
    for profile in profiles:
        metadata = profile.get('metadata', {})
        print(f"  • {metadata.get('name')}: {metadata.get('role')} - {metadata.get('notes', 'No notes')}")


def demo_device_inventory(memory):
    """Demonstrate storing and retrieving device information"""
    print_section("DEMO 2: Device Inventory")
    
    # Store devices
    devices = [
        ("Alex's Laptop", "laptop", "192.168.1.100", "Work device, Windows 11"),
        ("Sarah's iPad", "tablet", "192.168.1.101", "Educational apps only"),
        ("Tom's Gaming PC", "desktop", "192.168.1.102", "Gaming and coding"),
        ("Living Room TV", "smart_tv", "192.168.1.103", "Family streaming"),
        ("Emma's Phone", "smartphone", "192.168.1.104", "iPhone 14"),
        ("Home Router", "network", "192.168.1.1", "TP-Link AX3000")
    ]
    
    print("\n📝 Storing device inventory...")
    for name, device_type, ip, notes in devices:
        memory.store_device(
            device_name=name,
            device_type=device_type,
            ip_address=ip,
            notes=notes
        )
        print(f"  ✅ Added: {name} ({device_type}) at {ip}")
    
    # Search for specific devices
    print("\n🔍 Searching for 'Sarah's devices'...")
    results = memory.retrieve_relevant_memories("Sarah's devices", n_results=3)
    if results.get('device_inventory'):
        for result in results['device_inventory']:
            print(f"  • {result['document']}")


def demo_conversation_history(memory):
    """Demonstrate storing and retrieving conversation history"""
    print_section("DEMO 3: Conversation History")
    
    # Store conversations
    conversations = [
        (
            "How do I set up parental controls on Sarah's iPad?",
            "To set up parental controls on iPad: 1) Go to Settings > Screen Time, 2) Tap 'Turn On Screen Time', 3) Select 'This is My Child's iPad', 4) Set up Content & Privacy Restrictions..."
        ),
        (
            "What are good coding resources for Tom?",
            "For a 15-year-old interested in coding, I recommend: 1) freeCodeCamp.org for web development, 2) Python.org tutorials for Python, 3) Scratch for visual programming basics..."
        ),
        (
            "How can I block inappropriate websites?",
            "To block inappropriate websites: 1) Use router-level filtering (OpenDNS Family Shield), 2) Enable SafeSearch on browsers, 3) Use parental control software..."
        ),
        (
            "What's the best way to create strong passwords?",
            "Strong passwords should: 1) Be at least 12 characters long, 2) Include uppercase, lowercase, numbers, and symbols, 3) Avoid dictionary words, 4) Use a password manager..."
        )
    ]
    
    print("\n📝 Storing conversation history...")
    for query, response in conversations:
        memory.store_conversation(
            user_query=query,
            assistant_response=response,
            context={"demo": True}
        )
        print(f"  ✅ Stored: {query[:50]}...")
    
    # Search conversation history
    print("\n🔍 Searching for 'password security'...")
    results = memory.retrieve_relevant_memories("password security", n_results=2)
    if results.get('conversation_history'):
        for result in results['conversation_history']:
            query = result['metadata'].get('query', 'Unknown')
            print(f"  • Previous discussion: {query}")


def demo_semantic_search(memory):
    """Demonstrate semantic search capabilities"""
    print_section("DEMO 4: Semantic Search")
    
    search_queries = [
        "Tell me about the children in the family",
        "What devices does Tom use?",
        "Previous discussions about internet safety",
        "Show me all tablets and phones"
    ]
    
    for query in search_queries:
        print(f"\n🔍 Query: '{query}'")
        results = memory.retrieve_relevant_memories(query, n_results=3)
        
        for collection_name, items in results.items():
            if items:
                print(f"\n  📁 {collection_name.upper()}:")
                for item in items[:2]:  # Show top 2 results
                    print(f"    • {item['document'][:80]}...")


def demo_enriched_context(memory):
    """Demonstrate context enrichment for LLM queries"""
    print_section("DEMO 5: Enriched Context for LLM")
    
    queries = [
        "How can I keep Sarah safe online?",
        "What security settings should I use for Tom's gaming PC?",
        "Recommend parental controls for our family"
    ]
    
    for query in queries:
        print(f"\n❓ User Query: '{query}'")
        context = memory.get_enriched_context(query, max_context_length=300)
        
        if context:
            print(f"\n📚 Retrieved Context:")
            print(f"  {context}")
            print(f"\n💡 This context would be prepended to the LLM prompt")
            print(f"   to provide personalized, family-aware responses.")
        else:
            print("  (No relevant context found)")


def demo_statistics(memory):
    """Display memory vault statistics"""
    print_section("DEMO 6: Memory Statistics")
    
    stats = memory.get_stats()
    
    print("\n📊 Memory Vault Statistics:")
    print("-" * 50)
    total_items = 0
    for collection, count in stats.items():
        print(f"  {collection:.<35} {count:>3} items")
        total_items += count
    print("-" * 50)
    print(f"  {'TOTAL':.<35} {total_items:>3} items")
    
    if memory.is_available():
        print("\n✅ RAG System Status: OPERATIONAL")
        print("   • Vector database: ChromaDB")
        print("   • Embedding model: all-MiniLM-L6-v2")
        print("   • Storage: data/memory/chroma_db/")
    else:
        print("\n⚠️  RAG System Status: MOCK MODE")
        print("   Install chromadb and sentence-transformers for full functionality")


def demo_persistence(memory):
    """Demonstrate data persistence across sessions"""
    print_section("DEMO 7: Persistence Test")
    
    print("\n💾 Testing data persistence...")
    print("   Current session has stored data in memory vault.")
    print("   Data is persisted to disk at: data/memory/chroma_db/")
    print("\n   To verify persistence:")
    print("   1. Exit this demo")
    print("   2. Run the demo again")
    print("   3. Data will still be available!")
    
    if memory.is_available():
        print("\n✅ Persistence: ENABLED")
        print("   All data survives power cycles and restarts")
    else:
        print("\n⚠️  Persistence: DISABLED (Mock mode)")


def main():
    """Main demo function"""
    print("\n" + "=" * 70)
    print("  Guardian Node - RAG System Demo")
    print("  Persistent Memory for Family Cybersecurity")
    print("=" * 70)
    
    # Initialize memory vault
    print("\n🚀 Initializing Memory Vault...")
    memory = create_memory_vault(data_dir="data/demo_memory")
    
    if not memory.is_available():
        print("\n⚠️  WARNING: RAG dependencies not installed!")
        print("   Install with: pip install chromadb sentence-transformers")
        print("   Running in MOCK MODE for demonstration...\n")
    else:
        print("✅ Memory Vault initialized successfully!\n")
    
    # Run demos
    try:
        demo_family_profiles(memory)
        input("\nPress Enter to continue...")
        
        demo_device_inventory(memory)
        input("\nPress Enter to continue...")
        
        demo_conversation_history(memory)
        input("\nPress Enter to continue...")
        
        demo_semantic_search(memory)
        input("\nPress Enter to continue...")
        
        demo_enriched_context(memory)
        input("\nPress Enter to continue...")
        
        demo_statistics(memory)
        input("\nPress Enter to continue...")
        
        demo_persistence(memory)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    
    # Final summary
    print("\n" + "=" * 70)
    print("  Demo Complete!")
    print("=" * 70)
    print("\n✅ RAG System Features Demonstrated:")
    print("   • Family profile storage and retrieval")
    print("   • Device inventory management")
    print("   • Conversation history tracking")
    print("   • Semantic search across all data")
    print("   • Context enrichment for LLM queries")
    print("   • Persistent storage across sessions")
    
    print("\n📚 Next Steps:")
    print("   1. Run: python guardian_interpreter/main.py")
    print("   2. Try: memory stats")
    print("   3. Try: memory add profile")
    print("   4. Try: ask 'How can I keep my family safe online?'")
    
    print("\n📖 Documentation: RAG_IMPLEMENTATION_GUIDE.md")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
