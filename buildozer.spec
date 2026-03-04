[app]
title = TriviaQuizApp
package.name = myapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 0.1

# Requirements - הגרסה המצומצמת לבדיקה
requirements = python3,kivy==2.3.0,Cython==0.29.33,certifi,idna,charset-normalizer

orientation = portrait

# iOS specific
ios.codesign.allowed = false
ios.codesign.identity = 
ios.arch = arm64
ios.sdk = 18.5
ios.ios_deploy_target = 13.0

# Android specific
fullscreen = 0
android.permissions = INTERNET, ACCESS_NETWORK_STATE
android.api = 31
android.minapi = 21
android.enable_androidx = True
android.archs = arm64-v8a, armeabi-v7a
android.copy_libs = 1

[buildozer]
log_level = 2
warn_on_root = 1
