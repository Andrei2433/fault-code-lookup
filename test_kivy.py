#!/usr/bin/env python3
"""
Test script to verify the Kivy app works on desktop before building for Android.
"""

import sys
import os

def test_kivy_import():
    """Test if Kivy can be imported."""
    try:
        import kivy
        print(f"✅ Kivy version: {kivy.__version__}")
        return True
    except ImportError:
        print("❌ Kivy not installed. Install with: pip install kivy")
        return False

def test_database():
    """Test if database exists and is accessible."""
    if not os.path.exists('fault_codes.db'):
        print("❌ Database file not found")
        return False
    
    try:
        import sqlite3
        conn = sqlite3.connect('fault_codes.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM fault_codes")
        count = cursor.fetchone()[0]
        conn.close()
        print(f"✅ Database accessible with {count} fault codes")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def main():
    print("🧪 Testing Android app components...")
    print()
    
    # Test Kivy
    kivy_ok = test_kivy_import()
    
    # Test database
    db_ok = test_database()
    
    print()
    if kivy_ok and db_ok:
        print("🎉 All tests passed! Ready to build Android APK.")
        print()
        print("To test the Kivy app on desktop:")
        print("  python main.py")
        print()
        print("To build for Android:")
        print("  Follow instructions in ANDROID_SETUP.md")
    else:
        print("❌ Some tests failed. Please fix issues before building.")
        if not kivy_ok:
            print("  - Install Kivy: pip install kivy")
        if not db_ok:
            print("  - Ensure fault_codes.db exists and is accessible")

if __name__ == "__main__":
    main()
