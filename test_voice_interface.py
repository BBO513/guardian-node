#!/usr/bin/env python3
"""
Test script for Family Voice Interface integration with Guardian GUI
"""

import sys
import os
import logging

# Add the guardian_interpreter directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'guardian_interpreter'))

class MockLogger:
    """Mock logger for testing"""
    def info(self, msg): print(f"INFO: {msg}")
    def warning(self, msg): print(f"WARNING: {msg}")
    def error(self, msg): print(f"ERROR: {msg}")

class MockConfig:
    """Mock configuration for testing"""
    def __init__(self):
        self.config = {
            'family_assistant': {
                'voice_interface': {
                    'privacy_mode': True,
                    'offline_mode': True,
                    'speech_rate': 150,
                    'volume': 0.8,
                    'child_friendly_voice': True,
                    'timeout': 5,
                    'phrase_timeout': 3
                }
            }
        }
    
    def get(self, key, default=None):
        return self.config.get(key, default)

class MockGuardian:
    """Mock Guardian interpreter for testing"""
    def __init__(self):
        self.config = MockConfig()
        self.logger = MockLogger()

class MockStatusWidget:
    """Mock status widget for testing"""
    def __init__(self):
        self.status_label = MockLabel()
    
    def update_status(self):
        print("Status updated")

class MockLabel:
    """Mock label for testing"""
    def __init__(self):
        self.text = ""
    
    def setText(self, text):
        self.text = text
        print(f"Label text: {text}")
    
    def setStyleSheet(self, style):
        print(f"Label style updated")

class SimplifiedGuardianGUI:
    """Simplified version of the Guardian GUI for testing"""
    def __init__(self):
        self.guardian = MockGuardian()
        self.current_mode = "Kids"
        self.status_widget = MockStatusWidget()
    
    def start_voice_session(self):
        """Start voice assistant session"""
        from family_assistant.voice_interface import FamilyVoiceInterface
        
        # Update status
        print("Starting voice session...")
        self.status_widget.status_label.setText("🎤 Listening...")
        
        # Get family context based on current mode
        family_context = self.get_family_profile_for_mode(self.current_mode)
        
        # Initialize voice interface with mock mode
        voice_interface = FamilyVoiceInterface(config=self.guardian.config, logger=self.guardian.logger, mock_mode=True)
        result = voice_interface.start_voice_session(family_context)
        
        # Update status based on result
        if result and result.get('success'):
            self.status_widget.status_label.setText("🟢 Voice command completed")
        else:
            self.status_widget.status_label.setText("🔴 Voice command failed")
            
        # Show response if available
        if result and 'response' in result:
            print(f"Voice response: {result['response']}")
    
    def get_family_profile_for_mode(self, mode):
        """Get family profile configuration for the selected mode"""
        profiles = {
            "Adult": {
                'family_id': 'guardian_family',
                'members': [{'name': 'Parent', 'age_group': 'adult'}],
                'security_level': 'standard',
                'content_filtering': 'minimal'
            },
            "Kids": {
                'family_id': 'guardian_family', 
                'members': [{'name': 'Child', 'age_group': 'child'}],
                'security_level': 'maximum',
                'content_filtering': 'strict'
            },
            "Teens": {
                'family_id': 'guardian_family',
                'members': [{'name': 'Teen', 'age_group': 'teen'}], 
                'security_level': 'balanced',
                'content_filtering': 'moderate'
            }
        }
        return profiles.get(mode, profiles["Kids"])

def test_voice_interface_integration():
    """Test voice interface integration with Guardian GUI"""
    print("🎤 Testing Voice Interface Integration")
    print("=" * 50)
    
    try:
        # Create GUI instance
        print("1. Creating GUI instance...")
        gui = SimplifiedGuardianGUI()
        print("✅ GUI instance created")
        
        # Test voice session with different modes
        print("\n2. Testing voice session with different modes...")
        modes = ["Kids", "Teens", "Adult"]
        
        for mode in modes:
            print(f"\n   Testing with {mode} mode:")
            gui.current_mode = mode
            gui.start_voice_session()
        
        print("\n✅ Voice interface integration test completed!")
        return 0
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Speech recognition components may not be installed")
        return 1
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_voice_interface_integration())