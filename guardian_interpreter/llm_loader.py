"""
Guardian Node LLM Loader
Handles loading and management of GGUF models for the Family AI Assistant
"""

import os
import logging
import glob
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class ModelInfo:
    """Information about a loaded model"""
    name: str
    path: str
    size_mb: float
    loaded: bool = False
    performance_score: Optional[float] = None

class GuardianLLMLoader:
    """
    LLM Loader for Guardian Node Family AI Assistant
    Supports GGUF models with automatic discovery and benchmarking
    """
    
    def __init__(self):
        self.models_dir = os.getenv('GUARDIAN_MODELS_DIR', '/app/models')
        self.default_model_path = os.getenv('GUARDIAN_LLM_MODEL_PATH',
                                           '/app/models/phi-3-mini-4k-instruct-q4.gguf')
        self.current_model = None
        self.available_models: Dict[str, ModelInfo] = {}
        self.max_memory_mb = int(os.getenv('GUARDIAN_MAX_MEMORY_MB', '2048'))
        
        # Initialize model discovery
        self._discover_models()
    
    def _discover_models(self) -> None:
        """Discover all GGUF models in the models directory"""
        if not os.path.exists(self.models_dir):
            logger.warning(f"Models directory not found: {self.models_dir}")
            return
        
        # Find all GGUF files
        gguf_pattern = os.path.join(self.models_dir, "*.gguf")
        model_files = glob.glob(gguf_pattern)
        
        logger.info(f"Discovered {len(model_files)} GGUF models in {self.models_dir}")
        
        for model_path in model_files:
            model_name = os.path.basename(model_path)
            size_mb = os.path.getsize(model_path) / (1024 * 1024)
            
            self.available_models[model_name] = ModelInfo(
                name=model_name,
                path=model_path,
                size_mb=size_mb
            )
            
            logger.info(f"Found model: {model_name} ({size_mb:.1f} MB)")
    
    def load_default_model(self) -> bool:
        """Load the default production model"""
        if os.path.exists(self.default_model_path):
            return self.load_model(self.default_model_path)
        else:
            logger.error(f"Default model not found: {self.default_model_path}")
            # Try to load any available model as fallback
            return self._load_fallback_model()
    
    def load_model(self, model_path: str) -> bool:
        """
        Load a specific GGUF model
        
        Args:
            model_path: Path to the GGUF model file
            
        Returns:
            bool: True if model loaded successfully
        """
        try:
            if not os.path.exists(model_path):
                logger.error(f"Model file not found: {model_path}")
                return False
            
            model_name = os.path.basename(model_path)
            size_mb = os.path.getsize(model_path) / (1024 * 1024)
            
            # Check memory constraints
            if size_mb > self.max_memory_mb:
                logger.warning(f"Model {model_name} ({size_mb:.1f} MB) exceeds memory limit ({self.max_memory_mb} MB)")
            
            # TODO: Implement actual GGUF model loading with llama-cpp-python or similar
            # For now, simulate successful loading
            logger.info(f"Loading model: {model_name} ({size_mb:.1f} MB)")
            
            # Update model info
            if model_name in self.available_models:
                self.available_models[model_name].loaded = True
            else:
                self.available_models[model_name] = ModelInfo(
                    name=model_name,
                    path=model_path,
                    size_mb=size_mb,
                    loaded=True
                )
            
            self.current_model = model_path
            logger.info(f"Successfully loaded model: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model {model_path}: {str(e)}")
            return False
    
    def _load_fallback_model(self) -> bool:
        """Load the smallest available model as fallback"""
        if not self.available_models:
            logger.error("No models available for fallback")
            return False
        
        # Sort by size and try the smallest first
        sorted_models = sorted(self.available_models.values(), key=lambda m: m.size_mb)
        
        for model_info in sorted_models:
            if self.load_model(model_info.path):
                logger.info(f"Loaded fallback model: {model_info.name}")
                return True
        
        logger.error("Failed to load any fallback model")
        return False
    
    def get_available_models(self) -> List[ModelInfo]:
        """Get list of all available models"""
        return list(self.available_models.values())
    
    def get_current_model(self) -> Optional[str]:
        """Get the currently loaded model path"""
        return self.current_model
    
    def benchmark_model(self, model_path: str) -> Dict[str, Any]:
        """
        Benchmark a specific model for performance
        
        Args:
            model_path: Path to the model to benchmark
            
        Returns:
            Dict containing benchmark results
        """
        model_name = os.path.basename(model_path)
        
        # TODO: Implement actual benchmarking
        # For now, return simulated benchmark data
        benchmark_results = {
            'model_name': model_name,
            'model_path': model_path,
            'tokens_per_second': 25.5,  # Simulated
            'memory_usage_mb': 1024,    # Simulated
            'load_time_seconds': 3.2,   # Simulated
            'inference_latency_ms': 150, # Simulated
            'quality_score': 0.85       # Simulated
        }
        
        # Update model info with performance score
        if model_name in self.available_models:
            self.available_models[model_name].performance_score = benchmark_results['quality_score']
        
        logger.info(f"Benchmarked {model_name}: {benchmark_results['tokens_per_second']} tokens/sec")
        return benchmark_results
    
    def benchmark_all_models(self) -> List[Dict[str, Any]]:
        """Benchmark all available models"""
        results = []
        
        for model_info in self.available_models.values():
            try:
                benchmark = self.benchmark_model(model_info.path)
                results.append(benchmark)
            except Exception as e:
                logger.error(f"Failed to benchmark {model_info.name}: {str(e)}")
        
        return results
    
    def get_model_recommendations(self) -> List[str]:
        """Get model recommendations based on performance and constraints"""
        recommendations = []
        
        # Filter models that fit in memory
        suitable_models = [
            model for model in self.available_models.values()
            if model.size_mb <= self.max_memory_mb
        ]
        
        # Sort by performance score if available, otherwise by size
        suitable_models.sort(
            key=lambda m: (m.performance_score or 0, -m.size_mb),
            reverse=True
        )
        
        for model in suitable_models[:3]:  # Top 3 recommendations
            recommendations.append(f"{model.name} - {model.size_mb:.1f}MB")
        
        return recommendations

# Global loader instance
_loader_instance = None

def get_llm_loader() -> GuardianLLMLoader:
    """Get the global LLM loader instance"""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = GuardianLLMLoader()
    return _loader_instance

def initialize_llm() -> bool:
    """Initialize the LLM with default model"""
    loader = get_llm_loader()
    return loader.load_default_model()

if __name__ == "__main__":
    # Test the loader
    logging.basicConfig(level=logging.INFO)
    
    loader = GuardianLLMLoader()
    print(f"Available models: {len(loader.get_available_models())}")
    
    for model in loader.get_available_models():
        print(f"  - {model.name}: {model.size_mb:.1f} MB")
    
    # Test loading default model
    if loader.load_default_model():
        print(f"Loaded default model: {loader.get_current_model()}")
    
    # Test benchmarking
    results = loader.benchmark_all_models()
    print(f"Benchmarked {len(results)} models")
    
    # Show recommendations
    recommendations = loader.get_model_recommendations()
    print("Model recommendations:")
    for rec in recommendations:
        print(f"  - {rec}")