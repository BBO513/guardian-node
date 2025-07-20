"""
LLM Integration Module for Guardian Interpreter
Handles local LLM loading and inference using llama-cpp-python and GGUF models.
Completely offline operation with no external API calls.
Enhanced with family-friendly prompt support.
"""

import os
import logging
from typing import Optional, Dict, Any

try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False
    Llama = None

# Import family prompt management
try:
    from family_llm_prompts import (
        FamilyPromptManager, ChildSafetyFilter, FamilyContext, 
        ChildSafetyLevel, create_family_prompt_manager, create_child_safety_filter
    )
    FAMILY_PROMPTS_AVAILABLE = True
except ImportError:
    FAMILY_PROMPTS_AVAILABLE = False

class GuardianLLM:
    """
    Local LLM handler for Guardian Interpreter
    Uses llama-cpp-python for offline GGUF model inference
    Enhanced with family-friendly prompt support
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.llm = None
        self.model_loaded = False
        self.model_path = None
        
        # Initialize family prompt management if available
        if FAMILY_PROMPTS_AVAILABLE:
            self.family_prompt_manager = create_family_prompt_manager()
            self.child_safety_filter = create_child_safety_filter()
            self.logger.info("Family prompt management initialized")
        else:
            self.family_prompt_manager = None
            self.child_safety_filter = None
            self.logger.warning("Family prompt management not available")
        
    def load_model(self) -> bool:
        """
        Load the GGUF model specified in configuration
        
        Returns:
            bool: True if model loaded successfully, False otherwise
        """
        if not LLAMA_CPP_AVAILABLE:
            self.logger.error("llama-cpp-python not available. Install with: pip install llama-cpp-python")
            return False
        
        llm_config = self.config.get('llm', {})
        self.model_path = llm_config.get('model_path', 'models/your-model.gguf')
        
        # Check if model file exists
        if not os.path.exists(self.model_path):
            self.logger.error(f"Model file not found: {self.model_path}")
            return False
        
        try:
            self.logger.info(f"Loading LLM model: {self.model_path}")
            
            # Initialize Llama with configuration
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=llm_config.get('context_length', 4096),
                n_threads=llm_config.get('threads', 4),
                verbose=False  # Reduce output noise
            )
            
            self.model_loaded = True
            self.logger.info("LLM model loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load LLM model: {e}")
            self.model_loaded = False
            return False
    
    def is_loaded(self) -> bool:
        """Check if model is loaded and ready"""
        return self.model_loaded and self.llm is not None
    
    def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        """
        Generate a response using the local LLM
        
        Args:
            prompt: User input prompt
            system_prompt: Optional system prompt for context
            
        Returns:
            str: Generated response
        """
        if not self.is_loaded():
            return "Error: LLM model not loaded. Please check configuration and model file."
        
        try:
            llm_config = self.config.get('llm', {})
            
            # Prepare the full prompt
            full_prompt = self._prepare_prompt(prompt, system_prompt)
            
            self.logger.info(f"Generating response for prompt: {prompt[:100]}...")
            
            # Generate response
            response = self.llm(
                full_prompt,
                max_tokens=llm_config.get('max_tokens', 512),
                temperature=llm_config.get('temperature', 0.7),
                stop=["Human:", "User:", "\n\n"],  # Stop sequences
                echo=False
            )
            
            # Extract the generated text
            generated_text = response['choices'][0]['text'].strip()
            
            self.logger.info(f"Generated response: {generated_text[:100]}...")
            return generated_text
            
        except Exception as e:
            error_msg = f"Error generating response: {e}"
            self.logger.error(error_msg)
            return error_msg
    
    def generate_family_response(self, 
                               prompt: str, 
                               context: 'FamilyContext' = None,
                               child_safe_mode: bool = False,
                               safety_level: 'ChildSafetyLevel' = None,
                               family_profile: Optional[Dict] = None) -> str:
        """
        Generate a family-friendly response using specialized prompts and filtering
        
        Args:
            prompt: User input prompt
            context: Family context for specialized prompting
            child_safe_mode: Whether to enable child safety filtering
            safety_level: Level of child safety filtering to apply
            family_profile: Optional family profile for personalization
            
        Returns:
            str: Family-friendly response
        """
        if not self.is_loaded():
            return "Error: LLM model not loaded. Please check configuration and model file."
        
        if not FAMILY_PROMPTS_AVAILABLE:
            self.logger.warning("Family prompts not available, using standard response")
            return self.generate_response(prompt)
        
        try:
            # Import enums if not already available in scope
            if context is None:
                from family_llm_prompts import FamilyContext
                context = FamilyContext.GENERAL
            
            if safety_level is None:
                from family_llm_prompts import ChildSafetyLevel
                safety_level = ChildSafetyLevel.STANDARD
            
            # Generate family-friendly system prompt
            family_system_prompt = self.family_prompt_manager.get_system_prompt(
                context=context,
                child_safe_mode=child_safe_mode,
                safety_level=safety_level,
                family_profile=family_profile
            )
            
            # Format the complete prompt
            formatted_prompt = self.family_prompt_manager.format_prompt_for_context(
                prompt, context, family_system_prompt
            )
            
            self.logger.info(f"Generating family response for context: {context.value}")
            
            # Generate response using the family-friendly prompt
            llm_config = self.config.get('llm', {})
            response = self.llm(
                formatted_prompt,
                max_tokens=llm_config.get('max_tokens', 512),
                temperature=llm_config.get('temperature', 0.7),
                stop=["Human:", "User:", "\n\n"],
                echo=False
            )
            
            # Extract the generated text
            generated_text = response['choices'][0]['text'].strip()
            
            # Apply child safety filtering if enabled
            if child_safe_mode and self.child_safety_filter:
                generated_text = self.child_safety_filter.filter_response(
                    generated_text, safety_level
                )
                self.logger.info(f"Applied {safety_level.value} child safety filtering")
            
            self.logger.info(f"Generated family response: {generated_text[:100]}...")
            return generated_text
            
        except Exception as e:
            error_msg = f"Error generating family response: {e}"
            self.logger.error(error_msg)
            return error_msg
    
    def _prepare_prompt(self, user_prompt: str, system_prompt: str = None) -> str:
        """
        Prepare the prompt for the LLM with proper formatting
        
        Args:
            user_prompt: The user's input
            system_prompt: Optional system context
            
        Returns:
            str: Formatted prompt
        """
        if system_prompt:
            return f"System: {system_prompt}\n\nHuman: {user_prompt}\n\nAssistant:"
        else:
            # Default Guardian system prompt
            default_system = (
                "You are Nodie, the Guardian AI assistant. You are running locally on a Guardian Node "
                "for network security and system monitoring. You help with network analysis, security "
                "assessment, and system administration. You are privacy-focused and operate completely "
                "offline. Be helpful, concise, and security-conscious in your responses."
            )
            return f"System: {default_system}\n\nHuman: {user_prompt}\n\nAssistant:"
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model
        
        Returns:
            dict: Model information
        """
        info = {
            'loaded': self.model_loaded,
            'model_path': self.model_path,
            'available': LLAMA_CPP_AVAILABLE
        }
        
        if self.is_loaded():
            llm_config = self.config.get('llm', {})
            info.update({
                'context_length': llm_config.get('context_length', 4096),
                'temperature': llm_config.get('temperature', 0.7),
                'max_tokens': llm_config.get('max_tokens', 512),
                'threads': llm_config.get('threads', 4)
            })
        
        return info
    
    def unload_model(self):
        """Unload the model to free memory"""
        if self.llm:
            del self.llm
            self.llm = None
            self.model_loaded = False
            self.logger.info("LLM model unloaded")

