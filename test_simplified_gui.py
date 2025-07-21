#!/usr/bin/env python3
"""
Test script for simplified Guardian GUI mode switching
"""

import sys
import os
import logging

# Add the guardian_interpreter directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'guardian_interpreter'))

class MockFamilyManager:
    """Mock family manager for testing"""
    def __init__(self):
        self.current_profile = None
        
    def update_profile(self, profile):
        """Update the current family profile"""
        self.current_profile = profile
        print(f"Profile updated: {profile}")

class MockGuardian:
    """Mock Guardian interpreter for testing"""
    def __init__(self):
        self.family_manager = MockFamilyManager()

class MockStatusWidget:
    """Mock status widget for testing"""
    def update_status(self):
        """Update the status display"""
        print("Status updated")

class SimplifiedGuardianGUI:
    """Simplified version of the Guardian GUI for testing"""
    def __init__(self):
        self.guardian = MockGuardian()
        self.current_mode = "Kids"
        self.status_widget = MockStatusWidget()
    
    def handle_mode_change(self, mode):
        """Handle mode changes and integrate with backend"""
        self.current_mode = mode
        if self.guardian and hasattr(self.guardian, 'family_manager'):
            profile = self.get_family_profile_for_mode(mode)
            self.guardian.family_manager.update_profile(profile)
            self.status_widget.update_status()
    
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

def main():
    """Main test function"""
    print("🖥️ Testing Simplified Guardian GUI Mode Switching")
    print("=" * 50)
    
    try:
        # Create GUI instance
        print("1. Creating GUI instance...")
        gui = SimplifiedGuardianGUI()
        print("✅ GUI instance created")
        
        # Test mode switching
        print("\n2. Testing mode switching...")
        modes = ["Kids", "Teens", "Adult"]
        
        for mode in modes:
            print(f"\n   Switching to {mode} mode:")
            gui.handle_mode_change(mode)
            print(f"   Current mode: {gui.current_mode}")
            print(f"   Current profile: {gui.guardian.family_manager.current_profile}")
        
        print("\n✅ Simplified GUI mode switching test completed!")
        return 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())