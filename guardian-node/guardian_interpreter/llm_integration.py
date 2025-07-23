# LLM Integration Module for Guardian Interpreter
# Handles local LLM loading and inference using llama-cpp-python and GGUF models.
# Completely offline operation with no external API calls.

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
        self.config = config
        self.models = config.get('llm', {}).get('models', {})
        self.current_model = None
        self.logger = logger
        self.llm = None
        self.model_loaded = False
        self.model_path = None

    def load_model(self) -> bool:
        if not LLAMA_CPP_AVAILABLE:
            self.logger.error("llama-cpp-python not available. Install with: pip install llama-cpp-python")
            return False

        llm_config = self.config.get('llm', {})
        self.model_path = llm_config.get('model_path', '/mnt/c/Users/works/Desktop/Offline AI Cyber Sec/guardian_interpreter_v1.0.0/guardian_interpreter/models/Phi-3-mini-4k-instruct-q4.gguf')

        if not os.path.exists(self.model_path):
            self.logger.error(f"Model file not found: {self.model_path}")
            return False

        try:
            self.logger.info(f"Loading LLM model: {self.model_path}")
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=llm_config.get('context_length', 4096),
                n_threads=llm_config.get('threads', 4),
                verbose=False
            )
            self.model_loaded = True
            self.logger.info("LLM model loaded successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load LLM model: {e}")
            self.model_loaded = False
            return False

    def is_loaded(self) -> bool:
        return self.model_loaded and self.llm is not None

    def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        if not self.is_loaded():
            return "Error: LLM model not loaded. Please check configuration and model file."

        try:
            llm_config = self.config.get('llm', {})
            full_prompt = self._prepare_prompt(prompt, system_prompt)
            self.logger.info(f"Generating response for prompt: {prompt[:100]}...")
            response = self.llm(
                full_prompt,
                max_tokens=llm_config.get('max_tokens', 512),
                temperature=llm_config.get('temperature', 0.7),
                stop=["Human:", "User:", "\n\n"],
                echo=False
            )
            generated_text = response['choices'][0]['text'].strip()
            self.logger.info(f"Generated response: {generated_text[:100]}...")
            return generated_text
        except Exception as e:
            error_msg = f"Error generating response: {e}"
            self.logger.error(error_msg)
            return error_msg

    def _prepare_prompt(self, user_prompt: str, system_prompt: str = None) -> str:
        if system_prompt:
            return f"System: {system_prompt}\n\nHuman: {user_prompt}\n\nAssistant:"
        else:
            default_system = (
                "You are Nodie, the Guardian AI assistant. You are running locally on a Guardian Node "
                "for network security and system monitoring. You help with network analysis, security "
                "assessment, and system administration. You are privacy-focused and operate completely "
                "offline. Be helpful, concise, and security-conscious in your responses."
            )
            return f"System: {default_system}\n\nHuman: {user_prompt}\n\nAssistant:"

    def get_model_info(self) -> Dict[str, Any]:
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
        if self.llm:
            del self.llm
            self.llm = None
            self.model_loaded = False
            self.logger.info("LLM model unloaded")

class MockLLM:
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.model_loaded = False

    def load_model(self) -> bool:
        self.logger.warning("Using mock LLM - llama-cpp-python not available")
        self.model_loaded = True
        return True

    def is_loaded(self) -> bool:
        return self.model_loaded

    def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        responses = [
            f"Mock Nodie response to: '{prompt}'. Install llama-cpp-python and add a GGUF model for real AI responses.",
            f"I'm a placeholder AI. Your prompt was: '{prompt}'. Configure a real GGUF model to enable full functionality.",
            f"Guardian mock mode active. Received: '{prompt}'. Add llama-cpp-python and a model file to activate real AI."
        ]
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
    if LLAMA_CPP_AVAILABLE:
        return GuardianLLM(config, logger)
    else:
        return MockLLM(config, logger)
             