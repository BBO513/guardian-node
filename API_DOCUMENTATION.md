# Guardian Node REST API Documentation

## Overview

The Guardian Node REST API provides mobile app integration, remote control, and monitoring capabilities. All sensitive operations require password authentication.

**Base URL**: `http://your-raspberry-pi-ip:5000`

---

## 🔐 Authentication

Most endpoints require an override password for authentication. The password is:
- **Secret from children** (should not be shared with kids)
- **Logged on every use** (parents get notified)
- **Securely hashed** (SHA-256)

### First Run
On first startup, a random password is generated and logged. **Change it immediately!**

---

## 📡 API Endpoints

### System Status

#### GET /api/status
Get current system status and available features.

**Response**:
```json
{
  "system_status": "Operational",
  "llm_loaded": true,
  "online_mode": false,
  "api_port": 5000,
  "current_time": "Sat Dec  6 01:00:00 2025",
  "features": {
    "memory_vault": true,
    "network_scanner": true,
    "voice_interface": true
  }
}
```

#### GET /api/health
Health check endpoint for monitoring.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": 1701820800.0
}
```

---

### Online Mode Control

#### GET /api/online_mode
Get current online/offline mode status.

**Response**:
```json
{
  "online_mode": false
}
```

#### POST /api/online_mode
Set online/offline mode (requires password).

**Request**:
```json
{
  "state": true,
  "password": "your-override-password"
}
```

**Response**:
```json
{
  "success": true,
  "online_mode": true
}
```

---

### Password Management

#### POST /api/password/set
Change override password (requires old password).

**Request**:
```json
{
  "old_password": "current-password",
  "new_password": "new-secure-password"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Password updated successfully"
}
```

**Note**: Password usage is logged and triggers notification.

#### POST /api/password/verify
Verify if a password is correct.

**Request**:
```json
{
  "password": "password-to-verify"
}
```

**Response**:
```json
{
  "valid": true
}
```

#### GET /api/password/usage
Get password usage log (requires password).

**Query Parameters**:
- `password`: Override password

**Response**:
```json
{
  "usage_log": [
    {
      "timestamp": "2025-12-06T01:00:00",
      "success": true,
      "source": "online_mode_change",
      "ip": "192.168.1.100"
    }
  ]
}
```

---

### LLM Queries

#### POST /api/query
Send a query to the LLM for processing.

**Request**:
```json
{
  "query": "How do I set up parental controls on iPad?"
}
```

**Response**:
```json
{
  "success": true,
  "query": "How do I set up parental controls on iPad?",
  "response": "To set up parental controls on iPad...",
  "timestamp": "2025-12-06T01:00:00"
}
```

---

### Memory Vault

#### GET /api/memory/stats
Get memory vault statistics.

**Response**:
```json
{
  "family_profiles": 2,
  "conversations": 15,
  "devices": 8,
  "security_events": 3
}
```

#### POST /api/memory/search
Search stored memories.

**Request**:
```json
{
  "query": "Alex's devices"
}
```

**Response**:
```json
{
  "results": {
    "family_profiles": [...],
    "devices": [...]
  }
}
```

---

### Network Scanning

#### POST /api/scan/network
Scan local network for devices (requires password).

**Request**:
```json
{
  "network_range": "192.168.1.0/24",
  "password": "your-override-password"
}
```

**Response**:
```json
{
  "success": true,
  "devices": [
    {
      "ip": "192.168.1.100",
      "mac": "AA:BB:CC:DD:EE:FF",
      "vendor": "Apple Inc."
    }
  ],
  "count": 1
}
```

---

### Notifications

#### GET /api/notifications/config
Get notification configuration (sensitive data removed).

**Response**:
```json
{
  "enabled": true,
  "methods": {
    "log": true,
    "pushover": false,
    "email": false,
    "webhook": false
  },
  "pushover": {
    "configured": false
  },
  "email": {
    "configured": false
  }
}
```

#### POST /api/notifications/config
Update notification configuration (requires password).

**Request**:
```json
{
  "password": "your-override-password",
  "config": {
    "enabled": true,
    "methods": {
      "log": true,
      "pushover": true
    },
    "pushover": {
      "user_key": "your-pushover-user-key",
      "api_token": "your-pushover-api-token"
    }
  }
}
```

**Response**:
```json
{
  "success": true,
  "message": "Notification config updated"
}
```

#### POST /api/notifications/test
Send test notification (requires password).

**Request**:
```json
{
  "password": "your-override-password"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Test notification sent"
}
```

---

### Smart Home Control (Placeholder)

#### GET /api/smarthome/devices
List available smart home devices.

**Response**:
```json
{
  "devices": [],
  "message": "Smart home integration not yet configured"
}
```

#### POST /api/smarthome/control
Control smart home device (requires password).

**Request**:
```json
{
  "password": "your-override-password",
  "device": "kettle",
  "action": "turn_on"
}
```

**Response**:
```json
{
  "success": false,
  "message": "Smart home integration not yet implemented"
}
```

---

## 📱 Mobile App Integration

### iOS/Android App Development

The API is designed for mobile app integration with:
- **CORS enabled** for cross-origin requests
- **JSON responses** for easy parsing
- **RESTful design** following standard conventions
- **Password authentication** for security

### Example Mobile App Flow

1. **Check Status**: `GET /api/status`
2. **Authenticate**: `POST /api/password/verify`
3. **Query LLM**: `POST /api/query`
4. **Control Online Mode**: `POST /api/online_mode`
5. **Scan Network**: `POST /api/scan/network`

### Example cURL Commands

```bash
# Check status
curl http://192.168.1.100:5000/api/status