class MockLLM:
    """
    Mock LLM for testing when llama-cpp-python is not available
    Enhanced with family-friendly mock responses
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.model_loaded = False
        
        # Initialize family prompt management if available (for mock responses)
        if FAMILY_PROMPTS_AVAILABLE:
            self.family_prompt_manager = create_family_prompt_manager()
            self.child_safety_filter = create_child_safety_filter()
        else:
            self.family_prompt_manager = None
            self.child_safety_filter = None
    
    def load_model(self) -> bool:
        """Mock model loading"""
        self.logger.warning("Using mock LLM - llama-cpp-python not available")
        self.model_loaded = True
        return True
    
    def is_loaded(self) -> bool:
        return self.model_loaded
    
    def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        """Generate a mock response"""
        responses = [
            f"Mock Nodie response to: '{prompt}'. Install llama-cpp-python and add a GGUF model for real AI responses.",
            f"I'm a placeholder AI. Your prompt was: '{prompt}'. Configure a real GGUF model to enable full functionality.",
            f"Guardian mock mode active. Received: '{prompt}'. Add llama-cpp-python and a model file to activate real AI."
        ]
        
        # Simple hash-based selection for consistency
        response_index = hash(prompt) % len(responses)
        return responses[response_index]
    
    def generate_family_response(self, 
                               prompt: str, 
                               context: 'FamilyContext' = None,
                               child_safe_mode: bool = False,
                               safety_level: 'ChildSafetyLevel' = None,
                               family_profile: Optional[Dict] = None) -> str:
        """Generate a mock family-friendly response"""
        if not FAMILY_PROMPTS_AVAILABLE:
            return self.generate_response(prompt)
        
        # Import enums if not already available in scope
        if context is None:
            from family_llm_prompts import FamilyContext
            context = FamilyContext.GENERAL
        
        if safety_level is None:
            from family_llm_prompts import ChildSafetyLevel
            safety_level = ChildSafetyLevel.STANDARD
        
        # Generate context-appropriate mock responses
        family_responses = {
            'GENERAL': f"Hi there! I'm Nodie, your family cybersecurity assistant. You asked: '{prompt}'. I'd love to help, but I need a real AI model to give you proper guidance. Please install llama-cpp-python and add a GGUF model!",
            'CHILD_EDUCATION': f"Hey! That's a great question about staying safe online: '{prompt}'. I'm just a practice AI right now, but once you add a real model, I can teach you lots of fun ways to be cyber-safe!",
            'PARENT_GUIDANCE': f"Hello! As a parent, you're asking an important question: '{prompt}'. I'm currently in demo mode, but with a real AI model, I can provide detailed family cybersecurity guidance.",
            'DEVICE_SECURITY': f"Good thinking about device security! Your question: '{prompt}' is exactly what I'm designed to help with. Add a GGUF model and I'll give you step-by-step security instructions.",
            'THREAT_EXPLANATION': f"I understand you want to know about cybersecurity threats: '{prompt}'. In real mode, I explain these in family-friendly terms. Right now I'm just a placeholder!",
            'EMERGENCY_RESPONSE': f"MOCK EMERGENCY MODE: For '{prompt}' - In real operation, I'd provide immediate security guidance. Please configure a real AI model for actual emergency support."
        }
        
        mock_response = family_responses.get(context.value.upper(), family_responses['GENERAL'])
        
        # Apply mock child safety filtering if enabled
        if child_safe_mode and self.child_safety_filter:
            mock_response = self.child_safety_filter.filter_response(mock_response, safety_level)
            self.logger.info(f"Applied mock {safety_level.value} child safety filtering")
        
        return mock_response
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            'loaded': True,
            'model_path': 'Mock LLM',
            'available': False,
            'family_prompts_available': FAMILY_PROMPTS_AVAILABLE,
            'note': 'Install llama-cpp-python for real LLM functionality'
        }
    
    def unload_model(self):
        self.model_loaded = False

def create_llm(config: Dict[str, Any], logger: logging.Logger) -> GuardianLLM:
    """
    Factory function to create appropriate LLM instance
    
    Args:
        config: Guardian configuration
        logger: Logger instance
        
    Returns:
        GuardianLLM or MockLLM instance
    """
    if LLAMA_CPP_AVAILABLE:
        return GuardianLLM(config, logger)
    else:
        return MockLLM(config, logger)

