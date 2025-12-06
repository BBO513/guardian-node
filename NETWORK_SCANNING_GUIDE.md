# Network Scanning & Security Assessment Guide
## Guardian Node Network Visibility Feature

**Version**: Guardian Node v1.2.0  
**Status**: ✅ Production Ready  
**Date**: December 5, 2025

---

## 🎯 Overview

Guardian Node now includes **comprehensive network scanning and security assessment** capabilities. This feature enables proactive monitoring of your local network, device discovery, port scanning, and vulnerability detection.

### Key Capabilities

- 🔍 **Network Discovery** - Find all devices on your local network
- 🔌 **Port Scanning** - Identify open ports and running services
- 🛡️ **Vulnerability Scanning** - Detect security weaknesses using Nmap NSE
- 📊 **Security Assessment** - Get comprehensive network security reports
- 🤖 **AI Interpretation** - LLM explains findings in family-friendly language

---

## 📦 Installation

### Prerequisites

**System Requirements:**
- Nmap binary installed on your system
- Python 3.9+
- Root/Administrator privileges (for some scans)

### Step 1: Install Nmap Binary

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get update
sudo apt-get install nmap
```

**Linux (RHEL/CentOS):**
```bash
sudo yum install nmap
```

**macOS:**
```bash
brew install nmap
```

**Windows:**
- Download from [nmap.org](https://nmap.org/download.html)
- Run installer
- Add to PATH

### Step 2: Install Python Dependencies

```bash
cd guardian_node_clean/guardian_interpreter
pip install python-nmap scapy netifaces
```

### Step 3: Verify Installation

```bash
# Check Nmap
nmap --version

# Check Python packages
python -c "import nmap; import scapy; print('✅ Ready')"
```

---

## 🚀 Quick Start

### Start Guardian Node

```bash
cd guardian_interpreter
python main.py
```

You should see:
```
✅ Network Scanner initialized successfully
```

### Basic Commands

```bash
# Discover devices on network
guardian-family> scan network

# Scan specific host
guardian-family> scan host 192.168.1.100

# Run vulnerability scan
guardian-family> scan vuln 192.168.1.100

# Quick security assessment
guardian-family> scan assess
```

---

## 📖 Detailed Usage

### 1. Network Discovery

**Command**: `scan network`

**Purpose**: Discover all devices on your local network

**Example**:
```bash
guardian-family> scan network
Network range (default: 192.168.1.0/24): 

🔍 Scanning network: 192.168.1.0/24
This may take a moment...

📊 Found 8 devices:
------------------------------------------------------------
  IP: 192.168.1.1     MAC: AA:BB:CC:DD:EE:FF
      Vendor: TP-Link Technologies
  IP: 192.168.1.100   MAC: 11:22:33:44:55:66
      Vendor: Apple, Inc.
  IP: 192.168.1.101   MAC: 77:88:99:AA:BB:CC
      Vendor: Samsung Electronics
------------------------------------------------------------
💾 Stored 8 devices in memory
```

**What It Does**:
- Scans the specified network range
- Discovers active devices using ARP/ping
- Identifies MAC addresses and vendors
- Stores devices in memory vault for future reference

**Use Cases**:
- See what devices are on your network
- Identify unknown devices
- Monitor network changes
- Build device inventory

---

### 2. Port Scanning

**Command**: `scan host <ip>`

**Purpose**: Scan ports on a specific device to see what services are running

**Example**:
```bash
guardian-family> scan host 192.168.1.100
Port range (default: 1-1000): 22,80,443,8080

🔍 Scanning 192.168.1.100 ports 22,80,443,8080
This may take a moment...

📊 Port Scan Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Host: 192.168.1.100
Status: up
Open Ports: 3

Services:
  22/tcp: ssh
  80/tcp: http
  443/tcp: https
```

**What It Does**:
- Scans specified ports on target host
- Identifies running services
- Detects service versions
- Assesses security posture

**Common Port Ranges**:
- `1-1000` - Common ports (default)
- `22,80,443` - Web and SSH
- `1-65535` - All ports (slow!)
- `T:22,80,U:53,123` - TCP and UDP

**Use Cases**:
- Check if services are exposed
- Verify firewall rules
- Identify unnecessary services
- Security auditing

---

### 3. Vulnerability Scanning

**Command**: `scan vuln <ip>`

**Purpose**: Detect security vulnerabilities using Nmap NSE scripts

**Example**:
```bash
guardian-family> scan vuln 192.168.1.100
Scan type (basic/vuln/full, default: basic): vuln

🔍 Running vulnerability scan on 192.168.1.100
This may take several minutes...

📊 Vulnerability Scan Results:
------------------------------------------------------------
Host: 192.168.1.100
Total Findings: 3

