import sys
import os
import vlc
import sqlite3
import urllib.parse
from pathlib import Path
import random
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt,QTimer
from PyQt5.QtWidgets import QWidget,QMessageBox
from mutagen import File as MutagenFile
from mutagen.mp3 import HeaderNotFoundError

from src.frontend.kgm_media_player import MainWindow

import src.backend.database as database
from src.frontend.asset_loader import create_svg_icon, load_and_scale_image

#DIALOGUE about page
class AboutDialog(QDialog):
    def __init__(self, media_player_controller, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About KGM Media Player")
        self.setFixedSize(400, 300)
        self.media_player_controller = media_player_controller # Store controller reference if needed

        layout = QVBoxLayout()

        # Logo loading: Use resource_path instead of undefined create_svg_icon
        logo_label = QLabel()
        
        # Using a dummy path 'app.png' and ensuring resource_path is used
        logo_path = load_and_scale_image("app.png", size=70) 
        logo_label.setPixmap(logo_path)
        logo_label.setAlignment(Qt.AlignCenter)
        

        # App info text
        info_label = QLabel(
            "<h2>KGM Media Player</h2>"
            "<p>Version: 3.0.0</p>"
            "<p>Developed by: Kisakye Gibreel</p>"
            "<p>Thank you for using this player!</p>"
            "<p>Copyright October 2025</p>"
            "<p>Kampala, Uganda 🇺🇬</p>"
        )
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setWordWrap(True)

        layout.addWidget(logo_label)
        layout.addWidget(info_label)
        self.setLayout(layout)