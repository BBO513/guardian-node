"""
Voice Interface Module for Guardian Node
Handles offline speech-to-text (STT) and text-to-speech (TTS)
"""

import logging
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
        self.recognizer = None
        
        self._initialize_tts()
        self._initialize_stt()
    
    def _initialize_tts(self):
        """
        Initialize text-to-speech engine
        
        TODO: Full offline TTS implementation:
        1. Initialize pyttsx3 with offline voices
        2. Configure voice parameters (rate, volume, pitch)
        3. Support multiple languages
        4. Cache commonly used phrases
        """
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
        if not self.tts_engine:
            return []
        
        try:
            voices = self.tts_engine.getProperty('voices')
            return [
                {
                    'id': voice.id,
                    'name': voice.name,
                    'languages': voice.languages
                }
                for voice in voices
            ]
        except Exception as e:
            self.logger.error(f"Failed to get voices: {e}")
            return []
    
    def test_voice_interface(self):
        """
        Test the voice interface
        """
        self.logger.info("Testing voice interface...")
        
        # Test TTS
        if self.tts_engine:
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
