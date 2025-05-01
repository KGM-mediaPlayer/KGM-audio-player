from main import ModernMusicApp
from PyQt5.QtWidgets import QApplication
import sys

app=QApplication(sys.argv)
window=ModernMusicApp()
sys.exit(app.exec_())