#!/usr/bin/env python3
"""
COMPLETE GUI Test for Guardian Node
Tests actual GUI initialization, widgets, mode switching, and interactions
"""

import sys
import os

# Add guardian_interpreter to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'github_repos/guardian-node/guardian_interpreter'))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
import traceback

def test_gui_complete():
    """Complete GUI test with actual widget initialization"""
    results = {
        "test_name": "Complete GUI Interface Test",
        "tests": {}
    }
    
    # Create QApplication (required for any Qt GUI)
    app = QApplication(sys.argv)
    
    try:
        # Test 1: Import Guardian GUI
        print("Test 1: Importing Guardian GUI...")
        try:
            from guardian_gui import GuardianModeUI
            results["tests"]["gui_import"] = {"status": "PASS", "message": "GuardianModeUI imported successfully"}
            print("✓ GuardianModeUI imported successfully")
        except Exception as e:
            results["tests"]["gui_import"] = {"status": "FAIL", "message": str(e)}
            print(f"✗ Failed to import GuardianModeUI: {e}")
            return results
        
        # Test 2: Create GUI instance
        print("\nTest 2: Creating GUI instance...")
        try:
            gui_widget = GuardianModeUI()
            results["tests"]["gui_creation"] = {"status": "PASS", "message": "GUI widget created successfully"}
            print("✓ GUI widget created successfully")
        except Exception as e:
            results["tests"]["gui_creation"] = {"status": "FAIL", "message": str(e)}
            print(f"✗ Failed to create GUI widget: {e}")
            traceback.print_exc()
            return results
        
        # Test 3: Check GUI components
        print("\nTest 3: Checking GUI components...")
        try:
            has_title = hasattr(gui_widget, 'mode_title')
            has_desc = hasattr(gui_widget, 'mode_desc')
            has_image = hasattr(gui_widget, 'img_label')
            has_buttons = hasattr(gui_widget, 'btn_adult') and hasattr(gui_widget, 'btn_kids') and hasattr(gui_widget, 'btn_teens')
            
            if has_title and has_desc and has_image and has_buttons:
                results["tests"]["gui_components"] = {
                    "status": "PASS", 
                    "message": "All GUI components present (title, description, image, buttons)"
                }
                print("✓ All GUI components present")
            else:
                missing = []
                if not has_title: missing.append("title")
                if not has_desc: missing.append("description")
                if not has_image: missing.append("image label")
                if not has_buttons: missing.append("buttons")
                results["tests"]["gui_components"] = {
                    "status": "FAIL",
                    "message": f"Missing components: {', '.join(missing)}"
                }
                print(f"✗ Missing components: {', '.join(missing)}")
        except Exception as e:
            results["tests"]["gui_components"] = {"status": "FAIL", "message": str(e)}
            print(f"✗ Failed component check: {e}")
        
        # Test 4: Test mode switching
        print("\nTest 4: Testing mode switching...")
        try:
            modes_tested = []
            mode_results = []
            
            for mode in ["Kids", "Teens", "Adult"]:
                gui_widget.set_mode(mode)
                if gui_widget.current_mode == mode:
                    modes_tested.append(f"{mode}:OK")
                    mode_results.append(True)
                else:
                    modes_tested.append(f"{mode}:FAIL")
                    mode_results.append(False)
                print(f"  - {mode} mode: {'✓' if mode_results[-1] else '✗'}")
            
            if all(mode_results):
                results["tests"]["mode_switching"] = {
                    "status": "PASS",
                    "message": f"All modes work: {', '.join(modes_tested)}"
                }
                print("✓ Mode switching working")
            else:
                results["tests"]["mode_switching"] = {
                    "status": "PARTIAL",
                    "message": f"Mode results: {', '.join(modes_tested)}"
                }
                print("⚠ Some modes failed")
        except Exception as e:
            results["tests"]["mode_switching"] = {"status": "FAIL", "message": str(e)}
            print(f"✗ Mode switching failed: {e}")
            traceback.print_exc()
        
        # Test 5: Test button clicks (programmatically)
        print("\nTest 5: Testing button interactions...")
        try:
            # Simulate button clicks
            gui_widget.btn_kids.click()
            kids_mode = gui_widget.current_mode == "Kids"
            
            gui_widget.btn_teens.click()
            teens_mode = gui_widget.current_mode == "Teens"
            
            gui_widget.btn_adult.click()
            adult_mode = gui_widget.current_mode == "Adult"
            
            if kids_mode and teens_mode and adult_mode:
                results["tests"]["button_clicks"] = {
                    "status": "PASS",
                    "message": "All buttons respond correctly"
                }
                print("✓ All buttons working")
            else:
                results["tests"]["button_clicks"] = {
                    "status": "FAIL",
                    "message": f"Kids:{kids_mode}, Teens:{teens_mode}, Adult:{adult_mode}"
                }
                print(f"✗ Button issues: Kids:{kids_mode}, Teens:{teens_mode}, Adult:{adult_mode}")
        except Exception as e:
            results["tests"]["button_clicks"] = {"status": "FAIL", "message": str(e)}
            print(f"✗ Button test failed: {e}")
            traceback.print_exc()
        
        # Test 6: Test widget rendering
        print("\nTest 6: Testing widget rendering...")
        try:
            gui_widget.show()  # Make widget visible
            size = gui_widget.size()
            is_rendered = size.width() > 0 and size.height() > 0
            
            if is_rendered:
                results["tests"]["widget_rendering"] = {
                    "status": "PASS",
                    "message": f"Widget rendered with size {size.width()}x{size.height()}"
                }
                print(f"✓ Widget renders at {size.width()}x{size.height()}")
            else:
                results["tests"]["widget_rendering"] = {
                    "status": "FAIL",
                    "message": "Widget has zero size"
                }
                print("✗ Widget not rendering properly")
        except Exception as e:
            results["tests"]["widget_rendering"] = {"status": "FAIL", "message": str(e)}
            print(f"✗ Rendering test failed: {e}")
        
        # Test 7: Test signal emission
        print("\nTest 7: Testing mode change signals...")
        try:
            signal_received = []
            
            def on_mode_changed(mode):
                signal_received.append(mode)
            
            gui_widget.mode_changed.connect(on_mode_changed)
            gui_widget.set_mode("Teens")
            
            # Process events to ensure signal is delivered
            app.processEvents()
            
            if "Teens" in signal_received:
                results["tests"]["signal_emission"] = {
                    "status": "PASS",
                    "message": "Mode change signals working"
                }
                print("✓ Signals working correctly")
            else:
                results["tests"]["signal_emission"] = {
                    "status": "FAIL",
                    "message": f"Signal not received. Got: {signal_received}"
                }
                print(f"✗ Signal not received. Got: {signal_received}")
        except Exception as e:
            results["tests"]["signal_emission"] = {"status": "FAIL", "message": str(e)}
            print(f"✗ Signal test failed: {e}")
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        traceback.print_exc()
        results["tests"]["unexpected_error"] = {"status": "FAIL", "message": str(e)}
    
    return results

def main():
    print("=" * 70)
    print("GUARDIAN NODE - COMPLETE GUI FUNCTIONAL TEST")
    print("=" * 70)
    print()
    
    results = test_gui_complete()
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    total = len(results["tests"])
    passed = sum(1 for t in results["tests"].values() if t["status"] == "PASS")
    partial = sum(1 for t in results["tests"].values() if t["status"] == "PARTIAL")
    failed = sum(1 for t in results["tests"].values() if t["status"] == "FAIL")
    
    for test_name, test_result in results["tests"].items():
        status_symbol = "✓" if test_result["status"] == "PASS" else ("⚠" if test_result["status"] == "PARTIAL" else "✗")
        print(f"{status_symbol} {test_name}: {test_result['status']} - {test_result['message']}")
    
    print(f"\nTotal: {total} | Passed: {passed} | Partial: {partial} | Failed: {failed}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
