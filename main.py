from PyQt5 import QtWidgets, QtCore, QtGui
from src.frontend.kgm_media_player import MainWindow
from src.frontend.videoPlayer import VideoPlayerWindow
from src.backend.player_logic import MediaPlayer, resource_path 
import sys

def load_styles(app):
    try:
        with open(resource_path("styles.qss"), "r") as f: 
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Warning: styles.qss not found. Running without custom styles.")
    except Exception as e:
        print(f"Error loading QSS: {e}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    load_styles(app) 
    appWindow = MainWindow()
    logic_controller = MediaPlayer(appWindow)
    appWindow.show()
    sys.exit(app.exec_())