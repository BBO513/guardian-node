"""
Family Voice Interface for Guardian Node
Handles voice input/output for family-friendly interactions
"""

import os
import logging
import time
from typing import Dict, Any, Optional

class FamilyVoiceInterface:
    """
    Voice interface for family-friendly interactions
    Handles speech recognition and text-to-speech with privacy controls
    """
    
    def __init__(self, config: Dict[str, Any] = None, logger: logging.Logger = None, mock_mode: bool = False):
        self.config = config or {}
        self.logger = logger or logging.getLogger(__name__)
        self.voice_config = self._get_voice_config()
        self.privacy_mode = self.voice_config.get('privacy_mode', True)
        self.offline_mode = self.voice_config.get('offline_mode', True)
        self.mock_mode = mock_mode or self.voice_config.get('mock_mode', False)
        
        # Initialize speech components
        self._initialize_components()
    
    def _get_voice_config(self) -> Dict[str, Any]:
        """Get voice configuration from main config"""
        family_config = self.config.get('family_assistant', {})
        return family_config.get('voice_interface', {})
    
    def _initialize_components(self):
        """Initialize speech recognition and synthesis components"""
        try:
            # Import optional speech components
            import speech_recognition
            import pyttsx3
            
            self.recognizer = speech_recognition.Recognizer()
            self.engine = pyttsx3.init()
            
            # Configure TTS engine
            self.engine.setProperty('rate', self.voice_config.get('speech_rate', 150))
            self.engine.setProperty('volume', self.voice_config.get('volume', 0.8))
            
            # Set child-friendly voice if available
            if self.voice_config.get('child_friendly_voice', True):
                voices = self.engine.getProperty('voices')
                # Try to find a female voice which tends to be more soothing for children
                for voice in voices:
                    if "female" in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
            
            self.speech_components_available = True
            self.logger.info("Voice interface components initialized")
            
        except ImportError:
            self.speech_components_available = False
            self.logger.warning("Speech components not available. Install speech_recognition and pyttsx3.")
    
    def start_voice_session(self, family_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Start a voice interaction session
        
        Args:
            family_context: Family profile and context information
            
        Returns:
            Dict with session results
        """
        if not self.speech_components_available:
            self.logger.warning("Cannot start voice session - speech components not available")
            return {'success': False, 'error': 'Speech components not available'}
        
        try:
            # Determine age group from context
            age_group = self._get_age_group(family_context)
            
            # Speak welcome message
            welcome_message = self._get_welcome_message(age_group)
            self._speak(welcome_message)
            
            # Listen for command
            self.logger.info("Listening for voice command...")
            command = self._listen()
            
            if not command:
                self._speak("I'm sorry, I didn't hear anything.")
                return {'success': False, 'error': 'No speech detected'}
            
            # Process command
            self.logger.info(f"Processing command: {command}")
            
            # Get response based on age group
            response = self._get_response_for_command(command, age_group)
            
            # Speak response
            self._speak(response)
            
            return {
                'success': True,
                'command': command,
                'response': response,
                'age_group': age_group
            }
            
        except Exception as e:
            self.logger.error(f"Voice session error: {e}")
            self._speak("I'm sorry, there was a problem with the voice assistant.")
            return {'success': False, 'error': str(e)}
    
    def _get_age_group(self, family_context: Optional[Dict[str, Any]]) -> str:
        """Determine age group from family context"""
        if not family_context:
            return 'adult'
        
        members = family_context.get('members', [])
        if not members:
            return 'adult'
        
        # Use first member's age group
        return members[0].get('age_group', 'adult')
    
    def _get_welcome_message(self, age_group: str) -> str:
        """Get age-appropriate welcome message"""
        if age_group == 'child':
            return "Hi there! I'm your Guardian helper. What would you like to know about staying safe online?"
        elif age_group == 'teen':
            return "Hey! I'm your Guardian assistant. How can I help with your online security today?"
        else:
            return "Hello. I'm your Guardian security assistant. How may I help you?"
    
    def _listen(self) -> Optional[str]:
        """Listen for voice input"""
        # Use mock mode for testing without actual speech recognition
        if self.mock_mode:
            self.logger.info("Mock mode active. Simulating voice input.")
            import random
            mock_commands = [
                "How do I create a strong password?",
                "What should I do if someone asks for my personal information online?",
                "How can I stay safe on social media?",
                "What are parental controls?"
            ]
            return random.choice(mock_commands)
        
        try:
            # Import Microphone class
            from speech_recognition import Microphone
            
            with Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(
                    source,
                    timeout=self.voice_config.get('timeout', 5),
                    phrase_time_limit=self.voice_config.get('phrase_timeout', 5)
                )
            
            # Use offline recognition if configured
            if self.offline_mode:
                return self.recognizer.recognize_sphinx(audio)
            else:
                return self.recognizer.recognize_google(audio)
                
        except Exception as e:
            self.logger.error(f"Error listening: {e}")
            return None
    
    def _speak(self, text: str):
        """Convert text to speech"""
        if self.privacy_mode:
            self.logger.info(f"Privacy mode active. Would speak: {text}")
            # In privacy mode, log but don't actually speak
            return
            
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            self.logger.error(f"Error speaking: {e}")
    
    def _get_response_for_command(self, command: str, age_group: str) -> str:
        """
        Get response for voice command
        
        In a real implementation, this would integrate with the family assistant manager
        For now, we'll use simple pattern matching for demo purposes
        """
        command_lower = command.lower()
        
        # Child-appropriate responses
        if age_group == 'child':
            if any(word in command_lower for word in ['password', 'passwords']):
                return "Passwords are like secret codes that keep your information safe. It's important to use different passwords for different places and never share them with anyone except your parents."
                
            elif any(word in command_lower for word in ['internet', 'online', 'web']):
                return "The internet is a place where we can learn and have fun, but we need to be careful. Always ask a grown-up before clicking on things or talking to people online."
                
            elif any(word in command_lower for word in ['stranger', 'strangers']):
                return "Remember, never talk to strangers online or share your personal information. If someone you don't know tries to talk to you, tell a grown-up right away."
                
            else:
                return "That's a great question! Let's ask a grown-up to help us learn more about staying safe online."
        
        # Teen-appropriate responses
        elif age_group == 'teen':
            if any(word in command_lower for word in ['password', 'passwords']):
                return "Strong passwords are essential for online security. Use a mix of letters, numbers, and symbols, and consider using a password manager to keep track of different passwords for different sites."
                
            elif any(word in command_lower for word in ['social', 'media', 'instagram', 'tiktok']):
                return "On social media, be careful about what you share. Check your privacy settings regularly, and remember that anything you post might be seen by more people than you intended."
                
            elif any(word in command_lower for word in ['privacy', 'private']):
                return "Protecting your privacy online is important. Regularly review app permissions, use private browsing when needed, and be thoughtful about the information you share online."
                
            else:
                return "That's a good question about online security. I can help you find more information about staying safe online."
        
        # Adult responses
        else:
            if any(word in command_lower for word in ['password', 'passwords']):
                return "Password security is critical. Use strong, unique passwords for each account, enable two-factor authentication where available, and consider using a reputable password manager."
                
            elif any(word in command_lower for word in ['network', 'wifi']):
                return "To secure your home network, use WPA3 encryption if available, change default router credentials, keep firmware updated, and consider setting up a guest network for visitors."
                
            elif any(word in command_lower for word in ['child', 'children', 'kids']):
                return "For child online safety, use parental controls, maintain open communication about online activities, set clear boundaries, and educate children about potential online risks in an age-appropriate way."
                
            else:
                return "I understand you're asking about cybersecurity. Could you provide more specific details about what you'd like to know?"

# For testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("voice_test")
    
    voice = FamilyVoiceInterface(logger=logger)
    
    # Test with different family contexts
    contexts = [
        {'members': [{'name': 'Child', 'age_group': 'child'}]},
        {'members': [{'name': 'Teen', 'age_group': 'teen'}]},
        {'members': [{'name': 'Parent', 'age_group': 'adult'}]}
    ]
    
    for context in contexts:
        print(f"\nTesting with context: {context}")
        result = voice.start_voice_session(context)
        print(f"Result: {result}")
        time.sleep(1)  # Pause between tests