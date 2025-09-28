[app]

# (str) Title of your application
title = Ross-Tech VCDS Fault Codes

# (str) Package name
package.name = faultcodes

# (str) Package domain (needed for android/ios packaging)
package.domain = com.ross.tech

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (leave empty to include all)
source.include_exts = py,png,jpg,kv,atlas,db

# Include your SQLite database
source.include_patterns = fault_codes.db

# Application version
version = 1.0

# List of requirements
requirements = python3,kivy,sqlite3

# Supported orientation
orientation = portrait

# Fullscreen
fullscreen = 0

# Permissions
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# AndroidX support
android.use_androidx = True

# Android theme
android.theme = "@android:style/Theme.NoTitleBar"

# Android logcat filters
android.logcat_filters = *:S python:D

# Architectures to build for
android.archs = arm64-v8a, armeabi-v7a

# Enable Android auto backup (API >= 23)
android.allow_backup = True

# Debug/release artifact formats
android.debug_artifact = apk

[buildozer]

# Log level (0=error, 1=info, 2=debug)
log_level = 2

# Warn if run as root
warn_on_root = 1

# --- Critical SDK/NDK fixes for CI ---

# Use environment variables for SDK/NDK (pre-installed in CI)
android.sdk_path =
android.ndk_path =

# API level and Build Tools version to match pre-installed SDK
android.api = 33
android.build_tools_version = 36.1.0

# Prevent Buildozer from attempting to update SDK/NDK
android.update_sdk = False
