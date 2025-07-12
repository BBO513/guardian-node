"""
LLM Integration Module for Guardian Interpreter
Handles local LLM loading and inference using llama-cpp-python and GGUF models.
Completely offline operation with no external API calls.
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

class GuardianLLM:
    """
    Local LLM handler for Guardian Interpreter
    Uses llama-cpp-python for offline GGUF model inference
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.llm = None
        self.model_loaded = False
        self.model_path = None
        
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
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.model_loaded = False
    
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
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            'loaded': True,
            'model_path': 'Mock LLM',
            'available': False,
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

