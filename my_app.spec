# my_app.spec

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run.py'],  # Entry point
    pathex=[],
    binaries=[],
    datas=[
        ('icon.ico', '.'),  # Include your app icon
        ('main.ui', '.'),   # Include your .ui file if loaded at runtime
        ('utils/bg_imgs/*', 'utils/bg_imgs'),  # Include all background images
        ('utils/images/*', 'utils/images'),    # Include other image resources
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='KGM audio player',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want a terminal
    icon='icon.ico'
)