# Verify password
curl -X POST http://192.168.1.100:5000/api/password/verify \
  -H "Content-Type: application/json" \
  -d '{"password":"your-password"}'

# Send query
curl -X POST http://192.168.1.100:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query":"How do I secure my home network?"}'

# Toggle online mode
curl -X POST http://192.168.1.100:5000/api/online_mode \
  -H "Content-Type: application/json" \
  -d '{"state":true,"password":"your-password"}'
```

---

## 🔔 Notification Setup

### Pushover (Mobile Push Notifications)

1. Sign up at [pushover.net](https://pushover.net)
2. Get your User Key and create an API Token
3. Configure via API:

```bash
curl -X POST http://192.168.1.100:5000/api/notifications/config \
  -H "Content-Type: application/json" \
  -d '{
    "password": "your-password",
    "config": {
      "enabled": true,
      "methods": {"pushover": true},
      "pushover": {
        "user_key": "your-user-key",
        "api_token": "your-api-token"
      }
    }
  }'
```

### Email Notifications

Configure SMTP settings:

```json
{
  "password": "your-password",
  "config": {
    "enabled": true,
    "methods": {"email": true},
    "email": {
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "username": "your-email@gmail.com",
      "password": "your-app-password",
      "to_address": "parent@example.com"
    }
  }
}
```

### Webhook Notifications

Send notifications to any webhook URL:

```json
{
  "password": "your-password",
  "config": {
    "enabled": true,
    "methods": {"webhook": true},
    "webhook": {
      "url": "https://your-webhook-url.com/notify"
    }
  }
}
```

---

## 🔒 Security Features

### Password Protection
- All sensitive operations require password
- Password is hashed with SHA-256
- Usage is logged with timestamp and IP
- Notifications sent on password use

### Usage Logging
Every password use is logged:
- Timestamp
- Success/failure
- Source (what action was performed)
- IP address

### Notifications
Parents are notified when:
- Override password is used
- Online mode is changed
- Network scans are performed
- Security events occur

---

## 🏠 Smart Home Integration (Future)

### Planned Integrations
- **Home Assistant**: Local API integration
- **Zigbee**: Direct device control via zigpy
- **Tuya**: Local control via tinytuya
- **MQTT**: Publish/subscribe for IoT devices

### LLM Tool Use
The LLM will be able to:
- Understand natural language commands
- Control devices via function calling
- Maintain device state awareness
- Provide safety checks

Example:
```
User: "Turn on the kettle"
LLM: Calls smart_home.turn_on(device='kettle')
Response: "I've turned on the kettle for you."
```

---

## 🐛 Troubleshooting

### API Not Responding
```bash
# Check if API is running
curl http://localhost:5000/api/health

# Check Docker logs
docker logs guardian-node-family-assistant

# Restart container
docker-compose restart
```

### Password Not Working
```bash
# Check password file
cat data/config/override_password.json

# Reset password (requires file system access)
rm data/config/override_password.json
# Restart - new password will be generated
```

### Notifications Not Sending
```bash
# Test notification
curl -X POST http://localhost:5000/api/notifications/test \
  -H "Content-Type: application/json" \
  -d '{"password":"your-password"}'

# Check logs
docker logs guardian-node-family-assistant | grep NOTIFICATION
```

---

## 📊 API Response Codes

- **200 OK**: Request successful
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Invalid password
- **500 Internal Server Error**: Server error
- **501 Not Implemented**: Feature not yet implemented
- **503 Service Unavailable**: Required service not available

---

## 🔄 Future Enhancements

### Planned Features
- [ ] Headless browser integration for web access
- [ ] Smart home device control
- [ ] Voice command via API
- [ ] Real-time event streaming (WebSocket)
- [ ] Multi-user authentication
- [ ] API rate limiting
- [ ] API key authentication (alternative to password)
- [ ] Encrypted communication (HTTPS)

---

## 📝 Configuration Files

### Password Storage
**Location**: `data/config/override_password.json`

```json
{
  "password_hash": "sha256-hash-here",
  "created_at": "2025-12-06T01:00:00",
  "secret_from_kids": true
}
```

### Notification Config
**Location**: `data/config/notifications.json`

```json
{
  "enabled": true,
  "methods": {
    "log": true,
    "pushover": true,
    "email": false,
    "webhook": false
  },
  "pushover": {
    "user_key": "your-key",
    "api_token": "your-token"
  }
}
```

---

## 🎯 Quick Start

1. **Start Guardian Node**:
   ```bash
   cd guardian_node_clean/guardian_interpreter
   python main.py
   ```

2. **Check API Status**:
   ```bash
   curl http://localhost:5000/api/status
   ```

3. **Get Default Password**:
   Check logs for generated password on first run

4. **Change Password**:
   ```bash
   curl -X POST http://localhost:5000/api/password/set \
     -H "Content-Type: application/json" \
     -d '{"old_password":"default-password","new_password":"new-secure-password"}'
   ```

5. **Test Query**:
   ```bash
   curl -X POST http://localhost:5000/api/query \
     -H "Content-Type: application/json" \
     -d '{"query":"What is cybersecurity?"}'
   ```

---

**API Version**: 1.0
**Last Updated**: 2025-12-06
**Status**: Production Ready
