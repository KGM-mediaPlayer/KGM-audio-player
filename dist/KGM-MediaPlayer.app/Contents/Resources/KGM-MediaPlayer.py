from PyQt5 import QtWidgets, QtCore
from main import MusicPlayer # Your generated UI
import sys

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    player = MusicPlayer()
    player.show()
    sys.exit(app.exec_())