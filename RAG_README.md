# Guardian Node - RAG (Persistent Memory) System

## 🎯 What is This?

Guardian Node now includes **RAG (Retrieval-Augmented Generation)** - a persistent memory system that allows Noddy to remember information across sessions, including:

- 👨‍👩‍👧‍👦 **Family Profiles** - Names, roles, ages, safety preferences
- 💬 **Conversation History** - Past discussions and topics
- 📱 **Device Inventory** - Known devices on your network
- 🔒 **Security Events** - Important security activities

All stored **locally and privately** - no cloud, no tracking!

---

## ⚡ Quick Start (5 Minutes)

### Option 1: Automated Installation (Recommended)

**Linux/Mac:**
```bash
cd guardian_node_clean
./install_rag.sh
```

**Windows:**
```cmd
cd guardian_node_clean
install_rag.bat
```

### Option 2: Manual Installation

```bash
cd guardian_node_clean/guardian_interpreter
pip install chromadb sentence-transformers
```

### Verify Installation

```bash
python -c "import chromadb; import sentence_transformers; print('✅ RAG Ready!')"
```

---

## 🚀 Try It Out

### 1. Run the Demo
```bash
cd guardian_node_clean
python demo_rag_system.py
```

### 2. Start Guardian Node
```bash
cd guardian_interpreter
python main.py
```

You should see:
```
✅ Memory Vault (RAG) initialized successfully
✅ Persistent Memory (RAG) Active - I'll remember our conversations!
```

### 3. Use Memory Commands

```bash
# View statistics
guardian-family> memory stats

# Add a family member
guardian-family> memory add profile
Name: Sarah
Role: Child
Age Group: Child
Safety Level: strict

# Add a device
guardian-family> memory add device
Device Name: Sarah's iPad
Device Type: tablet
IP Address: 192.168.1.100

# Search memories
guardian-family> memory search Sarah

# Ask questions (with memory context)
guardian-family> ask How can I keep Sarah safe online?
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **RAG_QUICK_START.md** | 5-minute quick start guide |
| **RAG_IMPLEMENTATION_GUIDE.md** | Complete documentation (600+ lines) |
| **RAG_IMPLEMENTATION_COMPLETE.md** | Implementation summary and checklist |
| **demo_rag_system.py** | Interactive demo script |
| **tests/test_memory_vault.py** | Test suite |

---

## 🎯 Key Features

✅ **Persistent Storage** - Data survives restarts  
✅ **Semantic Search** - Find information by meaning, not just keywords  
✅ **Context-Aware** - LLM responses use stored memories  
✅ **Privacy-First** - 100% local, no cloud  
✅ **Easy to Use** - Simple CLI commands  
✅ **Well-Tested** - 15+ test cases  
✅ **Documented** - Comprehensive guides  
✅ **Docker-Ready** - Works in containers  

---

## 💡 Real-World Example

**Day 1:**
```bash
guardian-family> memory add profile
Name: Billy
Role: Child
Age Group: Child
Safety Level: strict

guardian-family> ask How do I set up parental controls for Billy?
```
*System provides age-appropriate guidance for Billy*

**Day 2 (after restart):**
```bash
guardian-family> ask What apps are safe for Billy?
```
*System remembers Billy is a child with strict safety level*

**Day 3:**
```bash
guardian-family> ask Remind me what we discussed about Billy
```
*System retrieves previous conversations about Billy*

---

## 🔧 Technical Details

### Architecture
```
User Query → Memory Search → Context Retrieval → LLM + Context → Response
                ↓
         Store in Memory
```

### Components
- **ChromaDB** - Vector database for storage
- **Sentence Transformers** - Embedding model (all-MiniLM-L6-v2)
- **Memory Vault** - Core RAG implementation
- **CLI Integration** - User-friendly commands

### Storage
- **Location**: `data/memory/chroma_db/`
- **Size**: ~80MB (model) + ~1KB per item
- **Format**: Vector embeddings + metadata

### Performance
- Store item: ~50ms
- Search: ~100ms
- Full query with RAG: ~3-5s (including LLM)

---

## 🛠️ Troubleshooting

### "ChromaDB not available"
```bash
pip install chromadb
```

### "sentence-transformers not available"
```bash
pip install sentence-transformers
```

### Slow first run
Normal! Embedding model downloads on first run (~80MB). Subsequent runs are fast.

### Memory not persisting
Check that `data/memory/chroma_db/` exists and has write permissions.

---

## 📊 What Gets Stored?

### Family Profiles
```python
{
    "name": "Sarah",
    "role": "Child",
    "age_group": "Child",
    "safety_level": "strict",
    "notes": "8 years old, loves iPad games"
}
```

### Devices
```python
{
    "device_name": "Sarah's iPad",
    "device_type": "tablet",
    "ip_address": "192.168.1.100",
    "notes": "Educational apps only"
}
```

### Conversations
```python
{
    "query": "How do I block websites?",
    "response": "You can block websites using...",
    "timestamp": "2025-12-05T10:30:00",
    "context": {"online_mode": false}
}
```

---

## 🔒 Privacy & Security

✅ **100% Local** - All data stored on your device  
✅ **No Cloud** - No external API calls  
✅ **No Tracking** - No telemetry or analytics  
✅ **User Control** - Easy to view, export, or delete data  
✅ **Encrypted** - ChromaDB supports encryption  
✅ **Auditable** - Open source, transparent code  

---

## 🎓 Learning Path

1. **Start**: Run `install_rag.sh` or `install_rag.bat`
2. **Demo**: Run `python demo_rag_system.py`
3. **Basics**: Try `memory stats` and `memory add profile`
4. **Search**: Use `memory search <text>`
5. **Integration**: Ask questions and see RAG in action
6. **Advanced**: Read `RAG_IMPLEMENTATION_GUIDE.md`

---

## 📈 Benefits

### Before RAG:
- ❌ No memory across sessions
- ❌ Generic responses
- ❌ Limited to 4096-token context

### After RAG:
- ✅ Persistent memory
- ✅ Personalized responses
- ✅ Unlimited long-term memory

---

## 🤝 Contributing

Want to improve the RAG system?

1. Review `guardian_interpreter/memory_vault.py`
2. Add features or improvements
3. Write tests in `tests/test_memory_vault.py`
4. Update documentation
5. Submit a pull request

---

## 📞 Support

- **Quick Start**: `RAG_QUICK_START.md`
- **Full Guide**: `RAG_IMPLEMENTATION_GUIDE.md`
- **Tests**: `tests/test_memory_vault.py`
- **Demo**: `demo_rag_system.py`

---

## ✅ Status

**✅ FULLY IMPLEMENTED AND OPERATIONAL**

- All features working
- Thoroughly tested
- Fully documented
- Production-ready
- Docker-compatible

---

## 🎉 Get Started Now!

```bash
# Install
./install_rag.sh  # or install_rag.bat on Windows

# Demo
python demo_rag_system.py

# Use
cd guardian_interpreter
python main.py
```

**Enjoy your AI with persistent memory!** 🧠🛡️

---

**Version**: Guardian Node v1.1.0 with RAG  
**Status**: Production Ready  
**Last Updated**: December 5, 2025