Findings:
  Port 22: ssh-auth-methods
    Severity: low
    Supported authentication methods: publickey, password
  
  Port 80: http-vuln-cve2017-5638
    Severity: high
    VULNERABLE: Apache Struts Remote Code Execution
  
  Port 443: ssl-cert
    Severity: medium
    Certificate expires in 15 days
------------------------------------------------------------
```

**Scan Types**:
- **basic** - Safe, default scripts
- **vuln** - Vulnerability detection scripts
- **full** - Comprehensive scan (slow, intrusive)

**What It Does**:
- Runs Nmap Scripting Engine (NSE)
- Detects known vulnerabilities
- Checks SSL/TLS configuration
- Identifies weak authentication
- Tests for common exploits

**Use Cases**:
- Security auditing
- Compliance checking
- Vulnerability management
- Patch verification

---

### 4. Quick Security Assessment

**Command**: `scan assess`

**Purpose**: Comprehensive network security assessment with recommendations

**Example**:
```bash
guardian-family> scan assess
Network range (default: 192.168.1.0/24): 

🔍 Running network security assessment
This will scan your network and assess security risks...
This may take several minutes...

📊 Network Assessment Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Network: 192.168.1.0/24
Devices Found: 8
Assessed: 8

Risk Levels:
  🔴 High: 1
  🟡 Medium: 2
  🟢 Low: 5

Recommendations:
  ⚠️ 1 high-risk device(s) detected. Review open ports and disable unnecessary services.
  🔒 Telnet (port 23) detected on 192.168.1.50. Use SSH instead for secure remote access.
  🔒 SMB (port 445) detected on 192.168.1.100. Ensure SMB is properly secured and updated.

💾 Results saved to: data/scans/scan_results.json
```

**What It Does**:
- Discovers all network devices
- Scans common ports on each device
- Assesses security risks
- Generates actionable recommendations
- Exports detailed results

**Use Cases**:
- Regular security audits
- Network health checks
- Compliance reporting
- Security awareness

---

## 🤖 AI-Powered Interpretation

Guardian Node's LLM can interpret scan results and provide family-friendly explanations.

### Ask About Scanning

```bash
guardian-family> ask How do I scan my Wi-Fi network?

Family Assistant Response:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
I can help you scan your Wi-Fi network! Here's how:

1. Use the 'scan network' command to discover all devices
2. Use 'scan assess' for a complete security assessment
3. Use 'scan host <ip>' to check a specific device

Would you like me to explain what each scan does?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Ask About Results

```bash
guardian-family> ask What does it mean if port 23 is open?

Family Assistant Response:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Port 23 is used by Telnet, an old remote access protocol. 
Having it open is a security risk because:

1. Telnet sends passwords in plain text (not encrypted)
2. Anyone on the network can see your login credentials
3. It's often targeted by hackers

Recommendation: Disable Telnet and use SSH (port 22) instead, 
which encrypts all communication.

Would you like help securing this device?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🔧 Configuration

### Network Scanner Settings

Edit `guardian_interpreter/config.yaml`:

```yaml
network_scanner:
  enabled: true
  default_network_range: "192.168.1.0/24"
  default_port_range: "1-1000"
  scan_timeout: 300  # seconds
  max_devices_to_assess: 10
  
  # Scan options
  options:
    ping_scan: true
    service_detection: true
    os_detection: false  # Requires root
    aggressive_scan: false
  
  # Export settings
  export:
    auto_export: true
    export_dir: "data/scans"
    format: "json"  # json, csv, xml
```

---

## 📊 Understanding Results

### Device Discovery Results

```json
{
  "ip": "192.168.1.100",
  "mac": "AA:BB:CC:DD:EE:FF",
  "vendor": "Apple, Inc.",
  "status": "up",
  "method": "nmap_ping",
  "timestamp": "2025-12-05T10:30:00"
}
```

### Port Scan Results

```json
{
  "host": "192.168.1.100",
  "status": "up",
  "open_ports": [
    {
      "port": 22,
      "protocol": "tcp",
      "state": "open",
      "service": "ssh",
      "version": "OpenSSH 8.2",
      "product": "OpenSSH"
    }
  ],
  "total_open_ports": 1
}
```

### Vulnerability Scan Results

```json
{
  "host": "192.168.1.100",
  "vulnerabilities": [
    {
      "port": 80,
      "protocol": "tcp",
      "script": "http-vuln-cve2017-5638",
      "output": "VULNERABLE: Apache Struts RCE",
      "severity": "high"
    }
  ],
  "total_findings": 1
}
```

---

## 🛡️ Security Best Practices

### Scanning Ethics

✅ **DO**:
- Scan your own network
- Get permission before scanning
- Use results to improve security
- Scan during off-peak hours

❌ **DON'T**:
- Scan networks you don't own
- Scan without authorization
- Use for malicious purposes
- Scan production systems without planning

### Privacy Considerations

- ✅ All scanning is local
- ✅ No data sent to cloud
- ✅ Results stored locally
- ✅ User-controlled exports

### Legal Compliance

- Ensure you have authorization
- Follow organizational policies
- Comply with local laws
- Document scan activities

---

## 🔍 Troubleshooting

### Issue: "Nmap not available"

**Solution**:
```bash
# Install Nmap
sudo apt-get install nmap  # Linux
brew install nmap          # Mac

