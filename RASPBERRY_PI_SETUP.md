# Guardian Node - Raspberry Pi Setup Guide
## Complete Installation for Raspberry Pi (Linux)

**Target Platform**: Raspberry Pi 4/5 (4GB+ RAM recommended)  
**OS**: Raspberry Pi OS (Debian-based)  
**Version**: Guardian Node v1.2.0 with RAG + Network Scanning  
**Date**: December 5, 2025

---

## 🎯 Overview

This guide provides complete setup instructions for running Guardian Node on a Raspberry Pi. Guardian Node is optimized for Raspberry Pi hardware and provides:

- 🧠 **Persistent Memory (RAG)** - Remembers family members, conversations, devices
- 🔍 **Network Scanning** - Discovers devices and assesses security
- 🤖 **Local AI** - Runs completely offline with no cloud dependencies
- 🔒 **Privacy-First** - All data stays on your device

---

## 📋 Prerequisites

### Hardware Requirements

**Minimum**:
- Raspberry Pi 4 (4GB RAM)
- 32GB microSD card
- Power supply (5V/3A)
- Network connection (Ethernet or Wi-Fi)

**Recommended**:
- Raspberry Pi 5 (8GB+ RAM)
- 64GB+ microSD card (or SSD via USB)
- Active cooling (fan or heatsink)
- Ethernet connection for stability

### Software Requirements

- Raspberry Pi OS (64-bit recommended)
- Python 3.9+
- 10GB+ free disk space

---

## 🚀 Complete Installation

### Step 1: Update System

```bash
# Update package lists
sudo apt-get update

# Upgrade existing packages
sudo apt-get upgrade -y

# Install essential tools
sudo apt-get install -y git curl wget build-essential
```

### Step 2: Install Python Dependencies

```bash
# Install Python development tools
sudo apt-get install -y python3-pip python3-dev python3-venv

# Verify Python version (should be 3.9+)
python3 --version
```

### Step 3: Clone Guardian Node

```bash
# Navigate to home directory
cd ~

# Clone repository (or copy files)
# If you have the files already:
cd /path/to/guardian_node_clean

# Or clone from repository:
# git clone https://github.com/yourusername/guardian-node.git
# cd guardian-node/guardian_node_clean
```

### Step 4: Install Core Dependencies

```bash
cd guardian_node_clean/guardian_interpreter

# Install core Python packages
pip3 install -r requirements.txt

# This installs:
# - llama-cpp-python (LLM inference)
# - chromadb (persistent memory)
# - sentence-transformers (embeddings)
# - python-nmap (network scanning)
# - scapy (packet analysis)
# - PySide6 (GUI)
# - And all other dependencies
```

**Note**: This may take 10-20 minutes on Raspberry Pi.

### Step 5: Install System Dependencies

```bash
# Install Nmap for network scanning
sudo apt-get install -y nmap

# Install libpcap for scapy
sudo apt-get install -y libpcap-dev

# Install audio dependencies (for voice features, optional)
sudo apt-get install -y portaudio19-dev espeak-ng

# Verify installations
nmap --version
python3 -c "import nmap; import scapy; print('✅ Network scanning ready')"
```

### Step 6: Download LLM Model

```bash
# Create models directory
mkdir -p ~/guardian_node_clean/models

# Download Gemma 2 2B model (recommended for Raspberry Pi)
cd ~/guardian_node_clean/models

# Option 1: Download from HuggingFace (if you have the file)
# Copy your gemma-2-2b-it-Q4_K_M.gguf file here

# Option 2: Use wget/curl if you have a direct link
# wget https://your-model-url/gemma-2-2b-it-Q4_K_M.gguf

# Verify model file
ls -lh gemma-2-2b-it-Q4_K_M.gguf
```

**Model Size**: ~1.5GB (Q4 quantized)

### Step 7: Create Data Directories

```bash
cd ~/guardian_node_clean

# Create necessary directories
mkdir -p data/memory
mkdir -p data/scans
mkdir -p data/families
mkdir -p logs

# Set permissions
chmod -R 755 data logs
```

### Step 8: Configure Guardian Node

```bash
cd guardian_interpreter

# The config.yaml should already be configured
# Verify it points to the correct model path
cat config.yaml | grep model_path

# Should show: models/gemma-2-2b-it-Q4_K_M.gguf
```

---

## 🧪 Test Installation

### Quick Test

```bash
cd ~/guardian_node_clean/guardian_interpreter

# Run Guardian Node
python3 main.py
```

