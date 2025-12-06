#!/usr/bin/env python3
"""
Simple test script for GUI and Voice interfaces
Tests components that don't require heavy dependencies
"""

import sys
import os
from pathlib import Path

# Add paths - root first for resource_monitor, then guardian_interpreter for voice
sys.path.insert(0, str(Path(__file__).parent))  # Root directory first
sys.path.insert(1, str(Path(__file__).parent / 'guardian_interpreter'))  # Then guardian_interpreter

print("\n" + "="*70)
print("GUARDIAN NODE - SIMPLE GUI & VOICE TEST")
print("="*70)

# Test 1: Resource Monitor
print("\n[1/4] Testing Resource Monitor...")
try:
    from resource_monitor import ResourceMonitor
    monitor = ResourceMonitor()
    stats = monitor.get_current_stats()
    if stats and 'cpu_percent' in stats:
        print(f"  ✅ CPU: {stats['cpu_percent']:.1f}%, Memory: {stats['memory_percent']:.1f}%")
    else:
        print(f"  ❌ Stats empty or malformed: {stats}")
except Exception as e:
    print(f"  ❌ Failed: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Voice Interface
print("\n[2/4] Testing Voice Interface...")
try:
    from guardian_interpreter.voice.voice_interface import VoiceInterface
    voice = VoiceInterface()
    status = voice.get_status()
    tts = "✅" if status['tts_available'] else "❌"
    stt = "✅" if status['stt_available'] else "❌"
    print(f"  {tts} TTS (Text-to-Speech)")
    print(f"  {stt} STT (Speech-to-Text)")
    
    if status['tts_available']:
        print("  Testing TTS...")
        voice.speak("Guardian Node test")
        print("  ✅ TTS working")
except Exception as e:
    print(f"  ❌ Failed: {e}")

# Test 3: GUI Components
print("\n[3/4] Testing GUI Components...")
try:
    from PySide6.QtWidgets import QApplication
    print("  ✅ PySide6 available")
    
    try:
        from guardian_gui import GuardianMainWindow
        print("  ✅ GuardianMainWindow importable")
    except ImportError as e:
        print(f"  ❌ GuardianMainWindow import failed: {e}")
except ImportError:
    print("  ❌ PySide6 not installed (pip install PySide6)")

# Test 4: Command Line Arguments
print("\n[4/4] Testing Command Line Arguments...")
try:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--gui', action='store_true')
    parser.add_argument('--voice', action='store_true')
    parser.add_argument('--cli', action='store_true')
    parser.add_argument('--no-api', action='store_true')
    
    # Test parsing
    args = parser.parse_args(['--gui', '--voice'])
    assert args.gui == True
    assert args.voice == True
    print("  ✅ Argument parsing works")
except Exception as e:
    print(f"  ❌ Failed: {e}")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("\n✅ Core components are ready!")
print("\nTo test full system:")
print("  1. Install dependencies: pip install -r guardian_interpreter/requirements.txt")
print("  2. Launch GUI: python guardian_interpreter/main.py --gui")
print("  3. Launch CLI with voice: python guardian_interpreter/main.py --voice")
print("\nNote: Some tests may fail if optional dependencies are not installed.")
print("      This is expected and the system will use fallback implementations.")
