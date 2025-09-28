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

# CI-friendly Android configuration
android.api = 30
android.build_tools_version = 30.0.3
android.update_sdk = False
android.sdk_path =
android.ndk_path =

[buildozer]

# Logging
log_level = 2
warn_on_root = 1

# Build directories (optional)
# build_dir = ./.buildozer
# bin_dir = ./bin
