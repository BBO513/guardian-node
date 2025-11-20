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
        self.config = config  # Store config for later use
        self.models = config.get('llm', {}).get('models', {})
        self.current_model = None
        self.logger = logger
        self.llm = None
        self.model_loaded = False
        self.model_path = None
        self.load_default_model()

    def load_default_model(self) -> bool:
        """
        Load the default LLM model for Guardian Node
        
        TODO - LLM MODEL SETUP INSTRUCTIONS:
        ====================================
        This function currently expects GGUF format models compatible with llama-cpp-python.
        
        STEP 1: Install Dependencies
        ----------------------------
        pip install llama-cpp-python
        
        STEP 2: Download a Model
        -------------------------
        Recommended models (family-friendly, moderate size):
        
        - Phi-3-mini (Recommended for Guardian Node):
          https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf
          Download: Phi-3-mini-4k-instruct-q4.gguf (~2.3GB)
        
        - Mistral-7B (For advanced security analysis):
          https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF
          Download: mistral-7b-instruct-v0.2.Q4_K_M.gguf (~4.4GB)
        
        STEP 3: Place Model File
        -------------------------
        Create models/ directory in project root and place downloaded .gguf file:
          guardian-node/models/Phi-3-mini-4k-instruct-q4.gguf
        
        STEP 4: Configure (Optional)
        -----------------------------
        Update guardian_interpreter/config.yaml to customize:
        - model_path: Path to your model file
        - context_length: Token context window (default: 4096)
        - threads: CPU threads to use (default: 4)
        - temperature: Response creativity (0.0-1.0, default: 0.7)
        
        FALLBACK BEHAVIOR:
        ------------------
        If model file is not found, Guardian Node will run in limited mode with
        simulated responses for testing. For full functionality, a model is required.
        """
        if not LLAMA_CPP_AVAILABLE:
            self.logger.error("llama-cpp-python not available. Install with: pip install llama-cpp-python")
            return False

        llm_config = self.config.get('llm', {})
        # Use portable path relative to project root
        default_model_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'models',
            'Phi-3-mini-4k-instruct-q4.gguf'
        )
        self.model_path = llm_config.get('model_path', default_model_path)

        if not os.path.exists(self.model_path):
            self.logger.error(f"Model file not found: {self.model_path}")
            self.logger.error("TODO: Download a GGUF model and place it in the models/ directory")
            self.logger.error("See docstring in load_default_model() for detailed instructions")
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
             