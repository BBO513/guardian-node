# Guardian Node Deployment Guide

**Complete deployment instructions for Guardian Node Family Cybersecurity Assistant**

---

## 🎯 Deployment Overview

Guardian Node can be deployed in multiple configurations:
- **Raspberry Pi 5** (Recommended for families)
- **Docker Container** (Cross-platform)
- **Local Development** (Testing and development)
- **Production Server** (Enterprise deployment)

---

## 🔧 Prerequisites

### Hardware Requirements

#### Raspberry Pi 5 (Recommended)
- **RAM**: 16GB (8GB minimum)
- **Storage**: 64GB+ microSD card (Class 10 or better)
- **Network**: Ethernet or WiFi capability
- **Optional**: Touchscreen display (7" recommended)

#### Alternative Hardware
- **x86_64 System**: 8GB+ RAM, 20GB+ storage
- **ARM64 System**: 4GB+ RAM, 20GB+ storage

### Software Requirements
- **Python**: 3.11+ (3.9+ supported)
- **Docker**: 20.10+ (for container deployment)
- **Git**: For source code management

---

## 🚀 Quick Start Deployment

### Option 1: Docker Deployment (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/guardian-node.git
cd guardian-node

# Build and start with docker-compose
docker-compose up --build -d

# Check status
docker-compose ps
docker-compose logs guardian-node
```

### Option 2: Direct Python Installation

```bash
# Clone repository
git clone https://github.com/your-org/guardian-node.git
cd guardian-node/guardian_interpreter

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

---

## 🐳 Docker Deployment (Production)

### 1. Environment Setup

Create environment file:
```bash
# Create .env file
cat > .env << EOF
GUARDIAN_MODE=family
GUARDIAN_OFFLINE=true
GUARDIAN_GUI_ENABLED=true
GUARDIAN_FAMILY_MODE=true
TZ=America/New_York
EOF
```

### 2. Docker Compose Configuration

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  guardian-node:
    build: 
      context: .
      dockerfile: Dockerfile
    container_name: guardian-node-family
    restart: unless-stopped
    ports:
      - "8080:8080"
      - "8443:8443"
    environment:
      - GUARDIAN_MODE=family
      - GUARDIAN_OFFLINE=true
      - GUARDIAN_GUI_ENABLED=true
    volumes:
      - ./data:/data
      - ./logs:/logs
      - ./models:/app/models
      - ./config:/app/config
    deploy:
      resources:
        limits:
          cpus: '3.0'
          memory: 12G
        reservations:
          cpus: '0.5'
          memory: 2G
    healthcheck:
      test: ["CMD", "python", "/app/health_check.py"]
      interval: 30s
      timeout: 15s
      retries: 3
      start_period: 120s
```

### 3. Deploy Production Container

```bash
# Deploy production version
docker-compose -f docker-compose.prod.yml up -d

# Monitor logs
docker-compose -f docker-compose.prod.yml logs -f

# Update deployment
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🥧 Raspberry Pi 5 Deployment

### 1. Raspberry Pi OS Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip git docker.io docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install Python dependencies
sudo apt install -y python3-dev build-essential
```

### 2. Guardian Node Installation

```bash
# Clone repository
cd /opt
sudo git clone https://github.com/your-org/guardian-node.git
sudo chown -R $USER:$USER guardian-node
cd guardian-node

# Install Python dependencies
pip3 install -r guardian_interpreter/requirements.txt

# Create directories
mkdir -p data logs models config
```

### 3. System Service Setup

Create systemd service:
```bash
sudo tee /etc/systemd/system/guardian-node.service << EOF
[Unit]
Description=Guardian Node Family Cybersecurity Assistant
After=network.target
Wants=network.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=/opt/guardian-node
Environment=PYTHONPATH=/opt/guardian-node
ExecStart=/usr/bin/python3 /opt/guardian-node/guardian_interpreter/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable guardian-node
sudo systemctl start guardian-node

# Check status
sudo systemctl status guardian-node
```

### 4. Touchscreen Setup (Optional)

```bash
# Install touchscreen support
sudo apt install -y xinput-calibrator

# Configure display rotation (if needed)
echo "display_rotate=1" | sudo tee -a /boot/config.txt

# Install GUI dependencies
pip3 install PySide6

# Reboot to apply changes
sudo reboot
```

---

## ⚙️ Configuration

### 1. Main Configuration File

Create `config/config.yaml`:
```yaml
# Guardian Node Configuration
system:
  name: "Guardian Node Family Assistant"
  version: "1.0.0"
  owner: "Your Family Name"

# Network Security (Privacy-First)
network:
  ALLOW_ONLINE: false  # Keep offline for privacy
  allowed_domains: []
  log_blocked_calls: true

# Family Assistant Settings
family_assistant:
  enabled: true
  gui_enabled: true
  default_interface: "gui"
  
  # Family-specific settings
  family_llm:
    child_safe_mode: true
    default_safety_level: "standard"
    
  # Voice interface
  voice_interface:
    enabled: true
    wake_word: "guardian"
    privacy_mode: true

# Logging
logging:
  level: "INFO"
  main_log: "logs/guardian.log"
  blocked_calls_log: "logs/blocked_calls.log"
  max_log_size_mb: 10

# CLI Settings
cli:
  prompt_prefix: "Guardian> "
  show_skill_list_on_start: true
```

### 2. Environment Variables

```bash
# Create environment file
cat > .env << EOF
# Guardian Node Environment
GUARDIAN_MODE=family
GUARDIAN_OFFLINE=true
GUARDIAN_GUI_ENABLED=true
GUARDIAN_FAMILY_MODE=true
GUARDIAN_DATA_PATH=/opt/guardian-node/data
GUARDIAN_LOGS_PATH=/opt/guardian-node/logs
PYTHONPATH=/opt/guardian-node
TZ=America/New_York
EOF
```

---

## 🔒 Security Configuration

### 1. Firewall Setup

```bash
# Configure UFW firewall
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (if needed)
sudo ufw allow ssh

# Allow Guardian Node ports
sudo ufw allow 8080/tcp comment 'Guardian Node Web Interface'
sudo ufw allow 8443/tcp comment 'Guardian Node Secure Interface'

# Check status
sudo ufw status verbose
```

### 2. SSL/TLS Setup (Optional)

```bash
# Generate self-signed certificate for local use
openssl req -x509 -newkey rsa:4096 -keyout config/guardian.key -out config/guardian.crt -days 365 -nodes -subj "/CN=guardian-node.local"

# Set proper permissions
chmod 600 config/guardian.key
chmod 644 config/guardian.crt
```

### 3. User Security

```bash
# Create dedicated guardian user
sudo useradd -r -s /bin/false guardian
sudo usermod -aG guardian $USER

# Set file permissions
sudo chown -R guardian:guardian /opt/guardian-node/data
sudo chown -R guardian:guardian /opt/guardian-node/logs
sudo chmod -R 750 /opt/guardian-node/data
sudo chmod -R 750 /opt/guardian-node/logs
```

---

## 📊 Monitoring & Maintenance

### 1. Health Monitoring

```bash
# Check service status
sudo systemctl status guardian-node

# View logs
sudo journalctl -u guardian-node -f

# Check application logs
tail -f /opt/guardian-node/logs/guardian.log

# Monitor resource usage
htop
df -h
```

### 2. Log Rotation

```bash
# Configure logrotate
sudo tee /etc/logrotate.d/guardian-node << EOF
/opt/guardian-node/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 guardian guardian
    postrotate
        systemctl reload guardian-node
    endscript
}
EOF
```

### 3. Backup Strategy

```bash
# Create backup script
cat > /opt/guardian-node/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/guardian-node/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup configuration and data
tar -czf $BACKUP_DIR/guardian-config-$DATE.tar.gz config/
tar -czf $BACKUP_DIR/guardian-data-$DATE.tar.gz data/
tar -czf $BACKUP_DIR/guardian-logs-$DATE.tar.gz logs/

