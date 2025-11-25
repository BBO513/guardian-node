# 🔄 Guardian Node: Windows 11 → GitHub → Raspberry Pi Workflow

## 📋 Table of Contents
1. [Workflow Overview](#workflow-overview)
2. [Prerequisites](#prerequisites)
3. [Part 1: Windows 11 Setup](#part-1-windows-11-setup)
4. [Part 2: Push to GitHub](#part-2-push-to-github)
5. [Part 3: Raspberry Pi Setup](#part-3-raspberry-pi-setup)
6. [Part 4: Pull and Deploy on Pi](#part-4-pull-and-deploy-on-pi)
7. [Part 5: Generate Voice Files](#part-5-generate-voice-files)
8. [Part 6: Testing](#part-6-testing)
9. [Troubleshooting](#troubleshooting)
10. [Maintenance Workflow](#maintenance-workflow)

---

## 🎯 Workflow Overview

This guide walks you through the complete development and deployment workflow:

```
┌─────────────────────────────────────────────────────────────────┐
│                     DEVELOPMENT CYCLE                            │
└─────────────────────────────────────────────────────────────────┘

[Windows 11 PC]           [GitHub]              [Raspberry Pi 5]
      │                      │                         │
      │  1. Git Push         │                         │
      ├─────────────────────>│                         │
      │                      │  2. Git Pull            │
      │                      ├────────────────────────>│
      │                      │                         │
      │                      │  3. Install Dependencies│
      │                      │         └───────────────┤
      │                      │                         │
      │                      │  4. Generate Audio      │
      │                      │         └───────────────┤
      │                      │                         │
      │                      │  5. Test Voice System   │
      │                      │         └───────────────┤
      │                      │                         │
      │  6. Make Changes     │                         │
      │  └──────────────────>│                         │
      │                      │                         │
      └──────────────────────┴─────────────────────────┘
```

### Process Summary

| Phase | Location | Task | Internet Required |
|-------|----------|------|-------------------|
| **1. Development** | Windows 11 | Code changes, testing | No |
| **2. Version Control** | Windows 11 | Git commit, push | Yes |
| **3. Distribution** | GitHub | Repository hosting | N/A |
| **4. Deployment** | Raspberry Pi | Git pull, setup | Yes (first time) |
| **5. Operation** | Raspberry Pi | Run voice system | No |

---

## ✅ Prerequisites

### Windows 11 PC Requirements

#### Software Needed

- [ ] **Git for Windows** - Version control
  - Download: https://git-scm.com/download/win
  - Verify: `git --version` in Command Prompt

- [ ] **GitHub Account** - Code hosting
  - Sign up: https://github.com/signup
  - Create repository: `guardian-node`

- [ ] **Text Editor** - Code editing (choose one)
  - VS Code: https://code.visualstudio.com/
  - Notepad++: https://notepad-plus-plus.org/
  - Sublime Text: https://www.sublimetext.com/

- [ ] **Python 3.8+** (Optional for local testing)
  - Download: https://www.python.org/downloads/
  - Check during install: "Add Python to PATH"

#### GitHub Setup

1. **Create Personal Access Token** (for HTTPS authentication)
   - Go to: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token (classic)
   - Permissions: `repo` (all), `workflow`
   - **Save token securely** - you won't see it again!

2. **Or Configure SSH Key** (recommended for security)
   ```cmd
   :: Generate SSH key
   ssh-keygen -t ed25519 -C "your_email@example.com"
   
   :: Copy public key
   type %USERPROFILE%\.ssh\id_ed25519.pub
   
   :: Add to GitHub: Settings → SSH and GPG keys → New SSH key
   ```

### Raspberry Pi 5 Requirements

#### Hardware

- [ ] **Raspberry Pi 5** (4GB+ RAM recommended)
- [ ] **MicroSD Card** (32GB+ recommended)
- [ ] **Power Supply** (27W USB-C)
- [ ] **Audio Output** (3.5mm jack or HDMI for testing)
- [ ] **Network Connection** (Ethernet or WiFi)

#### Software

- [ ] **Raspberry Pi OS** (64-bit recommended)
  - Download: https://www.raspberrypi.com/software/
  - Use Raspberry Pi Imager
  - Configure WiFi and SSH before first boot

- [ ] **Python 3.8+** (Usually pre-installed)
  ```bash
  python3 --version
  ```

- [ ] **Git** (Usually pre-installed)
  ```bash
  git --version
  ```

---

## 🖥️ Part 1: Windows 11 Setup

### Step 1.1: Install Git for Windows

1. **Download Git**
   - Visit: https://git-scm.com/download/win
   - Download 64-bit installer
   - Run installer

2. **Installation Options**
   - Editor: Choose your preferred editor (VS Code recommended)
   - PATH environment: "Git from the command line and also from 3rd-party software"
   - HTTPS transport backend: "Use the OpenSSL library"
   - Line ending conversions: "Checkout Windows-style, commit Unix-style"
   - Terminal emulator: "Use MinTTY"

3. **Verify Installation**
   ```cmd
   git --version
   :: Should show: git version 2.x.x
   ```

### Step 1.2: Configure Git

```cmd
:: Set your identity
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"

:: Verify configuration
git config --list
```

### Step 1.3: Create Local Repository Directory

```cmd
:: Create project directory
cd C:\Users\YourUsername\Documents
mkdir guardian-node
cd guardian-node

:: Initialize git repository
git init
```

### Step 1.4: Clone Repository (If Already Exists)

```cmd
:: If repository already exists on GitHub
git clone https://github.com/YOUR_USERNAME/guardian-node.git
cd guardian-node

:: Or with SSH
git clone git@github.com:YOUR_USERNAME/guardian-node.git
cd guardian-node
```

---

## 📤 Part 2: Push to GitHub

### Step 2.1: Create GitHub Repository

**Via GitHub Web Interface:**

1. Go to: https://github.com/new
2. Repository name: `guardian-node`
3. Description: "Privacy-first AI security assistant with offline voice system"
4. Visibility: **Private** (recommended for personal projects)
5. **Do NOT** initialize with README, .gitignore, or license (we already have files)
6. Click "Create repository"

### Step 2.2: Connect Local Repository to GitHub

**If you created a new repository:**

```cmd
:: Add remote origin
git remote add origin https://github.com/YOUR_USERNAME/guardian-node.git

:: Or with SSH
git remote add origin git@github.com:YOUR_USERNAME/guardian-node.git

:: Verify remote
git remote -v
```

### Step 2.3: Stage and Commit Voice Integration Files

```cmd
:: Check current status
git status

:: Add voice integration files
git add guardian_interpreter_starter/voice/
git add guardian_interpreter_starter/config.yaml
git add guardian_interpreter_starter/setup_offline_voice.bat
git add guardian_interpreter_starter/demo_voice_system.py
git add guardian_interpreter_starter/skills/audio_explanations/

:: Add documentation
git add VOICE_INTEGRATION_GUIDE.md
git add WINDOWS_TO_PI_WORKFLOW.md
git add VOICE_QUICK_REFERENCE.md

:: Or add all changes
git add .

:: Commit with descriptive message
git commit -m "Add voice system integration with Edge TTS neural voices

- Integrated voice module (input/output/interface)
- Updated config.yaml with comprehensive voice settings
- Added offline voice explanation system
- Configured 3 age groups (child/teen/adult) with neural voices
- Added setup and demo scripts
- Created complete documentation"

:: Verify commit
git log --oneline -1
```

### Step 2.4: Push to GitHub

```cmd
:: Push to main branch
git push -u origin main

:: If you get an error about main vs master:
git branch -M main
git push -u origin main

:: Enter credentials if prompted (Personal Access Token or SSH passphrase)
```

**Troubleshooting Push Issues:**

```cmd
:: If push is rejected (remote has changes you don't have)
git pull origin main --rebase
git push origin main

:: If authentication fails
:: Use Personal Access Token as password (not your GitHub password)
:: Token generated at: GitHub → Settings → Developer settings → Personal access tokens
```

### Step 2.5: Verify Push on GitHub

1. Go to: https://github.com/YOUR_USERNAME/guardian-node
2. Verify files are present:
   - `guardian_interpreter_starter/voice/`
   - `guardian_interpreter_starter/config.yaml`
   - `VOICE_INTEGRATION_GUIDE.md`
   - `WINDOWS_TO_PI_WORKFLOW.md`

---

## 🥧 Part 3: Raspberry Pi Setup

### Step 3.1: Initial Pi Configuration

**Connect to your Raspberry Pi:**

```bash
# Via SSH from Windows (using PowerShell or Command Prompt)
ssh pi@raspberrypi.local

# Or if using IP address
ssh pi@192.168.1.XXX

# Default password: raspberry (change it immediately!)
```

**Update System:**

```bash
# Update package lists
sudo apt update

# Upgrade installed packages
sudo apt upgrade -y

# Reboot to apply updates
sudo reboot
```

### Step 3.2: Install Required System Dependencies

```bash
# Audio libraries for pygame
sudo apt install -y python3-pygame

# Audio playback tools
sudo apt install -y pulseaudio alsa-utils

# Git (if not already installed)
sudo apt install -y git

# Python development headers
sudo apt install -y python3-dev python3-pip

# Additional audio codecs
sudo apt install -y libmpg123-0 libsndfile1
```

### Step 3.3: Configure Audio Output

```bash
# Test audio output
speaker-test -t wav -c 2

# If no sound, check audio output
sudo raspi-config
# Navigate to: System Options → Audio → Select output device

# Set volume
alsamixer
# Use arrow keys to adjust, ESC to exit

# Test with a sound
aplay /usr/share/sounds/alsa/Front_Center.wav
```

### Step 3.4: Create Project Directory

```bash
# Create projects directory
mkdir -p ~/projects
cd ~/projects

# Set permissions
chmod 755 ~/projects
```

---

## 📥 Part 4: Pull and Deploy on Pi

### Step 4.1: Clone Repository on Raspberry Pi

**Using HTTPS:**

```bash
cd ~/projects

# Clone repository
git clone https://github.com/YOUR_USERNAME/guardian-node.git

# Enter credentials when prompted
# Username: YOUR_USERNAME
# Password: Personal Access Token (not your GitHub password)

cd guardian-node
```

**Using SSH (If configured):**

```bash
cd ~/projects

# Clone with SSH
git clone git@github.com:YOUR_USERNAME/guardian-node.git

cd guardian-node
```

### Step 4.2: Verify Files

```bash
# Check directory structure
ls -la guardian_interpreter_starter/voice/
ls -la guardian_interpreter_starter/skills/audio_explanations/

# Verify configuration
cat guardian_interpreter_starter/config.yaml

# Check documentation
ls -la *.md
```

### Step 4.3: Install Python Dependencies

```bash
cd ~/projects/guardian-node/guardian_interpreter_starter

# Create virtual environment (recommended)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install edge-tts pygame pyttsx3 pyyaml

# Verify installations
pip list | grep -E "edge-tts|pygame|pyttsx3|pyyaml"
```

**Expected Output:**
```
edge-tts        6.1.10
pygame          2.5.2
pyttsx3         2.90
PyYAML          6.0.1
```

### Step 4.4: Create Directory Structure

```bash
cd ~/projects/guardian-node/guardian_interpreter_starter

# Create audio directories
mkdir -p skills/audio_explanations/audio_files
mkdir -p skills/audio_explanations/cache
mkdir -p logs

# Set permissions
chmod -R 755 skills/audio_explanations/

# Verify structure
tree skills/audio_explanations/ -L 2
```

---

## 🎤 Part 5: Generate Voice Files

### Step 5.1: Create Audio Pre-recorder Script

The audio pre-recorder script generates all 12 voice explanations.

```bash
cd ~/projects/guardian-node/guardian_interpreter_starter
```

**Create `skills/audio_pre_recorder.py`:**

```python
#!/usr/bin/env python3
"""
Audio Pre-recorder for Guardian Node
Generates pre-recorded security explanations using Edge TTS
"""

import asyncio
import edge_tts
import os
import json
from pathlib import Path

# Output directory
AUDIO_DIR = Path(__file__).parent / "audio_explanations" / "audio_files"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Voice profiles
VOICES = {
    "child": "en-US-JennyNeural",
    "teen": "en-US-AriaNeural",
    "adult": "en-US-DavisNeural"
}

# Security explanations
EXPLANATIONS = {
    "phishing": {
        "child": "Hey there! Phishing is when bad people try to trick you by pretending to be someone you trust, like sending a fake email that looks like it's from your teacher or a game you play. Always ask a grown-up before clicking on links in emails!",
        
        "teen": "Phishing attacks are social engineering techniques where attackers create fake emails or websites that look legitimate to steal your personal information. Look for warning signs like spelling errors, suspicious URLs, or urgent requests for passwords. Always verify the sender through a separate channel before clicking links or sharing information.",
        
        "adult": "Phishing is a sophisticated attack vector utilizing social engineering and domain spoofing to compromise credentials and exfiltrate sensitive data. Implement technical controls including SPF, DKIM, and DMARC email authentication, deploy MFA across all systems, and conduct regular security awareness training. Verify sender authenticity through secondary channels before responding to any requests for credentials or financial transactions."
    },
    
    "malware": {
        "child": "Malware is bad software that can hurt your computer or tablet. It's like a cold for your device! Never download games or programs from websites you don't know. Only download apps from official app stores with a parent's permission.",
        
        "teen": "Malware, or malicious software, includes viruses, trojans, ransomware, and spyware designed to damage systems or steal data. Protect yourself by keeping your software updated, using reputable antivirus software, and avoiding downloads from untrusted sources. Be especially careful with email attachments and USB drives from unknown sources.",
        
        "adult": "Malware encompasses a broad spectrum of malicious code including ransomware, trojans, rootkits, and advanced persistent threats. Implement a defense-in-depth strategy including endpoint protection, network segmentation, application whitelisting, and regular security patching. Deploy EDR solutions for threat detection and maintain offline encrypted backups to mitigate ransomware impact. Conduct regular vulnerability assessments and penetration testing."
    },
    
    "weak_password": {
        "child": "Passwords are like secret keys that protect your stuff online. Make them strong by using a mix of letters, numbers, and special characters. Don't use easy words like your pet's name or birthday. And never share your passwords with anyone except your parents!",
        
        "teen": "Weak passwords are one of the easiest ways for hackers to access your accounts. Create strong passwords by using at least 12 characters with a mix of uppercase, lowercase, numbers, and symbols. Never reuse passwords across different accounts. Consider using a password manager to generate and store complex passwords securely. Enable two-factor authentication whenever available for extra security.",
        
        "adult": "Password security requires implementing enterprise-grade authentication controls. Deploy a password manager with strong encryption, enforce minimum complexity requirements of 16+ characters with entropy-based validation, implement MFA using FIDO2 or authenticator apps, and consider passwordless authentication using biometrics or hardware tokens. Conduct regular password audits, monitor for compromised credentials using breach databases, and implement account lockout policies with exponential backoff to prevent brute force attacks."
    },
    
    "suspicious_network": {
        "child": "When you're using WiFi at places like coffee shops or libraries, bad people might try to see what you're doing on your tablet or computer. At home, your WiFi is safe. But in public places, don't type in passwords or look at private information. Wait until you get home!",
        
        "teen": "Public WiFi networks are often unsecured, making it easy for attackers to intercept your data through man-in-the-middle attacks. When using public networks, avoid accessing sensitive accounts or making online purchases. Use a VPN to encrypt your connection, ensure websites use HTTPS, and turn off auto-connect features. Your mobile hotspot is a safer alternative than untrusted public WiFi.",
        
        "adult": "Unsecured networks present significant attack surfaces including packet sniffing, ARP spoofing, SSL stripping, and rogue access point attacks. Implement mandatory VPN usage for all remote connections with perfect forward secrecy, deploy certificate pinning for critical applications, enforce DNSSEC validation, and utilize network isolation through VLANs. For enterprise environments, implement 802.1X authentication, deploy wireless intrusion detection systems, and enforce device posture assessment before network access. Consider zero-trust network architecture principles."
    }
}

async def generate_audio_file(text: str, voice: str, output_path: Path):
    """Generate audio file using Edge TTS"""
    print(f"Generating: {output_path.name}...")
    
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))
    
    # Get file size
    size_kb = output_path.stat().st_size / 1024
    print(f"✅ Created {output_path.name} ({size_kb:.1f} KB)")

async def generate_all_explanations():
    """Generate all 12 explanation audio files"""
    print("=" * 60)
    print("Guardian Node Audio Pre-recorder")
    print("=" * 60)
    print(f"Output directory: {AUDIO_DIR}")
    print(f"Generating {len(EXPLANATIONS) * len(VOICES)} audio files...")
    print()
    
    metadata = {}
    total_size = 0
    
    tasks = []
    
    for risk_type, texts in EXPLANATIONS.items():
        for age_group, text in texts.items():
            voice = VOICES[age_group]
            filename = f"{risk_type}_{age_group}.mp3"
            output_path = AUDIO_DIR / filename
            
            tasks.append(generate_audio_file(text, voice, output_path))
            
            # Store metadata
            metadata[filename] = {
                "risk_type": risk_type,
                "age_group": age_group,
                "voice": voice,
                "duration_estimate": len(text.split()) / 2.5,  # Rough estimate
                "text_preview": text[:100] + "..."
            }
    
    # Generate all files concurrently
    await asyncio.gather(*tasks)
    
    # Calculate total size
    for file_path in AUDIO_DIR.glob("*.mp3"):
        total_size += file_path.stat().st_size
    
    # Save metadata
    metadata_path = AUDIO_DIR.parent / "metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print()
    print("=" * 60)
    print("✅ Generation Complete!")
    print("=" * 60)
    print(f"Files created: {len(list(AUDIO_DIR.glob('*.mp3')))}")
    print(f"Total size: {total_size / 1024:.1f} KB ({total_size / 1024 / 1024:.2f} MB)")
    print(f"Metadata saved: {metadata_path}")
    print()
    print("Next steps:")
    print("1. Test playback: python3 skills/offline_voice_explain.py --risk phishing --age teen")
    print("2. Run demo: python3 demo_voice_system.py")

if __name__ == "__main__":
    asyncio.run(generate_all_explanations())
```

**Make script executable:**

```bash
chmod +x skills/audio_pre_recorder.py
```

### Step 5.2: Generate Audio Files

**⚠️ Important: This requires internet connection!**

```bash
cd ~/projects/guardian-node/guardian_interpreter_starter

# Activate virtual environment if not already active
source venv/bin/activate

# Generate all 12 audio files
python3 skills/audio_pre_recorder.py
```

**Expected Output:**

```
============================================================
Guardian Node Audio Pre-recorder
============================================================
Output directory: /home/pi/projects/guardian-node/guardian_interpreter_starter/skills/audio_explanations/audio_files
Generating 12 audio files...

Generating: phishing_child.mp3...
✅ Created phishing_child.mp3 (156.3 KB)
Generating: phishing_teen.mp3...
✅ Created phishing_teen.mp3 (187.5 KB)
Generating: phishing_adult.mp3...
✅ Created phishing_adult.mp3 (245.8 KB)
...
============================================================
✅ Generation Complete!
============================================================
Files created: 12
Total size: 2134.5 KB (2.08 MB)
Metadata saved: /home/pi/projects/guardian-node/guardian_interpreter_starter/skills/audio_explanations/metadata.json
```

### Step 5.3: Verify Audio Files

```bash
# List generated files
ls -lh skills/audio_explanations/audio_files/

# Check metadata
cat skills/audio_explanations/metadata.json | python3 -m json.tool

# Count files
ls skills/audio_explanations/audio_files/*.mp3 | wc -l
# Should output: 12
```

### Step 5.4: Optional - Add Audio Files to Git

**⚠️ Note:** Audio files are typically excluded from Git due to size. However, for this project (~2MB total), you can include them if desired.

**If you want to track audio files in Git:**

```bash
cd ~/projects/guardian-node

# Add audio files
git add guardian_interpreter_starter/skills/audio_explanations/audio_files/*.mp3
git add guardian_interpreter_starter/skills/audio_explanations/metadata.json

# Commit
git commit -m "Add pre-generated voice audio files (12 MP3s, ~2MB)"

# Push to GitHub
git push origin main
```

**If you want to exclude audio files from Git:**

Create `.gitignore`:

```bash
cd ~/projects/guardian-node

# Add to .gitignore
echo "guardian_interpreter_starter/skills/audio_explanations/audio_files/*.mp3" >> .gitignore
echo "guardian_interpreter_starter/skills/audio_explanations/cache/*" >> .gitignore

# Commit .gitignore
git add .gitignore
git commit -m "Exclude audio files from version control"
git push origin main
```

---

## 🧪 Part 6: Testing

### Step 6.1: Create Offline Voice Explainer Script

**Create `skills/offline_voice_explain.py`:**

```bash
cd ~/projects/guardian-node/guardian_interpreter_starter
```

```python
#!/usr/bin/env python3
"""
Offline Voice Explainer for Guardian Node
Plays pre-recorded security explanations
"""

import pygame
import argparse
import json
from pathlib import Path
import time

# Audio files directory
AUDIO_DIR = Path(__file__).parent / "audio_explanations" / "audio_files"
METADATA_PATH = Path(__file__).parent / "audio_explanations" / "metadata.json"

# Initialize pygame mixer
pygame.mixer.init()

def load_metadata():
    """Load audio file metadata"""
    if METADATA_PATH.exists():
        with open(METADATA_PATH, 'r') as f:
            return json.load(f)
    return {}

def list_explanations():
    """List all available explanations"""
    metadata = load_metadata()
    
    print("=" * 60)
    print("Available Voice Explanations")
    print("=" * 60)
    
    if not metadata:
        print("No explanations found. Run audio_pre_recorder.py first.")
        return
    
    # Group by risk type
    by_risk = {}
    for filename, info in metadata.items():
        risk = info['risk_type']
        if risk not in by_risk:
            by_risk[risk] = []
        by_risk[risk].append(info['age_group'])
    
    for risk, ages in sorted(by_risk.items()):
        print(f"\n📋 {risk.upper()}")
        for age in sorted(ages):
            filename = f"{risk}_{age}.mp3"
            if (AUDIO_DIR / filename).exists():
                print(f"   ✅ {age}: {filename}")
            else:
                print(f"   ❌ {age}: {filename} (missing)")
    
    print()
    print(f"Total: {len(metadata)} explanations")
    print(f"Storage: {sum(f.stat().st_size for f in AUDIO_DIR.glob('*.mp3')) / 1024:.1f} KB")

def play_explanation(risk: str, age: str):
    """Play a specific explanation"""
    filename = f"{risk}_{age}.mp3"
    filepath = AUDIO_DIR / filename
    
    if not filepath.exists():
        print(f"❌ Error: Audio file not found: {filepath}")
        print(f"Run audio_pre_recorder.py to generate audio files.")
        return False
    
    print(f"🔊 Playing: {filename}")
    print(f"   Risk: {risk}")
    print(f"   Age: {age}")
    print(f"   File: {filepath}")
    print()
    
    try:
        pygame.mixer.music.load(str(filepath))
        pygame.mixer.music.play()
        
        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        
        print("✅ Playback complete")
        return True
        
    except Exception as e:
        print(f"❌ Error playing audio: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Guardian Node Offline Voice Explainer")
    parser.add_argument("--list", action="store_true", help="List all available explanations")
    parser.add_argument("--risk", type=str, choices=["phishing", "malware", "weak_password", "suspicious_network"],
                        help="Risk type to explain")
    parser.add_argument("--age", type=str, choices=["child", "teen", "adult"],
                        help="Age group for explanation")
    
    args = parser.parse_args()
    
    if args.list:
        list_explanations()
    elif args.risk and args.age:
        play_explanation(args.risk, args.age)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
```

**Make executable:**

```bash
chmod +x skills/offline_voice_explain.py
```

### Step 6.2: Test Audio Playback

```bash
cd ~/projects/guardian-node/guardian_interpreter_starter

# Activate virtual environment
source venv/bin/activate

# List all available explanations
python3 skills/offline_voice_explain.py --list

# Test child explanation
python3 skills/offline_voice_explain.py --risk phishing --age child

# Test teen explanation
python3 skills/offline_voice_explain.py --risk malware --age teen

# Test adult explanation
python3 skills/offline_voice_explain.py --risk weak_password --age adult
```

### Step 6.3: Test Voice Module

**Create test script `test_voice_module.py`:**

```python
#!/usr/bin/env python3
"""Test Voice Module Integration"""

import sys
from pathlib import Path

# Add voice module to path
sys.path.insert(0, str(Path(__file__).parent / "voice"))

def test_imports():
    """Test voice module imports"""
    print("Testing voice module imports...")
    
    try:
        from voice_output import VoiceOutput
        print("✅ VoiceOutput imported")
    except Exception as e:
        print(f"❌ Failed to import VoiceOutput: {e}")
        return False
    
    try:
        from voice_input import VoiceInput
        print("✅ VoiceInput imported")
    except Exception as e:
        print(f"❌ Failed to import VoiceInput: {e}")
        return False
    
    try:
        from voice_interface import VoiceInterface
        print("✅ VoiceInterface imported")
    except Exception as e:
        print(f"❌ Failed to import VoiceInterface: {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    import yaml
    
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        assert 'voice_system' in config, "voice_system not in config"
        assert config['voice_system']['enabled'], "voice_system not enabled"
        assert 'voice_profiles' in config, "voice_profiles not in config"
        
        print("✅ Configuration valid")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def main():
    print("=" * 60)
    print("Guardian Node Voice Module Test")
    print("=" * 60)
    print()
    
    results = []
    
    results.append(("Module Imports", test_imports()))
    results.append(("Configuration", test_configuration()))
    
    print("\n" + "=" * 60)
    print("Test Results")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    print()
    
    if all_passed:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

**Run tests:**

```bash
chmod +x test_voice_module.py
python3 test_voice_module.py
```

### Step 6.4: Comprehensive System Test

**Run the demo script:**

```bash
cd ~/projects/guardian-node/guardian_interpreter_starter

# Run voice system demo
python3 demo_voice_system.py
```

**Expected behavior:**
- Lists available explanations
- Plays sample audio for each age group
- Tests all risk types
- Shows system status

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Issue 1: No Sound Output

**Symptoms:**
- Scripts run without errors but no audio plays

**Solutions:**

```bash
# Check audio devices
aplay -l

# Test audio
speaker-test -t wav -c 2

# Set correct audio output
sudo raspi-config
# → System Options → Audio → Select device

# Check volume
alsamixer

# Test with pygame
python3 << EOF
import pygame
pygame.mixer.init()
print("Audio initialized successfully")
EOF
```

#### Issue 2: Permission Denied Errors

**Symptoms:**
- Cannot create files or directories

**Solutions:**

```bash
# Fix directory permissions
cd ~/projects/guardian-node
sudo chown -R $USER:$USER guardian_interpreter_starter/
chmod -R 755 guardian_interpreter_starter/

# Verify
ls -la guardian_interpreter_starter/skills/
```

#### Issue 3: Module Import Errors

**Symptoms:**
- `ModuleNotFoundError: No module named 'edge_tts'`

**Solutions:**

```bash
# Activate virtual environment
cd ~/projects/guardian-node/guardian_interpreter_starter
source venv/bin/activate

# Reinstall dependencies
pip install edge-tts pygame pyttsx3 pyyaml

# Verify installation
pip list | grep edge-tts
```

#### Issue 4: Git Authentication Fails

**Symptoms:**
- `Authentication failed` when pushing/pulling

**Solutions:**

```bash
# Use Personal Access Token instead of password
git remote set-url origin https://YOUR_USERNAME:YOUR_TOKEN@github.com/YOUR_USERNAME/guardian-node.git

# Or configure credential helper
git config --global credential.helper store
git pull  # Enter credentials once, they'll be saved
```

#### Issue 5: Audio Files Not Generated

**Symptoms:**
- `audio_pre_recorder.py` completes but files missing

**Solutions:**

```bash
# Check internet connection
ping -c 3 google.com

# Verify directory permissions
ls -la skills/audio_explanations/audio_files/

# Check for errors in generation
python3 skills/audio_pre_recorder.py 2>&1 | tee audio_gen.log
cat audio_gen.log

# Try generating one file manually
python3 << EOF
import asyncio
import edge_tts

async def test():
    communicate = edge_tts.Communicate("Test audio", "en-US-JennyNeural")
    await communicate.save("test.mp3")
    print("Success!")

asyncio.run(test())
EOF
```

---

## 🔄 Maintenance Workflow

### Making Changes on Windows and Deploying to Pi

#### Workflow 1: Update Configuration

**On Windows 11:**

```cmd
:: Navigate to repository
cd C:\Users\YourUsername\Documents\guardian-node

:: Edit config.yaml
notepad guardian_interpreter_starter\config.yaml

:: Stage and commit
git add guardian_interpreter_starter\config.yaml
git commit -m "Update voice system configuration"

:: Push to GitHub
git push origin main
```

**On Raspberry Pi:**

```bash
cd ~/projects/guardian-node

# Pull changes
git pull origin main

# Restart service if running
# (implement service restart command if applicable)
```

#### Workflow 2: Add New Voice Module Features

**On Windows 11:**

```cmd
:: Edit voice module
notepad guardian_interpreter_starter\voice\voice_output.py

:: Test locally (if Python installed)
cd guardian_interpreter_starter
python test_voice_module.py

:: Commit and push
git add guardian_interpreter_starter\voice\voice_output.py
git commit -m "Add new voice output feature"
git push origin main
```

**On Raspberry Pi:**

```bash
cd ~/projects/guardian-node

# Pull updates
git pull origin main

# Test changes
cd guardian_interpreter_starter
python3 test_voice_module.py

# Test voice system
python3 demo_voice_system.py
```

#### Workflow 3: Update Documentation

**On Windows 11:**

```cmd
:: Edit documentation
notepad VOICE_INTEGRATION_GUIDE.md

:: Commit and push
git add VOICE_INTEGRATION_GUIDE.md
git commit -m "Update voice integration documentation"
git push origin main
```

**On Raspberry Pi:**

```bash
cd ~/projects/guardian-node

# Pull documentation updates
git pull origin main

# View updated docs
cat VOICE_INTEGRATION_GUIDE.md | less
```

### Regular Maintenance Tasks

#### Weekly

- [ ] Pull latest changes from GitHub
- [ ] Test voice system functionality
- [ ] Check log files for errors

```bash
cd ~/projects/guardian-node
git pull origin main
cd guardian_interpreter_starter
python3 test_voice_module.py
python3 skills/offline_voice_explain.py --list
```

#### Monthly

- [ ] Update system packages
- [ ] Update Python dependencies
- [ ] Review and rotate logs

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Update Python packages
cd ~/projects/guardian-node/guardian_interpreter_starter
source venv/bin/activate
pip list --outdated
pip install --upgrade edge-tts pygame pyttsx3

# Clear old logs
find logs/ -name "*.log" -mtime +30 -delete
```

#### As Needed

- [ ] Regenerate audio files (if voices updated)
- [ ] Add new security risk explanations
- [ ] Update voice profiles

```bash
cd ~/projects/guardian-node/guardian_interpreter_starter
source venv/bin/activate

# Regenerate audio files
python3 skills/audio_pre_recorder.py

# Verify generation
python3 skills/offline_voice_explain.py --list
```

---

## 📊 Deployment Checklist

Use this checklist to ensure complete deployment:

### Pre-Deployment (Windows 11)

- [ ] Voice module files integrated
- [ ] config.yaml updated
- [ ] Documentation created
- [ ] Changes committed to Git
- [ ] Pushed to GitHub
- [ ] Verified files on GitHub web interface

### Initial Deployment (Raspberry Pi)

- [ ] Raspberry Pi OS updated
- [ ] Git installed and configured
- [ ] Audio system tested
- [ ] Repository cloned
- [ ] Python virtual environment created
- [ ] Dependencies installed
- [ ] Directory structure created
- [ ] Audio files generated
- [ ] Metadata created

### Testing & Verification

- [ ] Module imports successful
- [ ] Configuration loads correctly
- [ ] Audio files playback works
- [ ] All age groups tested
- [ ] All risk types tested
- [ ] Demo script runs successfully
- [ ] No error messages

### Post-Deployment

- [ ] Document any issues encountered
- [ ] Update documentation if needed
- [ ] Create backup of audio files (optional)
- [ ] Set up automated updates (optional)

---

## 🎉 Success Criteria

Your deployment is successful when:

✅ **On Windows 11:**
- Repository synced to GitHub
- All files pushed successfully
- Documentation complete

✅ **On Raspberry Pi:**
- Repository cloned and updated
- All dependencies installed
- 12 audio files generated (~2MB)
- Audio playback works for all age groups
- No errors in test scripts

✅ **End-to-End:**
- Changes made on Windows appear on Pi after pull
- Voice system operates completely offline
- High-quality audio output
- Privacy controls enforced

---

## 📚 Additional Resources

### Git Resources

- **Git Documentation**: https://git-scm.com/doc
- **GitHub Docs**: https://docs.github.com/
- **Git Cheat Sheet**: https://education.github.com/git-cheat-sheet-education.pdf

### Raspberry Pi Resources

- **Raspberry Pi Documentation**: https://www.raspberrypi.com/documentation/
- **Raspberry Pi Audio Setup**: https://www.raspberrypi.com/documentation/computers/configuration.html#audio-config
- **SSH Setup**: https://www.raspberrypi.com/documentation/computers/remote-access.html

### Python Resources

- **Edge TTS Documentation**: https://github.com/rany2/edge-tts
- **Pygame Documentation**: https://www.pygame.org/docs/
- **PyYAML Documentation**: https://pyyaml.org/wiki/PyYAMLDocumentation

### Guardian Node Resources

- **VOICE_INTEGRATION_GUIDE.md** - Complete integration details
- **VOICE_QUICK_REFERENCE.md** - Quick command reference
- **config.yaml** - Full configuration options

---

**Guardian Node Deployment Workflow**  
*From Windows 11 development to Raspberry Pi 5 production deployment*  
*Privacy-first, offline-capable, family-friendly security coaching*
