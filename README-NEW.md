# Guardian Node

**Offline AI Family Cybersecurity Assistant**  
_"Your Own AI. No Cloud. No Spying."_

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-5-red.svg)](https://www.raspberrypi.org/)

---

## 🛡️ What It Is

**Guardian Node** is a complete family cybersecurity assistant that runs entirely offline in your home. It combines AI-powered threat analysis, educational tools, and practical security features to protect your family from cyber threats while keeping all your data private and secure.

### 🎯 Core Mission
- **Privacy-First**: All data stays in your home - no cloud, no telemetry, no external data collection
- **Family-Focused**: Age-appropriate cybersecurity education and protection for the whole family
- **AI-Powered**: Local LLM provides intelligent responses and analysis without internet dependency
- **Production-Ready**: Complete deployment infrastructure with monitoring, updates, and maintenance

---

## ✨ Key Features

### 🏠 Family Cybersecurity Assistant
- **👨‍👩‍👧‍👦 6 Specialized Skills**: Threat analysis, password checking, device scanning, parental controls, phishing education, network security
- **🤖 Natural Language Interface**: Ask questions in plain English - "How can I keep my child safe online?"
- **📊 Security Analysis**: Comprehensive family security posture assessment with personalized recommendations
- **🎓 Educational Content**: Age-appropriate cybersecurity learning for children and adults

### 🔒 Privacy & Security
- **🚫 Offline-First**: Hard-blocked internet access by default - no accidental data leaks
- **📝 Comprehensive Logging**: Full audit trail of all activities for security review
- **🔐 Data Encryption**: Secure storage of family profiles and security data
- **🛡️ Network Isolation**: Runs in isolated environment with controlled network access

### 🚀 Deployment Options
- **🐳 Docker**: One-command deployment with automatic updates and health monitoring
- **🥧 Raspberry Pi 5**: Optimized for home deployment with touchscreen support
- **💻 Cross-Platform**: Runs on Linux, macOS, Windows, and ARM64 systems
- **☁️ Production-Ready**: Complete infrastructure with monitoring, backups, and maintenance
- **🤖 Kiro Integration**: MCP-enabled for AI-powered assistance via Grok while maintaining privacy

### 🧠 AI Capabilities
- **🤖 Local LLM**: Runs GGUF models completely offline (Mistral, Llama, etc.)
- **💬 Intelligent Responses**: Context-aware answers to cybersecurity questions
- **📈 Learning System**: Adapts recommendations based on family security profile
- **🎯 Threat Intelligence**: Built-in knowledge of current cybersecurity threats

---

## 🚀 Quick Start

### Option 1: Docker Deployment (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/guardian-node.git
cd guardian-node

# Start Guardian Node (downloads and configures everything automatically)
docker-compose up -d

# Access the interface
open http://localhost:8080
```

### Option 2: Direct Installation

```bash
# Clone and setup
git clone https://github.com/your-org/guardian-node.git
cd guardian-node/guardian_interpreter

# Install dependencies
pip install -r requirements.txt

# Start Guardian Node
python main.py
```

### Option 3: Raspberry Pi Production

```bash
# Automated Raspberry Pi setup
curl -sSL https://raw.githubusercontent.com/your-org/guardian-node/main/install.sh | bash
```

---

## 💬 Family Usage Examples

### Direct Guardian Node Usage

**Daily Security Check:**
```bash
Guardian> family analyze
Guardian> family recommendations
```

**Teaching Kids Online Safety:**
```bash
Guardian> ask "How do I explain phishing to my 10-year-old?"
Guardian> family skill phishing_education
```

**Password Security:**
```bash
Guardian> family skill password_check mypassword123
Guardian> ask "How do I create strong passwords for my family?"
```

**Network Security:**
```bash
Guardian> family skill network_security_audit
Guardian> ask "How do I secure my home WiFi?"
```

### Grok + Kiro Integration Examples

**Family Cybersecurity Education:**
```
Ask Grok: "Using Guardian Node, help me teach my teenager about social media privacy"
Ask Grok: "Using Guardian Node, what are age-appropriate cybersecurity lessons for a 12-year-old?"
```

**Security Analysis:**
```
Ask Grok: "Using Guardian Node, analyze my family's current security posture"
Ask Grok: "Using Guardian Node, what are the top 3 security improvements my family should make?"
```

**Device Protection:**
```
Ask Grok: "Using Guardian Node, how do I secure my family's smartphones and tablets?"
Ask Grok: "Using Guardian Node, check if my home network is properly secured"
```

**Threat Education:**
```
Ask Grok: "Using Guardian Node, explain current phishing threats in family-friendly terms"
Ask Grok: "Using Guardian Node, how do I protect my family from online scams?"
```

**Expected Grok Responses:**
- ✅ Family-friendly, educational tone
- ✅ Privacy-first language ("offline processing", "local analysis")
- ✅ Age-appropriate content filtering
- ✅ Actionable, specific recommendations
- ✅ Guardian Node tool integration and results

---

## 🏗️ Architecture

### Core Components

```
guardian-node/
├── guardian_interpreter/           # Main application
│   ├── main.py                    # Application entry point
│   ├── family_assistant/          # Family cybersecurity features
│   ├── protocols/                 # Security analysis modules
│   ├── skills/                    # Modular cybersecurity tools
│   ├── security/                  # Data protection and encryption
│   └── voice/                     # Voice interface components
├── docker/                        # Container deployment
├── docs/                          # Complete documentation
├── tests/                         # Comprehensive test suite
└── config/                        # Configuration templates
```

### Family Assistant Skills

1. **🔍 Threat Analysis** - Comprehensive security threat assessment
2. **🔐 Password Checker** - Real-time password strength analysis with feedback
3. **📱 Device Scanner** - Family device security audit and vulnerability detection
4. **👶 Parental Controls** - Child safety settings verification and configuration
5. **🎣 Phishing Education** - Interactive learning about email security and scams
6. **🌐 Network Security** - Home WiFi and network security comprehensive audit

---

## 🔧 Configuration

### Basic Configuration (`config/config.yaml`)

```yaml
# Guardian Node Family Configuration
system:
  name: "Guardian Node Family Assistant"
  version: "1.0.0"
  owner: "Your Family Name"

# Privacy-First Network Settings
network:
  ALLOW_ONLINE: false              # Hard block internet by default
  allowed_domains: []              # Whitelist for updates only
  log_blocked_calls: true          # Log all blocked requests

# Family Assistant Settings
family_assistant:
  enabled: true
  gui_enabled: true
  child_safe_mode: true
  default_safety_level: "standard"
  
  # Voice interface
  voice_interface:
    enabled: true
    wake_word: "guardian"
    privacy_mode: true

# Local AI Settings
llm:
  model_path: "models/your-model.gguf"
  context_length: 4096
  temperature: 0.7
  child_safe_responses: true
```

### Environment Variables

```bash
# Docker environment
GUARDIAN_MODE=family
GUARDIAN_OFFLINE=true
GUARDIAN_GUI_ENABLED=true
GUARDIAN_FAMILY_MODE=true

# MCP Integration (optional)
GUARDIAN_MCP_ENABLED=true
GUARDIAN_MCP_PORT=8080
GUARDIAN_PRIVACY_MODE=strict
GUARDIAN_CHILD_SAFE=true
```

### MCP Configuration (`.kiro/settings/mcp.json`)

```json
{
  "mcpServers": {
    "guardian-node": {
      "command": "python",
      "args": [
        "-m", "guardian_interpreter.mcp_server",
        "--privacy-mode", "strict",
        "--child-safe", "true"
      ],
      "cwd": "./guardian-node",
      "env": {
        "GUARDIAN_OFFLINE": "true",
        "GUARDIAN_PRIVACY_MODE": "strict"
      },
      "autoApprove": [
        "ask_family_question",
        "get_security_recommendations",
        "guardian_status"
      ]
    }
  }
}
```

---

## 📊 Monitoring & Maintenance

### Health Monitoring
```bash
# Check system health
docker-compose exec guardian-node python /app/health_check.py --comprehensive

# View logs
docker-compose logs -f guardian-node

# Monitor resources
docker stats guardian-node
```

### Updates
```bash
# Safe update with automatic backup
./docker/update_container.sh

# Update with cleanup
./docker/update_container.sh --cleanup
```

### Backup & Recovery
```bash
# Create backup
./docker/update_container.sh --backup-only

# Restore from backup (automatic on failed updates)
```

---

## 🔒 Security Features

### Privacy Protection
- **🚫 No External Calls**: All processing happens locally
- **📝 Audit Logging**: Complete record of all activities
- **🔐 Data Encryption**: Secure storage of family information
- **🛡️ Network Isolation**: Controlled network access with monitoring

### Family Safety
- **👶 Child-Safe Responses**: Age-appropriate content filtering
- **🎓 Educational Focus**: Learning-oriented cybersecurity guidance
- **👨‍👩‍👧‍👦 Family Profiles**: Customized security for different family members
- **⚠️ Threat Alerts**: Proactive notification of security issues

### System Security
- **🐳 Container Isolation**: Runs in secure Docker environment
- **🔥 Firewall Integration**: Automatic firewall configuration
- **🔄 Automatic Updates**: Secure update mechanism with rollback
- **📊 Health Monitoring**: Continuous system health verification

---

## 🤖 Kiro IDE Integration

### Connect Guardian Node to Grok via Kiro

Guardian Node integrates seamlessly with **Grok AI** through **Kiro IDE** using the Model Context Protocol (MCP), giving you AI-powered cybersecurity assistance while maintaining complete privacy.

**Quick Setup:**
```bash
# 1. Start Guardian Node with MCP support
docker-compose up -d

# 2. Open your Guardian Node project in Kiro IDE

# 3. MCP configuration is pre-configured at .kiro/settings/mcp.json

# 4. Test the connection
# Ask Grok: "Using Guardian Node, how can I keep my family safe online?"
```

**What You Get:**
- 🤖 **AI-Enhanced Guidance** - Grok can access Guardian Node's family cybersecurity expertise
- 🔒 **Privacy-First** - All processing stays local, no data leaves your home
- 👨‍👩‍👧‍👦 **Family-Safe Responses** - All content filtered for family use
- 🎓 **Educational Focus** - Learn cybersecurity while getting protection

**Available Grok Commands:**
```bash
# Family cybersecurity questions
"Using Guardian Node, how do I teach my child about online safety?"

# Security analysis
"Using Guardian Node, analyze my family's security posture"

# Skill execution
"Using Guardian Node, check the strength of password 'mypassword123'"

# Device guidance
"Using Guardian Node, how do I secure my family's smartphones?"
```

**Complete Integration Guide:** [docs/grok-kiro-integration.md](docs/grok-kiro-integration.md)

---

## 📚 Documentation

### For Families
- **[Family User Guide](docs/family-user-guide.md)** - Complete setup and usage guide for families
- **[Grok + Kiro Integration](docs/grok-kiro-integration.md)** - AI-powered cybersecurity with privacy
- **[Quick Start Examples](docs/family-user-guide.md#daily-usage-examples)** - Common usage scenarios

### For Developers & IT
- **[Deployment Guide](docs/deployment-guide.md)** - Complete deployment instructions
- **[MCP Integration Guide](docs/grok-kiro-integration.md)** - Model Context Protocol setup
- **[API Documentation](docs/api-reference.md)** - REST API reference
- **[Architecture Guide](docs/architecture.md)** - System architecture and design

### For System Administrators
- **[Production Deployment](docs/deployment-guide.md#production-deployment)** - Enterprise deployment
- **[Monitoring & Maintenance](docs/deployment-guide.md#monitoring--maintenance)** - Operations guide
- **[Security Configuration](docs/deployment-guide.md#security-configuration)** - Security hardening

---

## 🧪 Testing

### Run Tests
```bash
# Unit tests
python -m pytest tests/unit/

# Integration tests
python test_guardian_integration.py

# End-to-end tests
python tests/e2e/test_family_assistant_workflow.py

# Docker deployment tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

### Test Coverage
- **Unit Tests**: Individual component testing
- **Integration Tests**: Cross-component functionality
- **End-to-End Tests**: Complete workflow validation
- **Security Tests**: Privacy and security compliance
- **Performance Tests**: Resource usage and optimization

---

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone https://github.com/your-org/guardian-node.git
cd guardian-node

# Setup development environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r guardian_interpreter/requirements.txt

# Run in development mode
cd guardian_interpreter
python main.py --dev
```

### Contributing Guidelines
1. **Privacy First**: All features must maintain offline-first operation
2. **Family Safe**: Content must be appropriate for all ages
3. **Security Focused**: Security considerations in all changes
4. **Well Tested**: Include tests for new functionality
5. **Documented**: Update documentation for user-facing changes

---

## 🎯 Roadmap

### Current Version (1.0.0)
- ✅ Complete family cybersecurity assistant
- ✅ 6 specialized security skills
- ✅ Natural language query processing
- ✅ Docker deployment infrastructure
- ✅ Comprehensive documentation
- ✅ End-to-end testing

### Upcoming Features (1.1.0)
- 🔄 Voice interface with wake word detection
- 📱 Mobile companion app
- 🏠 Smart home device integration
- 🎮 Gamified cybersecurity education for kids
- 📊 Advanced threat intelligence

### Future Vision (2.0.0)
- 🤖 Advanced AI with local fine-tuning
- 🌐 Mesh networking for family device protection
- 🔍 Real-time threat detection and response
- 📈 Community threat intelligence sharing (privacy-preserving)
- 🏢 Enterprise family office deployment

---

## 📞 Support

### Getting Help
- **📖 Documentation**: Check the comprehensive guides in `docs/`
- **🐛 Issues**: Report bugs via GitHub Issues
- **💬 Discussions**: Join community discussions
- **📧 Contact**: guardian-support@example.com

### Community
- **🌟 GitHub**: Star the repository to show support
- **🔄 Contributions**: Pull requests welcome
- **📢 Feedback**: Share your family's experience
- **🎓 Education**: Help improve cybersecurity education

---

## 📄 License

**MIT License** - Free for personal and commercial use with attribution.

```
Copyright (c) 2025 Guardian Node Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 🏆 Recognition

### First Disclosure Notice
> This invention was publicly disclosed by **[BBO513](https://github.com/BBO513)** on **July 12, 2025** via this repository. All concept content, system architecture, and visual mockups represent original work and public claim as of this date.

### Acknowledgments
- **Privacy Advocates**: For inspiring offline-first design
- **Cybersecurity Community**: For threat intelligence and best practices
- **Open Source Community**: For the tools and libraries that make this possible
- **Families**: For feedback and real-world testing

---

## 🌟 Why Guardian Node?

### For Families
- **🏠 Runs in Your Home**: Your data never leaves your house
- **👨‍👩‍👧‍👦 Family-Friendly**: Designed specifically for family cybersecurity needs
- **🎓 Educational**: Teaches cybersecurity while protecting
- **🔒 Private**: No tracking, no data collection, no cloud dependency

### For Privacy Advocates
- **🚫 No Telemetry**: Zero data collection or external communication
- **🔍 Transparent**: Open source with full audit capability
- **🛡️ Secure**: Military-grade security practices
- **🏠 Self-Hosted**: Complete control over your security infrastructure

### For IT Professionals
- **🚀 Production-Ready**: Complete deployment and monitoring infrastructure
- **📊 Enterprise-Grade**: Comprehensive logging, monitoring, and maintenance
- **🔧 Customizable**: Extensible architecture for specific needs
- **📈 Scalable**: From single family to enterprise deployment

---

**Guardian Node - Protecting your family's digital life with privacy-first AI.**

_No cloud. No spying. 100% yours._ 🛡️