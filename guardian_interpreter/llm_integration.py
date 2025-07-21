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
    Simplified implementation with direct GGUF model loading and context-based switching
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.models = config.get('llm', {}).get('models', {})
        self.current_model = None
        self.logger = logger
        self.load_default_model()
    
    def load_default_model(self):
        """Load the default GGUF model"""
        default_path = self.models.get('default', 'models/your-model.gguf')
        if os.path.exists(default_path):
            self.current_model = Llama(default_path, n_ctx=4096, n_threads=4)
            self.logger.info("Loaded default GGUF model")
    
    def switch_model(self, context):
        """
        Switch to the appropriate model based on context
        
        Args:
            context: Dictionary containing age_group and other context
        """
        age_group = context.get('age_group', 'adult')
        model_path = self.models.get(age_group, self.models.get('default'))
        if model_path and os.path.exists(model_path):
            self.current_model = Llama(model_path, n_ctx=4096, n_threads=4)
            self.logger.info(f"Switched to {age_group} model")
        else:
            self.logger.warning(f"No model for {age_group} - using default")
    
    def generate_response(self, prompt, system_prompt=None):
        """
        Generate a response using the loaded LLM
        
        Args:
            prompt: User input prompt
            system_prompt: Optional system prompt for context
            
        Returns:
            str: Generated response
        """
        # Add fallback mechanism
        try:
            # Generate response
            response = self.current_model(prompt, max_tokens=512)
            return response['choices'][0]['text'].strip()
        except:
            return "Fallback: Model unavailable - please check setup."

def create_llm(config: Dict[str, Any], logger: logging.Logger) -> GuardianLLM:
    """
    Factory function to create LLM instance
    
    Args:
        config: Guardian configuration
        logger: Logger instance
        
    Returns:
        GuardianLLM instance
    """
    return GuardianLLM(config, logger)