#!/usr/bin/env python3
"""
Voice Explain Test Script
Tests the voice_explain.py skill with espeak text-to-speech functionality
"""

import os
import sys
import subprocess
import time
from datetime import datetime
from pathlib import Path

def log_message(message, log_file="test_voice.log"):
    """Log message to file with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Warning: Could not write to log file: {e}")
    
    print(message)

def check_espeak_installation():
    """Check if espeak is installed and available"""
    log_message("🔍 Checking espeak installation...")
    
    try:
        # Try to run espeak with version flag
        result = subprocess.run(
            ["espeak", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            version_info = result.stdout.strip()
            log_message(f"✅ espeak found: {version_info}")
            return True
        else:
            log_message("❌ espeak command failed")
            return False
            
    except FileNotFoundError:
        log_message("❌ espeak not found in PATH")
        return False
    except subprocess.TimeoutExpired:
        log_message("⏰ espeak version check timed out")
        return False
    except Exception as e:
        log_message(f"❌ Error checking espeak: {e}")
        return False

def suggest_espeak_installation():
    """Provide installation suggestions for espeak"""
    log_message("\n📦 espeak Installation Required")
    log_message("=" * 50)
    
    # Check if chocolatey is available
    choco_available = False
    try:
        result = subprocess.run(
            ["choco", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            choco_available = True
            log_message("✅ Chocolatey detected")
    except:
        pass
    
    if choco_available:
        log_message("🍫 Recommended installation (using Chocolatey):")
        log_message("   choco install espeak")
        log_message("\nRun this command in an Administrator PowerShell/CMD:")
        log_message("   1. Open PowerShell as Administrator")
        log_message("   2. Run: choco install espeak")
        log_message("   3. Restart your terminal")
    else:
        log_message("📋 Installation options:")
        log_message("1. Install Chocolatey first, then espeak:")
        log_message("   - Visit: https://chocolatey.org/install")
        log_message("   - Then run: choco install espeak")
        log_message("\n2. Manual installation:")
        log_message("   - Download from: http://espeak.sourceforge.net/download.html")
        log_message("   - Add to PATH environment variable")
        log_message("\n3. Alternative TTS options:")
        log_message("   - Windows built-in SAPI (PowerShell: Add-Type -AssemblyName System.Speech)")
        log_message("   - Python pyttsx3: pip install pyttsx3")

def check_voice_explain_file():
    """Check if voice_explain.py exists in the skills directory"""
    log_message("📁 Checking voice_explain.py file...")
    
    voice_explain_path = Path("guardian_interpreter_starter/skills/voice_explain.py")
    
    if voice_explain_path.exists():
        log_message(f"✅ Found: {voice_explain_path}")
        return str(voice_explain_path)
    
    # Try alternative locations
    alternative_paths = [
        Path("skills/voice_explain.py"),
        Path("voice_explain.py"),
        Path("guardian_interpreter_starter/voice_explain.py")
    ]
    
    for path in alternative_paths:
        if path.exists():
            log_message(f"✅ Found: {path}")
            return str(path)
    
    log_message("❌ voice_explain.py not found in expected locations")
    log_message("   Searched:")
    log_message(f"   - {voice_explain_path}")
    for path in alternative_paths:
        log_message(f"   - {path}")
    
    return None

def test_voice_explain_direct():
    """Test voice_explain.py directly without espeak"""
    log_message("\n🧪 Testing voice_explain.py directly...")
    
    voice_explain_path = check_voice_explain_file()
    if not voice_explain_path:
        return False
    
    try:
        # Test the script with sample parameters
        result = subprocess.run(
            [sys.executable, voice_explain_path, "--risk", "phishing", "--age", "teen"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.getcwd()
        )
        
        log_message(f"Exit code: {result.returncode}")
        
        if result.stdout:
            log_message("📄 Output:")
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    log_message(f"   {line}")
        
        if result.stderr:
            log_message("⚠️  Errors:")
            for line in result.stderr.strip().split('\n'):
                if line.strip():
                    log_message(f"   {line}")
        
        if result.returncode == 0:
            log_message("✅ voice_explain.py executed successfully")
            return True
        else:
            log_message("❌ voice_explain.py failed")
            return False
            
    except subprocess.TimeoutExpired:
        log_message("⏰ voice_explain.py timed out")
        return False
    except Exception as e:
        log_message(f"❌ Error running voice_explain.py: {e}")
        return False

def test_voice_explain_with_espeak():
    """Test voice_explain.py with espeak piping"""
    log_message("\n🔊 Testing voice_explain.py with espeak...")
    
    voice_explain_path = check_voice_explain_file()
    if not voice_explain_path:
        return False
    
    try:
        # Create the full command pipeline
        # python skills/voice_explain.py --risk "phishing" --age "teen" | espeak
        
        # First process: voice_explain.py
        voice_process = subprocess.Popen(
            [sys.executable, voice_explain_path, "--risk", "phishing", "--age", "teen"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.getcwd()
        )
        
        # Second process: espeak
        espeak_process = subprocess.Popen(
            ["espeak"],
            stdin=voice_process.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Close the first process's stdout to allow proper piping
        voice_process.stdout.close()
        
        # Wait for both processes to complete
        try:
            espeak_output, espeak_error = espeak_process.communicate(timeout=60)
            voice_process.wait(timeout=10)
            
            log_message(f"voice_explain.py exit code: {voice_process.returncode}")
            log_message(f"espeak exit code: {espeak_process.returncode}")
            
            # Check for errors from voice_explain.py
            if voice_process.stderr:
                voice_error = voice_process.stderr.read()
                if voice_error.strip():
                    log_message("⚠️  voice_explain.py errors:")
                    for line in voice_error.strip().split('\n'):
                        if line.strip():
                            log_message(f"   {line}")
            
            # Check for errors from espeak
            if espeak_error and espeak_error.strip():
                log_message("⚠️  espeak errors:")
                for line in espeak_error.strip().split('\n'):
                    if line.strip():
                        log_message(f"   {line}")
            
            if voice_process.returncode == 0 and espeak_process.returncode == 0:
                log_message("✅ Voice explanation with espeak completed successfully")
                log_message("🔊 Audio should have been played through speakers")
                return True
            else:
                log_message("❌ Pipeline failed")
                return False
                
        except subprocess.TimeoutExpired:
            log_message("⏰ Pipeline timed out")
            voice_process.kill()
            espeak_process.kill()
            return False
            
    except Exception as e:
        log_message(f"❌ Error in pipeline: {e}")
        return False

def test_alternative_tts():
    """Test alternative text-to-speech if espeak is not available"""
    log_message("\n🎤 Testing alternative TTS (Windows SAPI)...")
    
    voice_explain_path = check_voice_explain_file()
    if not voice_explain_path:
        return False
    
    try:
        # Get text from voice_explain.py
        result = subprocess.run(
            [sys.executable, voice_explain_path, "--risk", "phishing", "--age", "teen"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.getcwd()
        )
        
        if result.returncode != 0 or not result.stdout.strip():
            log_message("❌ Could not get text from voice_explain.py")
            return False
        
        text_to_speak = result.stdout.strip()
        log_message(f"📝 Text to speak: {text_to_speak[:100]}...")
        
        # Try Windows SAPI via PowerShell
        powershell_command = f'''
Add-Type -AssemblyName System.Speech
$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer
$speak.Speak("{text_to_speak.replace('"', '""')}")
'''
        
        log_message("🔊 Attempting Windows SAPI TTS...")
        sapi_result = subprocess.run(
            ["powershell", "-Command", powershell_command],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if sapi_result.returncode == 0:
            log_message("✅ Windows SAPI TTS completed successfully")
            return True
        else:
            log_message("❌ Windows SAPI TTS failed")
            if sapi_result.stderr:
                log_message(f"   Error: {sapi_result.stderr}")
            return False
            
    except Exception as e:
        log_message(f"❌ Error with alternative TTS: {e}")
        return False

def main():
    """Main test execution"""
    log_message("🛡️  Voice Explain Test Script")
    log_message("=" * 50)
    log_message("Testing voice_explain.py with text-to-speech functionality")
    
    # Initialize log file
    log_file = "test_voice.log"
    if os.path.exists(log_file):
        # Archive previous log
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"test_voice_{timestamp}.log"
        try:
            os.rename(log_file, archive_name)
            log_message(f"📋 Previous log archived as: {archive_name}")
        except:
            pass
    
    # Test sequence
    success_count = 0
    total_tests = 0
    
    # Test 1: Check if voice_explain.py exists and runs
    total_tests += 1
    if test_voice_explain_direct():
        success_count += 1
    
    # Test 2: Check espeak installation
    espeak_available = check_espeak_installation()
    
    if espeak_available:
        # Test 3: Test with espeak
        total_tests += 1
        if test_voice_explain_with_espeak():
            success_count += 1
    else:
        # Suggest espeak installation
        suggest_espeak_installation()
        
        # Test 3: Try alternative TTS
        total_tests += 1
        if test_alternative_tts():
            success_count += 1
    
    # Final summary
    log_message("\n" + "=" * 50)
    log_message("🎯 TEST SUMMARY")
    log_message("=" * 50)
    log_message(f"Tests passed: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        log_message("🎉 All tests passed!")
        log_message("✅ voice_explain.py is working correctly")
        if espeak_available:
            log_message("🔊 espeak integration is functional")
        else:
            log_message("🎤 Alternative TTS is working")
    else:
        log_message("⚠️  Some tests failed")
        if not espeak_available:
            log_message("💡 Consider installing espeak for better TTS support")
    
    log_message(f"\n📋 Full test log saved to: {log_file}")
    
    return success_count == total_tests

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Test cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)