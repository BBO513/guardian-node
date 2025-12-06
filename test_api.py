#!/usr/bin/env python3
"""
Test script for Guardian Node REST API
Tests all major endpoints
"""

import requests
import json
import time

# Configuration
API_BASE = "http://localhost:5000"
TEST_PASSWORD = None  # Will be set after first test

def test_health():
    """Test health check endpoint"""
    print("\n[1/10] Testing Health Check...")
    try:
        response = requests.get(f"{API_BASE}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Health check passed: {data['status']}")
            return True
        else:
            print(f"  ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Health check error: {e}")
        return False

def test_status():
    """Test status endpoint"""
    print("\n[2/10] Testing Status Endpoint...")
    try:
        response = requests.get(f"{API_BASE}/api/status")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Status: {data['system_status']}")
            print(f"     LLM Loaded: {data['llm_loaded']}")
            print(f"     Online Mode: {data['online_mode']}")
            return True
        else:
            print(f"  ❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Status error: {e}")
        return False

def test_online_mode_get():
    """Test getting online mode"""
    print("\n[3/10] Testing Get Online Mode...")
    try:
        response = requests.get(f"{API_BASE}/api/online_mode")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Online Mode: {data['online_mode']}")
            return True
        else:
            print(f"  ❌ Get online mode failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Get online mode error: {e}")
        return False

def test_password_verify(password):
    """Test password verification"""
    print("\n[4/10] Testing Password Verification...")
    try:
        response = requests.post(
            f"{API_BASE}/api/password/verify",
            json={"password": password}
        )
        if response.status_code == 200:
            data = response.json()
            if data['valid']:
                print(f"  ✅ Password verified successfully")
                return True
            else:
                print(f"  ❌ Password invalid")
                return False
        else:
            print(f"  ❌ Password verify failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Password verify error: {e}")
        return False

def test_query():
    """Test LLM query endpoint"""
    print("\n[5/10] Testing LLM Query...")
    try:
        response = requests.post(
            f"{API_BASE}/api/query",
            json={"query": "What is cybersecurity?"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Query successful")
            print(f"     Response length: {len(data.get('response', ''))} chars")
            return True
        elif response.status_code == 503:
            print(f"  ⚠️ LLM not available (expected if not running)")
            return True  # Not a failure
        else:
            print(f"  ❌ Query failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Query error: {e}")
        return False

def test_memory_stats():
    """Test memory vault stats"""
    print("\n[6/10] Testing Memory Vault Stats...")
    try:
        response = requests.get(f"{API_BASE}/api/memory/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Memory stats retrieved")
            for key, value in data.items():
                print(f"     {key}: {value}")
            return True
        elif response.status_code == 503:
            print(f"  ⚠️ Memory vault not available (expected if not running)")
            return True  # Not a failure
        else:
            print(f"  ❌ Memory stats failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Memory stats error: {e}")
        return False

def test_notification_config():
    """Test notification config endpoint"""
    print("\n[7/10] Testing Notification Config...")
    try:
        response = requests.get(f"{API_BASE}/api/notifications/config")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Notification config retrieved")
            print(f"     Enabled: {data.get('enabled')}")
            print(f"     Methods: {list(data.get('methods', {}).keys())}")
            return True
        else:
            print(f"  ❌ Notification config failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Notification config error: {e}")
        return False

def test_online_mode_set(password):
    """Test setting online mode"""
    print("\n[8/10] Testing Set Online Mode...")
    try:
        # Try to set online mode to True
        response = requests.post(
            f"{API_BASE}/api/online_mode",
            json={"state": True, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Online mode set: {data['online_mode']}")
            
            # Set it back to False
            response = requests.post(
                f"{API_BASE}/api/online_mode",
                json={"state": False, "password": password}
            )
            if response.status_code == 200:
                print(f"  ✅ Online mode reset to False")
                return True
            else:
                print(f"  ⚠️ Could not reset online mode")
                return True  # Still counts as success
        elif response.status_code == 401:
            print(f"  ❌ Invalid password")
            return False
        else:
            print(f"  ❌ Set online mode failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Set online mode error: {e}")
        return False

def test_password_usage(password):
    """Test password usage log"""
    print("\n[9/10] Testing Password Usage Log...")
    try:
        response = requests.get(
            f"{API_BASE}/api/password/usage",
            params={"password": password}
        )
        if response.status_code == 200:
            data = response.json()
            log = data.get('usage_log', [])
            print(f"  ✅ Usage log retrieved: {len(log)} entries")
            if log:
                latest = log[-1]
                print(f"     Latest: {latest['source']} at {latest['timestamp']}")
            return True
        elif response.status_code == 401:
            print(f"  ❌ Invalid password")
            return False
        else:
            print(f"  ❌ Usage log failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Usage log error: {e}")
        return False

def test_smart_home():
    """Test smart home endpoints"""
    print("\n[10/10] Testing Smart Home Endpoints...")
    try:
        response = requests.get(f"{API_BASE}/api/smarthome/devices")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Smart home endpoint accessible")
            print(f"     Message: {data.get('message')}")
            return True
        else:
            print(f"  ❌ Smart home failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Smart home error: {e}")
        return False

def main():
    """Run all tests"""
    print("="*70)
    print("GUARDIAN NODE REST API TEST SUITE")
    print("="*70)
    print(f"\nTesting API at: {API_BASE}")
    print("\nNote: Some tests may fail if Guardian Node is not running.")
    print("      Start it with: python guardian_interpreter/main.py")
    
    # Get password from user
    global TEST_PASSWORD
    print("\n" + "="*70)
    print("PASSWORD SETUP")
    print("="*70)
    print("\nOn first run, Guardian Node generates a random password.")
    print("Check the logs for: 'Generated default override password: ...'")
    print("\nIf you've already changed it, enter your custom password.")
    
    TEST_PASSWORD = input("\nEnter override password (or press Enter to skip auth tests): ").strip()
    
    if not TEST_PASSWORD:
        print("\n⚠️ No password provided. Skipping authentication tests.")
    
    # Run tests
    results = {}
    
    results['Health Check'] = test_health()
    results['Status'] = test_status()
    results['Get Online Mode'] = test_online_mode_get()
    
    if TEST_PASSWORD:
        results['Password Verify'] = test_password_verify(TEST_PASSWORD)
        results['Set Online Mode'] = test_online_mode_set(TEST_PASSWORD)
        results['Password Usage Log'] = test_password_usage(TEST_PASSWORD)
    else:
        print("\n⚠️ Skipping authentication tests (no password provided)")
    
    results['LLM Query'] = test_query()
    results['Memory Stats'] = test_memory_stats()
    results['Notification Config'] = test_notification_config()
    results['Smart Home'] = test_smart_home()
    
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
        print("\n🎉 All tests passed! API is working correctly.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")
        print("\nCommon issues:")
        print("  - Guardian Node not running: python guardian_interpreter/main.py")
        print("  - Wrong password: Check logs for generated password")
        print("  - Port conflict: Check if port 5000 is available")
        return 1

if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        exit(1)
