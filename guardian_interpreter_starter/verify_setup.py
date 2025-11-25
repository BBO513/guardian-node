#!/usr/bin/env python3
"""
Guardian Node Voice System Setup Verification
Comprehensive system check and validation
"""

import sys
import os
from pathlib import Path
import importlib.util

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

class VerificationResults:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
    
    def add_pass(self, test_name, message=""):
        self.passed.append((test_name, message))
        print(f"{GREEN}✅ PASS{RESET}: {test_name}")
        if message:
            print(f"         {message}")
    
    def add_fail(self, test_name, message=""):
        self.failed.append((test_name, message))
        print(f"{RED}❌ FAIL{RESET}: {test_name}")
        if message:
            print(f"         {RED}{message}{RESET}")
    
    def add_warning(self, test_name, message=""):
        self.warnings.append((test_name, message))
        print(f"{YELLOW}⚠️  WARN{RESET}: {test_name}")
        if message:
            print(f"         {YELLOW}{message}{RESET}")
    
    def print_summary(self):
        print("\n" + "=" * 70)
        print(f"{BOLD}VERIFICATION SUMMARY{RESET}")
        print("=" * 70)
        print(f"{GREEN}Passed{RESET}:   {len(self.passed)}")
        print(f"{RED}Failed{RESET}:   {len(self.failed)}")
        print(f"{YELLOW}Warnings{RESET}: {len(self.warnings)}")
        print("=" * 70)
        
        if len(self.failed) == 0 and len(self.warnings) == 0:
            print(f"\n{GREEN}{BOLD}🎉 All checks passed! Voice system is ready.{RESET}\n")
            return 0
        elif len(self.failed) == 0:
            print(f"\n{YELLOW}{BOLD}⚠️  System functional but has warnings.{RESET}\n")
            return 0
        else:
            print(f"\n{RED}{BOLD}❌ System has critical failures.{RESET}\n")
            return 1

def print_header():
    print(f"\n{BLUE}{BOLD}{'=' * 70}{RESET}")
    print(f"{BLUE}{BOLD}   Guardian Node Voice System - Setup Verification{RESET}")
    print(f"{BLUE}{BOLD}{'=' * 70}{RESET}\n")

def check_python_version(results):
    """Check Python version compatibility"""
    print(f"\n{BOLD}1. Python Environment{RESET}")
    print("-" * 70)
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major == 3 and version.minor >= 8:
        results.add_pass("Python Version", f"Python {version_str} (compatible)")
    else:
        results.add_fail("Python Version", f"Python {version_str} (requires 3.8+)")

def check_dependencies(results):
    """Check required Python packages"""
    print(f"\n{BOLD}2. Python Dependencies{RESET}")
    print("-" * 70)
    
    required_packages = {
        'edge_tts': 'edge-tts',
        'pygame': 'pygame',
        'pyttsx3': 'pyttsx3',
        'yaml': 'pyyaml'
    }
    
    for module_name, package_name in required_packages.items():
        spec = importlib.util.find_spec(module_name)
        if spec is not None:
            try:
                module = importlib.import_module(module_name)
                version = getattr(module, '__version__', 'unknown')
                results.add_pass(f"Package: {package_name}", f"Version {version}")
            except Exception as e:
                results.add_warning(f"Package: {package_name}", f"Installed but import failed: {e}")
        else:
            results.add_fail(f"Package: {package_name}", f"Not installed. Run: pip install {package_name}")

def check_directory_structure(results):
    """Check required directories exist"""
    print(f"\n{BOLD}3. Directory Structure{RESET}")
    print("-" * 70)
    
    required_dirs = [
        ("voice/", "Voice module directory"),
        ("skills/", "Skills directory"),
        ("skills/audio_explanations/", "Audio explanations directory"),
        ("skills/audio_explanations/audio_files/", "Audio files storage"),
        ("skills/audio_explanations/cache/", "Audio cache directory"),
    ]
    
    for dir_path, description in required_dirs:
        full_path = Path(dir_path)
        if full_path.exists() and full_path.is_dir():
            results.add_pass(description, f"{dir_path}")
        else:
            results.add_fail(description, f"{dir_path} does not exist")

