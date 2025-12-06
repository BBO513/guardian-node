# Memory Vault - Persistent RAG Memory System for Guardian Node (Noddy)
# Implements vector database storage for family profiles, conversation history, and device inventory

import os
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    chromadb = None

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None


class MemoryVault:
    """
    Persistent memory system using ChromaDB for vector storage
    Stores family profiles, conversation history, and device inventory
    """
    
    def __init__(self, data_dir: str = "data/memory", logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger('guardian.memory')
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.db = None
        self.embedding_model = None
        self.collections = {}
        
        # Initialize components
        self._initialize_database()
        self._initialize_embedding_model()
        self._initialize_collections()
    
    def _initialize_database(self):
        """Initialize ChromaDB for persistent vector storage"""
        if not CHROMADB_AVAILABLE:
            self.logger.error("ChromaDB not available. Install with: pip install chromadb")
            return False
        
        try:
            # Use persistent storage
            self.db = chromadb.PersistentClient(
                path=str(self.data_dir / "chroma_db"),
                settings=Settings(
                    anonymized_telemetry=False,  # Privacy-first
                    allow_reset=True
                )
            )
            self.logger.info(f"ChromaDB initialized at {self.data_dir / 'chroma_db'}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize ChromaDB: {e}")
            return False
    
    def _initialize_embedding_model(self):
        """Initialize sentence transformer for creating embeddings"""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            self.logger.error("sentence-transformers not available. Install with: pip install sentence-transformers")
            return False
        
        try:
            # Use lightweight, fast model for embeddings
            model_name = "all-MiniLM-L6-v2"  # 384 dimensions, 80MB
            self.embedding_model = SentenceTransformer(model_name)
            self.logger.info(f"Embedding model loaded: {model_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load embedding model: {e}")
            return False
    
    def _initialize_collections(self):
        """Create collections for different data types"""
        if not self.db:
            return
        
        collection_names = [
            "family_profiles",      # Family member information
            "conversation_history", # Past interactions
            "device_inventory",     # Known devices
            "security_events"       # Security-related events
        ]
        
        for name in collection_names:
            try:
                self.collections[name] = self.db.get_or_create_collection(
                    name=name,
                    metadata={"description": f"Guardian Node {name}"}
                )
                self.logger.info(f"Collection initialized: {name}")
            except Exception as e:
                self.logger.error(f"Failed to create collection {name}: {e}")
    
    def is_available(self) -> bool:
        """Check if RAG system is fully operational"""
        return (CHROMADB_AVAILABLE and 
                SENTENCE_TRANSFORMERS_AVAILABLE and 
                self.db is not None and 
                self.embedding_model is not None)
    
    def store_family_profile(self, name: str, role: str, age_group: str, 
                            safety_level: str = "standard", **kwargs):
        """Store or update a family member profile"""
        if not self.is_available():
            self.logger.warning("Memory Vault not available")
            return False
        
        try:
            profile_data = {
                "name": name,
                "role": role,
                "age_group": age_group,
                "safety_level": safety_level,
                "timestamp": datetime.now().isoformat(),
                **kwargs
            }
            
            # Create searchable text
            profile_text = f"{name} is a {role} ({age_group}) with {safety_level} safety level"
            
            # Generate embedding
            embedding = self.embedding_model.encode(profile_text).tolist()
            
            # Store in ChromaDB
            collection = self.collections["family_profiles"]
            doc_id = f"profile_{name.lower().replace(' ', '_')}"
            
            collection.upsert(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[profile_text],
                metadatas=[profile_data]
            )
            
            self.logger.info(f"Stored family profile: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store family profile: {e}")
            return False

    def store_conversation(self, user_query: str, assistant_response: str, 
                          context: Optional[Dict[str, Any]] = None):
        """Store conversation history for future reference"""
        if not self.is_available():
            return False
        
        try:
            conversation_data = {
                "query": user_query,
                "response": assistant_response[:200],  # Store summary
                "timestamp": datetime.now().isoformat(),
                "context": json.dumps(context) if context else "{}"
            }
            
            # Create searchable text
            conv_text = f"User asked: {user_query}. Assistant responded about: {assistant_response[:100]}"
            
            # Generate embedding
            embedding = self.embedding_model.encode(conv_text).tolist()
            
            # Store in ChromaDB
            collection = self.collections["conversation_history"]
            doc_id = f"conv_{datetime.now().timestamp()}"
            
            collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[conv_text],
                metadatas=[conversation_data]
            )
            
            self.logger.debug(f"Stored conversation: {user_query[:50]}...")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store conversation: {e}")
            return False
    
    def store_device(self, device_name: str, device_type: str, 
                    ip_address: Optional[str] = None, **kwargs):
        """Store device information"""
        if not self.is_available():
            return False
        
        try:
            device_data = {
                "name": device_name,
                "type": device_type,
                "ip_address": ip_address or "unknown",
                "timestamp": datetime.now().isoformat(),
                **kwargs
            }
            
            # Create searchable text
            device_text = f"{device_name} is a {device_type} device at {ip_address or 'unknown IP'}"
            
            # Generate embedding
            embedding = self.embedding_model.encode(device_text).tolist()
            
            # Store in ChromaDB
            collection = self.collections["device_inventory"]
            doc_id = f"device_{device_name.lower().replace(' ', '_')}"
            
            collection.upsert(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[device_text],
                metadatas=[device_data]
            )
            
            self.logger.info(f"Stored device: {device_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store device: {e}")
            return False
    
    def retrieve_relevant_memories(self, query: str, n_results: int = 5) -> Dict[str, List[Dict]]:
        """
        Retrieve relevant memories from all collections based on query
        Returns dictionary with results from each collection
        """
        if not self.is_available():
            return {}
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            results = {}
            
            # Search each collection
            for collection_name, collection in self.collections.items():
                try:
                    search_results = collection.query(
                        query_embeddings=[query_embedding],
                        n_results=n_results
                    )
                    
                    # Format results
                    formatted_results = []
                    if search_results['ids'] and search_results['ids'][0]:
                        for i, doc_id in enumerate(search_results['ids'][0]):
                            formatted_results.append({
                                'id': doc_id,
                                'document': search_results['documents'][0][i],
                                'metadata': search_results['metadatas'][0][i],
                                'distance': search_results['distances'][0][i] if 'distances' in search_results else None
                            })
                    
                    results[collection_name] = formatted_results
                    
                except Exception as e:
                    self.logger.error(f"Error searching {collection_name}: {e}")
                    results[collection_name] = []
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve memories: {e}")
            return {}
    
    def get_enriched_context(self, query: str, max_context_length: int = 500) -> str:
        """
        Retrieve relevant memories and format them as context for LLM
        """
        if not self.is_available():
            return ""
        
        memories = self.retrieve_relevant_memories(query, n_results=3)
        
        context_parts = []
        
        # Add family profiles
        if memories.get('family_profiles'):
            profiles = [m['document'] for m in memories['family_profiles'][:2]]
            if profiles:
                context_parts.append(f"Family Members: {'; '.join(profiles)}")
        
        # Add relevant past conversations
        if memories.get('conversation_history'):
            convs = [m['metadata']['query'] for m in memories['conversation_history'][:2]]
            if convs:
                context_parts.append(f"Recent Topics: {'; '.join(convs)}")
        
        # Add device information
        if memories.get('device_inventory'):
            devices = [m['document'] for m in memories['device_inventory'][:2]]
            if devices:
                context_parts.append(f"Known Devices: {'; '.join(devices)}")
        
        # Combine and truncate
        full_context = " | ".join(context_parts)
        if len(full_context) > max_context_length:
            full_context = full_context[:max_context_length] + "..."
        
        return full_context
    
    def get_all_family_profiles(self) -> List[Dict]:
        """Retrieve all stored family profiles"""
        if not self.is_available():
            return []
        
        try:
            collection = self.collections["family_profiles"]
            results = collection.get()
            
            profiles = []
            if results['ids']:
                for i, doc_id in enumerate(results['ids']):
                    profiles.append({
                        'id': doc_id,
                        'document': results['documents'][i],
                        'metadata': results['metadatas'][i]
                    })
            
            return profiles
            
        except Exception as e:
            self.logger.error(f"Failed to get family profiles: {e}")
            return []
    
    def clear_collection(self, collection_name: str) -> bool:
        """Clear all data from a specific collection"""
        if not self.is_available():
            return False
        
        try:
            if collection_name in self.collections:
                self.db.delete_collection(collection_name)
                self.collections[collection_name] = self.db.create_collection(
                    name=collection_name,
                    metadata={"description": f"Guardian Node {collection_name}"}
                )
                self.logger.info(f"Cleared collection: {collection_name}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to clear collection: {e}")
            return False
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about stored memories"""
        if not self.is_available():
            return {}
        
        stats = {}
        for name, collection in self.collections.items():
            try:
                count = collection.count()
                stats[name] = count
            except Exception as e:
                self.logger.error(f"Failed to get stats for {name}: {e}")
                stats[name] = 0
        
        return stats


class MockMemoryVault:
    """Fallback mock implementation when dependencies are not available"""
    
    def __init__(self, data_dir: str = "data/memory", logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger('guardian.memory')
        self.logger.warning("Using MockMemoryVault - install chromadb and sentence-transformers for full functionality")
        self.memory_store = {
            "family_profiles": [],
            "conversation_history": [],
            "device_inventory": []
        }
    
    def is_available(self) -> bool:
        return False
    
    def store_family_profile(self, name: str, role: str, age_group: str, 
                            safety_level: str = "standard", **kwargs):
        self.memory_store["family_profiles"].append({
            "name": name, "role": role, "age_group": age_group
        })
        return True
    
    def store_conversation(self, user_query: str, assistant_response: str, 
                          context: Optional[Dict[str, Any]] = None):
        self.memory_store["conversation_history"].append({
            "query": user_query, "response": assistant_response[:100]
        })
        return True
    
    def store_device(self, device_name: str, device_type: str, 
                    ip_address: Optional[str] = None, **kwargs):
        self.memory_store["device_inventory"].append({
            "name": device_name, "type": device_type
        })
        return True
    
    def retrieve_relevant_memories(self, query: str, n_results: int = 5) -> Dict[str, List[Dict]]:
        return {}
    
    def get_enriched_context(self, query: str, max_context_length: int = 500) -> str:
        return ""
    
    def get_all_family_profiles(self) -> List[Dict]:
        return self.memory_store["family_profiles"]
    
    def clear_collection(self, collection_name: str) -> bool:
        if collection_name in self.memory_store:
            self.memory_store[collection_name] = []
            return True
        return False
    
    def get_stats(self) -> Dict[str, int]:
        return {k: len(v) for k, v in self.memory_store.items()}


def create_memory_vault(data_dir: str = "data/memory", 
                       logger: Optional[logging.Logger] = None) -> MemoryVault:
    """Factory function to create appropriate memory vault implementation"""
    if CHROMADB_AVAILABLE and SENTENCE_TRANSFORMERS_AVAILABLE:
        return MemoryVault(data_dir, logger)
    else:
        return MockMemoryVault(data_dir, logger)
