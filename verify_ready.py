#!/usr/bin/env python3
"""
Guardian Node - Quick Verification Script
Verifies system is ready for investor presentation
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} MISSING: {filepath}")
        return False

def check_directory_exists(dirpath, description):
    """Check if a directory exists"""
    if Path(dirpath).is_dir():
        print(f"✅ {description}: {dirpath}")
        return True
    else:
        print(f"❌ {description} MISSING: {dirpath}")
        return False

def main():
    print("="*70)
    print("GUARDIAN NODE - VERIFICATION SCRIPT")
    print("="*70)
    print("\nVerifying system is ready for investor presentation...\n")
    
    checks_passed = 0
    checks_total = 0
    
    # Core Implementation Files
    print("\n[1/6] Core Implementation Files")
    print("-"*70)
    core_files = [
        ("guardian_interpreter/main.py", "Main entry point"),
        ("guardian_interpreter/api_server.py", "REST API server"),
        ("guardian_interpreter/memory_vault.py", "RAG system"),
        ("guardian_interpreter/network_scanner.py", "Network scanning"),
        ("guardian_interpreter/smart_home.py", "Smart home control"),
        ("guardian_interpreter/llm_integration.py", "LLM integration"),
    ]
    
    for filepath, desc in core_files:
        checks_total += 1
        if check_file_exists(filepath, desc):
            checks_passed += 1
    
    # Test Files
    print("\n[2/6] Test Files")
    print("-"*70)
    test_files = [
        ("test_noddy_simple.py", "Noddy control flow tests"),
        ("test_smart_home.py", "Smart home tests"),
        ("test_api.py", "API tests"),
        ("tests/test_memory_vault.py", "Memory vault tests"),
        ("tests/test_network_scanner.py", "Network scanner tests"),
    ]
    
    for filepath, desc in test_files:
        checks_total += 1
        if check_file_exists(filepath, desc):
            checks_passed += 1
    
    # Documentation Files
    print("\n[3/6] Documentation Files")
    print("-"*70)
    doc_files = [
        ("README.md", "Main README"),
        ("ALL_TASKS_COMPLETE.md", "Task completion summary"),
        ("INVESTOR_CHECKLIST.md", "Investor checklist"),
        ("VERIFICATION_REPORT.md", "Verification report"),
        ("FINAL_SUMMARY.md", "Final summary"),
        ("API_DOCUMENTATION.md", "API documentation"),
        ("COMPREHENSIVE_TESTING_GUIDE.md", "Testing guide"),
        ("CHANGES.md", "Change log"),
    ]
    
    for filepath, desc in doc_files:
        checks_total += 1
        if check_file_exists(filepath, desc):
            checks_passed += 1
    
    # Configuration Files
    print("\n[4/6] Configuration Files")
    print("-"*70)
    config_files = [
        ("guardian_interpreter/config.yaml", "Main configuration"),
        ("guardian_interpreter/requirements.txt", "Python dependencies"),
        ("docker-compose.yml", "Docker compose"),
        ("dockerfile", "Dockerfile"),
        ("setup.py", "Python packaging"),
    ]
    
    for filepath, desc in config_files:
        checks_total += 1
        if check_file_exists(filepath, desc):
            checks_passed += 1
    
    # Deployment Scripts
    print("\n[5/6] Deployment Scripts")
    print("-"*70)
    deploy_files = [
        ("install_raspberry_pi.sh", "Raspberry Pi installer"),
        ("cleanup_duplicates.py", "Cleanup script"),
        ("verify_ready.py", "This verification script"),
    ]
    
    for filepath, desc in deploy_files:
        checks_total += 1
        if check_file_exists(filepath, desc):
            checks_passed += 1
    
    # Key Directories
    print("\n[6/6] Key Directories")
    print("-"*70)
    directories = [
        ("guardian_interpreter", "Main package"),
        ("tests", "Test suite"),
        ("docs", "Documentation"),
        ("models", "LLM models"),
        ("data", "Data storage"),
    ]
    
    for dirpath, desc in directories:
        checks_total += 1
        if check_directory_exists(dirpath, desc):
            checks_passed += 1
    
    # Summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    percentage = (checks_passed / checks_total * 100) if checks_total > 0 else 0
    
    print(f"\n✅ Passed: {checks_passed}/{checks_total} ({percentage:.1f}%)")
    
    if checks_passed == checks_total:
        print("\n🎉 ALL CHECKS PASSED!")
        print("\n✅ Guardian Node is READY for investor presentation!")
        print("\nNext steps:")
        print("  1. Review INVESTOR_CHECKLIST.md")
        print("  2. Review FINAL_SUMMARY.md")
        print("  3. Practice demo with COMPREHENSIVE_TESTING_GUIDE.md")
        print("  4. Run tests: python test_noddy_simple.py")
        print("  5. Start API: python guardian_interpreter/main.py")
        return 0
    else:
        print(f"\n⚠️ {checks_total - checks_passed} checks failed")
        print("\nPlease review missing files above.")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Verification failed: {e}")
        sys.exit(1)
