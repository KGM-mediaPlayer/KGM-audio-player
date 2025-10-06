from PyQt5 import QtWidgets, QtCore
from src.frontend.kgm_media_player import qtw,MainWindow # Your generated UI
import sys

if __name__ == "__main__":
    app =qtw.QApplication([])
    appWindow=MainWindow()
    appWindow.show()

    sys.exit(app.exec_())
