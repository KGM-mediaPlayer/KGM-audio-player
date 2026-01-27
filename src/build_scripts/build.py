import os
import PyInstaller.__main__

# Optional: Clean previous builds
if os.path.exists("build"):
    os.system("rm -rf build")
if os.path.exists("dist"):
    os.system("rm -rf dist")

PyInstaller.__main__.run([
    'run.py',                          # Entry point of your app
    '--name=KGM Media Player',         # Name of the final app
    '--onefile',                       # Create single executable
    '--noconsole',                     # Hide console window
    '--add-data=UI_v2:UI_v2',         # Include your UI assets folder
    '--add-data=EQ.ui:.',             # Include EQ.ui in base dir
    '--add-data=music_library.db:.',  # Include database file
    '--icon=icon.ico',                # Optional icon
    '--hidden-import=PyQt5.sip',      # Required for PyQt
    '--hidden-import=vlc',            # Required for VLC
    '--hidden-import=mutagen',        # Required for metadata
])
