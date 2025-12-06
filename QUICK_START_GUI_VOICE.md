# Guardian Node - GUI & Voice Quick Start

## 🚀 Quick Launch Commands

### GUI Interface
```bash
cd guardian_node_clean/guardian_interpreter
python main.py --gui
```

### CLI with Voice
```bash
cd guardian_node_clean/guardian_interpreter
python main.py --voice
```

### CLI Only (Default)
```bash
cd guardian_node_clean/guardian_interpreter
python main.py
```

---

## 🎤 Voice Commands (in CLI)

```bash
guardian-family> voice status          # Check voice availability
guardian-family> voice speak Hello     # Test text-to-speech
guardian-family> voice listen          # Listen and process voice input
```

---

## 📦 Quick Install

### Install All Dependencies
```bash
cd guardian_node_clean
pip install -r guardian_interpreter/requirements.txt
```

### Install GUI Only
```bash
pip install PySide6 psutil
```

### Install Voice Only
```bash
pip install pyttsx3 SpeechRecognition pocketsphinx
```

---

## 🧪 Quick Test

```bash
cd guardian_node_clean
python test_gui_voice_simple.py
```

Expected: Resource monitor and voice TTS should pass

---

## 🖥️ GUI Features

- **Mode Switching**: Kids / Teens / Adult protection levels
- **System Monitor**: Real-time CPU, memory, temperature
- **Security Scan**: One-click network security assessment
- **Voice Assistant**: Click to start voice interaction
- **Family Profiles**: Manage family member settings

---

## 🔧 Troubleshooting

### GUI Won't Launch
```bash
pip install PySide6
```

### Voice Not Working
```bash
pip install pyttsx3 SpeechRecognition pocketsphinx
```

### System Falls Back to CLI
This is normal! The system automatically uses CLI if GUI unavailable.

---

## 📚 Full Documentation

- `GUI_VOICE_COMPLETE.md` - Complete implementation details
- `TASK_5_COMPLETE.md` - Task completion summary
- `GUI_VOICE_GUIDE.md` - User guide

---

## ✅ What's Working

✅ Voice TTS (Text-to-Speech)
✅ Resource Monitoring
✅ CLI Interface
✅ Command Line Arguments
✅ Graceful Fallbacks

⏳ Voice STT (requires SpeechRecognition)
⏳ GUI (requires PySide6)

---

**Status**: Ready for testing!
**Next**: Install dependencies and launch GUI
