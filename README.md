# Guardian Node

> **Your Family's Private AI Cybersecurity Assistant**  
> *"Your Own AI. No Cloud. No Spying."*

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey.svg)](https://github.com/BBO513/guardian-node)
[![Status](https://img.shields.io/badge/status-active%20development-brightgreen.svg)](https://github.com/BBO513/guardian-node)

---

## 🎯 Executive Summary

**Guardian Node** is an offline, privacy-first AI cybersecurity appliance designed for families, small businesses, and privacy-conscious individuals. It runs completely offline with no cloud dependencies, no telemetry, and no external data sharing.

**Key Value Propositions:**
- 🔒 **100% Offline Operation** - All AI processing happens locally
- 👨‍👩‍👧‍👦 **Family-Focused** - Age-appropriate cybersecurity education
- 🛡️ **Comprehensive Security** - Threat analysis, password checking, device monitoring
- 🖥️ **Easy to Use** - Web dashboard and touchscreen interface
- 🔧 **Open Source** - Transparent, auditable, and customizable

---

## 🚀 What Makes Guardian Node Unique

### 1. Privacy-First Architecture
- **No Cloud Dependencies:** All LLM processing happens locally using GGUF models
- **No Data Collection:** Zero telemetry, no user tracking, no external communication
- **Airgap Capable:** Can operate with physical network disconnect
- **Audit Logging:** Complete transparency of all operations

### 2. Family Cybersecurity Education
- **Age-Appropriate Content:** Responses tailored for children, teens, and adults
- **Interactive Learning:** Voice interface and visual guides
- **Parental Controls:** Safe exploration with guardian oversight
- **Real-World Scenarios:** Phishing education, password security, device safety

### 3. Enterprise-Grade Security
- **Threat Intelligence:** Preloaded with MITRE ATT&CK framework
- **Network Monitoring:** Device detection and security assessment
- **Password Auditing:** Strength checking and compromise detection
- **Security Recommendations:** Personalized advice based on family profile

### 4. Developer-Friendly
- **Open Source:** Fully transparent codebase
- **Extensible:** Plugin architecture for custom skills
- **MCP Protocol:** Integration with Grok/Claude via Model Context Protocol
- **Docker Support:** Easy deployment and containerization

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Guardian Node Core                      │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │   Local LLM   │  │   Family    │  │    Security     │  │
│  │  (Offline AI) │  │  Assistant  │  │     Skills      │  │
│  └───────┬───────┘  └──────┬──────┘  └────────┬────────┘  │
│          │                  │                   │           │
│          └──────────┬───────┴──────────────────┘           │
│                     │                                       │
│          ┌──────────▼───────────────────┐                  │
│          │   Guardian Interpreter       │                  │
│          │   (Main Orchestrator)        │                  │
│          └──────────┬───────────────────┘                  │
│                     │                                       │
│    ┌────────────────┼────────────────┐                     │
│    ▼                ▼                ▼                     │
│  ┌──────┐     ┌──────────┐    ┌──────────┐               │
│  │ MCP  │     │   Web    │    │  Voice   │               │
│  │Server│     │Dashboard │    │Interface │               │
│  └──────┘     └──────────┘    └──────────┘               │
└─────────────────────────────────────────────────────────────┘
         ▲                                         ▲
         │                                         │
    ┌────┴────┐                             ┌────┴────┐
    │  Grok   │                             │ Family  │
    │  Kiro   │                             │  Users  │
    └─────────┘                             └─────────┘
```

---

## 💻 Technology Stack

### Core Technologies
- **Python 3.9+** - Main programming language
- **llama-cpp-python** - Local LLM inference engine
- **PySide6** - Cross-platform GUI framework
- **YAML** - Configuration management

### AI/ML Stack
- **GGUF Models** - Quantized models for efficient local inference
- **Phi-3-mini** - Default family-friendly model (2.3GB)
- **Mistral-7B** - Advanced security analysis (4.4GB, optional)

### Integration & Deployment
- **Docker** - Containerized deployment
- **MCP Protocol** - AI assistant integration (Grok, Claude)
- **Raspberry Pi 5** - Primary target hardware (16GB)

---

## 📦 Quick Start

### Prerequisites
- Python 3.9 or higher
- 4GB+ RAM (8GB+ recommended)
- 10GB+ free disk space (for models)
- Linux, Windows, or macOS

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/BBO513/guardian-node.git
cd guardian-node
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Download LLM Model

**Recommended Model: Phi-3-mini (2.3GB)**
```bash
# Create models directory
mkdir -p models

# Download from HuggingFace
# Visit: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf
# Download: Phi-3-mini-4k-instruct-q4.gguf
# Place in: guardian-node/models/
```

#### 4. Configure
```bash
# Configuration is pre-set for offline operation
# Optional: Edit guardian_interpreter/config.yaml to customize
cp guardian_interpreter/config.yaml guardian_interpreter/config.local.yaml
```

#### 5. Run Guardian Node
```bash
cd guardian_interpreter
python main.py
```

### Docker Installation (Recommended)

```bash
# Build the image
docker-compose build

# Run Guardian Node
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

---

## 🎮 Usage Examples

### Family Cybersecurity Questions

```python
from guardian_interpreter import GuardianInterpreter

guardian = GuardianInterpreter()

# Ask family cybersecurity question
response = guardian.ask_family_question(
    "How do I teach my child about password security?",
    age_group="child"
)

print(response)
# Output: Age-appropriate, educational response about passwords
```

### Security Skills Execution

```python
# Run password security check
result = guardian.run_skill("password_check", "mypassword123")

# Run network device scan
devices = guardian.run_skill("device_scan")

# Analyze security threat
analysis = guardian.run_skill("threat_analysis", "suspicious_file.exe")
```

### MCP Integration (Grok/Kiro)

```bash
# Guardian Node provides MCP server for AI assistant integration
# See docs/grok-kiro-integration.md for complete setup guide

# Activate MCP server
cd guardian_interpreter
python mcp_server.py

# In Kiro IDE or Grok:
# "Using Guardian Node, how can I keep my family safe online?"
```

---

## 🔧 Configuration

Guardian Node uses YAML-based configuration in `guardian_interpreter/config.yaml`:

### Key Configuration Sections

```yaml
# System Information
system:
  name: "Guardian Node"
  version: "1.0.0"

# LLM Settings
llm:
  models:
    default:
      path: "models/Phi-3-mini-4k-instruct-q4.gguf"
      context_length: 4096
      threads: 4

# Network Settings (Privacy-First)
network:
  ALLOW_ONLINE: false          # Offline by default
  BLOCK_EXTERNAL_CALLS: true   # Block all external requests

# Family Assistant
family_assistant:
  enabled: true
  family_llm:
    default_safety_level: "standard"  # strict/moderate/standard
```

**Validate Configuration:**
```bash
python guardian_interpreter/config_validator.py guardian_interpreter/config.yaml
```

---

## 🛡️ Security Features

### Core Security Capabilities

1. **Threat Analysis**
   - Real-time threat detection
   - MITRE ATT&CK framework integration
   - Custom rule engine

2. **Password Security**
   - Strength assessment
   - Breach detection (offline database)
   - Policy compliance checking

3. **Device Monitoring**
   - Network device discovery
   - Security posture assessment
   - Vulnerability scanning

4. **Phishing Education**
   - Interactive training scenarios
   - Real-world examples
   - Age-appropriate content

5. **Parental Controls**
   - Content filtering
   - Time restrictions
   - Activity monitoring

### Privacy Features

- ✅ **No External API Calls** - All processing local
- ✅ **No Data Collection** - Zero telemetry
- ✅ **Comprehensive Audit Logs** - Complete transparency
- ✅ **Encrypted Storage** - Sensitive data protection
- ✅ **Airgap Operation** - Physical network isolation support

---

## 👥 Target Users

### Primary Audiences

1. **Families**
   - Parents concerned about online safety
   - Teaching children about cybersecurity
   - Managing multiple devices and accounts
   - Age-appropriate content filtering

2. **Small Businesses**
   - Legal practices (client confidentiality)
   - Medical offices (HIPAA compliance)
   - Consulting firms (proprietary information)
   - Startups (intellectual property protection)

3. **Privacy Advocates**
   - Journalists under surveillance
   - Activists in sensitive regions
   - Privacy-conscious individuals
   - Off-grid technology users

4. **Education**
   - Schools teaching cybersecurity
   - Homeschooling families
   - Educational institutions
   - Training programs

---

## 📊 Competitive Advantages

| Feature | Guardian Node | Cloud AI | Traditional Security |
|---------|--------------|----------|---------------------|
| **Privacy** | ✅ 100% Offline | ❌ Cloud-dependent | ⚠️ Varies |
| **Cost** | ✅ One-time | ❌ Subscription | ⚠️ Per-seat |
| **AI Education** | ✅ Built-in | ⚠️ Generic | ❌ None |
| **Family Focus** | ✅ Core feature | ❌ Not targeted | ❌ Enterprise-only |
| **Customization** | ✅ Open source | ❌ Proprietary | ⚠️ Limited |
| **Data Control** | ✅ 100% local | ❌ Cloud-stored | ⚠️ Varies |

---

## 🗺️ Roadmap

### Current Version (v1.0)
- [x] Core offline LLM integration
- [x] Family assistant functionality
- [x] Basic security skills
- [x] Web dashboard interface
- [x] MCP protocol support
- [x] Docker deployment

### Near-Term (v1.1-1.2)
- [ ] Enhanced device detection
- [ ] Voice interface completion
- [ ] Mobile app companion
- [ ] Advanced threat intelligence
- [ ] Custom skill marketplace

### Long-Term (v2.0+)
- [ ] Hardware appliance version
- [ ] Multi-node family network
- [ ] Machine learning model training
- [ ] Community threat sharing (privacy-preserving)
- [ ] Enterprise edition

---

## 🤝 Contributing

We welcome contributions from the community! Guardian Node is open source and thrives on collaboration.

### How to Contribute

1. **Fork the Repository**
2. **Create a Feature Branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit Changes** (`git commit -m 'Add AmazingFeature'`)
4. **Push to Branch** (`git push origin feature/AmazingFeature`)
5. **Open Pull Request**

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/guardian-node.git
cd guardian-node

# Install development dependencies
pip install -r requirements.txt
# Uncomment dev dependencies in requirements.txt for testing tools

# Run tests
pytest tests/

# Format code
black guardian_interpreter/
```

### Contribution Areas

- 🐛 **Bug Fixes** - Help squash bugs
- ✨ **New Features** - Add security skills or capabilities
- 📝 **Documentation** - Improve guides and tutorials
- 🌐 **Translations** - Make Guardian Node multilingual
- 🎨 **UI/UX** - Enhance the interface
- 🧪 **Testing** - Expand test coverage

---

## 📚 Documentation

### Core Documentation
- [Installation Guide](docs/installation.md)
- [Configuration Guide](docs/configuration.md)
- [User Manual](docs/user-manual.md)
- [API Reference](docs/api-reference.md)

### Integration Guides
- [Grok/Kiro Integration](docs/grok-kiro-integration.md)
- [MCP Server Setup](docs/mcp-server.md)
- [Docker Deployment](docs/docker-deployment.md)

### Development Guides
- [Contributing Guidelines](CONTRIBUTING.md)
- [Architecture Overview](docs/architecture.md)
- [Security Model](docs/security-model.md)
- [Plugin Development](docs/plugin-development.md)

---

## 🏆 Recognition & Credits

### First Disclosure
> This invention was publicly disclosed by **[BBO513](https://github.com/BBO513)** on **July 12, 2025** via this repository. All concept content, system architecture, and visual mockups represent the original work and public claim of the inventor as of this date.

### Technology Credits
- **LLaMA.cpp** - Efficient local inference
- **Microsoft Phi-3** - Family-friendly base model
- **PySide6** - Cross-platform GUI framework
- **MCP Protocol** - AI assistant integration standard

### Community
Special thanks to all contributors, testers, and early adopters who have helped shape Guardian Node into a robust, privacy-first family cybersecurity solution.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### What This Means
- ✅ **Commercial Use** - Use Guardian Node in commercial products
- ✅ **Modification** - Adapt and customize for your needs
- ✅ **Distribution** - Share with others
- ✅ **Private Use** - Use privately without restrictions
- ⚠️ **Liability** - Provided "as-is" without warranty

---

## 📞 Support & Contact

### Getting Help
- 📖 **Documentation:** Check [docs/](docs/) directory
- 🐛 **Bug Reports:** [GitHub Issues](https://github.com/BBO513/guardian-node/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/BBO513/guardian-node/discussions)
- 📧 **Email:** support@guardian-node.org (coming soon)

### Community
- 🌟 **Star this repo** to show support
- 🔔 **Watch** for updates and releases
- 🍴 **Fork** to contribute your improvements

### For Investors
- 📊 **Pitch Deck:** Available upon request
- 💼 **Business Plan:** Contact for details
- 📈 **Market Analysis:** Included in investment package
- 🤝 **Partnership Opportunities:** Let's talk!

---

## 🎯 Vision Statement

**Guardian Node exists to democratize family cybersecurity through privacy-respecting AI technology.**

We believe that:
- Families deserve enterprise-grade security without enterprise complexity
- Privacy is a fundamental right, not a premium feature
- AI should educate and empower, not surveil and monetize
- Cybersecurity knowledge should be accessible to everyone

Guardian Node is more than a product—it's a movement toward a safer, more private digital future for families worldwide.

---

## 📈 Project Status

**Current Status:** ✅ **Production-Ready for Investors**

- ✅ All critical bugs fixed
- ✅ Clean, professional codebase
- ✅ Comprehensive documentation
- ✅ Docker deployment ready
- ✅ MCP integration working
- ⚠️ Models need separate download (2-4GB)
- ⚠️ Optional features require additional setup

**Last Updated:** November 19, 2025  
**Version:** 1.0.0  
**Stability:** Stable

---

## 🔗 Quick Links

- **Repository:** https://github.com/BBO513/guardian-node
- **Documentation:** [docs/](docs/)
- **Issues:** [GitHub Issues](https://github.com/BBO513/guardian-node/issues)
- **Discussions:** [GitHub Discussions](https://github.com/BBO513/guardian-node/discussions)
- **Changelog:** [CHANGES.md](CHANGES.md)
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)

---

<div align="center">

**Built with ❤️ for families who value privacy and security**

[⬆ Back to Top](#guardian-node)

</div>
