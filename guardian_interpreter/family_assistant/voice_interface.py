"""
Voice Interface for Guardian Node Family Assistant
Integrates voice input/output with family cybersecurity assistance
"""

import logging
import threading
import time
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime

# Import voice components
from ..voice.voice_input import VoiceInput
from ..voice.voice_output import VoiceOutput
from .family_assistant_manager import FamilyAssistantManager

class FamilyVoiceInterface:
    """
    Voice interface for family cybersecurity assistance
    Handles voice commands and provides spoken responses
    """
    
    def __init__(self, config: Dict[str, Any] = None, logger: logging.Logger = None,
                 family_manager: FamilyAssistantManager = None):
        self.config = config or {}
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize voice components
        self.voice_input = VoiceInput(config, logger)
        self.voice_output = VoiceOutput(config, logger)
        
        # Initialize family assistant manager
        self.family_manager = family_manager or FamilyAssistantManager(config, logger)
        
        # Voice interface settings
        self.voice_config = self.config.get('voice_interface', {})
        self.wake_word = self.voice_config.get('wake_word', 'guardian')
        self.session_timeout = self.voice_config.get('session_timeout', 30)
        self.max_retries = self.voice_config.get('max_retries', 3)
        
        # Session management
        self.active_session = False
        self.session_start_time = None
        self.session_lock = threading.Lock()
        
        # Command mapping
        self.command_mappings = self._initialize_command_mappings()
        
        # Privacy and security
        self.voice_privacy_mode = self.voice_config.get('privacy_mode', True)
        self.require_confirmation = self.voice_config.get('require_confirmation', True)
        
        self.logger.info("FamilyVoiceInterface initialized")
    
    def _initialize_command_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Initialize voice command mappings to family assistant functions"""
        return {
            # Cybersecurity education commands
            'cyber safety': {
                'skill': 'child_education_skill',
                'description': 'Cybersecurity education for children',
                'confirmation_required': False
            },
            'teach kids': {
                'skill': 'child_education_skill', 
                'description': 'Child cybersecurity education',
                'confirmation_required': False
            },
            'online safety': {
                'skill': 'child_education_skill',
                'description': 'Online safety guidance',
                'confirmation_required': False
            },
            
            # Device security commands
            'device security': {
                'skill': 'device_guidance_skill',
                'description': 'Device security guidance',
                'confirmation_required': False
            },
            'phone security': {
                'skill': 'device_guidance_skill',
                'args': ['smartphone'],
                'description': 'Smartphone security guidance',
                'confirmation_required': False
            },
            'tablet security': {
                'skill': 'device_guidance_skill',
                'args': ['tablet'],
                'description': 'Tablet security guidance',
                'confirmation_required': False
            },
            
            # Threat analysis commands
            'current threats': {
                'skill': 'threat_analysis_skill',
                'description': 'Current cybersecurity threats',
                'confirmation_required': False
            },
            'security threats': {
                'skill': 'threat_analysis_skill',
                'description': 'Security threat analysis',
                'confirmation_required': False
            },
            
            # General family assistance
            'family security': {
                'skill': 'family_cyber_skills',
                'description': 'General family cybersecurity assistance',
                'confirmation_required': False
            },
            'security help': {
                'skill': 'family_cyber_skills',
                'description': 'General security help',
                'confirmation_required': False
            },
            
            # System commands
            'security scan': {
                'function': 'run_security_scan',
                'description': 'Run family security analysis',
                'confirmation_required': True
            },
            'family status': {
                'function': 'get_family_status',
                'description': 'Get family security status',
                'confirmation_required': False
            }
        }
    
    def is_available(self) -> bool:
        """Check if voice interface is available"""
        return self.voice_input.is_available() and self.voice_output.is_available()
    
    def start_voice_session(self, family_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Start an interactive voice session
        
        Args:
            family_context: Family context including member info, preferences
            
        Returns:
            Session result with success status and details
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'Voice interface not available',
                'message': 'Please check microphone and speaker setup'
            }
        
        with self.session_lock:
            if self.active_session:
                return {
                    'success': False,
                    'error': 'Voice session already active',
                    'message': 'Please wait for current session to complete'
                }
            
            self.active_session = True
            self.session_start_time = datetime.now()
        
        try:
            # Welcome message
            welcome_msg = self._get_welcome_message(family_context)
            self.voice_output.speak_family_response(welcome_msg, family_context)
            
            # Main interaction loop
            session_result = self._run_voice_interaction_loop(family_context)
            
            # Goodbye message
            goodbye_msg = "Thank you for using Guardian Family Assistant. Stay safe online!"
            self.voice_output.speak_family_response(goodbye_msg, family_context)
            
            return session_result
            
        except Exception as e:
            self.logger.error(f"Voice session error: {e}")
            error_msg = "I'm sorry, I encountered an error. Please try again later."
            self.voice_output.speak_text(error_msg)
            
            return {
                'success': False,
                'error': str(e),
                'message': 'Voice session failed'
            }
        
        finally:
            with self.session_lock:
                self.active_session = False
                self.session_start_time = None
    
    def _run_voice_interaction_loop(self, family_context: Dict[str, Any]) -> Dict[str, Any]:
        """Run the main voice interaction loop"""
        interactions = []
        retry_count = 0
        
        while retry_count < self.max_retries:
            # Check session timeout
            if self._is_session_expired():
                self.voice_output.speak_text("Session timeout. Goodbye!")
                break
            
            # Listen for user input
            self.voice_output.speak_text("How can I help you?")
            recognition_result = self.voice_input.recognize_speech(timeout=10)
            
            if not recognition_result['success']:
                retry_count += 1
                if retry_count < self.max_retries:
                    self.voice_output.speak_text("I didn't catch that. Could you please repeat?")
                    continue
                else:
                    self.voice_output.speak_text("I'm having trouble hearing you. Please try again later.")
                    break
            
            user_input = recognition_result['text'].lower()
            
            # Check for exit commands
            if any(word in user_input for word in ['goodbye', 'bye', 'exit', 'quit', 'stop']):
                break
            
            # Process the command
            response_result = self._process_voice_command(user_input, family_context)
            interactions.append({
                'user_input': user_input,
                'response': response_result,
                'timestamp': datetime.now().isoformat()
            })
            
            # Speak the response
            if response_result.get('success'):
                self.voice_output.speak_family_response(
                    response_result['response'], 
                    family_context
                )
            else:
                error_msg = "I'm sorry, I couldn't process that request. Could you try asking differently?"
                self.voice_output.speak_text(error_msg)
            
            # Reset retry count on successful interaction
            retry_count = 0
        
        return {
            'success': True,
            'interactions': interactions,
            'total_interactions': len(interactions),
            'session_duration': (datetime.now() - self.session_start_time).total_seconds()
        }
    
    def _process_voice_command(self, user_input: str, family_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a voice command and return response
        
        Args:
            user_input: Recognized speech text
            family_context: Family context information
            
        Returns:
            Response result with success status and message
        """
        try:
            # Find matching command
            command_info = self._match_command(user_input)
            
            if not command_info:
                # No specific command matched, try general query processing
                return self._process_general_query(user_input, family_context)
            
            # Check if confirmation is required
            if command_info.get('confirmation_required') and self.require_confirmation:
                if not self._get_voice_confirmation(command_info['description']):
                    return {
                        'success': True,
                        'response': "Okay, I won't run that command.",
                        'command': 'cancelled'
                    }
            
            # Execute the command
            if 'skill' in command_info:
                return self._execute_skill_command(command_info, user_input, family_context)
            elif 'function' in command_info:
                return self._execute_function_command(command_info, user_input, family_context)
            else:
                return {
                    'success': False,
                    'response': "I'm not sure how to handle that command.",
                    'error': 'Unknown command type'
                }
                
        except Exception as e:
            self.logger.error(f"Error processing voice command: {e}")
            return {
                'success': False,
                'response': "I encountered an error processing your request.",
                'error': str(e)
            }
    
    def _match_command(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Match user input to a command"""
        user_input_lower = user_input.lower()
        
        # Look for exact or partial matches
        for command_phrase, command_info in self.command_mappings.items():
            if command_phrase in user_input_lower:
                return command_info
        
        return None
    
    def _execute_skill_command(self, command_info: Dict[str, Any], user_input: str, 
                              family_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a family skill command"""
        skill_name = command_info['skill']
        args = command_info.get('args', [])
        
        # Add user input as context
        context = family_context.copy() if family_context else {}
        context['voice_query'] = user_input
        
        # Execute the skill
        skill_result = self.family_manager.run_family_skill(skill_name, *args, context=context)
        
        if skill_result.get('success'):
            response = skill_result.get('result', 'Command completed successfully.')
            if isinstance(response, dict):
                response = response.get('response', str(response))
            
            return {
                'success': True,
                'response': str(response),
                'skill_used': skill_name
            }
        else:
            return {
                'success': False,
                'response': f"I had trouble with the {command_info['description']} command.",
                'error': skill_result.get('error')
            }
    
    def _execute_function_command(self, command_info: Dict[str, Any], user_input: str,
                                 family_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a function command"""
        function_name = command_info['function']
        
        if function_name == 'run_security_scan':
            return self._run_security_scan(family_context)
        elif function_name == 'get_family_status':
            return self._get_family_status(family_context)
        else:
            return {
                'success': False,
                'response': f"Unknown function: {function_name}",
                'error': 'Function not implemented'
            }
    
    def _process_general_query(self, user_input: str, family_context: Dict[str, Any]) -> Dict[str, Any]:
        """Process a general query using the family assistant manager"""
        try:
            context = family_context.copy() if family_context else {}
            context['voice_input'] = True
            
            result = self.family_manager.process_family_query(user_input, context)
            
            return {
                'success': True,
                'response': result.get('response', 'I processed your request.'),
                'confidence': result.get('confidence', 0.5),
                'skill_used': result.get('skill_used', 'general')
            }
            
        except Exception as e:
            self.logger.error(f"Error processing general query: {e}")
            return {
                'success': False,
                'response': "I had trouble processing your question.",
                'error': str(e)
            }
    
    def _get_voice_confirmation(self, action_description: str) -> bool:
        """Get voice confirmation for sensitive actions"""
        try:
            confirmation_msg = f"Are you sure you want to {action_description}? Please say yes or no."
            self.voice_output.speak_text(confirmation_msg)
            
            result = self.voice_input.recognize_speech(timeout=10)
            
            if result['success']:
                response = result['text'].lower()
                return any(word in response for word in ['yes', 'yeah', 'okay', 'sure', 'confirm'])
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error getting voice confirmation: {e}")
            return False
    
    def _run_security_scan(self, family_context: Dict[str, Any]) -> Dict[str, Any]:
        """Run a family security scan"""
        try:
            family_profile = family_context.get('family_profile', {})
            if not family_profile:
                return {
                    'success': False,
                    'response': "I need family profile information to run a security scan.",
                    'error': 'No family profile'
                }
            
            analysis_result = self.family_manager.analyze_family_security(family_profile)
            
            # Format response for voice
            status = analysis_result.status
            score = analysis_result.overall_score
            
            if status == "secure":
                response = f"Great news! Your family's security looks good with a score of {score:.0f} out of 100."
            elif status == "warning":
                response = f"Your family security needs some attention. Current score is {score:.0f} out of 100. I found some areas for improvement."
            else:
                response = f"I found some important security issues that need attention. Your current score is {score:.0f} out of 100."
            
            return {
                'success': True,
                'response': response,
                'analysis_result': analysis_result
            }
            
        except Exception as e:
            self.logger.error(f"Error running security scan: {e}")
            return {
                'success': False,
                'response': "I had trouble running the security scan.",
                'error': str(e)
            }
    
    def _get_family_status(self, family_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get family security status"""
        try:
            # This would integrate with the family manager to get current status
            response = "Your Guardian Node is running and monitoring your family's digital security. All systems are operational."
            
            return {
                'success': True,
                'response': response
            }
            
        except Exception as e:
            self.logger.error(f"Error getting family status: {e}")
            return {
                'success': False,
                'response': "I had trouble getting the family status.",
                'error': str(e)
            }
    
    def _get_welcome_message(self, family_context: Dict[str, Any]) -> str:
        """Get personalized welcome message"""
        member_name = family_context.get('member_name') if family_context else None
        
        if member_name:
            return f"Hello {member_name}! I'm your Guardian Family Assistant. How can I help keep your family safe online today?"
        else:
            return "Hello! I'm your Guardian Family Assistant. How can I help keep your family safe online today?"
    
    def _is_session_expired(self) -> bool:
        """Check if the current session has expired"""
        if not self.session_start_time:
            return False
        
        elapsed = (datetime.now() - self.session_start_time).total_seconds()
        return elapsed > self.session_timeout
    
    def stop_session(self):
        """Stop the current voice session"""
        with self.session_lock:
            if self.active_session:
                self.voice_output.stop_speech()
                self.active_session = False
                self.session_start_time = None
                self.logger.info("Voice session stopped")

# Convenience function for simple voice session
def run_voice_session(config: Dict[str, Any] = None, logger: logging.Logger = None,
                     family_context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Run a simple voice session with the family assistant
    
    Args:
        config: Configuration dictionary
        logger: Logger instance
        family_context: Family context information
        
    Returns:
        Session result
    """
    voice_interface = FamilyVoiceInterface(config, logger)
    return voice_interface.start_voice_session(family_context)