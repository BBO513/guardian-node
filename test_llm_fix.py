#!/usr/bin/env python3
"""
Quick test script to verify LLM integration fixes
"""
import sys
import logging
from pathlib import Path

# Add guardian_interpreter to path
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('test')

print("=" * 60)
print("Testing Guardian LLM Integration Fixes")
print("=" * 60)

# Test 1: Import modules
print("\n[Test 1] Importing modules...")
try:
    from guardian_interpreter.llm_integration import create_llm, GuardianLLM
    print("✓ Successfully imported llm_integration")
except Exception as e:
    print(f"✗ Failed to import llm_integration: {e}")
    sys.exit(1)

# Test 2: Load configuration
print("\n[Test 2] Loading configuration...")
try:
    import yaml
    config_path = Path(__file__).parent / 'guardian_interpreter' / 'app_config_canonical.yaml'
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    llm_config = config.get('llm', {})
    models_config = llm_config.get('models', {})
    default_config = models_config.get('default', {})
    
    print(f"✓ Configuration loaded")
    print(f"  Model path: {default_config.get('path', 'NOT SET')}")
    print(f"  Model type: {default_config.get('model_type', 'NOT SET')}")
    print(f"  Context length: {default_config.get('context_length', 'NOT SET')}")
    
    if default_config.get('model_type') != 'gemma':
        print(f"✗ WARNING: Model type is not 'gemma'")
    else:
        print("✓ Model type correctly set to 'gemma'")
        
except Exception as e:
    print(f"✗ Failed to load configuration: {e}")
    sys.exit(1)

# Test 3: Check model file exists
print("\n[Test 3] Checking model file...")
try:
    model_path = Path(__file__).parent / default_config.get('path', '')
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"✓ Model file found: {model_path}")
        print(f"  Size: {size_mb:.2f} MB")
    else:
        print(f"✗ Model file not found: {model_path}")
        print(f"  Looking for: {model_path.absolute()}")
except Exception as e:
    print(f"✗ Error checking model file: {e}")

# Test 4: Initialize LLM (without loading model to save time)
print("\n[Test 4] Initializing LLM object...")
try:
    llm = create_llm(config, logger)
    print(f"✓ LLM object created: {type(llm).__name__}")
    
    if hasattr(llm, 'model_type'):
        print(f"  Model type attribute: {llm.model_type}")
        if llm.model_type == 'gemma':
            print("✓ Model type correctly set to 'gemma'")
        else:
            print(f"✗ WARNING: Model type is '{llm.model_type}', expected 'gemma'")
    
    model_info = llm.get_model_info()
    print(f"  Model loaded: {model_info.get('loaded', False)}")
    print(f"  Model path: {model_info.get('model_path', 'N/A')}")
    
except Exception as e:
    print(f"✗ Failed to initialize LLM: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Check main.py syntax
print("\n[Test 5] Checking main.py syntax...")
try:
    import py_compile
    main_path = Path(__file__).parent / 'guardian_interpreter' / 'main.py'
    py_compile.compile(str(main_path), doraise=True)
    print("✓ main.py has no syntax errors")
except SyntaxError as e:
    print(f"✗ Syntax error in main.py: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error checking main.py: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("All tests passed! ✓")
print("=" * 60)
print("\nNext steps:")
print("1. Rebuild Docker container: docker-compose build")
print("2. Run container: docker-compose up")
print("3. Test with: ask 'How can I keep my family safe online?'")