# Keep only last 7 backups
find $BACKUP_DIR -name "guardian-*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /opt/guardian-node/backup.sh

# Add to crontab for daily backups
echo "0 2 * * * /opt/guardian-node/backup.sh" | crontab -
```

---

## 🌐 Network Configuration

### 1. Local Network Access

```bash
# Find Raspberry Pi IP address
hostname -I

# Access Guardian Node
# Web Interface: http://[PI_IP]:8080
# Secure Interface: https://[PI_IP]:8443
```

### 2. DNS Configuration (Optional)

```bash
# Add local DNS entry
echo "192.168.1.100 guardian-node.local" | sudo tee -a /etc/hosts

# Configure mDNS (Bonjour/Avahi)
sudo apt install -y avahi-daemon
sudo systemctl enable avahi-daemon
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Service Won't Start
```bash
# Check service status
sudo systemctl status guardian-node

# Check logs
sudo journalctl -u guardian-node --no-pager

# Check Python dependencies
pip3 list | grep -E "(yaml|psutil|requests)"
```

#### 2. Permission Issues
```bash
# Fix file permissions
sudo chown -R guardian:guardian /opt/guardian-node
sudo chmod -R 755 /opt/guardian-node
```

#### 3. Memory Issues
```bash
# Check memory usage
free -h

# Increase swap (Raspberry Pi)
sudo dphys-swapfile swapoff
sudo sed -i 's/CONF_SWAPSIZE=100/CONF_SWAPSIZE=2048/' /etc/dphys-swapfile
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

#### 4. Network Connectivity
```bash
# Test network connectivity
ping -c 4 8.8.8.8

