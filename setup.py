"""
This is a setup.py script for py2app to create a macOS application bundle
for the Zoom Recording Prompt application.

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['zoom_recording_prompt.py']
DATA_FILES = ['env.example', 'README.md']
OPTIONS = {
    'argv_emulation': True,
    'packages': ['PyQt6', 'requests', 'pyautogui', 'dotenv', 'psutil'],
    'plist': {
        'CFBundleName': 'Zoom Recording Prompt',
        'CFBundleDisplayName': 'Zoom Recording Prompt',
        'CFBundleIdentifier': 'com.yourusername.zoomrecordingprompt',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2024 Your Name. All rights reserved.',
        'NSPrincipalClass': 'NSApplication',
        'LSUIElement': True,  # Makes the app run without a dock icon (background app)
    }
}

setup(
    name='Zoom Recording Prompt',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=[
        'PyQt6',
        'requests',
        'pyautogui',
        'python-dotenv',
        'psutil'
    ],
)
