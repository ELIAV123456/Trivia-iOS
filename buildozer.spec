[app]

# (str) Title of your application
title = Trivia Quiz

# (str) Package name
package.name = myapp

# (str) Package domain (needed for android/ios packaging)
package.domain = org.test

# (str) Source code where the main.py live
source.dir = .

# --- תיקון 1: הוספת json לסיומות הקבצים ---
source.include_exts = py,png,jpg,kv,atlas,json

# (str) Application versioning
version = 0.1

# --- תיקון 2: דרישות מערכת מלאות למניעת קריסה (כולל SSL ו-Requests) ---
requirements = python3,kivy==2.3.0,requests,openssl,urllib3,certifi,idna,charset-normalizer

# (list) Supported orientations
orientation = portrait

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# --- תיקון 3: הגדרת הרשאות אינטרנט ---
android.permissions = INTERNET, ACCESS_NETWORK_STATE

# (int) Target Android API
android.api = 31

# (int) Minimum API support
android.minapi = 21

# (bool) Enable AndroidX support (חשוב לגרסאות אנדרואיד חדשות)
android.enable_androidx = True

# (list) The Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

[buildozer]

# (int) Log level (2 = debug, הכי טוב כדי לראות שגיאות)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1