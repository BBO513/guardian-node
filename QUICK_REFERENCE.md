# Guardian Node - Quick Reference Card

## 🚀 Launch Commands

```bash
# CLI Mode (default)
python guardian_interpreter/main.py

# GUI Mode
python guardian_interpreter/main.py --gui

# CLI with Voice
python guardian_interpreter/main.py --voice

# Without API
python guardian_interpreter/main.py --no-api
```

## 🔐 First-Time Setup

```bash
# 1. Start Guardian Node
python guardian_interpreter/main.py

# 2. Check logs for generated password
# Look for: "Generated default override password: abc123xyz456"

# 3. Change password via API
curl -X POST http://localhost:5000/api/password/set \
  -H "Content-Type: application/json" \
  -d '{"old_password":"abc123xyz456","new_password":"MySecurePass123!"}'
```

## 💬 CLI Commands

```bash
# Help
help

# LLM Queries
ask "How do I secure my WiFi?"

# Memory
memory stats
memory add profile
memory search "Alex"

# Network Scanning
scan network
scan host 192.168.1.100
scan assess

# Voice
voice status
voice speak "Hello"
voice listen

# System
toggle online
exit
```

## 📡 API Endpoints

```bash
# Status
GET  /api/status
GET  /api/health

# Online Mode
GET  /api/online_mode
POST /api/online_mode

# Password
POST /api/password/set
POST /api/password/verify
GET  /api/password/usage

# LLM
POST /api/query

# Memory
GET  /api/memory/stats
POST /api/memory/search

# Network
POST /api/scan/network

# Notifications
GET  /api/notifications/config
POST /api/notifications/config
POST /api/notifications/test
```

## 🧪 Testing

```bash
# Test API
python test_api.py

# Test GUI/Voice
python test_gui_voice_simple.py

# Test Memory Vault
python tests/test_memory_vault.py
```

## 📱 Mobile App Examples

```javascript
// Check status
fetch('http://192.168.1.100:5000/api/status')
  .then(res => res.json())
  .then(data => console.log(data));

// Send query
fetch('http://192.168.1.100:5000/api/query', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({query: 'What is cybersecurity?'})
})
  .then(res => res.json())
  .then(data => console.log(data.response));

// Toggle online mode
fetch('http://192.168.1.100:5000/api/online_mode', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({state: true, password: 'MySecurePass123!'})
})
  .then(res => res.json())
  .then(data => console.log(data));
```

## 🔔 Notification Setup

```bash
# Pushover
curl -X POST http://localhost:5000/api/notifications/config \
  -H "Content-Type: application/json" \
  -d '{
    "password":"your-password",
    "config":{
      "enabled":true,
      "methods":{"pushover":true},
      "pushover":{
        "user_key":"your-key",
        "api_token":"your-token"
      }
    }
  }'

# Test notification
curl -X POST http://localhost:5000/api/notifications/test \
  -H "Content-Type: application/json" \
  -d '{"password":"your-password"}'
```

## 🐛 Troubleshooting

```bash
# API not responding
curl http://localhost:5000/api/health

# Check logs
docker logs guardian-node-family-assistant

# Restart
docker-compose restart

# Install dependencies
pip install -r guardian_interpreter/requirements.txt
```

## 📚 Documentation

- `IMPLEMENTATION_COMPLETE.md` - Complete summary
- `API_DOCUMENTATION.md` - Full API reference
- `QUICK_START_GUI_VOICE.md` - GUI/Voice guide
- `RASPBERRY_PI_SETUP.md` - Pi setup guide
- `REST_API_COMPLETE.md` - API implementation
- `START_HERE.md` - Getting started

## 🎯 Key Features

✅ Persistent Memory (RAG)
✅ Network Scanning
✅ GUI Interface
✅ Voice Interface
✅ REST API
✅ Password Auth
✅ Notifications
✅ Mobile App Ready
✅ Raspberry Pi Optimized

## 📊 Ports

- **5000**: REST API
- **8000**: Main service
- **8080**: GUI/Health check

## 🔒 Security

- All processing local
- No cloud dependencies
- Password protected
- Usage logging
- Notifications on password use
- Secret from children

---

**Quick Help**: Type `help` in CLI or visit `/api/status` for API