def check_voice_module_files(results):
    """Check voice module files"""
    print(f"\n{BOLD}4. Voice Module Files{RESET}")
    print("-" * 70)
    
    voice_files = [
        ("voice/__init__.py", "Module initialization"),
        ("voice/voice_input.py", "Voice input handler"),
        ("voice/voice_output.py", "Voice output handler"),
        ("voice/voice_interface.py", "Voice interface"),
    ]
    
    for file_path, description in voice_files:
        full_path = Path(file_path)
        if full_path.exists() and full_path.is_file():
            size = full_path.stat().st_size
            results.add_pass(description, f"{file_path} ({size} bytes)")
        else:
            results.add_fail(description, f"{file_path} does not exist")

def check_configuration(results):
    """Check configuration file"""
    print(f"\n{BOLD}5. Configuration File{RESET}")
    print("-" * 70)
    
    config_path = Path("config.yaml")
    
    if not config_path.exists():
        results.add_fail("config.yaml", "File does not exist")
        return
    
    results.add_pass("config.yaml exists", f"{config_path}")
    
    try:
        import yaml
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Check required sections
        required_sections = [
            ('voice_system', 'Voice system settings'),
            ('voice_output', 'Voice output settings'),
            ('voice_profiles', 'Voice profiles'),
            ('audio', 'Audio settings'),
            ('skills', 'Skills configuration'),
        ]
        
        for section, description in required_sections:
            if section in config:
                results.add_pass(description, f"Section '{section}' present")
            else:
                results.add_fail(description, f"Section '{section}' missing")
        
        # Check voice system is enabled
        if config.get('voice_system', {}).get('enabled') == True:
            results.add_pass("Voice system enabled", "voice_system.enabled = true")
        else:
            results.add_warning("Voice system disabled", "voice_system.enabled = false")
        
        # Check voice profiles
        profiles = config.get('voice_profiles', {})
        expected_profiles = ['child', 'teen', 'adult']
        for profile in expected_profiles:
            if profile in profiles:
                voice_name = profiles[profile].get('voice_name', 'unknown')
                results.add_pass(f"Voice profile: {profile}", f"{voice_name}")
            else:
                results.add_fail(f"Voice profile: {profile}", "Profile not configured")
        
    except yaml.YAMLError as e:
        results.add_fail("config.yaml parsing", f"YAML syntax error: {e}")
    except Exception as e:
        results.add_fail("config.yaml validation", f"Error: {e}")

def check_audio_files(results):
    """Check audio files"""
    print(f"\n{BOLD}6. Audio Files{RESET}")
    print("-" * 70)
    
    audio_dir = Path("skills/audio_explanations/audio_files")
    
    if not audio_dir.exists():
        results.add_fail("Audio directory", f"{audio_dir} does not exist")
        return
    
    # Expected audio files
    risk_types = ['phishing', 'malware', 'weak_password', 'suspicious_network']
    age_groups = ['child', 'teen', 'adult']
    
    expected_files = []
    for risk in risk_types:
        for age in age_groups:
            expected_files.append(f"{risk}_{age}.mp3")
    
    existing_files = list(audio_dir.glob("*.mp3"))
    existing_names = [f.name for f in existing_files]
    
    found_count = 0
    total_size = 0
    
    for expected in expected_files:
        if expected in existing_names:
            file_path = audio_dir / expected
            size = file_path.stat().st_size
            total_size += size
            found_count += 1
    
    if found_count == len(expected_files):
        size_mb = total_size / 1024 / 1024
        results.add_pass("Audio files complete", f"{found_count}/{len(expected_files)} files ({size_mb:.2f} MB)")
    elif found_count > 0:
        results.add_warning("Audio files incomplete", f"{found_count}/{len(expected_files)} files found. Run audio_pre_recorder.py")
    else:
        results.add_fail("Audio files missing", f"0/{len(expected_files)} files. Run audio_pre_recorder.py")
    
    # Check metadata
    metadata_path = Path("skills/audio_explanations/metadata.json")
    if metadata_path.exists():
        results.add_pass("Metadata file", f"{metadata_path}")
    else:
        results.add_warning("Metadata file", f"{metadata_path} not found")

