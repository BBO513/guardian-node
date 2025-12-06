# Guardian Node Voice System

## 🎯 Overview

Guardian Node's offline voice explanation system provides high-quality, privacy-first security coaching using pre-recorded neural voices. The system operates completely offline once initial setup is complete, ensuring zero data leakage and instant response times.

## 🏗️ Architecture

### Core Components

1. **Audio Pre-recorder** (`skills/audio_pre_recorder.py`)
   - Records security explanations using Edge TTS neural voices
   - Creates 12 high-quality MP3 files for offline use
   - Supports 4 risk types × 3 age groups

2. **Offline Voice Explainer** (`skills/offline_voice_explain.py`)
   - Plays pre-recorded explanations instantly
   - Manages audio file library
   - Supports custom explanation additions

3. **Security Coach** (`skills/security_coach.py`)
   - Interactive security coaching with voice integration
   - Threat assessment and risk analysis
   - Age-appropriate recommendations

4. **Setup Scripts**
   - `setup_offline_voice.bat` - Windows setup automation
   - `demo_voice_system.py` - Complete system demonstration

## 🚀 Quick Start

### 1. Initial Setup
```bash
# Run setup script
setup_offline_voice.bat

# Pre-record all explanations
python skills/audio_pre_recorder.py --record
```

### 2. Test Voice System
```bash
# List available explanations
python skills/offline_voice_explain.py --list

# Play specific explanation
python skills/offline_voice_explain.py --risk phishing --age teen
```

### 3. Use Security Coach
```bash
# List coaching scenarios
python main.py "skill security_coach list"

# Interactive coaching
python main.py "skill security_coach coach phishing_email teen"

# Threat assessment
python main.py "skill security_coach assess email suspicious_content adult"
```

## 📊 Content Library

### Security Risk Types
- **Phishing** - Email and web-based deception attacks
- **Malware** - Malicious software threats
- **Weak Password** - Password security vulnerabilities
- **Suspicious Network** - Network connection risks

### Age Groups
- **Child** - Simple, reassuring explanations
- **Teen** - Educational with practical advice
- **Adult** - Technical details and enterprise guidance

### Voice Profiles
- **Child**: Jenny Neural (warm, friendly)
- **Teen**: Aria Neural (clear, educational)
- **Adult**: Brian Neural (professional, authoritative)

## 🔧 Configuration

### Audio Settings (`skills/audio_config.json`)
```json
{
  "tts_service": "edge_tts_offline",
  "voice_settings": {
    "child": {"voice_name": "en-US-JennyNeural"},
    "teen": {"voice_name": "en-US-AriaNeural"},
    "adult": {"voice_name": "en-US-BrianNeural"}
  },
  "output_format": "mp3",
  "sample_rate": 24000,
  "cache_enabled": true,
  "offline_mode": true
}
```

### Guardian Config (`config.yaml`)
```yaml
skills:
  allowed_skills:
    - offline_voice_explain
    - audio_pre_recorder
    - security_coach
```

## 📁 File Structure

```
guardian_interpreter_starter/
├── skills/
│   ├── audio_explanations/
│   │   ├── audio_files/
│   │   │   ├── phishing_child.mp3
│   │   │   ├── phishing_teen.mp3
│   │   │   ├── phishing_adult.mp3
│   │   │   └── ... (12 total files)
│   │   └── metadata.json
│   ├── audio_config.json
│   ├── offline_voice_explain.py
│   ├── audio_pre_recorder.py
│   └── security_coach.py
├── setup_offline_voice.bat
└── demo_voice_system.py
```

## 🎮 Usage Examples

### Basic Voice Explanations
```bash
# Play phishing explanation for teenagers
python skills/offline_voice_explain.py --risk phishing --age teen

# List all available explanations
python skills/offline_voice_explain.py --list

# Add custom explanation
python skills/offline_voice_explain.py --add --risk custom_threat --age adult --file custom.mp3
```

### Security Coaching
```bash
# List coaching scenarios
python main.py "skill security_coach list"

# Coach phishing detection for teens
python main.py "skill security_coach coach phishing_email teen"

# Assess email threat for adults
python main.py "skill security_coach assess email urgent_verification adult"

# Check voice system status
python main.py "skill security_coach voice"
```

### Integration with Guardian
```python
from skills.security_coach import SecurityCoachSkill

# Initialize coach
coach = SecurityCoachSkill()

# Provide coaching with voice
result = coach.coach_scenario("phishing_email", "teen", voice_enabled=True)

# Assess threat
assessment = coach.assess_threat("email", "urgent verification", "adult")
```

## 🔒 Privacy & Security Features

### Privacy-First Design
- ✅ **Zero External Dependencies** - No cloud APIs after setup
- ✅ **Complete Offline Operation** - Works without internet
- ✅ **Local Data Storage** - All files stay on device
- ✅ **No Telemetry** - No usage tracking or analytics

### Security Controls
- ✅ **Skill Allowlists** - Only approved skills can execute
- ✅ **Timeout Protection** - Skills have execution time limits
- ✅ **Input Sanitization** - All inputs are validated
- ✅ **Audit Logging** - Complete activity trail

## 🛠️ Technical Details

### Dependencies
```
edge-tts>=6.1.0      # Neural voice synthesis
pygame>=2.6.0        # Audio playback
pyyaml>=6.0          # Configuration parsing
```

### Audio Specifications
- **Format**: MP3 (compressed for efficiency)
- **Sample Rate**: 24kHz (high quality)
- **Bitrate**: Variable (optimized for speech)
- **Total Size**: ~2MB for all 12 files

### Performance
- **Startup Time**: <1 second
- **Playback Latency**: Instant
- **Memory Usage**: <50MB
- **Storage**: ~2MB total

## 🚨 Troubleshooting

### No Audio Output
```bash
# Check audio system
python -c "import pygame; pygame.mixer.init(); print('Audio OK')"

# Verify files exist
python skills/offline_voice_explain.py --list
```

### Missing Explanations
```bash
# Re-record all explanations
python skills/audio_pre_recorder.py --record

# Verify recordings
python skills/audio_pre_recorder.py --verify
```

### Skill Loading Issues
```bash
# Check allowed skills in config.yaml
python main.py config

# Test skill directly
python skills/security_coach.py list
```

## 🔄 Updates & Maintenance

### Adding New Content
1. Update explanations in `audio_pre_recorder.py`
2. Re-run recording: `python skills/audio_pre_recorder.py --record`
3. Test new content: `python skills/offline_voice_explain.py --list`

### Voice Customization
1. Edit voice settings in `skills/audio_config.json`
2. Re-record with new voices
3. Test voice quality

### Performance Optimization
- Use compressed audio formats
- Implement lazy loading for large libraries
- Cache frequently used explanations

## 📈 Future Enhancements

### Planned Features
- [ ] Multi-language support
- [ ] Dynamic content generation
- [ ] Interactive Q&A sessions
- [ ] Voice customization options
- [ ] Advanced threat intelligence

### Integration Opportunities
- [ ] Home automation systems
- [ ] Educational platforms
- [ ] Enterprise security training
- [ ] IoT device coaching

## 🤝 Contributing

### Adding New Risk Types
1. Update `explanations` dict in `audio_pre_recorder.py`
2. Add scenarios to `security_coach.py`
3. Update documentation
4. Test all age groups

### Voice Quality Improvements
1. Test different neural voices
2. Optimize audio parameters
3. Implement quality metrics
4. User feedback integration

---

**Guardian Node Voice System** - Privacy-first security coaching with neural voices.
Built for offline operation, optimized for Raspberry Pi 5, designed for families and small businesses.