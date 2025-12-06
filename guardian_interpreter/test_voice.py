#!/usr/bin/env python3
"""Test voice interface for Guardian Node"""
import subprocess
import os

def test_tts_male():
    """Test male voice TTS"""
    print("Testing male voice (espeak-ng)...")
    try:
        subprocess.run([
            'espeak-ng', 
            '-v', 'en+m3',  # Male voice
            'Hello, I am Guardian Node. Male voice test successful.'
        ], check=True)
        print("✓ Male voice test PASSED")
        return True
    except Exception as e:
        print(f"✗ Male voice test FAILED: {e}")
        return False

def test_tts_female():
    """Test female voice TTS"""
    print("\nTesting female voice (espeak-ng)...")
    try:
        subprocess.run([
            'espeak-ng', 
            '-v', 'en+f3',  # Female voice
            'Hello, I am Guardian Node. Female voice test successful.'
        ], check=True)
        print("✓ Female voice test PASSED")
        return True
    except Exception as e:
        print(f"✗ Female voice test FAILED: {e}")
        return False

def test_available_voices():
    """List available voices"""
    print("\nAvailable voices:")
    try:
        result = subprocess.run(['espeak-ng', '--voices'], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        return True
    except Exception as e:
        print(f"✗ Failed to list voices: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Guardian Node Voice Interface Test")
    print("=" * 50)
    
    results = []
    results.append(("Male Voice", test_tts_male()))
    results.append(("Female Voice", test_tts_female()))
    results.append(("Voice List", test_available_voices()))
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print("=" * 50)
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    if all_passed:
        print("\n✓ All voice tests PASSED!")
    else:
        print("\n✗ Some voice tests FAILED")
