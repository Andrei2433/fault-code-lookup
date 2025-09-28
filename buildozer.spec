[app]

# Application metadata
title = Ross-Tech VCDS Fault Codes
package.name = faultcodes
package.domain = com.ross.tech
version = 1.0

# Source files
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db
source.include_patterns = fault_codes.db

# Requirements
requirements = python3,kivy,sqlite3

# Orientation and display
orientation = portrait
fullscreen = 0

# Permissions
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# AndroidX support
android.use_androidx = True

# Theme
android.theme = "@android:style/Theme.NoTitleBar"

# Logcat filters
android.logcat_filters = *:S python:D

# Architecture
android.archs = arm64-v8a, armeabi-v7a

# Backup
android.allow_backup = True

# Artifact type
android.debug_artifact = apk

# ------------------------------
# CI-friendly Android configuration
# ------------------------------

# Use pre-installed SDK + NDK
android.sdk_path = $HOME/Android/Sdk
android.ndk_path = $HOME/Android/Sdk/ndk/25.2.9519653

# Target API and Build Tools compatible with CI
android.api = 30
android.build_tools_version = 30.0.3

# Prevent Buildozer from trying to update SDK
android.update_sdk = False

[buildozer]

# Logging
log_level = 2
warn_on_root = 1

# Optional: build directories
# build_dir = ./.buildozer
# bin_dir = ./bin
