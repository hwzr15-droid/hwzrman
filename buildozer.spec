[app]
title = وكالة عبدالرحمن مبارك
package.name = debtapp
package.domain = com.hwzrman
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy,kivymd,pillow
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
presplash.filename = %(source.dir)s/presplash.png
icon.filename = %(source.dir)s/icon.png
