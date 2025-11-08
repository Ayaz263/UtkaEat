[app]

# (str) Title of your application
title = UtkaEat Client App

# (str) Package name
package.name = utkaeatclient

# (str) Package domain (needed for Google Play AAB format)
package.domain = org.test

# (str) Application version
version = 0.1

android.arch = armeabi-v7a
p4a.python_version = 3.10 

# (list) Application requirements
requirements = python3, kivy

# (str) Main application file and source directory
source.dir = .
main.py = main.py 

# (list) Permissions
permissions = INTERNET

# (str) Icon file - Используем относительный путь от source.dir (.)
icon.filename = icon.png 

# (list) Supported orientations
orientation = portrait

# (bool) Enable fullscreen mode
fullscreen = 0 

# Android target APIs
android.api = 27 
android.minapi = 21
android.targetapi = 27

# ----------------------------------------------------------------------
# Расширенные настройки, которые можно оставить по умолчанию
# ----------------------------------------------------------------------

# (bool) Use the Python environment bootstrap
# android.use_setup_env = true

# (str) Presplash image
# presplash.filename = %(source.dir)s/data/presplash.png
