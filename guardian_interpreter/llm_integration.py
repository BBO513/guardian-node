"""
LLM Integration Module for Guardian Interpreter
Handles local LLM loading and inference using multiple approaches:
1. Docker Model Runner (preferred for production)
2. Direct llama-cpp-python with GGUF models (development)
3. Mock LLM (fallback for testing)

Completely offline operation with no external API calls.
Enhanced with family-friendly prompt support.
"""

import os
import logging
import requests
import json
from typing import Optional, Dict, Any
from urllib.parse import urljoin

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
    Supports multiple inference backends and model management:
    1. Docker Model Runner API (preferred)
    2. Direct llama-cpp-python with GGUF models
    3. Multiple model support with context-based switching
    Enhanced with family-friendly prompt support and fallback mechanisms
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.llm = None
        self.model_loaded = False
        self.model_path = None
        self.inference_mode = None  # 'docker', 'direct', or 'mock'
        self.docker_api_url = None
        
        # Multiple model support
        self.models = {}  # Dictionary to store loaded models
        self.current_model_key = None
        self.model_configs = self._parse_model_configs()
        self.model_performance_stats = {}
        self.fallback_attempts = 0
        self.max_fallback_attempts = 3
        
        # Initialize family prompt management if available
        if FAMILY_PROMPTS_AVAILABLE:
            self.family_prompt_manager = create_family_prompt_manager()
            self.child_safety_filter = create_child_safety_filter()
            self.logger.info("Family prompt management initialized")
        else:
            self.family_prompt_manager = None
            self.child_safety_filter = None
            self.logger.warning("Family prompt management not available")
    
    def _parse_model_configs(self) -> Dict[str, Dict[str, Any]]:
        """Parse model configurations from config"""
        llm_config = self.config.get('llm', {})
        models_config = llm_config.get('models', {})
        
        # Default model configuration if not specified
        if not models_config:
            models_config = {
                'default': {
                    'path': llm_config.get('model_path', 'models/your-model.gguf'),
                    'context_length': llm_config.get('context_length', 4096),
                    'threads': llm_config.get('threads', 4),
                    'temperature': llm_config.get('temperature', 0.7),
                    'max_tokens': llm_config.get('max_tokens', 512),
                    'age_groups': ['adult', 'teen', 'child'],
                    'contexts': ['general', 'security', 'education']
                }
            }
        
        return models_config
        
    def load_model(self) -> bool:
        """
        Load the LLM model using the best available method:
        1. Try Docker Model Runner API first
        2. Fall back to direct GGUF loading with multiple model support
        3. Use mock if neither available
        
        Returns:
            bool: True if model loaded successfully, False otherwise
        """
        llm_config = self.config.get('llm', {})
        
        # Try Docker Model Runner first (preferred for production)
        if self._try_docker_model_runner(llm_config):
            return True
        
        # Fall back to direct GGUF loading with multiple model support
        if self._try_direct_gguf_loading_multi(llm_config):
            return True
        
        # If both fail, we'll use mock mode
        self.logger.warning("No LLM backend available, using mock mode")
        self.inference_mode = 'mock'
        self.model_loaded = True
        return True
    
    def load_default_model(self) -> bool:
        """Load the default model for initial setup"""
        return self.load_model()
    
    def switch_model(self, context: Dict[str, Any]) -> bool:
        """
        Switch to the most appropriate model based on context
        
        Args:
            context: Dictionary containing age_group, query_type, complexity, etc.
            
        Returns:
            bool: True if model switched successfully
        """
        if self.inference_mode == 'docker':
            # Docker Model Runner handles model selection internally
            self.logger.info("Using Docker Model Runner - model switching handled by API")
            return True
        elif self.inference_mode == 'direct':
            return self._switch_direct_model(context)
        else:
            # Mock mode - just log the switch attempt
            self.logger.info(f"Mock mode: would switch to model for context {context}")
            return True
    
    def _switch_direct_model(self, context: Dict[str, Any]) -> bool:
        """Switch direct GGUF model based on context"""
        try:
            age_group = context.get('age_group', 'adult')
            query_type = context.get('query_type', 'general')
            
            # Find the best model for this context
            best_model_key = self._find_best_model(age_group, query_type)
            
            if best_model_key == self.current_model_key:
                # Already using the right model
                return True
            
            if best_model_key in self.models:
                # Model already loaded
                self.llm = self.models[best_model_key]
                self.current_model_key = best_model_key
                self.logger.info(f"Switched to loaded model: {best_model_key}")
                return True
            else:
                # Need to load new model
                return self._load_specific_model(best_model_key)
                
        except Exception as e:
            self.logger.error(f"Error switching model: {e}")
            return False
    
    def _find_best_model(self, age_group: str, query_type: str) -> str:
        """Find the best model for given context"""
        # Score each model based on context match
        best_score = -1
        best_model = 'default'
        
        for model_key, model_config in self.model_configs.items():
            score = 0
            
            # Age group match
            if age_group in model_config.get('age_groups', []):
                score += 10
            
            # Query type match
            if query_type in model_config.get('contexts', []):
                score += 5
            
            # Performance history
            perf_stats = self.model_performance_stats.get(model_key, {})
            avg_response_time = perf_stats.get('avg_response_time', 1.0)
            success_rate = perf_stats.get('success_rate', 1.0)
            score += (success_rate * 5) - (avg_response_time * 0.1)
            
            if score > best_score:
                best_score = score
                best_model = model_key
        
        return best_model
    
    def _load_specific_model(self, model_key: str) -> bool:
        """Load a specific model by key"""
        if model_key not in self.model_configs:
            self.logger.error(f"Model configuration not found: {model_key}")
            return False
        
        model_config = self.model_configs[model_key]
        model_path = model_config.get('path')
        
        if not model_path or not os.path.exists(model_path):
            self.logger.error(f"Model file not found: {model_path}")
            return False
        
        try:
            self.logger.info(f"Loading model: {model_key} from {model_path}")
            
            # Unload current model if memory is limited
            if len(self.models) >= 2:  # Keep max 2 models in memory
                self._unload_least_used_model()
            
            # Load new model
            new_model = Llama(
                model_path=model_path,
                n_ctx=model_config.get('context_length', 4096),
                n_threads=model_config.get('threads', 4),
                verbose=False
            )
            
            self.models[model_key] = new_model
            self.llm = new_model
            self.current_model_key = model_key
            self.model_path = model_path
            
            # Initialize performance stats
            if model_key not in self.model_performance_stats:
                self.model_performance_stats[model_key] = {
                    'load_count': 0,
                    'success_count': 0,
                    'error_count': 0,
                    'total_response_time': 0.0,
                    'avg_response_time': 0.0,
                    'success_rate': 1.0
                }
            
            self.model_performance_stats[model_key]['load_count'] += 1
            self.logger.info(f"Successfully loaded model: {model_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load model {model_key}: {e}")
            return False
    
    def _unload_least_used_model(self):
        """Unload the least recently used model to free memory"""
        if not self.models:
            return
        
        # Find least used model (simple LRU based on load_count)
        least_used_key = min(
            self.models.keys(),
            key=lambda k: self.model_performance_stats.get(k, {}).get('load_count', 0)
        )
        
        if least_used_key != self.current_model_key:
            del self.models[least_used_key]
            self.logger.info(f"Unloaded model to free memory: {least_used_key}")
    
    def get_model_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for all models"""
        return {
            'current_model': self.current_model_key,
            'loaded_models': list(self.models.keys()),
            'performance_stats': self.model_performance_stats,
            'fallback_attempts': self.fallback_attempts
        }
    
    def _try_docker_model_runner(self, llm_config: Dict[str, Any]) -> bool:
        """Try to connect to Docker Model Runner API"""
        try:
            # Check if Docker Model Runner is configured
            docker_config = llm_config.get('docker_runner', {})
            if not docker_config.get('enabled', True):
                return False
            
            self.docker_api_url = docker_config.get('api_url', 'http://localhost:8080')
            
            # Test connection to Docker Model Runner
            health_url = urljoin(self.docker_api_url, '/health')
            response = requests.get(health_url, timeout=5)
            
            if response.status_code == 200:
                self.logger.info(f"Connected to Docker Model Runner at {self.docker_api_url}")
                self.inference_mode = 'docker'
                self.model_loaded = True
                return True
            else:
                self.logger.warning(f"Docker Model Runner health check failed: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.info(f"Docker Model Runner not available: {e}")
            return False
        except Exception as e:
            self.logger.warning(f"Error connecting to Docker Model Runner: {e}")
            return False
    
    def _try_direct_gguf_loading_multi(self, llm_config: Dict[str, Any]) -> bool:
        """Try to load GGUF models directly with multi-model support"""
        if not LLAMA_CPP_AVAILABLE:
            self.logger.info("llama-cpp-python not available for direct GGUF loading")
            return False
        
        # Try to load at least one model
        loaded_any = False
        
        for model_key, model_config in self.model_configs.items():
            model_path = model_config.get('path')
            
            if not model_path or not os.path.exists(model_path):
                self.logger.info(f"GGUF model file not found for {model_key}: {model_path}")
                continue
            
            try:
                self.logger.info(f"Loading GGUF model: {model_key} from {model_path}")
                
                # Initialize Llama with configuration
                model = Llama(
                    model_path=model_path,
                    n_ctx=model_config.get('context_length', 4096),
                    n_threads=model_config.get('threads', 4),
                    verbose=False  # Reduce output noise
                )
                
                self.models[model_key] = model
                
                # Set as current model if it's the first one loaded or default
                if not self.current_model_key or model_key == 'default':
                    self.llm = model
                    self.current_model_key = model_key
                    self.model_path = model_path
                
                # Initialize performance stats
                self.model_performance_stats[model_key] = {
                    'load_count': 1,
                    'success_count': 0,
                    'error_count': 0,
                    'total_response_time': 0.0,
                    'avg_response_time': 0.0,
                    'success_rate': 1.0
                }
                
                loaded_any = True
                self.logger.info(f"Successfully loaded GGUF model: {model_key}")
                
            except Exception as e:
                self.logger.warning(f"Failed to load GGUF model {model_key}: {e}")
                continue
        
        if loaded_any:
            self.inference_mode = 'direct'
            self.model_loaded = True
            self.logger.info(f"Direct GGUF loading successful. Loaded {len(self.models)} models.")
            return True
        else:
            self.logger.warning("Failed to load any GGUF models directly")
            return False
    
    def is_loaded(self) -> bool:
        """Check if model is loaded and ready"""
        return self.model_loaded and self.llm is not None
    
    def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        """
        Generate a response using the available LLM backend
        
        Args:
            prompt: User input prompt
            system_prompt: Optional system prompt for context
            
        Returns:
            str: Generated response
        """
        if not self.is_loaded():
            return "Error: LLM model not loaded. Please check configuration and model file."
        
        try:
            if self.inference_mode == 'docker':
                return self._generate_docker_response(prompt, system_prompt)
            elif self.inference_mode == 'direct':
                return self._generate_direct_response(prompt, system_prompt)
            else:  # mock mode
                return self._generate_mock_response(prompt, system_prompt)
                
        except Exception as e:
            error_msg = f"Error generating response: {e}"
            self.logger.error(error_msg)
            return error_msg
    
    def _generate_docker_response(self, prompt: str, system_prompt: str = None) -> str:
        """Generate response using Docker Model Runner API"""
        try:
            llm_config = self.config.get('llm', {})
            full_prompt = self._prepare_prompt(prompt, system_prompt)
            
            # Prepare request for Docker Model Runner
            api_url = urljoin(self.docker_api_url, '/v1/chat/completions')
            payload = {
                "messages": [
                    {"role": "system", "content": system_prompt or self._get_default_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": llm_config.get('max_tokens', 512),
                "temperature": llm_config.get('temperature', 0.7),
                "stream": False
            }
            
            self.logger.info(f"Sending request to Docker Model Runner: {prompt[:100]}...")
            
            response = requests.post(api_url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            generated_text = result['choices'][0]['message']['content'].strip()
            
            self.logger.info(f"Generated Docker response: {generated_text[:100]}...")
            return generated_text
            
        except Exception as e:
            self.logger.error(f"Docker Model Runner error: {e}")
            return f"Error with Docker Model Runner: {e}"
    
    def _generate_direct_response(self, prompt: str, system_prompt: str = None) -> str:
        """Generate response using direct GGUF model with fallback support"""
        import time
        
        start_time = time.time()
        
        try:
            # Get model config for current model
            model_config = self.model_configs.get(self.current_model_key, {})
            full_prompt = self._prepare_prompt(prompt, system_prompt)
            
            self.logger.info(f"Generating direct response with {self.current_model_key}: {prompt[:100]}...")
            
            # Generate response using llama-cpp-python
            response = self.llm(
                full_prompt,
                max_tokens=model_config.get('max_tokens', 512),
                temperature=model_config.get('temperature', 0.7),
                stop=["Human:", "User:", "\n\n"],  # Stop sequences
                echo=False
            )
            
            # Extract the generated text
            generated_text = response['choices'][0]['text'].strip()
            
            # Update performance stats
            response_time = time.time() - start_time
            self._update_model_performance(self.current_model_key, True, response_time)
            
            self.logger.info(f"Generated direct response: {generated_text[:100]}...")
            self.fallback_attempts = 0  # Reset fallback counter on success
            return generated_text
            
        except Exception as e:
            response_time = time.time() - start_time
            self._update_model_performance(self.current_model_key, False, response_time)
            
            self.logger.error(f"Direct GGUF generation error with {self.current_model_key}: {e}")
            
            # Try fallback to another model
            if self.fallback_attempts < self.max_fallback_attempts:
                return self._try_fallback_model(prompt, system_prompt)
            else:
                return f"Error: All model fallbacks exhausted. Last error: {e}"
    
    def _try_fallback_model(self, prompt: str, system_prompt: str = None) -> str:
        """Try to use a fallback model when the current model fails"""
        self.fallback_attempts += 1
        self.logger.warning(f"Attempting fallback #{self.fallback_attempts}")
        
        # Find an alternative model
        available_models = [k for k in self.models.keys() if k != self.current_model_key]
        
        if not available_models:
            # Try to load default model if not already loaded
            if 'default' not in self.models and 'default' in self.model_configs:
                if self._load_specific_model('default'):
                    available_models = ['default']
        
        if available_models:
            # Switch to first available alternative
            fallback_model = available_models[0]
            self.llm = self.models[fallback_model]
            old_model = self.current_model_key
            self.current_model_key = fallback_model
            
            self.logger.info(f"Switched from {old_model} to fallback model: {fallback_model}")
            
            # Try generating with fallback model
            try:
                return self._generate_direct_response(prompt, system_prompt)
            except Exception as e:
                self.logger.error(f"Fallback model {fallback_model} also failed: {e}")
                return f"Error: Fallback model failed: {e}"
        else:
            return "Error: No fallback models available"
    
    def _update_model_performance(self, model_key: str, success: bool, response_time: float):
        """Update performance statistics for a model"""
        if model_key not in self.model_performance_stats:
            self.model_performance_stats[model_key] = {
                'load_count': 0,
                'success_count': 0,
                'error_count': 0,
                'total_response_time': 0.0,
                'avg_response_time': 0.0,
                'success_rate': 1.0
            }
        
        stats = self.model_performance_stats[model_key]
        
        if success:
            stats['success_count'] += 1
        else:
            stats['error_count'] += 1
        
        stats['total_response_time'] += response_time
        total_requests = stats['success_count'] + stats['error_count']
        
        if total_requests > 0:
            stats['avg_response_time'] = stats['total_response_time'] / total_requests
            stats['success_rate'] = stats['success_count'] / total_requests
    
    def _generate_mock_response(self, prompt: str, system_prompt: str = None) -> str:
        """Generate mock response for testing"""
        responses = [
            f"Mock Nodie response to: '{prompt}'. Configure Docker Model Runner or add a GGUF model for real AI responses.",
            f"I'm a placeholder AI. Your prompt was: '{prompt}'. Set up Docker Model Runner or direct GGUF loading for full functionality.",
            f"Guardian mock mode active. Received: '{prompt}'. Configure LLM backend to activate real AI."
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
            return f"System: {self._get_default_system_prompt()}\n\nHuman: {user_prompt}\n\nAssistant:"
    
    def _get_default_system_prompt(self) -> str:
        """Get the default Guardian system prompt"""
        return (
            "You are Nodie, the Guardian AI assistant. You are running locally on a Guardian Node "
            "for network security and system monitoring. You help with network analysis, security "
            "assessment, and system administration. You are privacy-focused and operate completely "
            "offline. Be helpful, concise, and security-conscious in your responses."
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get comprehensive information about loaded models and performance
        
        Returns:
            dict: Model information including performance stats
        """
        info = {
            'loaded': self.model_loaded,
            'inference_mode': self.inference_mode,
            'current_model': self.current_model_key,
            'model_path': self.model_path,
            'docker_api_url': self.docker_api_url,
            'llama_cpp_available': LLAMA_CPP_AVAILABLE,
            'family_prompts_available': FAMILY_PROMPTS_AVAILABLE,
            'loaded_models': list(self.models.keys()),
            'available_models': list(self.model_configs.keys()),
            'fallback_attempts': self.fallback_attempts,
            'max_fallback_attempts': self.max_fallback_attempts
        }
        
        if self.is_loaded():
            # Add current model configuration
            if self.current_model_key and self.current_model_key in self.model_configs:
                current_config = self.model_configs[self.current_model_key]
                info.update({
                    'current_model_config': current_config,
                    'context_length': current_config.get('context_length', 4096),
                    'temperature': current_config.get('temperature', 0.7),
                    'max_tokens': current_config.get('max_tokens', 512),
                    'threads': current_config.get('threads', 4)
                })
            
            # Add performance statistics
            info['performance_stats'] = self.model_performance_stats
        
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

