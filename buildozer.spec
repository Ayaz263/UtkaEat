[app]

# (str) Title of your application
title = UtkaEat Client App

# (str) Package name
package.name = utkaeatclient

# (str) Package domain (needed for Google Play AAB format)
package.domain = org.test

# (str) Application version
version = 0.1

# (list) Application requirements
# python3 - основной интерпретатор
# kivy - фреймворк
# socket, threading, sys - стандартные библиотеки Python, их не нужно указывать в требованиях buildozer
requirements = python3, kivy

# (str) Main application file
source.include_exts = py, png, jpg, kv, atlas
source.dir = .
main.py = client.py

# (list) Permissions
# Для работы с сетью вам обязательно нужны эти разрешения на Android
permissions = INTERNET

# (str) Icon file
# icon.filename = %(source.dir)s/icon.png # Раскомментируйте и укажите путь к иконке

# (list) Supported orientations
# options: landscape, portrait, all
orientation = portrait

# (bool) Enable fullscreen mode
fullscreen = 0 # Используем 0, чтобы статус бар Android был виден

# Android target
# android.api = 33 # Рекомендуется использовать свежий API
# android.minapi = 21

# (str) Android screen orientation (portrait or landscape)
# screen.orientation = portrait

# ----------------------------------------------------------------------
# Расширенные настройки, которые можно оставить по умолчанию
# ----------------------------------------------------------------------

# (int) Android SDK version to use
# android.api = 27

# (int) Minimum API level your app supports
# android.minapi = 21

# (int) Android SDK version to compile against
# android.targetapi = 27

# (str) Android NDK version to use
# android.ndk = 19c

# (bool) Use the Python environment bootstrap
# android.use_setup_env = true

# (str) Presplash image
# presplash.filename = %(source.dir)s/data/presplash.png

# (str) AAB file name
# android.aab = %(app.name)s-%(app.version)s.aab
