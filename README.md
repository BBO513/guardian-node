# Guardian Node

**Offline AI Cybersecurity Appliance**  
_“Your Own AI. No Cloud. No Spying.”_

---

![Guardian Node](https://github.com/BBO513/guardian-node/assets/main/device_touchscreen_view.png)

## 🧠 What It Is

The **Guardian Node** is a plug-and-play, offline AI assistant designed to deliver private, AI-powered cybersecurity for homes, families, activists, and small offices. No cloud. No telemetry. No nonsense.

---

## 🔐 Key Features

- 💡 **Offline Large Language Model (LLM)** – SecureBERT, Mistral 7B, Dolphin, and more
- 🛡 **Cybersecurity Coach** – Detect phishing, audit passwords, and simulate threats
- 💾 **Preloaded Threat Database** – Includes MITRE ATT&CK & custom rules
- 📱 **Web Dashboard + Touchscreen Interface** – Control it from your browser or right on the device
- 📴 **Airgap Capable** – With a physical network cutoff and no internet dependency
- 🔧 **Customizable** – Built on Raspberry Pi 5 (16GB)

---

## Local AI Settings

Guardian Node uses a local GGUF model for offline AI capabilities. The default model is **Phi-3-mini-4k-instruct-q4.gguf**, provided locally at `guardian_interpreter/models/`.

To use:
- **Copy your existing `Phi-3-mini-4k-instruct-q4.gguf` to `guardian_interpreter/models/`**
  (e.g., from `C:\Users\works\Desktop\Offline AI Cyber Sec\guardian_interpreter_v1.0.0\guardian_interpreter\models` via USB or with WSL: `cp /mnt/c/...`).
- **Ensure `llama-cpp-python` is installed** (see `requirements.txt`, install offline with wheel if needed).
- **No internet required;** the model stays local and never leaves your device.

---


---

## 📦 Hardware Vision

- Fanless mini-PC case with matte black finish
- Front-facing **touchscreen panel** (no ports or switches on front)
- Hidden side ports for clean desk presentation
- E-ink or LCD display options for low power usage

---

## 🖼 Prototype Concept

![Touchscreen Guardian Node]https://github.com/BBO513/guardian-node/blob/main/image_offline_ai.png

---

## 👥 Who It’s For

- Families worried about scams and spying
- Journalists or activists working under surveillance
- Small legal/health practices needing local AI tools
- Privacy enthusiasts and off-grid tech users

---

## 💬 Example Commands

- “Audit my passwords”
- “Simulate a phishing attack for training”
- “Summarize this incident report for management”
- “Generate a secure network setup guide”

---

## 📅 First Disclosure Notice

> This invention was publicly disclosed by **[BBO513](https://github.com/BBO513)** on **July 12, 2025** via this repository.  
> All concept content, system architecture, and visual mockups herein represent the original work and public claim of the inventor as of this date.

---

## 📝 License

This README and the described concept are provided under the [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) license.  
You may share and adapt with attribution. Commercial implementations require permission from the original author.

---

## 👣 Next Steps

- ✅ Finalize Raspberry Pi & Raspberry Pi prototype
- 🔒 Begin legal/liability consultation for cybersecurity compliance
- 🧪 Launch early-access beta list
- 🚀 Crowdfund manufacturing with open source core

---

**Let’s bring private AI back home.**  
_No cloud. No spying. 100% yours._


# Guardian Interpreter – Local Modular AI Agent (Nodie Edition)

**Owner:** Blackbox Matrix  
**Status:** Foundation Starter – BOBO  
**Version:** 1.0.0

---

## 🧭 Purpose

Guardian Interpreter is a **fully offline, modular AI agent** framework designed for running on Raspberry Pi 5 (or PC) as the backend "brain" for the Guardian Node/Nodie project.

### Key Features

- **100% Offline Operation** - No cloud dependencies, no telemetry, no default API calls
- **Modular Skill System** - Add custom "protocol modules" as Python scripts ("skills")
- **Local LLM Integration** - Runs completely locally via `llama-cpp-python` and GGUF models
- **Privacy-First Security** - "Call home"/internet is **hard blocked by default**
- **Comprehensive Audit Logging** - All actions, network attempts, and user inputs are logged
- **CLI Interface** - Easy-to-use command-line interface for interaction and management

---

## 💾 Directory Structure

```
guardian_interpreter/
├── main.py                 # Main application entry point
├── config.yaml            # Configuration file
├── llm_integration.py      # LLM handling module
├── network_security.py     # Network security and audit logging
├── models/                 # Directory for GGUF model files
│   └── your-model.gguf    # Place your GGUF model here
├── skills/                 # Modular skills directory
│   ├── __init__.py
│   ├── example_skill.py    # Example skill template
│   ├── lan_scanner.py      # Network scanning skill
│   ├── router_checker.py   # Router security analysis
│   └── system_info.py      # System information skill
└── logs/                   # Log files directory
    ├── guardian.log        # Main application log
    ├── blocked_calls.log   # Blocked network requests
    └── audit.log          # Comprehensive audit trail
```

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or extract the Guardian Interpreter
cd guardian_interpreter

# Install required dependencies
pip install llama-cpp-python pyyaml psutil requests

# Optional: Install additional dependencies for enhanced functionality
pip install ipaddress threading
```

### 2. Configuration

1. **Add a GGUF Model** (Optional but recommended):
   - Download a GGUF model file (e.g., from Hugging Face)
   - Place it in the `models/` directory
   - Update the `model_path` in `config.yaml`

2. **Configure Settings**:
   - Edit `config.yaml` to customize behavior
   - Set `ALLOW_ONLINE: true` if you need internet access (disabled by default)

### 3. Run Guardian Interpreter

```bash
python main.py
```

### 4. Basic Usage

#### CLI Mode (Default)
```bash
# Start in CLI mode
python main.py

# Family assistant commands
guardian-family> help                           # Show family commands
guardian-family> family skills                  # List family skills
guardian-family> family skill threat_analysis   # Run threat analysis
guardian-family> ask "How do I protect my child online?"  # Ask family question
guardian-family> family analyze                 # Analyze family security
guardian-family> family recommendations         # Get security recommendations
```

#### GUI Mode (Family-Friendly Interface)
```bash
# Start with GUI interface
python main.py --gui

# Features:
# - Visual mode switching (Kids/Teens/Adult)
# - System status monitoring
# - Family profile management
# - Security recommendations display
# - Voice assistant integration
```

#### Advanced Options
```bash
# Enable MCP server integration
python main.py --mcp

# Enable family mode with enhanced features
python main.py --family-mode

# Combine options
python main.py --gui --family-mode
```

---

## ⚙️ Configuration

The `config.yaml` file controls all aspects of Guardian Interpreter:

### Network Security
```yaml
network:
  ALLOW_ONLINE: false              # Hard block internet by default
  allowed_domains: []              # Whitelist domains when online
  log_blocked_calls: true          # Log blocked requests
```

### LLM Settings
```yaml
llm:
  model_path: "models/your-model.gguf"
  context_length: 4096
  temperature: 0.7
  max_tokens: 512
  threads: 4
```

### Logging
```yaml
logging:
  level: "INFO"
  main_log: "logs/guardian.log"
  blocked_calls_log: "logs/blocked_calls.log"
  max_log_size_mb: 10
```

---

## 🧩 Skills System

### Available Skills

1. **example_skill** - Template for creating new skills
2. **lan_scanner** - Network device discovery and port scanning
3. **router_checker** - Router security analysis and configuration check
4. **system_info** - System information and status reporting

### Creating Custom Skills

Create a new `.py` file in the `skills/` directory:

```python
"""
My Custom Skill
Description of what this skill does.
"""

def run(*args, **kwargs):
    """
    Main entry point for the skill.
    
    Args:
        *args: Command line arguments
        **kwargs: Additional parameters
    
    Returns:
        str: Result message
    """
    # Your skill logic here
    return "Skill completed successfully"

# Optional metadata
__doc__ = "Brief description of the skill"
__version__ = "1.0.0"
__author__ = "Your Name"
```

### Using Skills

```bash
# List all skills
Guardian> skills

# Run by number
Guardian> skill 1

# Run by name
Guardian> skill lan_scanner

# Run with arguments
Guardian> skill lan_scanner 192.168.1.0/24 full
```

---

## 🤖 Nodie AI Assistant

Nodie is the local AI assistant powered by your GGUF model.

### Setup
1. Download a compatible GGUF model
2. Place it in `models/` directory
3. Update `config.yaml` with the correct path
4. Restart Guardian Interpreter

### Usage
```bash
Guardian> nodie What's my network status?
Guardian> nodie Scan the local network for devices
Guardian> nodie Help me analyze router security
```

---

## 🔒 Privacy & Security Features

### Network Security
- **Default Offline Mode**: All outbound requests blocked by default
- **Whitelist Control**: Only specified domains allowed when online
- **Request Logging**: All network attempts logged for audit
- **No Telemetry**: Zero data collection or external reporting

### Audit Logging
- **User Actions**: All commands and interactions logged
- **System Events**: Startup, shutdown, errors tracked
- **Security Events**: Network blocks, access attempts
- **Skill Execution**: All skill runs with arguments and results
- **LLM Interactions**: AI conversations (prompts and responses)

### Log Files
- `logs/guardian.log` - Main application events
- `logs/blocked_calls.log` - Blocked network requests
- `logs/audit.log` - Comprehensive audit trail

---

## 🛠️ Development

### Architecture

Guardian Interpreter follows a modular architecture:

- **main.py** - Core application and CLI interface
- **llm_integration.py** - Local LLM handling with llama-cpp-python
- **network_security.py** - Network monitoring and security controls
- **skills/** - Modular functionality as Python scripts

### Adding Features

1. **New Skills**: Add Python files to `skills/` directory
2. **Core Features**: Modify main application modules
3. **Configuration**: Update `config.yaml` schema as needed

### Testing

```bash
# Run with debug logging
python main.py

# Check logs
tail -f logs/guardian.log
tail -f logs/audit.log
```

---

## 📋 Requirements

### System Requirements
- Python 3.8+
- 4GB+ RAM (for LLM models)
- 10GB+ storage (for models and logs)
- Linux/macOS/Windows

### Python Dependencies
- `llama-cpp-python` - Local LLM inference
- `pyyaml` - Configuration file parsing
- `psutil` - System information
- `requests` - HTTP requests (when online mode enabled)

### Optional Dependencies
- CUDA support for GPU acceleration (if available)
- Additional Python packages as needed by custom skills

---

## 🔧 Troubleshooting

### Common Issues

**LLM Model Not Loading**
- Verify model file exists in `models/` directory
- Check file permissions and path in `config.yaml`
- Ensure sufficient RAM for model size

**Skills Not Loading**
- Check Python syntax in skill files
- Verify all dependencies are installed
- Review error messages in logs

**Network Requests Blocked**
- Set `ALLOW_ONLINE: true` in config if internet needed
- Add domains to `allowed_domains` list
- Check `logs/blocked_calls.log` for details

### Debug Mode

Enable debug logging in `config.yaml`:
```yaml
logging:
  level: "DEBUG"
```

---

## 📄 License

MIT License - Free for any non-malicious use, with attribution to owner.

---

## 💬 Support

**Contact:** blackboxmatrix@proton.me

For issues, feature requests, or contributions, please contact the owner.

---

## ✅ Completed Features (v1.0.0)

### Family Cybersecurity Assistant
- **Family-Friendly LLM Integration** - Enhanced prompts with child safety filtering
- **Age-Appropriate Skills** - Threat analysis, device guidance, and child education
- **Family Profile Management** - Multi-mode support (Kids/Teens/Adult)
- **Security Recommendations** - Personalized family cybersecurity guidance

### GUI Interface (PySide6)
- **Mode Switching Interface** - Visual mode selection with themed graphics
- **System Status Monitoring** - Real-time CPU, memory, and temperature display
- **Family Assistant Controls** - Voice assistant, profile management, recommendations
- **Raspberry Pi Touchscreen Optimized** - 800x480 resolution with touch-friendly UI

### Production Deployment
- **Docker Containerization** - Complete containerized deployment with health checks
- **LLM Integration** - Real LLM model support with family-friendly response formatting
- **Comprehensive Testing** - Unit, integration, and end-to-end test suites
- **Cross-Platform Support** - Windows, Linux, and ARM64 (Raspberry Pi) compatibility

### Enhanced Security & Privacy
- **Family Data Encryption** - Secure local storage with tamper protection
- **Comprehensive Audit Logging** - Family-specific activity tracking
- **Child Safety Filtering** - Age-appropriate content filtering at multiple levels
- **Offline-First Operation** - Complete functionality without internet connectivity

## 🎯 Future Roadmap

- [ ] Advanced family learning analytics
- [ ] Gamified cybersecurity education
- [ ] Voice recognition and natural language processing
- [ ] Advanced threat simulation and training
- [ ] Multi-language family support
- [ ] Enhanced IoT device security analysis

---

*Guardian Interpreter - Protecting your digital perimeter with privacy-first AI.*