# Check firewall
sudo ufw status

# Check port binding
sudo netstat -tlnp | grep :8080
```

### Log Analysis

```bash
# Check Guardian logs
tail -f /opt/guardian-node/logs/guardian.log

# Check blocked network calls
tail -f /opt/guardian-node/logs/blocked_calls.log

# Check family assistant logs
tail -f /opt/guardian-node/logs/family_audit.log

# System logs
sudo journalctl -u guardian-node -f
```

---

## 📈 Performance Optimization

### 1. Raspberry Pi Optimization

```bash
# GPU memory split (reduce for headless)
echo "gpu_mem=16" | sudo tee -a /boot/config.txt

# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable cups

# CPU governor for performance
echo 'GOVERNOR="performance"' | sudo tee /etc/default/cpufrequtils
```

### 2. Python Optimization

```bash
# Install optimized Python packages
pip3 install --upgrade pip setuptools wheel

# Use system packages where possible
sudo apt install -y python3-yaml python3-psutil
```

---

## 🔄 Updates & Maintenance

### 1. Application Updates

```bash
# Update Guardian Node
cd /opt/guardian-node
git pull origin main

# Update dependencies
pip3 install -r guardian_interpreter/requirements.txt --upgrade

# Restart service
sudo systemctl restart guardian-node
```

### 2. System Updates

```bash
# Update Raspberry Pi OS
sudo apt update && sudo apt upgrade -y

# Update Docker (if using containers)
sudo apt update docker.io docker-compose

# Reboot if kernel updated
sudo reboot
```

---

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Hardware requirements met
- [ ] Network connectivity verified
- [ ] Security requirements reviewed
- [ ] Backup strategy planned

### Installation
- [ ] Repository cloned
- [ ] Dependencies installed
- [ ] Configuration files created
- [ ] Permissions set correctly

### Security
- [ ] Firewall configured
- [ ] SSL certificates generated (if needed)
- [ ] User accounts secured
- [ ] Network access restricted

### Testing
- [ ] Service starts successfully
- [ ] Web interface accessible
- [ ] Family assistant functional
- [ ] Logs being generated
- [ ] Health checks passing

### Production
- [ ] Monitoring configured
- [ ] Backups scheduled
- [ ] Documentation updated
- [ ] Team trained on usage

---

## 📞 Support & Maintenance

### Getting Help
- **Documentation**: Check this guide and README files
- **Logs**: Review application and system logs
- **Community**: Guardian Node community forums
- **Issues**: GitHub issue tracker

### Regular Maintenance Tasks
- **Weekly**: Check logs and system status
- **Monthly**: Review security updates
- **Quarterly**: Full system backup and restore test
- **Annually**: Security audit and configuration review

---

**Guardian Node - Protecting your digital perimeter with privacy-first AI.**