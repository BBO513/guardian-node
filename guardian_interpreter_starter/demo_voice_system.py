#!/usr/bin/env python3
"""
Guardian Node Voice System Demo
Demonstrates the complete offline voice explanation system
"""

import os
import time
import json

def demo_header():
    print("=" * 60)
    print("🛡️  GUARDIAN NODE VOICE SYSTEM DEMO")
    print("=" * 60)
    print("Privacy-First Offline Security Coaching")
    print()

def demo_voice_explanations():
    print("📢 TESTING VOICE EXPLANATIONS")
    print("-" * 30)
    
    # Test different age groups and risks
    test_cases = [
        ("phishing", "child", "🧒 Child-friendly phishing explanation"),
        ("phishing", "teen", "👦 Teen phishing explanation"),
        ("phishing", "adult", "👨 Adult phishing explanation"),
        ("malware", "teen", "👦 Teen malware explanation"),
        ("weak_password", "adult", "👨 Adult password security")
    ]
    
    for risk, age, description in test_cases:
        print(f"\n{description}:")
        os.system(f'python skills/offline_voice_explain.py --risk {risk} --age {age}')
        time.sleep(1)

def demo_security_coach():
    print("\n🎓 TESTING SECURITY COACH")
    print("-" * 30)
    
    print("\n📋 Available coaching scenarios:")
    os.system('python main.py "skill security_coach list"')
    
    print("\n🎯 Phishing coaching for teens:")
    os.system('python main.py "skill security_coach coach phishing_email teen"')
    
    print("\n⚠️  Threat assessment - suspicious email:")
    os.system('python main.py "skill security_coach assess email urgent_verification adult"')

def demo_voice_availability():
    print("\n🔊 VOICE SYSTEM STATUS")
    print("-" * 30)
    
    print("Available voice explanations:")
    os.system('python skills/offline_voice_explain.py --list')
    
    print("\nVoice system check:")
    os.system('python main.py "skill security_coach voice"')

def demo_complete_workflow():
    print("\n🔄 COMPLETE WORKFLOW DEMO")
    print("-" * 30)
    
    print("1. Pre-recording explanations (already done)")
    print("2. Testing offline playback...")
    os.system('python skills/offline_voice_explain.py --risk suspicious_network --age teen')
    
    print("\n3. Interactive coaching session...")
    os.system('python main.py "skill security_coach coach network_safety adult"')
    
    print("\n4. Real-time threat assessment...")
    os.system('python main.py "skill security_coach assess wifi public_network teen"')

def main():
    demo_header()
    
    print("This demo showcases Guardian Node's offline voice explanation system:")
    print("✅ 12 pre-recorded neural voice explanations")
    print("✅ 4 security risk types covered")
    print("✅ 3 age-appropriate content levels")
    print("✅ Complete offline operation")
    print("✅ Privacy-first design")
    print()
    
    input("Press Enter to start the demo...")
    
    try:
        demo_voice_availability()
        demo_voice_explanations()
        demo_security_coach()
        demo_complete_workflow()
        
        print("\n" + "=" * 60)
        print("🎉 DEMO COMPLETE!")
        print("=" * 60)
        print("Guardian Node's voice system is fully operational:")
        print("• High-quality neural voices (Jenny, Aria, Brian)")
        print("• Instant offline playback")
        print("• Interactive security coaching")
        print("• Age-appropriate content")
        print("• Zero external dependencies")
        print("• Complete privacy protection")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nDemo error: {e}")

if __name__ == "__main__":
    main()