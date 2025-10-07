#!/usr/bin/env python3
"""
Test script to verify TikTok RSS environment is set up correctly
"""

import os
import sys

def test_imports():
    """Test that all required modules can be imported"""
    try:
        import asyncio
        import feedgen
        import TikTokApi
        import config
        import playwright
        print("✅ All required modules imported successfully!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_ms_token():
    """Test that MS_TOKEN environment variable is set"""
    ms_token = os.environ.get("MS_TOKEN")
    if ms_token:
        print(f"✅ MS_TOKEN is set (length: {len(ms_token)} characters)")
        return True
    else:
        print("⚠️  MS_TOKEN environment variable is not set")
        print("   Set it with: export MS_TOKEN=\"your_token_here\"")
        return False

def test_config():
    """Test that config.py is accessible"""
    try:
        import config
        print(f"✅ Config loaded successfully")
        print(f"   GitHub Pages URL: {config.ghPagesURL}")
        print(f"   GitHub Raw URL: {config.ghRawURL}")
        return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def test_subscriptions():
    """Test that subscriptions.csv exists and is readable"""
    try:
        with open('subscriptions.csv', 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            print(f"✅ Subscriptions file found with {len(lines)} users")
            if lines:
                print(f"   First few users: {', '.join(lines[:3])}{'...' if len(lines) > 3 else ''}")
            return True
    except FileNotFoundError:
        print("❌ subscriptions.csv file not found")
        return False
    except Exception as e:
        print(f"❌ Error reading subscriptions.csv: {e}")
        return False

def main():
    print("🧪 Testing TikTok RSS Environment\n")
    
    tests = [
        ("Import Test", test_imports),
        ("MS Token Test", test_ms_token),
        ("Config Test", test_config),
        ("Subscriptions Test", test_subscriptions),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        result = test_func()
        results.append(result)
    
    print(f"\n{'='*50}")
    print(f"Test Results: {sum(results)}/{len(results)} tests passed")
    
    if all(results):
        print("🎉 Environment is ready! You can now run:")
        print("   ./run.sh")
        print("   or")
        print("   python postprocessing.py")
    else:
        print("⚠️  Please fix the issues above before running the RSS generator")
    
    return 0 if all(results) else 1

if __name__ == "__main__":
    sys.exit(main())