def check_scripts(results):
    """Check required scripts"""
    print(f"\n{BOLD}7. Scripts and Tools{RESET}")
    print("-" * 70)
    
    scripts = [
        ("demo_voice_system.py", "Voice system demo"),
        ("test_voice_explain.py", "Voice explanation test"),
        ("setup_offline_voice.bat", "Windows setup script"),
    ]
    
    for script, description in scripts:
        script_path = Path(script)
        if script_path.exists():
            results.add_pass(description, f"{script}")
        else:
            results.add_warning(description, f"{script} not found")

def check_audio_system(results):
    """Check audio system (Linux only)"""
    print(f"\n{BOLD}8. Audio System (Raspberry Pi){RESET}")
    print("-" * 70)
    
    if sys.platform != 'linux':
        results.add_warning("Audio system check", "Skipped (not Linux)")
        return
    
    # Check if pygame can initialize audio
    try:
        import pygame
        pygame.mixer.init()
        results.add_pass("Pygame audio initialization", "Audio system available")
        pygame.mixer.quit()
    except Exception as e:
        results.add_fail("Pygame audio initialization", f"Failed: {e}")

def check_permissions(results):
    """Check file permissions"""
    print(f"\n{BOLD}9. File Permissions{RESET}")
    print("-" * 70)
    
    # Check if we can write to audio directories
    audio_dir = Path("skills/audio_explanations/audio_files")
    cache_dir = Path("skills/audio_explanations/cache")
    
    for directory in [audio_dir, cache_dir]:
        if directory.exists():
            if os.access(directory, os.W_OK):
                results.add_pass(f"Write access: {directory}", "Writable")
            else:
                results.add_fail(f"Write access: {directory}", "No write permission")
        else:
            results.add_warning(f"Directory check: {directory}", "Directory does not exist")

def check_documentation(results):
    """Check documentation files"""
    print(f"\n{BOLD}10. Documentation{RESET}")
    print("-" * 70)
    
    docs = [
        ("../VOICE_INTEGRATION_GUIDE.md", "Integration guide"),
        ("../WINDOWS_TO_PI_WORKFLOW.md", "Deployment workflow"),
        ("../VOICE_QUICK_REFERENCE.md", "Quick reference"),
    ]
    
    for doc, description in docs:
        doc_path = Path(doc)
        if doc_path.exists():
            size_kb = doc_path.stat().st_size / 1024
            results.add_pass(description, f"{doc} ({size_kb:.1f} KB)")
        else:
            results.add_warning(description, f"{doc} not found")

def print_next_steps(results):
    """Print recommended next steps"""
    print(f"\n{BOLD}Next Steps:{RESET}")
    print("-" * 70)
    
    if len(results.failed) > 0:
        print("\n❌ Critical issues found. Fix the following:\n")
        for test_name, message in results.failed:
            print(f"  • {test_name}")
            if message:
                print(f"    → {message}")
        print(f"\n{BOLD}Refer to WINDOWS_TO_PI_WORKFLOW.md for setup instructions.{RESET}")
    
    elif len(results.warnings) > 0:
        print("\n⚠️  Warnings found. Consider addressing:\n")
        for test_name, message in results.warnings:
            print(f"  • {test_name}")
            if message:
                print(f"    → {message}")
    
    else:
        print("\n✅ System is ready! Try these commands:\n")
        print("  • List audio files:")
        print("    python3 skills/offline_voice_explain.py --list")
        print()
        print("  • Play explanation:")
        print("    python3 skills/offline_voice_explain.py --risk phishing --age teen")
        print()
        print("  • Run demo:")
        print("    python3 demo_voice_system.py")
        print()
        print(f"{BOLD}Refer to VOICE_QUICK_REFERENCE.md for more commands.{RESET}")

def main():
    print_header()
    
    results = VerificationResults()
    
    # Run all checks
    check_python_version(results)
    check_dependencies(results)
    check_directory_structure(results)
    check_voice_module_files(results)
    check_configuration(results)
    check_audio_files(results)
    check_scripts(results)
    check_audio_system(results)
    check_permissions(results)
    check_documentation(results)
    
    # Print summary
    exit_code = results.print_summary()
    
    # Print next steps
    print_next_steps(results)
    
    print()
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
