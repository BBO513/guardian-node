"""
Voice Input Module for Guardian Node Family Assistant
Handles speech recognition with offline and online options
"""

import logging
import time
from typing import Optional, Dict, Any
from pathlib import Path

# Try to import speech recognition libraries
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False

class VoiceInput:
    """
    Voice input handler with multiple recognition backends
    Supports both online and offline speech recognition
    """
    
    def __init__(self, config: Dict[str, Any] = None, logger: logging.Logger = None):
        self.config = config or {}
        self.logger = logger or logging.getLogger(__name__)
        
        # Voice input settings
        self.voice_config = self.config.get('voice_input', {})
        self.timeout = self.voice_config.get('timeout', 5)
        self.phrase_timeout = self.voice_config.get('phrase_timeout', 1)
        self.energy_threshold = self.voice_config.get('energy_threshold', 300)
        self.offline_mode = self.voice_config.get('offline_mode', True)
        
        # Initialize recognizer
        self.recognizer = None
        self.microphone = None
        self._initialize_recognizer()
        
        # Privacy and security settings
        self.voice_privacy_mode = self.voice_config.get('privacy_mode', True)
        self.log_audio = self.voice_config.get('log_audio', False)
        
        self.logger.info(f"VoiceInput initialized - Offline mode: {self.offline_mode}")
    
    def _initialize_recognizer(self):
        """Initialize speech recognizer and microphone"""
        if not SPEECH_RECOGNITION_AVAILABLE:
            self.logger.warning("Speech recognition not available - install speechrecognition package")
            return
        
        try:
            self.recognizer = sr.Recognizer()
            
            # Configure recognizer settings
            self.recognizer.energy_threshold = self.energy_threshold
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            self.recognizer.phrase_threshold = 0.3
            
            # Initialize microphone
            self.microphone = sr.Microphone()
            
            # Calibrate for ambient noise
            with self.microphone as source:
                self.logger.info("Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            self.logger.info("Voice recognizer initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize voice recognizer: {e}")
            self.recognizer = None
            self.microphone = None
    
    def is_available(self) -> bool:
        """Check if voice input is available"""
        return SPEECH_RECOGNITION_AVAILABLE and self.recognizer is not None
    
    def recognize_speech(self, timeout: Optional[int] = None, 
                        phrase_timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Recognize speech from microphone
        
        Args:
            timeout: Maximum time to wait for speech (seconds)
            phrase_timeout: Maximum time to wait for phrase completion (seconds)
            
        Returns:
            Dict with recognition result, confidence, and metadata
        """
        if not self.is_available():
            return {
                'success': False,
                'text': '',
                'confidence': 0.0,
                'error': 'Voice recognition not available',
                'method': 'none'
            }
        
        timeout = timeout or self.timeout
        phrase_timeout = phrase_timeout or self.phrase_timeout
        
        try:
            self.logger.info("Listening for speech...")
            
            with self.microphone as source:
                # Listen for audio with timeout
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_timeout
                )
            
            # Try offline recognition first if enabled
            if self.offline_mode:
                result = self._recognize_offline(audio)
                if result['success']:
                    return result
                else:
                    self.logger.info("Offline recognition failed, trying online...")
            
            # Try online recognition as fallback
            return self._recognize_online(audio)
            
        except sr.WaitTimeoutError:
            self.logger.info("Speech recognition timeout - no speech detected")
            return {
                'success': False,
                'text': '',
                'confidence': 0.0,
                'error': 'No speech detected within timeout',
                'method': 'timeout'
            }
        except Exception as e:
            self.logger.error(f"Speech recognition error: {e}")
            return {
                'success': False,
                'text': '',
                'confidence': 0.0,
                'error': str(e),
                'method': 'error'
            }
    
    def _recognize_offline(self, audio) -> Dict[str, Any]:
        """
        Attempt offline speech recognition
        Uses various offline engines like Vosk, PocketSphinx, etc.
        """
        try:
            # Try PocketSphinx (offline)
            text = self.recognizer.recognize_sphinx(audio)
            
            if not self.log_audio and self.voice_privacy_mode:
                self.logger.info("Speech recognized offline (content not logged for privacy)")
            else:
                self.logger.info(f"Offline recognition result: {text}")
            
            return {
                'success': True,
                'text': text,
                'confidence': 0.7,  # PocketSphinx doesn't provide confidence
                'error': None,
                'method': 'offline_sphinx'
            }
            
        except sr.UnknownValueError:
            return {
                'success': False,
                'text': '',
                'confidence': 0.0,
                'error': 'Could not understand audio (offline)',
                'method': 'offline_sphinx'
            }
        except sr.RequestError as e:
            return {
                'success': False,
                'text': '',
                'confidence': 0.0,
                'error': f'Offline recognition error: {e}',
                'method': 'offline_sphinx'
            }
        except Exception as e:
            return {
                'success': False,
                'text': '',
                'confidence': 0.0,
                'error': f'Offline recognition not available: {e}',
                'method': 'offline_sphinx'
            }
    
    def _recognize_online(self, audio) -> Dict[str, Any]:
        """
        Attempt online speech recognition (only if offline fails and allowed)
        """
        # Check if online recognition is allowed
        if self.voice_config.get('block_online', True):
            return {
                'success': False,
                'text': '',
                'confidence': 0.0,
                'error': 'Online recognition blocked for privacy',
                'method': 'blocked'
            }
        
        try:
            # Use Google Speech Recognition (requires internet)
            text = self.recognizer.recognize_google(audio)
            
            if not self.log_audio and self.voice_privacy_mode:
                self.logger.info("Speech recognized online (content not logged for privacy)")
            else:
                self.logger.info(f"Online recognition result: {text}")
            
            return {
                'success': True,
                'text': text,
                'confidence': 0.9,  # Google typically has high accuracy
                'error': None,
                'method': 'online_google'
            }
            
        except sr.UnknownValueError:
            return {
                'success': False,
                'text': '',
                'confidence': 0.0,
                'error': 'Could not understand audio (online)',
                'method': 'online_google'
            }
        except sr.RequestError as e:
            return {
                'success': False,
                'text': '',
                'confidence': 0.0,
                'error': f'Online recognition error: {e}',
                'method': 'online_google'
            }
    
    def test_microphone(self) -> Dict[str, Any]:
        """Test microphone functionality"""
        if not self.is_available():
            return {
                'success': False,
                'error': 'Voice recognition not available'
            }
        
        try:
            with self.microphone as source:
                self.logger.info("Testing microphone - speak now...")
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=2)
            
            return {
                'success': True,
                'audio_length': len(audio.frame_data),
                'sample_rate': audio.sample_rate,
                'sample_width': audio.sample_width
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_microphone_info(self) -> Dict[str, Any]:
        """Get information about available microphones"""
        if not SPEECH_RECOGNITION_AVAILABLE:
            return {'error': 'Speech recognition not available'}
        
        try:
            mic_list = sr.Microphone.list_microphone_names()
            return {
                'available_microphones': mic_list,
                'default_microphone': mic_list[0] if mic_list else None,
                'total_count': len(mic_list)
            }
        except Exception as e:
            return {'error': str(e)}

# Convenience function for simple usage
def recognize_speech(timeout: int = 5, config: Dict[str, Any] = None, 
                    logger: logging.Logger = None) -> str:
    """
    Simple speech recognition function
    
    Args:
        timeout: Maximum time to wait for speech
        config: Voice configuration
        logger: Logger instance
        
    Returns:
        Recognized text or empty string if failed
    """
    voice_input = VoiceInput(config, logger)
    result = voice_input.recognize_speech(timeout=timeout)
    
    if result['success']:
        return result['text']
    else:
        if logger:
            logger.warning(f"Speech recognition failed: {result['error']}")
        return ""