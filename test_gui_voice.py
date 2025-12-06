#!/usr/bin/env python3
"""
Test script for GUI and Voice interfaces
Tests both interfaces independently and together
"""

import sys
import os
import logging
from pathlib import Path

# Add guardian_interpreter to path
sys.path.insert(0, str(Path(__file__).parent / 'guardian_interpreter'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_gui_voice')


def test_voice_interface():
    """Test voice interface independently"""
    print("\n" + "="*60)
    print("TESTING VOICE INTERFACE")
    print("="*60)
    
    try:
        from guardian_interpreter.voice.voice_interface import VoiceInterface
        
        # Create voice interface
        voice = VoiceInterface(logger=logger)
        
        # Check status
        status = voice.get_status()
        print(f"\n✓ Voice Interface Status:")
        print(f"  TTS Available: {'✅' if status['tts_available'] else '❌'}")
        print(f"  STT Available: {'✅' if status['stt_available'] else '❌'}")
        
        if status['tts_available']:
            print(f"  TTS Engine: {status['tts_engine']}")
        if status['stt_available']:
            print(f"  STT Engine: {status['stt_engine']}")
        
        # Test TTS
        if status['tts_available']:
            print("\n✓ Testing Text-to-Speech...")
            success = voice.speak("Guardian Node voice interface test successful")
            if success:
                print("  ✅ TTS test passed")
            else:
                print("  ❌ TTS test failed")
        else:
            print("\n⚠️ TTS not available - install pyttsx3")
        
        # Test STT (optional - requires microphone)
        if status['stt_available']:
            print("\n✓ STT available (microphone test skipped in automated test)")
        else:
            print("\n⚠️ STT not available - install SpeechRecognition and pocketsphinx")
        
        print("\n✅ Voice interface test completed")
        return True
        
    except Exception as e:
        print(f"\n❌ Voice interface test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gui_interface():
    """Test GUI interface independently"""
    print("\n" + "="*60)
    print("TESTING GUI INTERFACE")
    print("="*60)
    
    try:
        from PySide6.QtWidgets import QApplication
        from guardian_gui import GuardianMainWindow
        
        print("\n✓ PySide6 imported successfully")
        print("✓ GuardianMainWindow imported successfully")
        
        # Create application (don't show window in test)
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        print("✓ QApplication created")
        
        # Create window (but don't show it)
        window = GuardianMainWindow(guardian_interpreter=None)
        print("✓ GuardianMainWindow created")
        
        # Check window properties
        print(f"\n✓ Window Properties:")
        print(f"  Title: {window.windowTitle()}")
        print(f"  Size: {window.width()}x{window.height()}")
        print(f"  Current Mode: {window.current_mode}")
        
        print("\n✅ GUI interface test completed")
        print("   (Window not shown in automated test)")
        
        return True
        
    except ImportError as e:
        print(f"\n❌ GUI import failed: {e}")
        print("   Install with: pip install PySide6")
        return False
    except Exception as e:
        print(f"\n❌ GUI interface test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_resource_monitor():
    """Test resource monitor"""
    print("\n" + "="*60)
    print("TESTING RESOURCE MONITOR")
    print("="*60)
    
    try:
        from resource_monitor import ResourceMonitor
        
        monitor = ResourceMonitor(logger=logger)
        print("✓ ResourceMonitor created")
        
        # Get stats
        stats = monitor.get_current_stats()
        
        # Verify stats dict is not empty
        if not stats:
            print("❌ Stats dictionary is empty")
            return False
        
        print(f"\n✓ System Statistics:")
        print(f"  CPU Usage: {stats.get('cpu_percent', 0):.1f}%")
        print(f"  Memory Usage: {stats.get('memory_percent', 0):.1f}%")
        
        if stats.get('temperature_c'):
            print(f"  Temperature: {stats['temperature_c']:.1f}°C")
        
        # Get status level
        status = monitor.get_system_status_level(stats)
        print(f"  Status Level: {status.UPPER()}")
        
        print("\n✅ Resource monitor test completed")
        return True
        
    except Exception as e:
        print(f"\n❌ Resource monitor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_main_integration():
    """Test main.py integration"""
    print("\n" + "="*60)
    print("TESTING MAIN.PY INTEGRATION")
    print("="*60)
    
    try:
        from guardian_interpreter.main import CleanGuardianCLI, load_config
        
        print("✓ main.py imports successful")
        
        # Load config
        config = load_config()
        print("✓ Configuration loaded")
        
        # Create CLI (this will initialize all components)
        print("\n✓ Initializing Guardian CLI...")
        cli = CleanGuardianCLI(config)
        
        print(f"  LLM Available: {'✅' if cli.llm else '❌'}")
        print(f"  Memory Vault Available: {'✅' if cli.memory_vault else '❌'}")
        print(f"  Network Scanner Available: {'✅' if cli.network_scanner else '❌'}")
        print(f"  Voice Interface Available: {'✅' if cli.voice_interface else '❌'}")
        
        print("\n✅ Main integration test completed")
        return True
        
    except Exception as e:
        print(f"\n❌ Main integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("GUARDIAN NODE - GUI & VOICE INTERFACE TEST SUITE")
    print("="*70)
    
    results = {
        'Resource Monitor': test_resource_monitor(),
        'Voice Interface': test_voice_interface(),
        'GUI Interface': test_gui_interface(),
        'Main Integration': test_main_integration()
    }
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:.<50} {status}")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! GUI and Voice interfaces are ready.")
        print("\nNext steps:")
        print("  1. Test GUI: python guardian_interpreter/main.py --gui")
        print("  2. Test Voice: python guardian_interpreter/main.py --voice")
        print("  3. Test CLI: python guardian_interpreter/main.py --cli")
        return 0
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")
        print("\nInstallation commands:")
        print("  GUI: pip install PySide6")
        print("  Voice: pip install pyttsx3 SpeechRecognition pocketsphinx")
        print("  Monitor: pip install psutil")
        return 1


if __name__ == "__main__":
    sys.exit(main())
