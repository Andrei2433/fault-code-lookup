# Android APK Build Instructions

This guide will help you convert your Python fault codes app into an Android APK.

## Prerequisites

### Option 1: Using Google Colab (Recommended - Easiest)
1. Go to [Google Colab](https://colab.research.google.com/)
2. Create a new notebook
3. Follow the steps below

### Option 2: Using Ubuntu/Linux (Advanced)
1. Install Ubuntu 20.04 or later
2. Install required packages

## Step-by-Step Instructions

### Method 1: Google Colab (Easiest)

1. **Upload your files to Google Colab:**
   ```python
   # Run this in a Colab cell
   from google.colab import files
   uploaded = files.upload()
   ```

2. **Install Buildozer:**
   ```bash
   !pip install buildozer
   !sudo apt update
   !sudo apt install -y git zip unzip openjdk-8-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
   ```

3. **Install Android SDK:**
   ```bash
   !wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip
   !unzip commandlinetools-linux-9477386_latest.zip
   !mkdir -p android-sdk/cmdline-tools
   !mv cmdline-tools android-sdk/cmdline-tools/latest
   !export ANDROID_HOME=/content/android-sdk
   !export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin
   ```

4. **Build the APK:**
   ```bash
   !buildozer android debug
   ```

5. **Download the APK:**
   ```bash
   from google.colab import files
   files.download('bin/faultcodes-1.0-debug.apk')
   ```

### Method 2: Ubuntu/Linux

1. **Install dependencies:**
   ```bash
   sudo apt update
   sudo apt install -y git zip unzip openjdk-8-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
   ```

2. **Install Buildozer:**
   ```bash
   pip3 install buildozer
   ```

3. **Install Android SDK:**
   ```bash
   wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip
   unzip commandlinetools-linux-9477386_latest.zip
   mkdir -p android-sdk/cmdline-tools
   mv cmdline-tools android-sdk/cmdline-tools/latest
   export ANDROID_HOME=/path/to/android-sdk
   export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin
   ```

4. **Build the APK:**
   ```bash
   buildozer android debug
   ```

## Files You Need

Make sure you have these files in your project directory:
- `main.py` (Kivy app)
- `buildozer.spec` (Build configuration)
- `fault_codes.db` (Your database)
- `requirements_android.txt` (Dependencies)

## Installing the APK

1. **Enable Unknown Sources:**
   - Go to Settings > Security > Unknown Sources
   - Enable "Install from unknown sources"

2. **Install the APK:**
   - Copy the APK file to your Android device
   - Tap on the APK file to install
   - Follow the installation prompts

3. **Copy Database:**
   - Copy `fault_codes.db` to your device's Downloads folder
   - The app will automatically find it

## Troubleshooting

### Common Issues:

1. **Build fails with Java errors:**
   - Make sure Java 8 is installed
   - Set JAVA_HOME environment variable

2. **SDK not found:**
   - Verify ANDROID_HOME is set correctly
   - Make sure SDK tools are in the right location

3. **App crashes on Android:**
   - Check that the database file is accessible
   - Verify permissions are granted

### Alternative: Use Online Build Services

If building locally is too complex, consider:
- **GitHub Actions** with Android build workflows
- **AppVeyor** or **Travis CI** for automated builds
- **KivyMD** online build service

## Testing

1. Install the APK on your Android device
2. Copy the `fault_codes.db` file to the device
3. Open the app and test searching for fault codes
4. Verify all features work correctly

## Notes

- The APK will be around 50-100MB due to Python runtime
- First launch may take a few seconds to initialize
- Database file should be in the app's external storage directory
- App works completely offline once database is in place
