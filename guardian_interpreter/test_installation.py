#!/usr/bin/env python3
"""
Test script to verify Guardian Node installation
"""

import sys
import os
import importlib.util

def check_module(module_name, package_name=None):
    """Check if a module is installed"""
    if package_name is None:
        package_name = module_name
    
    try:
        importlib.import_module(module_name)
        print(f"✅ {package_name} is installed")
        return True
    except ImportError:
        print(f"❌ {package_name} is NOT installed")
        return False

def check_file(file_path, description):
    """Check if a file exists"""
    if os.path.exists(file_path):
        print(f"✅ {description} found: {file_path}")
        return True
    else:
        print(f"❌ {description} NOT found: {file_path}")
        return False

def main():
    """Main test function"""
    print("🛡️  Guardian Node Installation Test")
    print("=" * 50)
    
    # Check Python version
    python_version = sys.version.split()[0]
    print(f"Python version: {python_version}")
    
    # Check core dependencies
    core_modules = [
        ('yaml', 'pyyaml'),
        ('psutil', 'psutil'),
        ('requests', 'requests'),
        ('llama_cpp', 'llama-cpp-python')
    ]
    
    print("\nChecking core dependencies:")
    core_success = all(check_module(module, package) for module, package in core_modules)
    
    # Check GUI dependencies
    print("\nChecking GUI dependencies:")
    gui_success = check_module('PySide6', 'PySide6')
    
    # Check family assistant dependencies
    print("\nChecking family assistant dependencies:")
    family_modules = [
        ('cryptography', 'cryptography')
    ]
    family_success = all(check_module(module, package) for module, package in family_modules)
    
    # Check voice interface dependencies (optional)
    print("\nChecking voice interface dependencies (optional):")
    voice_modules = [
        ('speech_recognition', 'speechrecognition'),
        ('pyttsx3', 'pyttsx3')
    ]
    voice_success = all(check_module(module, package) for module, package in voice_modules)
    
    # Check monitoring dependencies
    print("\nChecking monitoring dependencies:")
    monitoring_success = check_module('prometheus_client', 'prometheus-client')
    
    # Check for model file
    print("\nChecking for model file:")
    model_paths = [
        'models/phi-3-mini-4k-instruct-q4.gguf',
        'models/your-model.gguf'
    ]
    model_success = any(check_file(path, "Model file") for path in model_paths)
    
    # Check for configuration file
    print("\nChecking for configuration file:")
    config_success = check_file('config.yaml', "Configuration file")
    
    # Summary
    print("\n" + "=" * 50)
    print("Installation Test Summary:")
    print(f"Core dependencies: {'✅ PASS' if core_success else '❌ FAIL'}")
    print(f"GUI dependencies: {'✅ PASS' if gui_success else '❌ FAIL'}")
    print(f"Family assistant: {'✅ PASS' if family_success else '❌ FAIL'}")
    print(f"Voice interface: {'✅ PASS' if voice_success else '⚠️  OPTIONAL'}")
    print(f"Monitoring: {'✅ PASS' if monitoring_success else '⚠️  OPTIONAL'}")
    print(f"Model file: {'✅ PASS' if model_success else '❌ FAIL'}")
    print(f"Configuration: {'✅ PASS' if config_success else '❌ FAIL'}")
    
    # Overall result
    required_success = core_success and family_success and config_success
    if required_success:
        print("\n✅ Installation PASSED! Guardian Node is ready to run.")
        if not model_success:
            print("⚠️  Warning: No model file found. Download a GGUF model to use the LLM features.")
        if not gui_success:
            print("⚠️  Warning: GUI dependencies not installed. Use --no-gui option or install PySide6.")
        return 0
    else:
        print("\n❌ Installation FAILED! Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())