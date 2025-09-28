#!/usr/bin/env python3
"""
Simple script to help build the Android APK.
This script provides instructions and checks for required files.
"""

import os
import sys

def check_files():
    """Check if all required files exist."""
    required_files = [
        'main.py',
        'buildozer.spec',
        'fault_codes.db',
        'requirements_android.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files found!")
    return True

def show_instructions():
    """Show build instructions."""
    print("""
🚀 ANDROID APK BUILD INSTRUCTIONS
================================

Your Python fault codes app is ready to be converted to Android!

📁 Required Files:
   ✅ main.py (Kivy mobile app)
   ✅ buildozer.spec (Build configuration)
   ✅ fault_codes.db (Your database)
   ✅ requirements_android.txt (Dependencies)

🔧 Build Options:

1. GOOGLE COLAB (Easiest - Recommended):
   - Go to: https://colab.research.google.com/
   - Upload all your files
   - Run the build commands from ANDROID_SETUP.md
   - Download the APK when complete

2. UBUNTU/LINUX (Advanced):
   - Install Ubuntu 20.04+
   - Follow instructions in ANDROID_SETUP.md
   - Run: buildozer android debug

3. WINDOWS (Using WSL):
   - Install Windows Subsystem for Linux
   - Install Ubuntu in WSL
   - Follow Ubuntu instructions

📱 What You'll Get:
   - APK file (~50-100MB)
   - Works on Android 5.0+
   - Completely offline
   - All 889+ fault codes included

⚠️  Important Notes:
   - Building requires Linux environment
   - Google Colab is the easiest option
   - First build may take 30-60 minutes
   - APK will include Python runtime

📖 For detailed instructions, see: ANDROID_SETUP.md
""")

def main():
    print("🔍 Checking Android build setup...")
    
    if not check_files():
        print("\n❌ Please ensure all required files are present before building.")
        return
    
    show_instructions()
    
    print("\n🎯 Next Steps:")
    print("1. Choose your build method (Google Colab recommended)")
    print("2. Follow the instructions in ANDROID_SETUP.md")
    print("3. Build your APK")
    print("4. Install on Android device")
    print("5. Copy fault_codes.db to device")
    print("6. Enjoy your mobile fault codes app!")

if __name__ == "__main__":
    main()
