[app]
title = Ross-Tech VCDS Fault Codes
package.name = faultcodes
package.domain = com.ross.tech
version = 1.0

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db
source.include_patterns = fault_codes.db
source.main = main.py

# Pin for CI stability
requirements = python3==3.10, kivy==2.3.0

orientation = portrait
fullscreen = 0

android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.api = 34
android.minapi = 21
android.ndk_api = 21
android.archs = arm64-v8a, armeabi-v7a
android.bootstrap = sdl2

android.use_androidx = True
android.theme = "@android:style/Theme.NoTitleBar"

android.logcat_filters = *:S python:D
android.allow_backup = True
android.debug_artifact = apk

# Use latest recipes
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1