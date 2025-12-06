# RAG Quick Start Guide
## Get Guardian Node's Persistent Memory Running in 5 Minutes

---

## 🚀 Quick Installation

### Step 1: Install RAG Dependencies (2 minutes)

```bash
cd guardian_node_clean/guardian_interpreter
pip install chromadb sentence-transformers
```

**What gets installed:**
- `chromadb` - Vector database for persistent storage (~50MB)
- `sentence-transformers` - Embedding model for semantic search (~80MB model download on first run)

---

### Step 2: Verify Installation (30 seconds)

```bash
python -c "import chromadb; import sentence_transformers; print('✅ RAG Ready!')"
```

If you see `✅ RAG Ready!`, you're good to go!

---

### Step 3: Run the Demo (2 minutes)

```bash
cd guardian_node_clean
python demo_rag_system.py
```

This will:
- Initialize the memory vault
- Store sample family profiles
- Store device inventory
- Store conversation history
- Demonstrate semantic search
- Show context enrichment

---

### Step 4: Start Guardian Node with RAG (1 minute)

```bash
cd guardian_node_clean/guardian_interpreter
python main.py
```

You should see:
```
✅ Memory Vault (RAG) initialized successfully
✅ Persistent Memory (RAG) Active - I'll remember our conversations!
```

---

## 💡 Quick Commands

### View Memory Statistics
```bash
guardian-family> memory stats
```

### Add a Family Member
```bash
guardian-family> memory add profile
Name: Sarah
Role: Child
Age Group: Child
Safety Level: strict
```

### Add a Device
```bash
guardian-family> memory add device
Device Name: Sarah's iPad
Device Type: tablet
IP Address: 192.168.1.100
```

### Search Memories
```bash
guardian-family> memory search Sarah
```

### Ask Questions (with Memory Context)
```bash
guardian-family> ask How can I keep Sarah safe online?
```

The system will automatically:
1. Search memory for information about Sarah
2. Retrieve her profile (Child, strict safety)
3. Retrieve her devices (iPad)
4. Provide personalized response using this context

---

## 🎯 Real-World Example

### Scenario: Setting Up Parental Controls

**Day 1 - Initial Setup:**
```bash
# Add family member
guardian-family> memory add profile
Name: Billy
Role: Child
Age Group: Child
Safety Level: strict

# Add device
guardian-family> memory add device
Device Name: Billy's Tablet
Device Type: tablet
IP Address: 192.168.1.105

# Ask for help
guardian-family> ask How do I set up parental controls for Billy?
```

**Response:** System knows Billy is a child with strict safety level and has a tablet. Provides age-appropriate, device-specific guidance.

**Day 2 - Follow-up (after restart):**
```bash
guardian-family> ask What apps are safe for Billy?
```

**Response:** System remembers Billy from previous session, knows he's a child with strict safety, and provides appropriate recommendations.

**Day 3 - Device-Specific Help:**
```bash
guardian-family> ask How do I block YouTube on Billy's tablet?
```

**Response:** System recalls Billy's tablet information and provides tablet-specific instructions.

---

## 🔧 Troubleshooting

### Issue: "ChromaDB not available"
```bash
pip install chromadb
```

### Issue: "sentence-transformers not available"
```bash
pip install sentence-transformers
```

### Issue: Slow first run
**Normal!** The embedding model downloads on first run (~80MB). Subsequent runs are fast.

### Issue: Memory not persisting
Check that `data/memory/chroma_db/` directory exists and has write permissions.

---

## 📊 What Gets Stored?

### Family Profiles
- Name, role, age group
- Safety level preferences
- Custom notes

### Conversation History
- User questions
- Assistant responses (summary)
- Timestamps and context

### Device Inventory
- Device names and types
- IP addresses
- Custom notes

### Security Events
- Important security activities
- Timestamps and details

---

## 🎓 Learning Path

1. **Start Here**: Run `demo_rag_system.py`
2. **Basic Usage**: Try `memory stats` and `memory add profile`
3. **Search**: Use `memory search <text>` to find stored data
4. **Integration**: Ask questions and see RAG in action
5. **Advanced**: Read `RAG_IMPLEMENTATION_GUIDE.md`

---

## 📈 Performance

**Typical Response Times:**
- Store profile: ~50ms
- Search memories: ~100ms
- Full query with RAG: ~3-5s (including LLM)

**Storage Requirements:**
- Embedding model: 80MB (one-time)
- Per family member: ~1KB
- Per conversation: ~2KB
- Per device: ~500 bytes

**Example:** 100 conversations + 10 profiles + 20 devices ≈ 280KB

---

## ✅ Success Checklist

- [ ] Installed chromadb and sentence-transformers
- [ ] Ran demo_rag_system.py successfully
- [ ] Started Guardian Node with RAG active
- [ ] Added at least one family profile
- [ ] Added at least one device
- [ ] Asked a question and saw context enrichment
- [ ] Verified memory persists after restart

---

## 🚀 Next Steps

1. **Populate Your Data**: Add your real family members and devices
2. **Use Daily**: Ask questions and let the system learn
3. **Explore**: Try different search queries
4. **Customize**: Edit `config.yaml` to adjust RAG settings
5. **Integrate**: Use RAG in your own scripts (see API examples)

---

## 📚 Documentation

- **Full Guide**: `RAG_IMPLEMENTATION_GUIDE.md`
- **API Reference**: `guardian_interpreter/memory_vault.py`
- **Tests**: `tests/test_memory_vault.py`
- **Configuration**: `guardian_interpreter/config.yaml`

---

## 🎉 You're Ready!

Guardian Node now has persistent memory. It will remember:
- Your family members and their preferences
- Past conversations and topics
- Devices on your network
- Security events and activities

All stored locally, privately, and securely. No cloud, no tracking, no external APIs.

**Enjoy your privacy-first AI with long-term memory!** 🛡️
