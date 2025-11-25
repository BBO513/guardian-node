# 🎤 Guardian Node Voice System Integration Guide

## 📋 Table of Contents
1. [Overview](#overview)
2. [What Was Added](#what-was-added)
3. [How the Voice System Works](#how-the-voice-system-works)
4. [Directory Structure](#directory-structure)
5. [Configuration Options](#configuration-options)
6. [Voice Profiles](#voice-profiles)
7. [Security Features](#security-features)
8. [Testing the Integration](#testing-the-integration)

---

## 🎯 Overview

The Guardian Node voice system provides **offline, privacy-first security coaching** using pre-recorded neural voices. After initial setup, the system operates completely offline, ensuring:

- ✅ **Zero data leakage** - No cloud communication
- ✅ **Instant responses** - Pre-recorded MP3s play immediately
- ✅ **High quality** - Microsoft Edge TTS neural voices
- ✅ **Age-appropriate** - Content adapted for children, teens, and adults
- ✅ **Privacy-first** - No logging of spoken content

### Key Features

| Feature | Description |
|---------|-------------|
| **Offline Operation** | Works without internet after setup |
| **Neural Voices** | High-quality Microsoft Edge TTS voices |
| **Age Groups** | 3 levels: child, teen, adult |
| **Risk Types** | 4 categories: phishing, malware, weak_password, suspicious_network |
| **Audio Files** | 12 pre-recorded MP3s (4 risks × 3 ages) |
| **Total Size** | ~2MB for complete voice library |
| **Latency** | Instant playback from local storage |

---

## 📦 What Was Added

### 1. Voice Module (`guardian_interpreter_starter/voice/`)

Four core files that handle voice input/output:

```
guardian_interpreter_starter/voice/
├── __init__.py              # Module initialization
├── voice_input.py           # Microphone input and speech recognition
├── voice_output.py          # Text-to-speech synthesis and playback
└── voice_interface.py       # High-level API for voice interactions
```

**Purpose:**
- `voice_input.py`: Captures and processes voice commands (speech-to-text)
- `voice_output.py`: Generates speech from text using Edge TTS or pyttsx3
- `voice_interface.py`: Unified interface combining input and output
- `__init__.py`: Exports voice classes for easy importing

### 2. Configuration File (`config.yaml`)

Enhanced configuration with comprehensive voice settings:

```yaml
voice_system:
  enabled: true
  offline_mode: true
  privacy_mode: true

voice_profiles:
  child: en-US-JennyNeural    # Warm, friendly
  teen: en-US-AriaNeural      # Clear, educational
  adult: en-US-DavisNeural    # Professional, authoritative

audio:
  tts_service: edge_tts_offline
  output_format: mp3
  sample_rate: 24000
  cache_enabled: true
```

### 3. Setup Scripts

**Windows Setup** (`setup_offline_voice.bat`):
- Creates directory structure
- Installs Python dependencies
- Generates audio configuration
- Provides setup instructions

**Demo Script** (`demo_voice_system.py`):
- Complete system demonstration
- Tests all voice profiles
- Shows security coaching examples
- Validates audio playback

### 4. Test Scripts

**Voice Explanation Test** (`test_voice_explain.py`):
- Tests pre-recorded explanation playback
- Validates audio file availability
- Checks voice profile switching

### 5. Directory Structure

New directories for audio management:

```
guardian_interpreter_starter/skills/
└── audio_explanations/
    ├── audio_files/         # Pre-recorded MP3s (12 files)
    │   ├── phishing_child.mp3
    │   ├── phishing_teen.mp3
    │   ├── phishing_adult.mp3
    │   ├── malware_child.mp3
    │   ├── malware_teen.mp3
    │   ├── malware_adult.mp3
    │   ├── weak_password_child.mp3
    │   ├── weak_password_teen.mp3
    │   ├── weak_password_adult.mp3
    │   ├── suspicious_network_child.mp3
    │   ├── suspicious_network_teen.mp3
    │   └── suspicious_network_adult.mp3
    ├── cache/               # Runtime audio cache
    └── metadata.json        # Audio file metadata
```

---

## 🔧 How the Voice System Works

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Guardian Node User                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Voice Interface (voice_interface.py)            │
│  • Unified API for voice input/output                       │
│  • Age group management                                     │
│  • Privacy controls                                         │
└──────────────┬──────────────────────────┬───────────────────┘
               │                          │
               ▼                          ▼
    ┌──────────────────┐      ┌──────────────────┐
    │  Voice Input     │      │  Voice Output    │
    │  (voice_input.py)│      │ (voice_output.py)│
    │                  │      │                  │
    │  • Speech-to-text│      │  • Text-to-speech│
    │  • Microphone    │      │  • Audio playback│
    │  • Command parsing│      │  • Voice profiles│
    └──────────────────┘      └─────────┬────────┘
                                        │
                                        ▼
                         ┌──────────────────────────┐
                         │   Edge TTS (Offline)     │
                         │  • Neural voice synthesis│
                         │  • MP3 generation        │
                         │  • Local caching         │
                         └──────────┬───────────────┘
                                    │
                                    ▼
                         ┌──────────────────────────┐
                         │  Pre-recorded Audio Files│
                         │  • 12 MP3 files          │
                         │  • ~2MB total            │
                         │  • Instant playback      │
                         └──────────────────────────┘
```

### Workflow: From Setup to Operation

#### Phase 1: Initial Setup (One-time, Requires Internet)

```
1. Install Dependencies
   ├── edge-tts (neural voice synthesis)
   ├── pygame (audio playback)
   └── pyttsx3 (fallback TTS)

2. Run Audio Pre-recorder
   ├── Generate 12 explanations
   ├── Save as MP3 files (~2MB)
   └── Create metadata.json

3. Result: Complete Offline System
   └── No more internet needed!
```

#### Phase 2: Offline Operation (Internet Not Required)

```
1. User Request
   └── "Explain phishing to a teenager"

2. Voice System
   ├── Identifies: risk=phishing, age=teen
   ├── Locates: audio_files/phishing_teen.mp3
   └── Plays: Pre-recorded explanation

3. Result: Instant Audio Response
   └── High-quality neural voice explanation
```

### Edge TTS Technology

**What is Edge TTS?**
- Microsoft's text-to-speech service using neural networks
- Produces natural, human-like voices
- Available through Python library `edge-tts`

**How We Use It:**

1. **Online Phase (Setup Only):**
   ```python
   import edge_tts
   
   # Generate audio with neural voice
   communicate = edge_tts.Communicate(
       text="Phishing is when bad actors try to trick you...",
       voice="en-US-JennyNeural"
   )
   
   # Save to MP3 file
   await communicate.save("phishing_child.mp3")
   ```

2. **Offline Phase (Runtime):**
   ```python
   import pygame
   
   # Simply play the pre-recorded file
   pygame.mixer.music.load("phishing_child.mp3")
   pygame.mixer.music.play()
   ```

**Why This Approach?**
- ✅ Best quality (neural voices during setup)
- ✅ True offline operation (no internet needed)
- ✅ Instant playback (no synthesis delay)
- ✅ Privacy-first (no cloud communication)
- ✅ Low storage (~170KB per audio file)

---

## 📁 Directory Structure

Complete file organization:

```
guardian-node/
├── guardian_interpreter_starter/
│   ├── voice/                          # Voice module
│   │   ├── __init__.py
│   │   ├── voice_input.py              # Speech recognition
│   │   ├── voice_output.py             # TTS and playback
│   │   └── voice_interface.py          # Unified API
│   │
│   ├── skills/                         # Guardian skills
│   │   ├── audio_explanations/
│   │   │   ├── audio_files/            # Pre-recorded MP3s (12 files)
│   │   │   │   ├── phishing_child.mp3
│   │   │   │   ├── phishing_teen.mp3
│   │   │   │   ├── phishing_adult.mp3
│   │   │   │   ├── malware_child.mp3
│   │   │   │   ├── malware_teen.mp3
│   │   │   │   ├── malware_adult.mp3
│   │   │   │   ├── weak_password_child.mp3
│   │   │   │   ├── weak_password_teen.mp3
│   │   │   │   ├── weak_password_adult.mp3
│   │   │   │   ├── suspicious_network_child.mp3
│   │   │   │   ├── suspicious_network_teen.mp3
│   │   │   │   └── suspicious_network_adult.mp3
│   │   │   ├── cache/                  # Runtime cache
│   │   │   └── metadata.json           # File metadata
│   │   │
│   │   ├── offline_voice_explain.py    # Explanation playback skill
│   │   ├── audio_pre_recorder.py       # Audio generation tool
│   │   └── security_coach.py           # Security coaching skill
│   │
│   ├── config.yaml                     # Main configuration
│   ├── setup_offline_voice.bat         # Windows setup script
│   ├── demo_voice_system.py            # System demonstration
│   └── test_voice_explain.py           # Testing script
│
├── VOICE_INTEGRATION_GUIDE.md          # This document
├── WINDOWS_TO_PI_WORKFLOW.md           # Deployment workflow
└── VOICE_QUICK_REFERENCE.md            # Quick reference guide
```

---

## ⚙️ Configuration Options

### Complete config.yaml Breakdown

#### Voice System Settings

```yaml
voice_system:
  enabled: true              # Enable/disable voice features
  offline_mode: true         # Require offline operation
  privacy_mode: true         # No content logging
```

| Setting | Values | Description |
|---------|--------|-------------|
| `enabled` | true/false | Master switch for voice system |
| `offline_mode` | true/false | Enforce offline operation |
| `privacy_mode` | true/false | Prevent logging of spoken content |

#### Voice Output Settings

```yaml
voice_output:
  speech_rate: 150           # 100-200 words per minute
  volume: 0.8                # 0.0 to 1.0
  family_mode: true          # Family-friendly filtering
  child_friendly_voice: true # Use appropriate voices
  log_speech: false          # Never log content
```

| Setting | Range | Recommended |
|---------|-------|-------------|
| `speech_rate` | 100-200 WPM | 150 WPM |
| `volume` | 0.0-1.0 | 0.8 |
| `family_mode` | true/false | true |

#### Audio System Settings

```yaml
audio:
  tts_service: "edge_tts_offline"
  output_format: "mp3"
  sample_rate: 24000
  bitrate: "variable"
  cache_enabled: true
  audio_files_path: "./skills/audio_explanations/audio_files"
  cache_path: "./skills/audio_explanations/cache"
  metadata_path: "./skills/audio_explanations/metadata.json"
```

| Setting | Options | Notes |
|---------|---------|-------|
| `tts_service` | edge_tts_offline, pyttsx3 | edge_tts_offline preferred |
| `output_format` | mp3, wav | mp3 for efficiency |
| `sample_rate` | 16000, 22050, 24000 | 24000 for quality |

#### Skills Configuration

```yaml
skills:
  enabled: true
  allowed_skills:
    - offline_voice_explain
    - audio_pre_recorder
    - security_coach
  skill_timeout: 300
  skill_isolation: true
  skill_logging: true
```

---

## 🎭 Voice Profiles

### Neural Voice Selection

Guardian Node uses three Microsoft Edge TTS neural voices, carefully selected for their quality and appropriateness:

#### 1. Child Profile: Jenny Neural

```yaml
child:
  voice_name: "en-US-JennyNeural"
  pitch: "+10Hz"
  rate: "+10%"
  description: "Child-friendly, reassuring tone"
```

**Characteristics:**
- 🎵 Warm and friendly tone
- 😊 Reassuring and comforting
- 📚 Simple vocabulary
- 🐢 Slightly slower pace
- 🎯 Ages 6-12

**Example Content:**
> "Hey there! Phishing is when bad people try to trick you by pretending to be someone you trust, like sending a fake email that looks like it's from your teacher or a game you play. Always ask a grown-up before clicking on links in emails!"

#### 2. Teen Profile: Aria Neural

```yaml
teen:
  voice_name: "en-US-AriaNeural"
  pitch: "0Hz"
  rate: "0%"
  description: "Educational and engaging"
```

**Characteristics:**
- 🎓 Clear and educational
- 💡 Engaging and informative
- 📖 Age-appropriate vocabulary
- ⚡ Normal pace
- 🎯 Ages 13-17

**Example Content:**
> "Phishing attacks are social engineering techniques where attackers create fake emails or websites that look legitimate to steal your personal information. Look for warning signs like spelling errors, suspicious URLs, or urgent requests for passwords."

#### 3. Adult Profile: Davis Neural

```yaml
adult:
  voice_name: "en-US-DavisNeural"
  pitch: "0Hz"
  rate: "0%"
  description: "Professional and technical"
```

**Characteristics:**
- 💼 Professional and authoritative
- 🔧 Technical vocabulary
- 📊 Comprehensive details
- 🚀 Efficient delivery
- 🎯 Ages 18+

**Example Content:**
> "Phishing is a sophisticated attack vector utilizing social engineering and domain spoofing to compromise credentials. Implement SPF, DKIM, and DMARC email authentication, enable MFA, and train users to verify sender authenticity through secondary channels before responding to sensitive requests."

### Voice Profile Comparison

| Aspect | Child (Jenny) | Teen (Aria) | Adult (Davis) |
|--------|---------------|-------------|---------------|
| **Tone** | Warm, friendly | Educational | Professional |
| **Complexity** | Simple | Moderate | Technical |
| **Pace** | Slower | Normal | Normal |
| **Vocabulary** | Basic | Intermediate | Advanced |
| **Focus** | Reassurance | Learning | Implementation |

---

## 🔒 Security Features

### Privacy Protections

1. **No Cloud Communication**
   - After setup, system operates completely offline
   - No data sent to external services
   - Zero telemetry or analytics

2. **Content Logging Disabled**
   ```yaml
   voice_output:
     log_speech: false
   privacy:
     no_telemetry: true
   ```

3. **Local Storage Only**
   - All audio files stored locally
   - No cloud synchronization
   - Complete data sovereignty

### Security Controls

1. **Skill Allowlisting**
   ```yaml
   skills:
     allowed_skills:
       - offline_voice_explain
       - audio_pre_recorder
       - security_coach
   ```

2. **Timeout Enforcement**
   ```yaml
   skills:
     skill_timeout: 300  # 5 minutes max
   ```

3. **Input Sanitization**
   ```yaml
   security:
     input_sanitization: true
   ```

4. **Resource Limits**
   ```yaml
   performance:
     memory_limit_mb: 512
   ```

---

## 🧪 Testing the Integration

### Quick Verification

#### 1. Check Files Exist

```bash
cd guardian-node/guardian_interpreter_starter

# Verify voice module
ls -la voice/
# Expected: __init__.py, voice_input.py, voice_output.py, voice_interface.py

# Verify directory structure
ls -la skills/audio_explanations/
# Expected: audio_files/, cache/, metadata.json
```

#### 2. Validate Configuration

```bash
# Check config.yaml syntax
python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"

# Should print nothing if valid, or show syntax errors
```

#### 3. Test Demo Script

```bash
# Run voice system demo (requires audio files)
python3 demo_voice_system.py
```

### Complete Test Procedure

#### Test 1: Voice Module Import

```python
# test_voice_import.py
from voice import VoiceInput, VoiceOutput, VoiceInterface

print("✅ Voice module imports successfully")
```

#### Test 2: Configuration Loading

```python
# test_config.py
import yaml

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

assert config['voice_system']['enabled'] == True
assert 'voice_profiles' in config
assert len(config['voice_profiles']) == 3

print("✅ Configuration valid")
```

#### Test 3: Audio Directory Structure

```bash
#!/bin/bash
# test_directories.sh

check_dir() {
    if [ -d "$1" ]; then
        echo "✅ $1 exists"
    else
        echo "❌ $1 missing"
        return 1
    fi
}

check_dir "skills/audio_explanations"
check_dir "skills/audio_explanations/audio_files"
check_dir "skills/audio_explanations/cache"
```

---

## 📊 Integration Summary

### What's Ready to Use

✅ **Voice Module** - Complete input/output functionality  
✅ **Configuration** - Comprehensive settings for all features  
✅ **Directory Structure** - All required folders created  
✅ **Setup Scripts** - Windows and Linux setup automation  
✅ **Demo Scripts** - Complete system demonstration  
✅ **Documentation** - This guide and quick reference  

### What Requires Setup on Raspberry Pi

⏸️ **Audio Files** - 12 MP3 files to be generated (requires internet once)  
⏸️ **Dependencies** - Python packages installation  
⏸️ **Testing** - Verification of audio playback  

### Storage Requirements

| Component | Size | Location |
|-----------|------|----------|
| Voice module | ~40KB | `voice/` |
| Config file | ~6KB | `config.yaml` |
| Audio files | ~2MB | `skills/audio_explanations/audio_files/` |
| Cache | ~5MB max | `skills/audio_explanations/cache/` |
| **Total** | **~7MB** | - |

### Performance Expectations

| Metric | Value | Notes |
|--------|-------|-------|
| Startup Time | <1 second | No preloading |
| Playback Latency | Instant | Pre-recorded files |
| Memory Usage | <50MB | During playback |
| CPU Usage | Minimal | No synthesis |
| Audio Quality | 24kHz MP3 | High quality |

---

## 🚀 Next Steps

### For Development (Windows 11 PC)

1. ✅ Voice integration complete
2. ➡️ Push to GitHub (see `WINDOWS_TO_PI_WORKFLOW.md`)
3. ➡️ Test on local machine

### For Deployment (Raspberry Pi 5)

1. ➡️ Pull from GitHub
2. ➡️ Install dependencies
3. ➡️ Generate audio files
4. ➡️ Test voice system

See **WINDOWS_TO_PI_WORKFLOW.md** for detailed deployment instructions.

---

## 📚 Additional Resources

- **VOICE_SYSTEM_README.md** - Original voice system documentation
- **WINDOWS_TO_PI_WORKFLOW.md** - Complete deployment workflow
- **VOICE_QUICK_REFERENCE.md** - Quick command reference
- **config.yaml** - Full configuration with comments

---

**Guardian Node Voice System** - Privacy-first security coaching with neural voices.  
*Built for offline operation, optimized for Raspberry Pi 5, designed for families.*