# Verify
nmap --version
```

### Issue: "Permission denied"

**Solution**:
```bash
# Some scans require root/admin privileges
sudo python main.py

# Or use non-privileged scans
# (avoid -sS, -O, -A flags)
```

### Issue: "Scan takes too long"

**Solution**:
- Reduce network range (e.g., /28 instead of /24)
- Limit port range (e.g., "22,80,443" instead of "1-65535")
- Use faster scan types
- Increase timeout in config

### Issue: "No devices found"

**Solution**:
- Check network range is correct
- Verify you're on the same network
- Check firewall settings
- Try different scan method (Scapy vs Nmap)

---

## 📈 Performance

### Scan Times (Typical)

| Scan Type | Network Size | Time |
|-----------|--------------|------|
| Network Discovery | /24 (256 hosts) | 30-60s |
| Port Scan (1-1000) | Single host | 10-30s |
| Port Scan (all ports) | Single host | 5-10min |
| Vulnerability Scan | Single host | 2-5min |
| Quick Assessment | /24 network | 5-10min |

### Optimization Tips

1. **Limit Scope**: Scan only necessary hosts/ports
2. **Use Timing Templates**: `-T4` for faster scans
3. **Parallel Scanning**: Scan multiple hosts simultaneously
4. **Cache Results**: Store and reuse recent scans
5. **Schedule Scans**: Run during off-peak hours

---

## 🔗 Integration with Memory Vault

Network scanning integrates with Guardian Node's memory system:

### Automatic Device Storage

Discovered devices are automatically stored in memory:

```bash
guardian-family> scan network
# Devices automatically stored

guardian-family> memory search devices
# Shows all discovered devices
```

### Historical Tracking

```bash
# View device history
guardian-family> memory search 192.168.1.100

# Shows:
# - When device was first seen
# - Previous scan results
# - Security assessments
```

---

## 📚 Advanced Usage

### Python API

```python
from guardian_interpreter.network_scanner import create_network_scanner

# Initialize scanner
scanner = create_network_scanner()

# Discover devices
devices = scanner.discover_local_network("192.168.1.0/24")

# Scan host
results = scanner.scan_host_ports("192.168.1.100", "1-1000")

# Vulnerability scan
vulns = scanner.vulnerability_scan("192.168.1.100", "vuln")

# Quick assessment
assessment = scanner.quick_network_assessment()

# Export results
scanner.export_results(assessment, "my_scan.json")
```

### Custom NSE Scripts

```python
# Run custom Nmap scripts
scanner.nm.scan(
    "192.168.1.100",
    arguments="--script=my-custom-script"
)
```

---

## 🎓 Learning Resources

### Understanding Nmap

- [Nmap Official Documentation](https://nmap.org/book/)
- [Nmap NSE Scripts](https://nmap.org/nsedoc/)
- [Port Numbers Reference](https://www.iana.org/assignments/service-names-port-numbers/)

### Network Security

- Understanding TCP/IP
- Common vulnerabilities (CVE database)
- Security best practices
- Firewall configuration

---

## ✅ Checklist

### Installation Verification

- [ ] Nmap binary installed
- [ ] Python packages installed (python-nmap, scapy)
- [ ] Guardian Node starts without errors
- [ ] Network scanner initialized successfully

### Functionality Testing

- [ ] Network discovery works
- [ ] Port scanning works
- [ ] Vulnerability scanning works
- [ ] Quick assessment works
- [ ] Results export works

### Integration Testing

- [ ] Devices stored in memory
- [ ] LLM interprets scan requests
- [ ] Results accessible via memory search

---

## 🎉 Summary

Guardian Node's network scanning feature provides:

✅ **Comprehensive Visibility** - See all devices on your network  
✅ **Security Assessment** - Identify vulnerabilities and risks  
✅ **AI Interpretation** - Understand results in plain language  
✅ **Privacy-First** - All scanning is local  
✅ **Easy to Use** - Simple CLI commands  
✅ **Well-Integrated** - Works with memory vault  
✅ **Production-Ready** - Robust and reliable  

**Start scanning your network today and improve your family's cybersecurity!** 🛡️

---

**Version**: Guardian Node v1.2.0 with Network Scanning  
**Status**: ✅ Production Ready  
**Date**: December 5, 2025
