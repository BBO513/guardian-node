"""
Voice Output Module for Guardian Node Family Assistant
Handles text-to-speech synthesis with offline and online options
"""

import logging
import threading
import time
from typing import Optional, Dict, Any, List
from pathlib import Path

# Try to import text-to-speech libraries
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

class VoiceOutput:
    """
    Voice output handler with multiple TTS backends
    Supports offline text-to-speech synthesis
    """
    
    def __init__(self, config: Dict[str, Any] = None, logger: logging.Logger = None):
        self.config = config or {}
        self.logger = logger or logging.getLogger(__name__)
        
        # Voice output settings
        self.voice_config = self.config.get('voice_output', {})
        self.rate = self.voice_config.get('speech_rate', 150)  # Words per minute
        self.volume = self.voice_config.get('volume', 0.8)  # 0.0 to 1.0
        self.voice_id = self.voice_config.get('voice_id', None)  # Specific voice
        
        # Family-friendly settings
        self.family_mode = self.voice_config.get('family_mode', True)
        self.child_friendly_voice = self.voice_config.get('child_friendly_voice', True)
        
        # Initialize TTS engine
        self.tts_engine = None
        self.engine_lock = threading.Lock()
        self._initialize_tts_engine()
        
        # Privacy settings
        self.log_speech = self.voice_config.get('log_speech', False)
        
        self.logger.info("VoiceOutput initialized")
    
    def _initialize_tts_engine(self):
        """Initialize text-to-speech engine"""
        if not PYTTSX3_AVAILABLE:
            self.logger.warning("Text-to-speech not available - install pyttsx3 package")
            return
        
        try:
            self.tts_engine = pyttsx3.init()
            
            # Configure TTS settings
            self.tts_engine.setProperty('rate', self.rate)
            self.tts_engine.setProperty('volume', self.volume)
            
            # Set voice if specified
            if self.voice_id or self.child_friendly_voice:
                self._configure_voice()
            
            self.logger.info("TTS engine initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize TTS engine: {e}")
            self.tts_engine = None
    
    def _configure_voice(self):
        """Configure voice settings for family-friendly output"""
        try:
            voices = self.tts_engine.getProperty('voices')
            
            if not voices:
                self.logger.warning("No voices available for TTS")
                return
            
            # If specific voice ID provided, use it
            if self.voice_id:
                for voice in voices:
                    if self.voice_id in voice.id:
                        self.tts_engine.setProperty('voice', voice.id)
                        self.logger.info(f"Set voice to: {voice.name}")
                        return
            
            # Otherwise, try to find a family-friendly voice
            if self.child_friendly_voice:
                # Prefer female voices for family assistant (often perceived as more friendly)
                female_voices = [v for v in voices if 'female' in v.name.lower() or 'woman' in v.name.lower()]
                if female_voices:
                    self.tts_engine.setProperty('voice', female_voices[0].id)
                    self.logger.info(f"Set family-friendly voice: {female_voices[0].name}")
                    return
                
                # Fallback to any available voice
                if voices:
                    self.tts_engine.setProperty('voice', voices[0].id)
                    self.logger.info(f"Set default voice: {voices[0].name}")
            
        except Exception as e:
            self.logger.error(f"Error configuring voice: {e}")
    
    def is_available(self) -> bool:
        """Check if voice output is available"""
        return PYTTSX3_AVAILABLE and self.tts_engine is not None
    
    def speak_text(self, text: str, wait: bool = True, priority: str = "normal") -> bool:
        """
        Speak the given text
        
        Args:
            text: Text to speak
            wait: Whether to wait for speech to complete
            priority: Priority level ("low", "normal", "high")
            
        Returns:
            True if speech was initiated successfully
        """
        if not self.is_available():
            self.logger.warning("TTS not available - cannot speak text")
            return False
        
        if not text or not text.strip():
            return False
        
        try:
            # Log speech request (respecting privacy settings)
            if self.log_speech:
                self.logger.info(f"Speaking: {text}")
            else:
                self.logger.info(f"Speaking text (length: {len(text)} chars)")
            
            # Format text for family-friendly speech
            formatted_text = self._format_for_speech(text)
            
            with self.engine_lock:
                # Clear any pending speech
                if priority == "high":
                    self.tts_engine.stop()
                
                # Speak the text
                self.tts_engine.say(formatted_text)
                
                if wait:
                    self.tts_engine.runAndWait()
                else:
                    # Start speech in background thread
                    threading.Thread(target=self.tts_engine.runAndWait, daemon=True).start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error speaking text: {e}")
            return False
    
    def speak_family_response(self, response: str, context: Dict[str, Any] = None) -> bool:
        """
        Speak a family assistant response with appropriate formatting
        
        Args:
            response: Response text to speak
            context: Context including family member info, urgency, etc.
            
        Returns:
            True if speech was initiated successfully
        """
        if not response:
            return False
        
        # Add family-friendly greeting if appropriate
        context = context or {}
        member_name = context.get('member_name')
        urgency = context.get('urgency', 'normal')
        
        # Format response for family context
        if member_name and self.family_mode:
            formatted_response = f"Hi {member_name}! {response}"
        else:
            formatted_response = response
        
        # Determine priority based on urgency
        priority = "high" if urgency == "critical" else "normal"
        
        return self.speak_text(formatted_response, wait=True, priority=priority)
    
    def speak_security_alert(self, alert: str, severity: str = "medium") -> bool:
        """
        Speak a security alert with appropriate urgency
        
        Args:
            alert: Alert message
            severity: Severity level ("low", "medium", "high", "critical")
            
        Returns:
            True if speech was initiated successfully
        """
        # Format alert based on severity
        if severity == "critical":
            formatted_alert = f"Important security alert: {alert}"
            priority = "high"
        elif severity == "high":
            formatted_alert = f"Security notice: {alert}"
            priority = "high"
        else:
            formatted_alert = f"Security tip: {alert}"
            priority = "normal"
        
        return self.speak_text(formatted_alert, wait=True, priority=priority)
    
    def _format_for_speech(self, text: str) -> str:
        """
        Format text for better speech synthesis
        
        Args:
            text: Original text
            
        Returns:
            Formatted text optimized for speech
        """
        # Remove or replace problematic characters/patterns
        formatted = text.replace("&", "and")
        formatted = formatted.replace("@", "at")
        formatted = formatted.replace("#", "number")
        formatted = formatted.replace("%", "percent")
        formatted = formatted.replace("$", "dollars")
        
        # Add pauses for better speech flow
        formatted = formatted.replace(". ", ". ... ")
        formatted = formatted.replace("! ", "! ... ")
        formatted = formatted.replace("? ", "? ... ")
        
        # Handle technical terms for family-friendly speech
        if self.family_mode:
            formatted = self._simplify_technical_terms(formatted)
        
        return formatted
    
    def _simplify_technical_terms(self, text: str) -> str:
        """
        Simplify technical terms for family-friendly speech
        
        Args:
            text: Text with technical terms
            
        Returns:
            Text with simplified terms
        """
        # Common technical term replacements
        replacements = {
            "WiFi": "Wi-Fi",
            "IoT": "Internet of Things",
            "VPN": "Virtual Private Network",
            "2FA": "Two Factor Authentication",
            "URL": "web address",
            "IP address": "internet address",
            "malware": "harmful software",
            "phishing": "fake email scam",
            "ransomware": "file-locking virus",
            "firewall": "security barrier"
        }
        
        formatted = text
        for technical, simple in replacements.items():
            formatted = formatted.replace(technical, simple)
        
        return formatted
    
    def stop_speech(self) -> bool:
        """Stop current speech"""
        if not self.is_available():
            return False
        
        try:
            with self.engine_lock:
                self.tts_engine.stop()
            return True
        except Exception as e:
            self.logger.error(f"Error stopping speech: {e}")
            return False
    
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get list of available voices"""
        if not self.is_available():
            return []
        
        try:
            voices = self.tts_engine.getProperty('voices')
            voice_list = []
            
            for voice in voices:
                voice_info = {
                    'id': voice.id,
                    'name': voice.name,
                    'languages': getattr(voice, 'languages', []),
                    'gender': getattr(voice, 'gender', 'unknown'),
                    'age': getattr(voice, 'age', 'unknown')
                }
                voice_list.append(voice_info)
            
            return voice_list
            
        except Exception as e:
            self.logger.error(f"Error getting available voices: {e}")
            return []
    
    def set_voice_settings(self, rate: Optional[int] = None, 
                          volume: Optional[float] = None,
                          voice_id: Optional[str] = None) -> bool:
        """
        Update voice settings
        
        Args:
            rate: Speech rate (words per minute)
            volume: Volume level (0.0 to 1.0)
            voice_id: Voice identifier
            
        Returns:
            True if settings were updated successfully
        """
        if not self.is_available():
            return False
        
        try:
            with self.engine_lock:
                if rate is not None:
                    self.tts_engine.setProperty('rate', rate)
                    self.rate = rate
                
                if volume is not None:
                    self.tts_engine.setProperty('volume', volume)
                    self.volume = volume
                
                if voice_id is not None:
                    voices = self.tts_engine.getProperty('voices')
                    for voice in voices:
                        if voice_id in voice.id:
                            self.tts_engine.setProperty('voice', voice.id)
                            self.voice_id = voice_id
                            break
            
            self.logger.info("Voice settings updated")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating voice settings: {e}")
            return False

# Convenience function for simple usage
def speak_text(text: str, config: Dict[str, Any] = None, 
               logger: logging.Logger = None, wait: bool = True) -> bool:
    """
    Simple text-to-speech function
    
    Args:
        text: Text to speak
        config: Voice configuration
        logger: Logger instance
        wait: Whether to wait for speech to complete
        
    Returns:
        True if speech was initiated successfully
    """
    voice_output = VoiceOutput(config, logger)
    return voice_output.speak_text(text, wait=wait)