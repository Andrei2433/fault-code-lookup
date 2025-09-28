[app]

title = Ross-Tech VCDS Fault Codes
package.name = faultcodes
package.domain = com.ross.tech
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db
source.include_patterns = fault_codes.db
version = 1.0
requirements = python3,kivy,sqlite3
orientation = portrait
fullscreen = 0
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.use_androidx = True
android.theme = "@android:style/Theme.NoTitleBar"
android.logcat_filters = *:S python:D
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.debug_artifact = apk

[buildozer]

log_level = 2
warn_on_root = 1

# --- Critical fixes for CI ---
android.sdk_path =
android.ndk_path =
android.api = 33
android.build_tools_version = 36.1.0
android.update_sdk = False
