#!/usr/bin/env python3
"""Test Gemma 2 2B LLM for Guardian Node"""
import os
import sys
import time
import yaml
from pathlib import Path
from llama_cpp import Llama

def load_config():
    """Load Guardian Node config"""
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def test_gemma2_loading():
    """Test loading Gemma 2 2B model"""
    print("=" * 60)
    print("Test 1: Loading Gemma 2 2B Model")
    print("=" * 60)
    
    config = load_config()
    model_path = config['llm']['models']['default']['path']
    context_length = config['llm']['models']['default']['context_length']
    threads = config['llm']['models']['default']['threads']
    
    full_path = Path(__file__).parent / model_path
    
    if not full_path.exists():
        print(f"✗ Model file not found: {full_path}")
        return None, False
    
    print(f"Model path: {full_path}")
    print(f"Context length: {context_length}")
    print(f"Threads: {threads}")
    print(f"Model size: {full_path.stat().st_size / (1024**3):.2f} GB")
    
    try:
        print("\nLoading model...")
        start_time = time.time()
        
        llm = Llama(
            model_path=str(full_path),
            n_ctx=context_length,
            n_threads=threads,
            verbose=False
        )
        
        load_time = time.time() - start_time
        print(f"✓ Model loaded successfully in {load_time:.2f} seconds")
        return llm, True
        
    except Exception as e:
        print(f"✗ Failed to load model: {e}")
        return None, False

def test_gemma2_inference(llm):
    """Test Gemma 2 2B inference"""
    print("\n" + "=" * 60)
    print("Test 2: Gemma 2 2B Inference Test")
    print("=" * 60)
    
    # Gemma 2 prompt format
    test_prompts = [
        {
            "name": "Security Question",
            "prompt": "<bos><start_of_turn>user\nWhat are the top 3 cybersecurity threats families should worry about in 2024?<end_of_turn>\n<start_of_turn>model\n"
        },
        {
            "name": "Child Safety",
            "prompt": "<bos><start_of_turn>user\nHow can parents keep their children safe online?<end_of_turn>\n<start_of_turn>model\n"
        },
        {
            "name": "Guardian Node Introduction",
            "prompt": "<bos><start_of_turn>user\nYou are Guardian Node, a family cybersecurity assistant. Introduce yourself in one sentence.<end_of_turn>\n<start_of_turn>model\n"
        }
    ]
    
    results = []
    
    for test in test_prompts:
        print(f"\n{test['name']}:")
        print("-" * 60)
        
        try:
            start_time = time.time()
            
            response = llm(
                test['prompt'],
                max_tokens=256,
                temperature=0.7,
                stop=["<end_of_turn>", "<start_of_turn>"],
                echo=False
            )
            
            inference_time = time.time() - start_time
            generated_text = response['choices'][0]['text'].strip()
            tokens_generated = response['usage']['completion_tokens']
            tokens_per_sec = tokens_generated / inference_time if inference_time > 0 else 0
            
            print(f"Response: {generated_text}")
            print(f"Time: {inference_time:.2f}s | Tokens: {tokens_generated} | Speed: {tokens_per_sec:.1f} tok/s")
            
            results.append({
                "test": test['name'],
                "passed": True,
                "time": inference_time,
                "tokens": tokens_generated,
                "speed": tokens_per_sec
            })
            
        except Exception as e:
            print(f"✗ Inference failed: {e}")
            results.append({"test": test['name'], "passed": False})
    
    return results

def test_memory_usage():
    """Test memory usage comparison"""
    print("\n" + "=" * 60)
    print("Test 3: Memory Usage Comparison")
    print("=" * 60)
    
    models_dir = Path(__file__).parent / "models"
    
    phi3_path = models_dir / "Phi-3-mini-4k-instruct-q4.gguf"
    gemma2_path = models_dir / "gemma-2-2b-it-Q4_K_M.gguf"
    
    print(f"\nPhi-3 Mini (old):")
    if phi3_path.exists():
        size_gb = phi3_path.stat().st_size / (1024**3)
        print(f"  Size: {size_gb:.2f} GB")
        print(f"  Context: 4096 tokens")
    else:
        print("  Not found")
    
    print(f"\nGemma 2 2B (new):")
    if gemma2_path.exists():
        size_gb = gemma2_path.stat().st_size / (1024**3)
        print(f"  Size: {size_gb:.2f} GB")
        print(f"  Context: 8192 tokens")
        
        if phi3_path.exists():
            size_diff = (phi3_path.stat().st_size - gemma2_path.stat().st_size) / (1024**2)
            print(f"  Savings: {size_diff:.0f} MB smaller than Phi-3")
    else:
        print("  Not found")
    
    return True

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Guardian Node - Gemma 2 2B LLM Test Suite")
    print("=" * 60)
    
    # Test 1: Load model
    llm, load_success = test_gemma2_loading()
    
    if not load_success or llm is None:
        print("\n✗ Model loading failed. Cannot continue with inference tests.")
        sys.exit(1)
    
    # Test 2: Inference
    inference_results = test_gemma2_inference(llm)
    
    # Test 3: Memory comparison
    test_memory_usage()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    total_tests = len(inference_results) + 1  # +1 for loading test
    passed_tests = sum(1 for r in inference_results if r.get('passed', False)) + (1 if load_success else 0)
    
    print(f"\nModel Loading: {'✓ PASSED' if load_success else '✗ FAILED'}")
    
    for result in inference_results:
        if result.get('passed'):
            print(f"{result['test']}: ✓ PASSED ({result['speed']:.1f} tok/s)")
        else:
            print(f"{result['test']}: ✗ FAILED")
    
    print(f"\n{'='*60}")
    print(f"Total: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("✓ All tests PASSED! Gemma 2 2B is ready for production.")
    else:
        print(f"✗ {total_tests - passed_tests} test(s) failed.")
    
    print("=" * 60)