**Expected Output**:
```
🛡️ Starting Guardian Node (Clean Build)...
✅ Memory Vault (RAG) initialized successfully
✅ Network Scanner initialized successfully
✅ Persistent Memory (RAG) Active - I'll remember our conversations!
Guardian Family Assistant CLI (Clean Build). Type 'help' for commands.
guardian-family>
```

### Test Commands

```bash
# Test help
guardian-family> help

# Test memory
guardian-family> memory stats

# Test network scanning
guardian-family> scan network

# Test AI query
guardian-family> ask What is phishing?

# Exit
guardian-family> exit
```

---

## 🔧 Raspberry Pi Optimizations

### Performance Tuning

Edit `config.yaml` for Raspberry Pi:

```yaml
# LLM Configuration (Optimized for Raspberry Pi)
llm:
  models:
    default:
      path: "models/gemma-2-2b-it-Q4_K_M.gguf"
      context_length: 4096  # Reduce if memory constrained
      threads: 4  # Use all 4 cores
      
# Performance Settings
performance:
  cache_enabled: true
  cache_size_mb: 100  # Adjust based on available RAM
  preload_models: false  # Don't preload to save memory
```

### Memory Management

```bash
# Check available memory
free -h

# Monitor during operation
watch -n 1 free -h

# If memory is tight, reduce context length in config.yaml
# Or use swap file (not recommended for SD cards)
```

### Storage Optimization

```bash
# Use SSD instead of SD card for better performance
# Connect via USB 3.0

# Or use external storage for models and data
sudo mkdir /mnt/guardian_data
sudo mount /dev/sda1 /mnt/guardian_data
ln -s /mnt/guardian_data ~/guardian_node_clean/data
```

---

## 🚀 Running as a Service

### Create Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/guardian-node.service
```

**Service Configuration**:
```ini
[Unit]
Description=Guardian Node Family Cybersecurity Assistant
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/guardian_node_clean/guardian_interpreter
ExecStart=/usr/bin/python3 /home/pi/guardian_node_clean/guardian_interpreter/main.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Enable and Start**:
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable guardian-node

# Start service
sudo systemctl start guardian-node

# Check status
sudo systemctl status guardian-node

# View logs
sudo journalctl -u guardian-node -f
```

---

## 🌐 Network Configuration

### Static IP (Recommended)

```bash
# Edit dhcpcd.conf
sudo nano /etc/dhcpcd.conf

# Add at the end:
interface eth0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8

# Restart networking
sudo systemctl restart dhcpcd
```

### Firewall Configuration

```bash
# Install UFW (if not installed)
sudo apt-get install -y ufw

# Allow SSH
sudo ufw allow 22/tcp

# Allow Guardian Node API (if using)
sudo ufw allow 5000/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

---

## 🔒 Security Hardening

### User Permissions

```bash
# Run Guardian Node as non-root user
# Already configured in systemd service

# For network scanning that requires root:
# Add user to specific groups
sudo usermod -aG netdev pi

# Or use sudo for specific scans
```

### File Permissions

```bash
cd ~/guardian_node_clean

# Secure configuration files
chmod 600 guardian_interpreter/config.yaml

# Secure data directories
chmod 700 data/memory
chmod 700 data/scans

# Secure logs
chmod 700 logs
```

### Automatic Updates

```bash
# Enable unattended upgrades
sudo apt-get install -y unattended-upgrades

# Configure
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## 📊 Monitoring

### System Monitoring

```bash
# Install monitoring tools
sudo apt-get install -y htop iotop

# Monitor CPU/Memory
htop

# Monitor disk I/O
sudo iotop

# Check temperature
vcgencmd measure_temp
```

### Guardian Node Monitoring

```bash
# View logs
tail -f ~/guardian_node_clean/logs/guardian.log

# Check memory usage
guardian-family> memory stats

# Check scan results
ls -lh ~/guardian_node_clean/data/scans/
```

---

## 🔄 Backup and Restore

### Backup Script

```bash
#!/bin/bash
# backup_guardian.sh

BACKUP_DIR="/mnt/backup/guardian_$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# Backup data
cp -r ~/guardian_node_clean/data "$BACKUP_DIR/"

# Backup configuration
cp ~/guardian_node_clean/guardian_interpreter/config.yaml "$BACKUP_DIR/"

# Backup logs (last 7 days)
find ~/guardian_node_clean/logs -mtime -7 -exec cp {} "$BACKUP_DIR/" \;

echo "Backup completed: $BACKUP_DIR"
```

### Restore

```bash
# Restore data
cp -r /mnt/backup/guardian_20251205/data ~/guardian_node_clean/

