# Guardian Node - Comprehensive Testing Guide

## 🧪 Complete Testing Suite for Investor Demo

This guide covers all testing procedures for Guardian Node, including API tests, Raspberry Pi deployment, and investor demonstrations.

---

## 📋 Table of Contents

1. [Quick Start Testing](#quick-start-testing)
2. [API Testing](#api-testing)
3. [Feature Testing](#feature-testing)
4. [Raspberry Pi Testing](#raspberry-pi-testing)
5. [Performance Testing](#performance-testing)
6. [Investor Demo Script](#investor-demo-script)

---

## 🚀 Quick Start Testing

### Prerequisites

```bash
# Install dependencies
cd guardian_node_clean
pip install -r guardian_interpreter/requirements.txt

# Verify installation
python -c "import flask, chromadb, pyttsx3; print('✅ Core dependencies installed')"
```

### Run All Tests

```bash
# Test 1: Noddy Control Flow
python test_noddy_simple.py

# Test 2: Smart Home Control
python test_smart_home.py

# Test 3: API Endpoints
python test_api.py

# Test 4: GUI/Voice (if dependencies installed)
python test_gui_voice_simple.py
```

**Expected Results**: All tests should pass with 80%+ success rate.

---

## 🌐 API Testing

### 1. Start the API Server

```bash
cd guardian_interpreter
python main.py
```

The API will be available at: `http://localhost:5000`

### 2. Basic API Tests

#### Test 1: Health Check

```bash
curl http://localhost:5000/api/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "timestamp": 1701820800.0
}
```

#### Test 2: System Status

```bash
curl http://localhost:5000/api/status
```

**Expected Response**:
```json
{
  "system_status": "Operational",
  "llm_loaded": true,
  "online_mode": false,
  "api_port": 5000,
  "features": {
    "memory_vault": true,
    "network_scanner": true,
    "voice_interface": true
  }
}
```

#### Test 3: LLM Query

```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is cybersecurity?"}'
```

**Expected Response**:
```json
{
  "success": true,
  "query": "What is cybersecurity?",
  "response": "[LLM response text]",
  "timestamp": "2025-12-06T01:00:00"
}
```

#### Test 4: Online Mode Check

```bash
curl http://localhost:5000/api/online_mode
```

**Expected Response**:
```json
{
  "online_mode": false
}
```

#### Test 5: Noddy Permission Check

```bash
curl -X POST http://localhost:5000/api/noddy/check_query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the weather today?"}'
```

**Expected Response**:
```json
{
  "query": "What is the weather today?",
  "needs_internet": true,
  "current_online_mode": false
}
```

#### Test 6: Memory Vault Stats

```bash
curl http://localhost:5000/api/memory/stats
```

**Expected Response**:
```json
{
  "family_profiles": 1,
  "conversations": 0,
  "devices": 0,
  "security_events": 0
}
```

#### Test 7: Smart Home Devices

```bash
curl http://localhost:5000/api/smarthome/devices
```

**Expected Response**:
```json
{
  "devices": [
    {
      "id": "kettle",
      "name": "Electric Kettle",
      "type": "switch",
      "state": "off"
    }
  ],
  "count": 5,
  "integration": "mock"
}
```

#### Test 8: Password Verification (requires password)

First, get the default password from logs when starting Guardian Node.

```bash
curl -X POST http://localhost:5000/api/password/verify \
  -H "Content-Type: application/json" \
  -d '{"password": "your-default-password"}'
```

**Expected Response**:
```json
{
  "valid": true
}
```

#### Test 9: Smart Home Control (requires password)

```bash
curl -X POST http://localhost:5000/api/smarthome/control \
  -H "Content-Type: application/json" \
  -d '{
    "password": "your-password",
    "device": "kettle",
    "action": "turn_on"
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "device": "kettle",
  "state": "on",
  "message": "Mock: Turned on Electric Kettle"
}
```

#### Test 10: Set Online Mode (requires password)

```bash
curl -X POST http://localhost:5000/api/online_mode \
  -H "Content-Type: application/json" \
  -d '{
    "state": true,
    "password": "your-password"
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "online_mode": true
}
```

### 3. API Test Script

Save this as `test_api_comprehensive.sh`:

```bash
#!/bin/bash

echo "================================"
echo "Guardian Node API Test Suite"
echo "================================"

API_URL="http://localhost:5000"

# Test 1: Health Check
echo -e "\n[1/10] Health Check..."
curl -s $API_URL/api/health | jq .

# Test 2: Status
echo -e "\n[2/10] System Status..."
curl -s $API_URL/api/status | jq .

# Test 3: Online Mode
echo -e "\n[3/10] Online Mode..."
curl -s $API_URL/api/online_mode | jq .

# Test 4: Query Check
echo -e "\n[4/10] Query Check..."
curl -s -X POST $API_URL/api/noddy/check_query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the weather?"}' | jq .

# Test 5: Memory Stats
echo -e "\n[5/10] Memory Stats..."
curl -s $API_URL/api/memory/stats | jq .

# Test 6: Smart Home Devices
echo -e "\n[6/10] Smart Home Devices..."
curl -s $API_URL/api/smarthome/devices | jq .

# Test 7: LLM Query
echo -e "\n[7/10] LLM Query..."
curl -s -X POST $API_URL/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is a firewall?"}' | jq .

echo -e "\n================================"
echo "API Tests Complete!"
echo "================================"
```

Run with: `bash test_api_comprehensive.sh`

---

## 🎯 Feature Testing

### 1. Memory Vault (RAG) Testing

```bash
# Start Guardian Node
python main.py

# Test memory commands
guardian-family> memory stats
guardian-family> memory add profile
# Enter: Name=John, Role=Parent, Age Group=Adult, Safety Level=standard

guardian-family> memory search "John"
guardian-family> ask "What do you know about John?"
```

**Expected**: System should remember John and personalize responses.

### 2. Network Scanning Testing

```bash
guardian-family> scan network
# Should discover devices on local network

guardian-family> scan assess
# Should provide security assessment
```

**Expected**: Discovers devices, provides security recommendations.

### 3. Noddy Control Flow Testing

```bash
# Test 1: Query needing internet
guardian-family> ask "What's the weather today?"
# Should prompt for permission

# Test 2: Query not needing internet
guardian-family> ask "How do I secure my WiFi?"
# Should NOT prompt, uses local knowledge
```

**Expected**: Permission dialogue appears for online queries only.

### 4. Smart Home Testing

```bash
# Test 1: List devices
guardian-family> smarthome list

# Test 2: Control device
guardian-family> smarthome on kettle

# Test 3: Natural language
guardian-family> ask "turn on the kettle"

# Test 4: Temperature control
guardian-family> ask "set AC to 24 degrees"
```

**Expected**: Devices respond to commands, status updates correctly.

### 5. Voice Interface Testing

```bash
guardian-family> voice status
# Check TTS/STT availability

guardian-family> voice speak "Hello world"
# Should speak text

guardian-family> voice listen
# Should listen and process voice input
```

**Expected**: Voice commands work (if dependencies installed).

---

## 🥧 Raspberry Pi Testing

### 1. Pre-Deployment Checklist

- [ ] Raspberry Pi 4 or 5 (4GB+ RAM recommended)
- [ ] 32GB+ SD card
- [ ] Raspberry Pi OS installed
- [ ] Network connection
- [ ] (Optional) Official touchscreen

### 2. Installation on Raspberry Pi

```bash
# SSH into Raspberry Pi
ssh pi@raspberrypi.local

# Clone or copy Guardian Node
cd ~
# (Copy guardian_node_clean folder)

# Run one-command installation
cd guardian_node_clean
bash install_raspberry_pi.sh
```

### 3. Performance Testing on Pi

```bash
# Test 1: System resources
python -c "
import psutil
print(f'CPU: {psutil.cpu_percent()}%')
print(f'Memory: {psutil.virtual_memory().percent}%')
print(f'Temp: {open(\"/sys/class/thermal/thermal_zone0/temp\").read().strip()}')
"

# Test 2: LLM response time
time python -c "
from guardian_interpreter.main import CleanGuardianCLI, load_config
cli = CleanGuardianCLI(load_config())
cli.run_query('What is cybersecurity?')
"
```

**Expected Performance**:
- CPU: 30-60% during query
- Memory: 40-70% usage
- Temperature: <70°C
- Response time: 2-10 seconds

### 4. Touchscreen Testing (if available)

```bash
# Launch GUI
python main.py --gui

# Test:
# - Mode switching (Kids/Teens/Adult)
# - Button responsiveness
# - System status display
# - Touch accuracy
```

### 5. Systemd Service Testing

```bash
# Install service
sudo cp guardian_node_clean/guardian.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable guardian
sudo systemctl start guardian

# Check status
sudo systemctl status guardian

# View logs
sudo journalctl -u guardian -f
```

### 6. Network Testing on Pi

```bash
# Test local network access
curl http://localhost:5000/api/status

# Test from another device on network
curl http://raspberrypi.local:5000/api/status
```

---

## ⚡ Performance Testing

### 1. Load Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test API performance
ab -n 100 -c 10 http://localhost:5000/api/status

# Expected results:
# - Requests per second: 50-200
# - Time per request: 5-20ms
# - Failed requests: 0
```

### 2. Memory Leak Testing

```bash
# Monitor memory over time
watch -n 5 'ps aux | grep python | grep main.py'

# Run continuous queries
for i in {1..100}; do
  curl -X POST http://localhost:5000/api/query \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"Test query $i\"}"
  sleep 1
done

# Check memory after
# Should not increase significantly
```

### 3. Stress Testing

```bash
# Test concurrent requests
for i in {1..10}; do
  curl -X POST http://localhost:5000/api/query \
    -H "Content-Type: application/json" \
    -d '{"query": "What is cybersecurity?"}' &
done
wait

# All requests should complete successfully
```

---

## 🎬 Investor Demo Script

### Setup (5 minutes before demo)

```bash
# 1. Start Guardian Node
cd guardian_node_clean/guardian_interpreter
python main.py

# 2. Verify API is running
curl http://localhost:5000/api/health

# 3. Add demo family profile
# In another terminal:
python -c "
from guardian_interpreter.main import CleanGuardianCLI, load_config
cli = CleanGuardianCLI(load_config())
if cli.memory_vault:
    cli.memory_vault.store_family_profile('Sarah', 'Child', 'Child', 'strict')
    cli.memory_vault.store_family_profile('John', 'Parent', 'Adult', 'standard')
    print('✅ Demo profiles created')
"
```

### Demo Script (15 minutes)

#### Part 1: Introduction (2 min)

"Guardian Node is a privacy-first family cybersecurity assistant that runs entirely on a Raspberry Pi. No cloud, no subscriptions, complete privacy."

#### Part 2: Memory & Personalization (3 min)

```bash
# Show memory
guardian-family> memory stats

# Personalized query
guardian-family> ask "How should I set up parental controls?"
# Noddy mentions Sarah by name and provides age-appropriate advice
```

**Key Point**: "Notice how it remembers Sarah is a child and personalizes the advice."

#### Part 3: Privacy Control (3 min)

```bash
# Offline query
guardian-family> ask "What is a VPN?"
# Answers immediately with local knowledge

# Online query
guardian-family> ask "What's the weather today?"
# Prompts for permission
# Type: yes
# Shows permission dialogue
# Type: no (to go back offline)
```

**Key Point**: "It asks permission before going online, giving parents complete control."

#### Part 4: Smart Home Control (3 min)

```bash
# List devices
guardian-family> smarthome list

# Natural language control
guardian-family> ask "turn on the kettle"
guardian-family> ask "set AC to 24 degrees"
```

**Key Point**: "Control your smart home with natural language, all processed locally."

#### Part 5: Network Security (2 min)

```bash
# Quick scan
guardian-family> scan assess
# Shows security assessment
```

**Key Point**: "Monitors your home network for security issues."

#### Part 6: Mobile App Demo (2 min)

```bash
# Show API in browser or Postman
# GET http://localhost:5000/api/status
# POST http://localhost:5000/api/query
```

**Key Point**: "Full REST API for iOS and Android apps."

### Demo Talking Points

1. **Privacy-First**: "Everything runs locally on Raspberry Pi. No cloud, no data collection."

2. **Persistent Memory**: "Remembers your family members and personalizes advice."

3. **Smart Permissions**: "Asks before going online, giving parents control."

4. **Smart Home**: "Control devices with natural language, all offline."

5. **Network Security**: "Monitors and protects your home network."

6. **Mobile Ready**: "Full API for mobile apps on iOS and Android."

7. **Open Source**: "Transparent, auditable, community-driven."

8. **Cost Effective**: "One-time hardware cost, no subscriptions."

---

## 📊 Test Results Template

### System Test Report

**Date**: _____________
**Tester**: _____________
**Platform**: Raspberry Pi 4/5 / Desktop / Other: _____________

#### Core Features

| Feature | Status | Notes |
|---------|--------|-------|
| LLM Queries | ⬜ Pass ⬜ Fail | |
| Memory Vault | ⬜ Pass ⬜ Fail | |
| Network Scanning | ⬜ Pass ⬜ Fail | |
| Noddy Control | ⬜ Pass ⬜ Fail | |
| Smart Home | ⬜ Pass ⬜ Fail | |
| Voice Interface | ⬜ Pass ⬜ Fail | |
| GUI Interface | ⬜ Pass ⬜ Fail | |
| REST API | ⬜ Pass ⬜ Fail | |

#### API Endpoints

| Endpoint | Status | Response Time |
|----------|--------|---------------|
| /api/health | ⬜ Pass ⬜ Fail | _____ ms |
| /api/status | ⬜ Pass ⬜ Fail | _____ ms |
| /api/query | ⬜ Pass ⬜ Fail | _____ ms |
| /api/online_mode | ⬜ Pass ⬜ Fail | _____ ms |
| /api/smarthome/devices | ⬜ Pass ⬜ Fail | _____ ms |

#### Performance Metrics

- **CPU Usage**: _____%
- **Memory Usage**: _____%
- **Temperature**: _____°C
- **Query Response Time**: _____ seconds
- **API Requests/Second**: _____

#### Issues Found

1. _____________________________________________
2. _____________________________________________
3. _____________________________________________

#### Overall Assessment

⬜ Ready for Production
⬜ Minor Issues (list above)
⬜ Major Issues (list above)

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: API not responding
```bash
# Check if running
ps aux | grep python | grep main.py

# Check port
netstat -an | grep 5000

# Restart
pkill -f main.py
python main.py
```

**Issue**: LLM not loading
```bash
# Check model file
ls -lh models/

# Check memory
free -h

# Try smaller model
```

**Issue**: Memory vault errors
```bash
# Check ChromaDB
pip install "numpy<2.0"
pip install --upgrade chromadb
```

**Issue**: Permission denied on Pi
```bash
# Fix permissions
chmod +x install_raspberry_pi.sh
sudo chown -R pi:pi guardian_node_clean/
```

---

## ✅ Pre-Investor Checklist

- [ ] All tests passing (80%+ success rate)
- [ ] API responding to all endpoints
- [ ] Demo profiles created
- [ ] Performance acceptable on Pi
- [ ] Documentation complete
- [ ] No errors in logs
- [ ] Mobile app demo ready
- [ ] Talking points prepared
- [ ] Backup plan if demo fails

---

## 📞 Support

For issues during testing:
1. Check logs: `tail -f logs/guardian.log`
2. Review documentation
3. Run test scripts
4. Check GitHub issues

---

**Testing Status**: Ready for Investor Demo
**Last Updated**: 2025-12-06
**Version**: 1.0
