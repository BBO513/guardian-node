# Guardian Node

Minimal offline AI guardian for Raspberry Pi with voice interface.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure:**
   - Edit `config.yaml` to set your model path and preferences

3. **Run:**
   ```bash
   python main.py
   ```

## Voice System

The voice module provides offline speech recognition and text-to-speech using:
- **Input:** Vosk (offline speech recognition)
- **Output:** pyttsx3 (offline TTS)

## Files

- `main.py` - Main application
- `voice/` - Voice interface modules
- `skills/` - Skill modules
- `config.yaml` - Configuration
- `requirements.txt` - Python dependencies

## Commands

- `nodie <prompt>` - Ask the LLM
- `skill <name>` - Call a skill
- `skills` - List available skills
- `exit` - Quit

## License

MIT
