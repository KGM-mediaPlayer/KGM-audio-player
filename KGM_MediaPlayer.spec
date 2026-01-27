import os
import sys
from PyInstaller.utils.hooks import collect_submodules

BASE_DIR = os.path.abspath(os.getcwd())
block_cipher = None

vlc_lib_path = '/Applications/VLC.app/Contents/MacOS/lib/libvlc.5.dylib'
vlc_plugins_path = '/Applications/VLC.app/Contents/MacOS/plugins'

vlc_submodules = collect_submodules('vlc')

a = Analysis(
    ['main.py'],
    pathex=[BASE_DIR],
    binaries=[(vlc_lib_path, '.')],
    datas=[
        (os.path.join(BASE_DIR, 'src/frontend/assets'), 'assets'),
        (os.path.join(BASE_DIR, 'src/backend/assets'), 'assets'),
        (os.path.join(BASE_DIR, 'src/frontend/themes'), 'themes'),
        (os.path.join(BASE_DIR, 'src/frontend/styles.qss'), '.'),
        (vlc_plugins_path, 'vlc_plugins')
    ],
    hiddenimports=['PyQt5.sip'] + vlc_submodules,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='KGM-MediaPlayer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='KGM-MediaPlayer',
)

app = BUNDLE(
    exe,
    name='KGM-MediaPlayer.app',
    icon='src/frontend/assets/icon.icns', # Make sure this is a .icns file for Mac
    bundle_identifier='com.kgm.player',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'LSBackgroundOnly': 'False',
        'NSRequiresAquaSystemAppearance': 'False',
    },
)