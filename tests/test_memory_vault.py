# Test Suite for Memory Vault (RAG System)
# Tests persistent memory functionality for Guardian Node

import pytest
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from guardian_interpreter.memory_vault import create_memory_vault, MemoryVault, MockMemoryVault

# Test data directory
TEST_DATA_DIR = "data/test_memory"


@pytest.fixture
def memory_vault():
    """Create a memory vault instance for testing"""
    vault = create_memory_vault(data_dir=TEST_DATA_DIR)
    yield vault
    # Cleanup after tests
    if vault.is_available():
        for collection in vault.collections.keys():
            vault.clear_collection(collection)


def test_memory_vault_initialization(memory_vault):
    """Test that memory vault initializes correctly"""
    assert memory_vault is not None
    # Should work with either real or mock implementation
    assert hasattr(memory_vault, 'store_family_profile')
    assert hasattr(memory_vault, 'store_conversation')
    assert hasattr(memory_vault, 'store_device')


def test_store_family_profile(memory_vault):
    """Test storing family member profiles"""
    result = memory_vault.store_family_profile(
        name="Alex",
        role="Parent",
        age_group="Adult",
        safety_level="standard"
    )
    assert result is True
    
    # Verify storage
    profiles = memory_vault.get_all_family_profiles()
    if memory_vault.is_available():
        assert len(profiles) > 0
        assert any(p['metadata']['name'] == "Alex" for p in profiles)


def test_store_conversation(memory_vault):
    """Test storing conversation history"""
    result = memory_vault.store_conversation(
        user_query="How do I set up parental controls on iPad?",
        assistant_response="To set up parental controls on iPad, go to Settings > Screen Time...",
        context={"online_mode": False}
    )
    assert result is True


def test_store_device(memory_vault):
    """Test storing device information"""
    result = memory_vault.store_device(
        device_name="Alex's iPad",
        device_type="tablet",
        ip_address="192.168.1.100"
    )
    assert result is True


def test_retrieve_relevant_memories(memory_vault):
    """Test retrieving relevant memories based on query"""
    # Store some test data
    memory_vault.store_family_profile("Sarah", "Child", "Child", "strict")
    memory_vault.store_device("Sarah's Phone", "smartphone", "192.168.1.101")
    memory_vault.store_conversation(
        "What apps are safe for kids?",
        "Safe apps for kids include educational games and monitored messaging apps."
    )
    
    # Retrieve memories
    memories = memory_vault.retrieve_relevant_memories("Sarah's phone safety")
    
    assert isinstance(memories, dict)
    # Should return results from multiple collections
    if memory_vault.is_available():
        assert len(memories) > 0


def test_get_enriched_context(memory_vault):
    """Test getting enriched context for LLM prompts"""
    # Store test data
    memory_vault.store_family_profile("Tom", "Teen", "Teen", "moderate")
    memory_vault.store_device("Tom's Laptop", "laptop", "192.168.1.102")
    
    # Get enriched context
    context = memory_vault.get_enriched_context("Tell me about Tom's devices")
    
    assert isinstance(context, str)
    # Context should be empty for mock, populated for real implementation
    if memory_vault.is_available():
        assert len(context) > 0


def test_memory_persistence(memory_vault):
    """Test that memories persist across sessions"""
    if not memory_vault.is_available():
        pytest.skip("Skipping persistence test for mock implementation")
    
    # Store data
    memory_vault.store_family_profile("Emma", "Parent", "Adult", "standard")
    
    # Create new instance (simulating restart)
    new_vault = create_memory_vault(data_dir=TEST_DATA_DIR)
    
    # Verify data persists
    profiles = new_vault.get_all_family_profiles()
    assert len(profiles) > 0
    assert any(p['metadata']['name'] == "Emma" for p in profiles)


def test_get_stats(memory_vault):
    """Test getting memory vault statistics"""
    # Add some data
    memory_vault.store_family_profile("John", "Parent", "Adult", "standard")
    memory_vault.store_device("Router", "network", "192.168.1.1")
    
    stats = memory_vault.get_stats()
    
    assert isinstance(stats, dict)
    assert 'family_profiles' in stats
    assert 'device_inventory' in stats
    
    if memory_vault.is_available():
        assert stats['family_profiles'] >= 1
        assert stats['device_inventory'] >= 1


def test_clear_collection(memory_vault):
    """Test clearing a specific collection"""
    # Add data
    memory_vault.store_family_profile("Test User", "Parent", "Adult", "standard")
    
    # Clear collection
    result = memory_vault.clear_collection("family_profiles")
    
    if memory_vault.is_available():
        assert result is True
        stats = memory_vault.get_stats()
        assert stats['family_profiles'] == 0


def test_multiple_family_members(memory_vault):
    """Test storing and retrieving multiple family members"""
    family_members = [
        ("Dad", "Parent", "Adult", "standard"),
        ("Mom", "Parent", "Adult", "standard"),
        ("Billy", "Child", "Child", "strict"),
        ("Jenny", "Teen", "Teen", "moderate")
    ]
    
    for name, role, age_group, safety_level in family_members:
        result = memory_vault.store_family_profile(name, role, age_group, safety_level)
        assert result is True
    
    profiles = memory_vault.get_all_family_profiles()
    if memory_vault.is_available():
        assert len(profiles) >= len(family_members)


def test_device_inventory(memory_vault):
    """Test comprehensive device inventory"""
    devices = [
        ("Living Room TV", "smart_tv", "192.168.1.50"),
        ("Dad's Laptop", "laptop", "192.168.1.51"),
        ("Mom's Phone", "smartphone", "192.168.1.52"),
        ("Billy's Tablet", "tablet", "192.168.1.53")
    ]
    
    for name, device_type, ip in devices:
        result = memory_vault.store_device(name, device_type, ip)
        assert result is True
    
    # Search for devices
    memories = memory_vault.retrieve_relevant_memories("show me all devices")
    assert isinstance(memories, dict)


def test_conversation_history(memory_vault):
    """Test storing multiple conversations"""
    conversations = [
        ("How do I block websites?", "You can block websites using parental controls..."),
        ("What is phishing?", "Phishing is a type of cyber attack where..."),
        ("How to create strong passwords?", "Strong passwords should be at least 12 characters...")
    ]
    
    for query, response in conversations:
        result = memory_vault.store_conversation(query, response)
        assert result is True
    
    # Search conversation history
    memories = memory_vault.retrieve_relevant_memories("password security")
    assert isinstance(memories, dict)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
