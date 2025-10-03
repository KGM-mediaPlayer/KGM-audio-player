from setuptools import setup
import os
import glob

APP = ['KGM-MediaPlayer.py']

# Include all PNGs from UI_v2 dynamically
DATA_FILES = [
    ('UI_v2', glob.glob('UI_v2/*.png')),
    ('', ['EQ.ui', 'music_library.db'])
]

OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'icon.icns',  # must be .icns for macOS
    'includes': [
        'pkg_resources',
        'jaraco.text',
        'PyQt5',
        'vlc',
        'mutagen'
    ],
    'packages': [
        'PyQt5',
        'vlc',
        'mutagen',
    ],
    'resources': [
        'UI_v2',             # Needed so py2app copies entire folder
        'EQ.ui',
        'music_library.db'
    ],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

