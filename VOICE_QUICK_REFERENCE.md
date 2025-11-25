# 🎤 Guardian Node Voice System - Quick Reference

## 📋 Contents
- [Essential Commands](#essential-commands)
- [Common Tasks](#common-tasks)
- [Configuration Quick Edits](#configuration-quick-edits)
- [Troubleshooting Quick Fixes](#troubleshooting-quick-fixes)
- [Voice Profiles Reference](#voice-profiles-reference)

---

## ⚡ Essential Commands

### Play Voice Explanations

```bash
# Navigate to project
cd ~/projects/guardian-node/guardian_interpreter_starter

# Activate virtual environment (if not already active)
source venv/bin/activate

# List all available explanations
python3 skills/offline_voice_explain.py --list

# Play specific explanation
python3 skills/offline_voice_explain.py --risk RISK_TYPE --age AGE_GROUP
```

### Risk Types
- `phishing`
- `malware`
- `weak_password`
- `suspicious_network`

### Age Groups
- `child` (6-12 years)
- `teen` (13-17 years)
- `adult` (18+ years)

### Example Commands

```bash
# Child-friendly phishing explanation
python3 skills/offline_voice_explain.py --risk phishing --age child

# Teen malware explanation
python3 skills/offline_voice_explain.py --risk malware --age teen

# Adult password security explanation
python3 skills/offline_voice_explain.py --risk weak_password --age adult

# Adult network security explanation
python3 skills/offline_voice_explain.py --risk suspicious_network --age adult
```

---

## 🔧 Common Tasks

### 1. Regenerate Audio Files

```bash
cd ~/projects/guardian-node/guardian_interpreter_starter
source venv/bin/activate

# Generate all 12 audio files (requires internet)
python3 skills/audio_pre_recorder.py

# Verify generation
ls -lh skills/audio_explanations/audio_files/
python3 skills/offline_voice_explain.py --list
```

### 2. Test Voice System

```bash
cd ~/projects/guardian-node/guardian_interpreter_starter
source venv/bin/activate

# Run comprehensive demo
python3 demo_voice_system.py

# Test voice module
python3 test_voice_module.py
```

### 3. Check Audio Status

```bash
# List audio files
ls -lh skills/audio_explanations/audio_files/

# Count files (should be 12)
ls skills/audio_explanations/audio_files/*.mp3 | wc -l

# Check total size
du -sh skills/audio_explanations/audio_files/

# View metadata
cat skills/audio_explanations/metadata.json | python3 -m json.tool | less
```

### 4. Update from GitHub

```bash
cd ~/projects/guardian-node

# Pull latest changes
git pull origin main

# Reinstall dependencies if needed
cd guardian_interpreter_starter
source venv/bin/activate
pip install -r requirements.txt  # if requirements.txt exists
```

### 5. Push Changes to GitHub (from Windows)

```cmd
REM Navigate to repository
cd C:\Users\YourUsername\Documents\guardian-node

REM Check status
git status

REM Add changes
git add .

REM Commit with message
git commit -m "Your commit message"

REM Push to GitHub
git push origin main
```

---

## ⚙️ Configuration Quick Edits

### Change Voice Speed

Edit `config.yaml`:

```yaml
voice_output:
  speech_rate: 150  # Change this (100-200)
  # 100 = slow, 150 = normal, 200 = fast
```

### Change Volume

```yaml
voice_output:
  volume: 0.8  # Change this (0.0-1.0)
  # 0.0 = mute, 0.5 = half, 1.0 = max
```

### Change Voice Profile

```yaml
voice_profiles:
  child:
    voice_name: "en-US-JennyNeural"  # Change voice
    pitch: "+10Hz"                    # Adjust pitch
    rate: "+10%"                      # Adjust speed
```

### Available Edge TTS Voices (Neural)

**Female Voices:**
- `en-US-JennyNeural` - Warm, friendly (default child)
- `en-US-AriaNeural` - Clear, professional (default teen)
- `en-US-MichelleNeural` - Enthusiastic, bright
- `en-US-AmberNeural` - Upbeat, energetic

**Male Voices:**
- `en-US-DavisNeural` - Professional, authoritative (default adult)
- `en-US-GuyNeural` - Clear, conversational
- `en-US-TonyNeural` - Confident, news anchor style
- `en-US-AndrewNeural` - Warm, storytelling

### Apply Configuration Changes

```bash
# Configuration changes take effect immediately on next run
# No restart needed for standalone scripts

# Test new settings
python3 skills/offline_voice_explain.py --risk phishing --age teen
```

---

## 🆘 Troubleshooting Quick Fixes

### No Sound Output

```bash
# 1. Check audio devices
aplay -l

# 2. Test system audio
speaker-test -t wav -c 2
# Press Ctrl+C to stop

# 3. Set correct output
sudo raspi-config
# → System Options → Audio → Select your device

# 4. Adjust volume
alsamixer
# Use arrow keys, ESC to exit

# 5. Test with simple file
aplay /usr/share/sounds/alsa/Front_Center.wav
```

### Audio Files Missing

```bash
# Check if files exist
ls skills/audio_explanations/audio_files/*.mp3

# If missing, regenerate
cd ~/projects/guardian-node/guardian_interpreter_starter
source venv/bin/activate
python3 skills/audio_pre_recorder.py
```

### Module Import Errors

```bash
# Activate virtual environment
cd ~/projects/guardian-node/guardian_interpreter_starter
source venv/bin/activate

# Check if dependencies installed
pip list | grep -E "edge-tts|pygame|pyttsx3"

# Reinstall if missing
pip install edge-tts pygame pyttsx3 pyyaml
```

### Permission Errors

```bash
# Fix directory permissions
cd ~/projects/guardian-node
chmod -R 755 guardian_interpreter_starter/

# Fix file ownership
sudo chown -R $USER:$USER guardian_interpreter_starter/
```

### Git Authentication Issues

```bash
# Use personal access token (not password)
git remote set-url origin https://YOUR_USERNAME:YOUR_TOKEN@github.com/YOUR_USERNAME/guardian-node.git

# Or configure credential storage
git config --global credential.helper store
```

---

## 🎭 Voice Profiles Reference

### Quick Comparison Table

| Age Group | Voice | Tone | Vocabulary | Example Use Case |
|-----------|-------|------|------------|------------------|
| **Child** | Jenny | Warm, friendly | Simple | Explaining to kids |
| **Teen** | Aria | Educational | Moderate | Teaching teenagers |
| **Adult** | Davis | Professional | Technical | Enterprise training |

### Voice Characteristics

#### Child (Jenny Neural)
- 🎵 **Tone:** Warm and reassuring
- 📚 **Language:** Simple, everyday words
- 🐢 **Pace:** Slightly slower
- 🎯 **Focus:** Safety and comfort
- ⏱️ **Duration:** ~30-45 seconds per explanation

#### Teen (Aria Neural)
- 🎓 **Tone:** Educational and engaging
- 📖 **Language:** Age-appropriate technical terms
- ⚡ **Pace:** Normal speed
- 🎯 **Focus:** Learning and awareness
- ⏱️ **Duration:** ~45-60 seconds per explanation

#### Adult (Davis Neural)
- 💼 **Tone:** Professional and authoritative
- 🔧 **Language:** Technical vocabulary
- 🚀 **Pace:** Efficient delivery
- 🎯 **Focus:** Implementation and best practices
- ⏱️ **Duration:** ~60-90 seconds per explanation

### Content Adaptation Examples

#### Phishing Explanation

**Child Version (Simple):**
> "Phishing is when bad people pretend to be someone you trust..."

**Teen Version (Educational):**
> "Phishing attacks use social engineering to create fake emails..."

**Adult Version (Technical):**
> "Phishing is a sophisticated attack vector utilizing domain spoofing and social engineering to compromise credentials..."

---

## 📊 System Status Commands

### Check Everything at Once

```bash
cd ~/projects/guardian-node/guardian_interpreter_starter
source venv/bin/activate

# Create quick status check script
cat << 'EOF' > check_status.sh
#!/bin/bash
echo "================================"
echo "Guardian Node Voice System Status"
echo "================================"
echo ""

echo "📁 Audio Files:"
FILE_COUNT=$(ls skills/audio_explanations/audio_files/*.mp3 2>/dev/null | wc -l)
echo "   Count: $FILE_COUNT/12"
SIZE=$(du -sh skills/audio_explanations/audio_files/ 2>/dev/null | cut -f1)
echo "   Size: $SIZE"
echo ""

echo "🔊 Audio System:"
if speaker-test -t wav -c 2 -P 1 &>/dev/null; then
    echo "   ✅ Audio output working"
else
    echo "   ❌ Audio output issue"
fi
echo ""

echo "🐍 Python Dependencies:"
source venv/bin/activate 2>/dev/null
for pkg in edge-tts pygame pyttsx3 pyyaml; do
    if pip show $pkg &>/dev/null; then
        VERSION=$(pip show $pkg | grep Version | cut -d' ' -f2)
        echo "   ✅ $pkg ($VERSION)"
    else
        echo "   ❌ $pkg (not installed)"
    fi
done
echo ""

echo "⚙️  Configuration:"
if [ -f "config.yaml" ]; then
    echo "   ✅ config.yaml exists"
    ENABLED=$(grep "enabled: true" config.yaml | wc -l)
    echo "   Enabled features: $ENABLED"
else
    echo "   ❌ config.yaml missing"
fi
echo ""

echo "📝 Git Status:"
cd ~/projects/guardian-node
BRANCH=$(git branch --show-current)
echo "   Branch: $BRANCH"
STATUS=$(git status --porcelain | wc -l)
if [ $STATUS -eq 0 ]; then
    echo "   ✅ Clean working tree"
else
    echo "   ⚠️  $STATUS uncommitted changes"
fi
echo ""
EOF

chmod +x check_status.sh
./check_status.sh
```

### Quick Test Command

```bash
# One-liner to test audio playback
cd ~/projects/guardian-node/guardian_interpreter_starter && source venv/bin/activate && python3 skills/offline_voice_explain.py --risk phishing --age teen
```

---

## 🔗 Useful File Paths

### Project Structure

```
~/projects/guardian-node/                    # Root directory
├── guardian_interpreter_starter/            # Main application
│   ├── voice/                               # Voice module
│   │   ├── voice_input.py
│   │   ├── voice_output.py
│   │   └── voice_interface.py
│   ├── skills/                              # Skills directory
│   │   ├── audio_explanations/
│   │   │   ├── audio_files/                 # 12 MP3 files (~2MB)
│   │   │   ├── cache/                       # Runtime cache
│   │   │   └── metadata.json                # File metadata
│   │   ├── audio_pre_recorder.py            # Generate audio
│   │   └── offline_voice_explain.py         # Play audio
│   ├── config.yaml                          # Main configuration
│   ├── demo_voice_system.py                 # System demo
│   └── venv/                                # Python virtual environment
├── VOICE_INTEGRATION_GUIDE.md               # Complete guide
├── WINDOWS_TO_PI_WORKFLOW.md                # Deployment workflow
└── VOICE_QUICK_REFERENCE.md                 # This file
```

### Configuration Files

```bash
# Main configuration
~/projects/guardian-node/guardian_interpreter_starter/config.yaml

# Audio metadata
~/projects/guardian-node/guardian_interpreter_starter/skills/audio_explanations/metadata.json

# Logs (if enabled)
~/projects/guardian-node/guardian_interpreter_starter/logs/guardian.log
```

---

## 💾 Backup Commands

### Backup Audio Files

```bash
# Create backup directory
mkdir -p ~/guardian_backups/audio_$(date +%Y%m%d)

# Copy audio files
cp -r ~/projects/guardian-node/guardian_interpreter_starter/skills/audio_explanations/audio_files/ \
      ~/guardian_backups/audio_$(date +%Y%m%d)/

# Copy metadata
cp ~/projects/guardian-node/guardian_interpreter_starter/skills/audio_explanations/metadata.json \
   ~/guardian_backups/audio_$(date +%Y%m%d)/

echo "Backup created in ~/guardian_backups/audio_$(date +%Y%m%d)/"
```

### Restore from Backup

```bash
# List backups
ls -la ~/guardian_backups/

# Restore from specific backup
cp -r ~/guardian_backups/audio_YYYYMMDD/audio_files/* \
      ~/projects/guardian-node/guardian_interpreter_starter/skills/audio_explanations/audio_files/

cp ~/guardian_backups/audio_YYYYMMDD/metadata.json \
   ~/projects/guardian-node/guardian_interpreter_starter/skills/audio_explanations/

# Verify restoration
python3 ~/projects/guardian-node/guardian_interpreter_starter/skills/offline_voice_explain.py --list
```

---

## 🚀 Performance Tips

### Speed Up Loading

```yaml
# In config.yaml
performance:
  lazy_loading: true          # Load resources on demand
  cache_preloading: false     # Don't preload at startup
  memory_limit_mb: 512        # Adjust based on Pi memory
```

### Optimize Audio Quality vs Size

```yaml
# In config.yaml
audio:
  sample_rate: 24000          # 24kHz (high quality)
  # Use 22050 for smaller files
  # Use 16000 for even smaller files (lower quality)
```

### Reduce Memory Usage

```bash
# Close unnecessary applications
sudo systemctl stop <service_name>

# Check memory usage
free -h

# Clear cache if needed
sudo sync && sudo sh -c "echo 3 > /proc/sys/vm/drop_caches"
```

---

## 📱 Integration Examples

### Use in Python Scripts

```python
#!/usr/bin/env python3
"""Example: Using Guardian Voice System in Python"""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path("~/projects/guardian-node/guardian_interpreter_starter").expanduser()))

from voice.voice_output import VoiceOutput
import yaml

# Load configuration
with open("config.yaml", 'r') as f:
    config = yaml.safe_load(f)

# Initialize voice output
voice = VoiceOutput(config)

# Speak text
voice.speak("This is a test of the Guardian voice system.")

# Use specific voice profile
voice.speak("Child-friendly message", profile="child")
voice.speak("Technical explanation", profile="adult")
```

### Bash Script Integration

```bash
#!/bin/bash
# Example: Play explanation based on detected threat

THREAT_TYPE="phishing"
USER_AGE="teen"

cd ~/projects/guardian-node/guardian_interpreter_starter
source venv/bin/activate

python3 skills/offline_voice_explain.py --risk $THREAT_TYPE --age $USER_AGE
```

---

## 🔄 Update Procedures

### Weekly Update Routine

```bash
# 1. Update system packages
sudo apt update && sudo apt upgrade -y

# 2. Pull latest code
cd ~/projects/guardian-node
git pull origin main

# 3. Update Python dependencies
cd guardian_interpreter_starter
source venv/bin/activate
pip install --upgrade edge-tts pygame pyttsx3

# 4. Test system
python3 test_voice_module.py
python3 skills/offline_voice_explain.py --list

# 5. Clean cache
rm -rf skills/audio_explanations/cache/*
```

### After Configuration Changes

```bash
# 1. Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"

# 2. Test with new settings
python3 skills/offline_voice_explain.py --risk phishing --age child

# 3. Commit if satisfied
git add config.yaml
git commit -m "Update voice configuration"
git push origin main
```

---

## 📞 Quick Help

### Get Help for Commands

```bash
# Offline voice explainer help
python3 skills/offline_voice_explain.py --help

# Audio pre-recorder help
python3 skills/audio_pre_recorder.py --help

# View configuration
cat config.yaml | less

# View documentation
cat VOICE_INTEGRATION_GUIDE.md | less
```

### Common Command Aliases

Add these to `~/.bashrc` for quick access:

```bash
# Guardian Voice System Aliases
alias gv-cd='cd ~/projects/guardian-node/guardian_interpreter_starter'
alias gv-activate='cd ~/projects/guardian-node/guardian_interpreter_starter && source venv/bin/activate'
alias gv-list='gv-activate && python3 skills/offline_voice_explain.py --list'
alias gv-play='gv-activate && python3 skills/offline_voice_explain.py'
alias gv-demo='gv-activate && python3 demo_voice_system.py'
alias gv-test='gv-activate && python3 test_voice_module.py'
alias gv-status='cd ~/projects/guardian-node && git status'
alias gv-pull='cd ~/projects/guardian-node && git pull origin main'

# Usage examples:
# gv-list                               # List all explanations
# gv-play --risk phishing --age teen    # Play explanation
# gv-demo                               # Run demo
```

Reload bashrc:
```bash
source ~/.bashrc
```

---

## 🎯 Quick Start Checklist

For first-time setup, complete in order:

- [ ] 1. Clone repository
- [ ] 2. Install dependencies
- [ ] 3. Create virtual environment
- [ ] 4. Generate audio files
- [ ] 5. Test audio playback
- [ ] 6. Run demo script

**One-liner for experienced users:**

```bash
cd ~/projects && git clone https://github.com/YOUR_USERNAME/guardian-node.git && cd guardian-node/guardian_interpreter_starter && python3 -m venv venv && source venv/bin/activate && pip install edge-tts pygame pyttsx3 pyyaml && python3 skills/audio_pre_recorder.py && python3 skills/offline_voice_explain.py --list
```

---

## 📚 Additional References

- **Full Integration Guide:** `VOICE_INTEGRATION_GUIDE.md`
- **Deployment Workflow:** `WINDOWS_TO_PI_WORKFLOW.md`
- **Configuration Reference:** `config.yaml` (with inline comments)
- **Edge TTS Docs:** https://github.com/rany2/edge-tts
- **Pygame Audio Docs:** https://www.pygame.org/docs/ref/mixer.html

---

**Guardian Node Voice System Quick Reference**  
*Version 1.0 - For Raspberry Pi 5 deployment*  
*Privacy-first, offline-capable, family-friendly security coaching*

---

## 📝 Notes

- All commands assume you're starting from the home directory (`~`)
- Virtual environment must be activated for Python commands
- Audio generation requires internet (one-time only)
- Playback works completely offline after setup
- Configuration changes take effect immediately
- No service restart needed for standalone scripts

**For complete documentation, see:** `VOICE_INTEGRATION_GUIDE.md`
