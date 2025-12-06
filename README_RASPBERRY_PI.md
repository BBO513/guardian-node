# 🛡️ Guardian Node for Raspberry Pi

**Your Family's Private AI Cybersecurity Assistant**  
*Optimized for Raspberry Pi - 100% Offline, 100% Private*

[![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi-red.svg)](https://www.raspberrypi.org/)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🎯 What is Guardian Node?

Guardian Node is a **privacy-first AI cybersecurity assistant** designed to run on Raspberry Pi. It provides:

- 🧠 **AI-Powered Assistance** - Local LLM (Gemma 2B) for cybersecurity advice
- 🔍 **Network Scanning** - Discover devices and assess security risks
- 💾 **Persistent Memory** - Remembers family members, devices, and conversations
- 🔒 **Complete Privacy** - Everything runs locally, no cloud, no tracking

**Perfect for families, small businesses, and privacy-conscious users!**

---

## ⚡ One-Command Installation

```bash
cd guardian_node_clean
./install_raspberry_pi.sh
```

That's it! The script will:
- ✅ Install all system dependencies
- ✅ Install Python packages
- ✅ Set up network scanning (Nmap)
- ✅ Configure persistent memory (RAG)
- ✅ Create data directories
- ✅ Optimize for Raspberry Pi
- ✅ Optionally set up as a system service

**Time**: 15-20 minutes (mostly downloading packages)

---

## 📋 Requirements

### Hardware

**Minimum**:
- Raspberry Pi 4 (4GB RAM)
- 32GB microSD card
- Power supply (5V/3A)

**Recommended**:
- Raspberry Pi 5 (8GB RAM)
- 64GB+ microSD card or SSD
- Active cooling
- Ethernet connection

### Software

- Raspberry Pi OS (64-bit recommended)
- Python 3.9+
- 10GB+ free disk space

---

## 🚀 Quick Start

### 1. Install

```bash
./install_raspberry_pi.sh
```

### 2. Download Model

Download the Gemma 2 2B model (~1.5GB):
- Place in: `models/gemma-2-2b-it-Q4_K_M.gguf`

### 3. Start

```bash
cd guardian_interpreter
python3 main.py
```

### 4. Use

```bash
guardian-family> help              # Show commands
guardian-family> memory stats      # Memory statistics
guardian-family> scan network      # Discover devices
guardian-family> scan assess       # Security assessment
guardian-family> ask What is phishing?  # Ask AI
```

---

## 🎯 Key Features

### 🧠 Persistent Memory (RAG)

Guardian Node remembers:
- **Family Members** - Names, roles, ages, safety preferences
- **Conversations** - Past discussions and topics
- **Devices** - Network inventory with details
- **Security Events** - Important activities

```bash
# Add family member
guardian-family> memory add profile
Name: Sarah
Role: Child
Age Group: Child
Safety Level: strict

# Search memories
guardian-family> memory search Sarah

# AI uses this context automatically!
guardian-family> ask How can I keep Sarah safe online?
```

### 🔍 Network Scanning

Comprehensive network visibility:
- **Device Discovery** - Find all devices on your network
- **Port Scanning** - Identify open ports and services
- **Vulnerability Detection** - Detect security weaknesses
- **Security Assessment** - Get actionable recommendations

```bash
# Discover devices
guardian-family> scan network

# Scan specific device
guardian-family> scan host 192.168.1.100

# Vulnerability scan
guardian-family> scan vuln 192.168.1.100

# Full assessment
guardian-family> scan assess
```

### 🤖 AI-Powered Assistance

Local AI that understands your family:
- **Cybersecurity Advice** - Expert guidance
- **Family-Friendly** - Age-appropriate responses
- **Context-Aware** - Uses stored memories
- **Completely Offline** - No cloud, no tracking

```bash
guardian-family> ask How do I secure my home Wi-Fi?
guardian-family> ask What apps are safe for kids?
guardian-family> ask Explain phishing to a 10-year-old
```

---

## 📊 Performance

### Raspberry Pi 5 (8GB)

- **Model Loading**: ~10 seconds
- **Query Response**: 3-5 seconds
- **Network Scan**: 30-60 seconds
- **Memory Usage**: 1-2GB
- **Recommended**: ✅ Excellent performance

### Raspberry Pi 4 (4GB)

- **Model Loading**: ~15 seconds
- **Query Response**: 5-8 seconds
- **Network Scan**: 45-90 seconds
- **Memory Usage**: 1.5-2.5GB
- **Recommended**: ✅ Good performance

---

## 🔧 Configuration

### Optimize for Your Pi

Edit `guardian_interpreter/config.yaml`:

```yaml
# For Raspberry Pi 4 (4GB)
llm:
  models:
    default:
      context_length: 2048  # Reduce for less memory
      threads: 4

# For Raspberry Pi 5 (8GB)
llm:
  models:
    default:
      context_length: 4096  # Full context
      threads: 4
```

### Run as Service

```bash
# Set up during installation, or manually:
sudo systemctl enable guardian-node
sudo systemctl start guardian-node
sudo systemctl status guardian-node
```

---

## 🔒 Privacy & Security

### Privacy Features

- ✅ **100% Local** - All processing on your Raspberry Pi
- ✅ **No Cloud** - Zero external API calls
- ✅ **No Tracking** - No telemetry or analytics
- ✅ **No Internet Required** - Works completely offline
- ✅ **Your Data** - Everything stays on your device

### Security Features

- ✅ **Network Scanning** - Identify security risks
- ✅ **Vulnerability Detection** - Find weaknesses
- ✅ **AI Guidance** - Expert security advice
- ✅ **Audit Logging** - Track all activities
- ✅ **Encrypted Storage** - Protect sensitive data

---

## 📚 Documentation

### Quick Guides

- **[RASPBERRY_PI_SETUP.md](RASPBERRY_PI_SETUP.md)** - Complete setup guide
- **[RAG_QUICK_START.md](RAG_QUICK_START.md)** - Memory system guide
- **[NETWORK_SCANNING_GUIDE.md](NETWORK_SCANNING_GUIDE.md)** - Scanning guide

### Detailed Documentation

- **[RAG_IMPLEMENTATION_GUIDE.md](RAG_IMPLEMENTATION_GUIDE.md)** - Memory system details
- **[RAG_ARCHITECTURE.txt](RAG_ARCHITECTURE.txt)** - System architecture
- **[START_HERE.md](START_HERE.md)** - Navigation guide

---

## 🎓 Use Cases

### Home Network Security

- Monitor your home network
- Discover unknown devices
- Identify security risks
- Get AI-powered recommendations

### Family Protection

- Teach kids about cybersecurity
- Set up parental controls
- Monitor family devices
- Age-appropriate guidance

### Small Business

- Network inventory
- Security assessments
- Compliance checking
- Privacy-first solution

### Learning & Education

- Learn about networking
- Practice ethical hacking
- Understand security concepts
- Hands-on cybersecurity

---

## 🛠️ Troubleshooting

### Out of Memory

```bash
# Reduce context length in config.yaml
context_length: 2048

# Or add swap (not recommended for SD card)
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### Slow Performance

```bash
# Use SSD instead of SD card
# Enable performance governor
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Reduce model size or context length
```

### Network Scanning Issues

```bash
# Run with sudo for privileged scans
sudo python3 main.py

# Or add capabilities
sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/python3.9
```

---

## 🔄 Updates

### Update Guardian Node

```bash
cd ~/guardian_node_clean
git pull  # If using git

# Or copy new files

# Reinstall dependencies if needed
cd guardian_interpreter
pip3 install -r requirements.txt --upgrade
```

### Update System

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

---

## 💾 Backup

### Backup Data

```bash
# Backup everything
tar -czf guardian_backup_$(date +%Y%m%d).tar.gz \
    data/ \
    guardian_interpreter/config.yaml \
    logs/

# Or just data
cp -r data/ /mnt/backup/guardian_data_$(date +%Y%m%d)/
```

### Restore

```bash
# Restore from backup
tar -xzf guardian_backup_20251205.tar.gz
```

---

## 🎉 What You Get

### Complete Package

✅ **AI Assistant** - Local LLM for cybersecurity advice  
✅ **Network Scanner** - Comprehensive network visibility  
✅ **Persistent Memory** - Remembers family and devices  
✅ **Privacy-First** - 100% offline, no cloud  
✅ **Easy to Use** - Simple CLI commands  
✅ **Well-Documented** - Comprehensive guides  
✅ **Production-Ready** - Robust and reliable  
✅ **Raspberry Pi Optimized** - Runs great on Pi 4/5  

### Storage Requirements

- **System**: ~15MB (dependencies)
- **Model**: ~1.5GB (Gemma 2B Q4)
- **Embeddings**: ~80MB (sentence transformers)
- **Data**: Grows with usage (~1KB per item)
- **Total**: ~2GB initial + usage

---

## 🚀 Getting Started Checklist

- [ ] Raspberry Pi 4/5 with 4GB+ RAM
- [ ] Raspberry Pi OS installed
- [ ] Internet connection (for installation)
- [ ] Run `./install_raspberry_pi.sh`
- [ ] Download LLM model
- [ ] Start Guardian Node
- [ ] Add family members
- [ ] Scan your network
- [ ] Ask security questions

---

## 📞 Support

### Documentation

- Complete setup guide: `RASPBERRY_PI_SETUP.md`
- Memory system: `RAG_QUICK_START.md`
- Network scanning: `NETWORK_SCANNING_GUIDE.md`

### Community

- GitHub Issues: Report bugs and request features
- GitHub Discussions: Ask questions and share ideas

---

## 🏆 Why Guardian Node?

### For Families

- ✅ Teach kids about cybersecurity
- ✅ Monitor home network
- ✅ Get expert advice
- ✅ Complete privacy

### For Privacy Advocates

- ✅ No cloud dependencies
- ✅ No data collection
- ✅ No tracking
- ✅ Open source

### For Raspberry Pi Users

- ✅ Optimized for Pi hardware
- ✅ Low power consumption
- ✅ Runs 24/7
- ✅ Easy to set up

### For Everyone

- ✅ Easy to use
- ✅ Well-documented
- ✅ Production-ready
- ✅ Free and open source

---

## 📈 Roadmap

### Current (v1.2.0)

- ✅ RAG persistent memory
- ✅ Network scanning
- ✅ AI assistance
- ✅ Raspberry Pi optimization

### Coming Soon

- [ ] Web dashboard
- [ ] Mobile app companion
- [ ] Voice interface
- [ ] Advanced threat detection
- [ ] Multi-language support

---

## 🎯 Quick Commands Reference

```bash
# Installation
./install_raspberry_pi.sh

# Start
cd guardian_interpreter && python3 main.py

# Memory
guardian-family> memory stats
guardian-family> memory add profile
guardian-family> memory search <text>

# Scanning
guardian-family> scan network
guardian-family> scan host <ip>
guardian-family> scan vuln <ip>
guardian-family> scan assess

# AI
guardian-family> ask <question>

# Service
sudo systemctl start guardian-node
sudo systemctl status guardian-node
sudo journalctl -u guardian-node -f
```

---

## ✅ Final Checklist

Before you start:

- [ ] Raspberry Pi 4/5 ready
- [ ] Raspberry Pi OS installed
- [ ] Internet connection available
- [ ] 10GB+ free disk space
- [ ] Power supply adequate

After installation:

- [ ] All dependencies installed
- [ ] LLM model downloaded
- [ ] Guardian Node starts
- [ ] Memory vault working
- [ ] Network scanner working
- [ ] Test commands successful

---

## 🎉 You're Ready!

Guardian Node is now ready to protect your family's digital life!

**Start with**:
```bash
./install_raspberry_pi.sh
```

**Then**:
1. Add your family members
2. Scan your network
3. Ask security questions
4. Enjoy complete privacy!

---

**Version**: Guardian Node v1.2.0 for Raspberry Pi  
**Status**: ✅ Production Ready  
**Platform**: Raspberry Pi 4/5 (Linux)  
**License**: MIT  
**Date**: December 5, 2025

**🛡️ Your Family's Private AI Cybersecurity Assistant 🛡️**

*No Cloud. No Tracking. Complete Privacy.*