# Restore configuration
cp /mnt/backup/guardian_20251205/config.yaml ~/guardian_node_clean/guardian_interpreter/

# Restart service
sudo systemctl restart guardian-node
```

---

## 🐛 Troubleshooting

### Issue: Out of Memory

**Solution**:
```bash
# Reduce context length in config.yaml
context_length: 2048  # Instead of 4096

# Disable preloading
preload_models: false

# Add swap (not recommended for SD card)
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### Issue: Slow Performance

**Solution**:
```bash
# Use SSD instead of SD card
# Reduce model size (use smaller quantization)
# Increase thread count if CPU allows
# Enable CPU governor for performance
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

### Issue: Network Scanning Fails

**Solution**:
```bash
# Run with sudo for privileged scans
sudo python3 main.py

# Or add capabilities
sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/python3.9

# Verify nmap installation
nmap --version
```

### Issue: Model Not Loading

**Solution**:
```bash
# Check model file exists
ls -lh ~/guardian_node_clean/models/gemma-2-2b-it-Q4_K_M.gguf

# Check file permissions
chmod 644 ~/guardian_node_clean/models/*.gguf

# Verify path in config.yaml
cat guardian_interpreter/config.yaml | grep model_path
```

---

## 📈 Performance Benchmarks

### Raspberry Pi 5 (8GB)

- **Model Loading**: ~10 seconds
- **Query Response**: 3-5 seconds
- **Network Scan (/24)**: 30-60 seconds
- **Memory Usage**: 1-2GB
- **CPU Usage**: 50-80% during inference

### Raspberry Pi 4 (4GB)

- **Model Loading**: ~15 seconds
- **Query Response**: 5-8 seconds
- **Network Scan (/24)**: 45-90 seconds
- **Memory Usage**: 1.5-2.5GB
- **CPU Usage**: 70-90% during inference

---

## 🎯 Recommended Setup

### For Best Performance

1. **Raspberry Pi 5 (8GB RAM)**
2. **USB 3.0 SSD** (for models and data)
3. **Active cooling** (fan or heatsink)
4. **Ethernet connection**
5. **Static IP address**
6. **Run as systemd service**

### For Budget Setup

1. **Raspberry Pi 4 (4GB RAM)**
2. **High-quality SD card** (Class 10, A2)
3. **Passive cooling** (heatsink)
4. **Wi-Fi connection**
5. **Manual start**

---

## ✅ Post-Installation Checklist

- [ ] System updated and upgraded
- [ ] Python 3.9+ installed
- [ ] All dependencies installed
- [ ] Nmap and network tools working
- [ ] LLM model downloaded and verified
- [ ] Data directories created
- [ ] Guardian Node starts successfully
- [ ] Memory vault initialized
- [ ] Network scanner initialized
- [ ] Test commands work
- [ ] Service configured (optional)
- [ ] Backups configured
- [ ] Monitoring set up

---

## 📚 Quick Reference

### Start Guardian Node
```bash
cd ~/guardian_node_clean/guardian_interpreter
python3 main.py
```

### Common Commands
```bash
guardian-family> help              # Show all commands
guardian-family> memory stats      # Memory statistics
guardian-family> scan network      # Discover devices
guardian-family> scan assess       # Security assessment
guardian-family> ask <question>    # Ask AI
```

### Service Management
```bash
sudo systemctl start guardian-node    # Start
sudo systemctl stop guardian-node     # Stop
sudo systemctl restart guardian-node  # Restart
sudo systemctl status guardian-node   # Status
```

### Logs
```bash
tail -f ~/guardian_node_clean/logs/guardian.log
sudo journalctl -u guardian-node -f
```

---

## 🎉 You're Ready!

Guardian Node is now fully configured on your Raspberry Pi!

**What you can do**:
- ✅ Discover devices on your network
- ✅ Scan for security vulnerabilities
- ✅ Get AI-powered cybersecurity advice
- ✅ Manage family profiles and devices
- ✅ All completely offline and private

**Next Steps**:
1. Add your family members: `memory add profile`
2. Scan your network: `scan assess`
3. Ask security questions: `ask How do I secure my home network?`

---

**Version**: Guardian Node v1.2.0 for Raspberry Pi  
**Status**: ✅ Production Ready  
**Platform**: Raspberry Pi OS (Linux)  
**Date**: December 5, 2025

**🛡️ Enjoy your private, AI-powered family cybersecurity assistant! 🛡️**
