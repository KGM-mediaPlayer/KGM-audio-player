from PyQt5 import QtWidgets, QtCore, QtGui
from src.frontend.kgm_media_player import MainWindow
from src.frontend.videoPlayer import VideoWindow
from src.backend.player_logic import MediaPlayer, resource_path 
import sys
import os

def setup_environment():
    if hasattr(sys, '_MEIPASS'):
        os.chdir(sys._MEIPASS)
    else:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

def load_styles(app):
    try:
        qss_path = resource_path("styles.qss")
        with open(qss_path, "r") as f: 
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print(f"Warning: styles.qss not found at {qss_path}")
    except Exception as e:
        print(f"Error loading QSS: {e}")

if __name__ == "__main__":
    setup_environment()
    
    app = QtWidgets.QApplication(sys.argv)
    
    load_styles(app) 
    
    appWindow = MainWindow()
    logic_controller = MediaPlayer(appWindow)
    
    appWindow.show()
    sys.exit(app.exec_())