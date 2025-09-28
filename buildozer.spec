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

# Requirements - pinned versions for stability
requirements = python3==3.10, kivy==2.3.0

# Entry point
source.main = main.py

# Orientation and display
orientation = portrait
fullscreen = 0

# Permissions
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Modern Android config
android.api = 34
android.minapi = 21
android.ndk_api = 21
android.archs = arm64-v8a, armeabi-v7a
android.bootstrap = sdl2

# AndroidX support
android.use_androidx = True

# Theme
android.theme = "@android:style/Theme.NoTitleBar"

# Logcat filters
android.logcat_filters = *:S python:D

# Backup
android.allow_backup = True

# Artifact type
android.debug_artifact = apk

# P4A branch
p4a.branch = master

[buildozer]
# Logging
log_level = 2
warn_on_root = 1