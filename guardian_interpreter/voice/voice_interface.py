"""
Voice Interface Module for Guardian Node
Handles offline speech-to-text (STT) and text-to-speech (TTS)
"""

import logging
import os
from typing import Dict, Any, Optional

# TODO: For full offline voice implementation, install:
# - pyttsx3 for offline text-to-speech
# - SpeechRecognition with pocketsphinx for offline speech recognition
# Install with: pip install pyttsx3 SpeechRecognition pocketsphinx

# Try to import voice libraries
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

try:
    import speech_recognition as sr
    STT_AVAILABLE = True
except ImportError:
    STT_AVAILABLE = False

# Piper (neural, offline) is the preferred TTS engine; pyttsx3 is the fallback.
try:
    from piper import PiperVoice
    PIPER_AVAILABLE = True
except Exception:
    PiperVoice = None
    PIPER_AVAILABLE = False

PIPER_VOICE_NAME = os.environ.get("PIPER_VOICE_NAME", "en_US-lessac-medium")


def _piper_voice_dir() -> str:
    """Directory holding the bundled Piper voice model (works source + frozen)."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "piper_voices")


def _play_wav(wav_path: str) -> bool:
    """Play a WAV file using the best available backend (Windows-first)."""
    try:
        import winsound
        winsound.PlaySound(wav_path, winsound.SND_FILENAME)
        return True
    except Exception:
        pass
    # Linux (Pi): play through PipeWire/PulseAudio, which resamples to whatever the device
    # supports (USB headsets are often 48 kHz only; Piper voices are 22.05 kHz).
    import shutil
    import subprocess
    for player in (["pw-play"], ["paplay"]):
        if shutil.which(player[0]):
            try:
                return subprocess.run(player + [wav_path], timeout=120).returncode == 0
            except Exception:
                pass
    try:
        import numpy as np
        import sounddevice as sd
        import wave as _wave
        with _wave.open(wav_path, "rb") as wf:
            data = wf.readframes(wf.getnframes())
            rate = wf.getframerate()
            width = wf.getsampwidth()
        dtype = {1: np.int8, 2: np.int16, 4: np.int32}.get(width, np.int16)
        sd.play(np.frombuffer(data, dtype=dtype), samplerate=rate)
        sd.wait()
        return True
    except Exception:
        return False


def _voice_log(msg: str) -> None:
    """Append a status line to a log file (windowed apps have no stderr)."""
    try:
        log_path = os.path.join(os.environ.get("TEMP", os.path.expanduser("~")), "guardian_voice.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass


class VoiceInterface:
    """
    Offline voice interface for Guardian Node
    
    TODO: Full implementation requires:
    1. Offline speech recognition (pocketsphinx or vosk)
    2. Offline text-to-speech (pyttsx3 or festival)
    3. Wake word detection for hands-free operation
    4. Voice activity detection
    5. Noise cancellation
    """
    
    def __init__(self, config: Dict[str, Any] = None, logger: logging.Logger = None):
        """
        Initialize voice interface
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config or {}
        self.logger = logger or logging.getLogger(__name__)
        self.voice_config = self.config.get('voice', {})
        
        # Initialize components
        self.tts_engine = None
        self.piper_voice = None
        self.recognizer = None
        
        self._initialize_tts()
        self._initialize_stt()
    
    def _initialize_tts(self):
        """
        Initialize text-to-speech engine.

        Prefers Piper (neural, offline); falls back to pyttsx3 (SAPI5) if Piper
        or its voice model is unavailable.
        """
        if PIPER_AVAILABLE:
            try:
                model = os.path.join(_piper_voice_dir(), PIPER_VOICE_NAME + ".onnx")
                config = model + ".json"
                if not os.path.exists(model):
                    raise FileNotFoundError(f"Piper voice model not found: {model}")
                self.logger.info(f"Loading Piper voice: {PIPER_VOICE_NAME}")
                self.piper_voice = PiperVoice.load(model, config_path=config)
                self.logger.info("Piper TTS initialized successfully")
                _voice_log(f"TTS engine: piper ({PIPER_VOICE_NAME})")
                return
            except Exception as e:
                self.logger.warning(f"Piper TTS unavailable, falling back to pyttsx3: {e}")
                _voice_log(f"Piper TTS failed: {e}")
                self.piper_voice = None

        if not TTS_AVAILABLE:
            self.logger.warning("pyttsx3 not available. Install with: pip install pyttsx3")
            return
        
        try:
            self.tts_engine = pyttsx3.init()
            
            # Configure TTS settings
            rate = self.voice_config.get('speech_rate', 150)
            volume = self.voice_config.get('volume', 0.9)
            
            self.tts_engine.setProperty('rate', rate)
            self.tts_engine.setProperty('volume', volume)
            
            # Select voice if configured
            voice_id = self.voice_config.get('voice_id')
            if voice_id:
                self.tts_engine.setProperty('voice', voice_id)
            
            self.logger.info("Text-to-speech initialized successfully")
            _voice_log("TTS engine: pyttsx3")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize TTS: {e}")
            self.tts_engine = None
    
    def _initialize_stt(self):
        """
        Initialize speech-to-text engine
        
        TODO: Full offline STT implementation:
        1. Initialize pocketsphinx or vosk for offline recognition
        2. Load language models
        3. Configure acoustic models
        4. Set up microphone input
        """
        if not STT_AVAILABLE:
            self.logger.warning("SpeechRecognition not available. Install with: pip install SpeechRecognition pocketsphinx")
            return
        
        try:
            self.recognizer = sr.Recognizer()
            
            # Configure recognition parameters
            self.recognizer.energy_threshold = self.voice_config.get('energy_threshold', 4000)
            self.recognizer.pause_threshold = self.voice_config.get('pause_threshold', 0.8)
            
            self.logger.info("Speech-to-text initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize STT: {e}")
            self.recognizer = None
    
    def speak(self, text: str) -> bool:
        """
        Convert text to speech
        
        Args:
            text: Text to speak
            
        Returns:
            True if successful, False otherwise
        """
        if not text or not text.strip():
            return False

        if getattr(self, "piper_voice", None):
            return self._speak_piper(text)

        if not self.tts_engine:
            self.logger.warning(f"TTS not available. Would speak: {text}")
            return False
        
        try:
            self.logger.info(f"Speaking: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to speak: {e}")
            return False

    def _speak_piper(self, text: str) -> bool:
        """Synthesize with Piper and play the resulting WAV."""
        import wave as _wave
        import tempfile as _tempfile

        wav_path = None
        try:
            fd, wav_path = _tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            self.logger.info(f"Speaking (Piper): {text}")
            with _wave.open(wav_path, "wb") as wav_file:
                self.piper_voice.synthesize_wav(text, wav_file)
            return _play_wav(wav_path)
        except Exception as e:
            self.logger.error(f"Failed to speak (Piper): {e}")
            return False
        finally:
            if wav_path and os.path.exists(wav_path):
                try:
                    os.unlink(wav_path)
                except OSError:
                    pass
    
    def listen(self, timeout: int = 5, phrase_time_limit: int = 10) -> Optional[str]:
        """
        Listen for speech input
        
        Args:
            timeout: Seconds to wait for speech to start
            phrase_time_limit: Maximum seconds for the phrase
            
        Returns:
            Recognized text or None if failed
            
        TODO: Full offline STT implementation:
        1. Use pocketsphinx for offline recognition
        2. Implement wake word detection
        3. Add voice activity detection
        4. Support continuous recognition
        """
        if not self.recognizer:
            self.logger.warning("STT not available. Cannot listen.")
            return None
        
        try:
            # Check if microphone is available
            if not STT_AVAILABLE:
                return None
            
            with sr.Microphone() as source:
                self.logger.info("Listening...")
                
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Listen for speech
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                
                self.logger.info("Processing speech...")
                
                # Try offline recognition first (pocketsphinx)
                try:
                    text = self.recognizer.recognize_sphinx(audio)
                    self.logger.info(f"Recognized (offline): {text}")
                    return text
                except:
                    self.logger.warning("Offline recognition not available or failed")
                    return None
                
        except sr.WaitTimeoutError:
            self.logger.warning("No speech detected within timeout")
            return None
        except Exception as e:
            self.logger.error(f"Failed to listen: {e}")
            return None
    
    def get_available_voices(self) -> list:
        """
        Get list of available TTS voices
        
        Returns:
            List of available voice IDs and names
        """
        voices = []
        if getattr(self, "piper_voice", None):
            voices.append({
                'id': PIPER_VOICE_NAME,
                'name': PIPER_VOICE_NAME,
                'languages': ['en-US']
            })
        if self.tts_engine:
            try:
                voices += [
                    {'id': voice.id, 'name': voice.name, 'languages': voice.languages}
                    for voice in self.tts_engine.getProperty('voices')
                ]
            except Exception as e:
                self.logger.error(f"Failed to get voices: {e}")
        return voices
    
    def test_voice_interface(self):
        """
        Test the voice interface
        """
        self.logger.info("Testing voice interface...")
        
        # Test TTS
        if self.tts_engine or getattr(self, "piper_voice", None):
            self.speak("Guardian Node voice interface test. Text to speech is working.")
        else:
            self.logger.warning("TTS not available for testing")
        
        # Test STT
        if self.recognizer:
            self.logger.info("Please say something to test speech recognition...")
            result = self.listen(timeout=5)
            if result:
                self.logger.info(f"STT Test successful. Recognized: {result}")
            else:
                self.logger.warning("STT test failed or no speech detected")
        else:
            self.logger.warning("STT not available for testing")


# For testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("voice_interface_test")
    
    voice = VoiceInterface(logger=logger)
    
    # Show available voices
    print("\n=== Available Voices ===")
    voices = voice.get_available_voices()
    for voice_info in voices[:5]:  # Show first 5
        print(f"- {voice_info['name']} ({voice_info['id']})")
    
    # Test TTS
    print("\n=== Testing Text-to-Speech ===")
    voice.speak("Hello! This is the Guardian Node voice interface.")
    
    # Test full interface
    print("\n=== Full Voice Interface Test ===")
    voice.test_voice_interface()
