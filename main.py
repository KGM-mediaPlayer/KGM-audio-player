from PyQt5.QtWidgets import *
from music import Ui_MusicApp
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QUrl, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtGui import QIcon,QImage,QPixmap
from PyQt5.QtCore import Qt,pyqtSignal
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from config_loader import load_config, save_config
import sys
import json
import time
import os 
import songs

class ModernMusicApp(QMainWindow, Ui_MusicApp):
    def __init__(self):
        super().__init__()
        self.wondow = QMainWindow  # (still unused, but kept per request)
        self.setupUi(self)

        # Remove title bar
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowTitle("KGM audio player")
        self.setWindowIcon(QIcon(":/img/utils/images/KGM app logo.png"))
        
        # Globals
        global stopped
        global looped
        global is_shuffled
        stopped = False
        looped = False
        is_shuffled = False

        # Create player
        self.player = QMediaPlayer()

        self.inititial_volume = 20
        self.player.setVolume(self.inititial_volume)
        self.volume_dial.setValue(self.inititial_volume)

        # Initial position of the window
        self.inititial_position = None
        
        # Slider timer
        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.move_slider)

        # Connections
        self.add_songs_btn.clicked.connect(self.add_Songs)
        self.play_btn.clicked.connect(self.play_audio)
        self.pause_btn.clicked.connect(self.pause_and_unpause)
        self.stop_btn.clicked.connect(self.stop_song)
        self.next_btn.clicked.connect(self.next_song)
        self.prev_btn.clicked.connect(self.previous_song)
        self.loop_btn.clicked.connect(self.looped_next)
        self.shuffle_songs_btn.clicked.connect(self.toggle_shuffle_mode)
        self.delete_selected_btn.clicked.connect(self.remove_one_song)
        self.delete_all_songs_btn.clicked.connect(self.remove_all_songs)
        self.listWidget.itemDoubleClicked.connect(self.play_audio)
        self.favourites_btn.clicked.connect(self.show_favourite_songs)
        self.playlist_btn.clicked.connect(self.show_playlist)
        self.song_list_btn.clicked.connect(self.song_list)
        self.App_logo.clicked.connect(self.show_about_dialog)


        
        # loop/suffle/playback
        self.player.mediaStatusChanged.connect(self.handle_media_status)
        self.loop_playlist = True 
        self.shuffle_mode = False
        
        # data storage
        self.favorites_file = "data/favorites.json"
        os.makedirs("data", exist_ok=True)  # Ensure directory exists
        self.favourites_list = songs.favorite_songs_list
        self.playlist = songs.current_song_list
        self.default_music_folder = self.get_or_select_music_folder()
        self.load_tracks_from_folder(self.default_music_folder)


        # Slider interactions
        self.music_slider.sliderPressed.connect(lambda: setattr(self, 'stopped', True))
        self.music_slider.sliderReleased.connect(self.seek_slider_release)

        self.volume_dial.valueChanged.connect(self.volume_changed)


        # Define mouse move function for dragging
        def moveApp(event):
            if event.buttons() == QtCore.Qt.LeftButton and self.inititial_position:
                self.move(event.globalPos() - self.inititial_position)
                event.accept()

        self.title_frame.mouseMoveEvent = moveApp

        # Define mouse press function to get offset
        def pressApp(event):
            if event.button() == QtCore.Qt.LeftButton:
                self.inititial_position = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()

        self.title_frame.mousePressEvent = pressApp

        self.show()

    def handle_media_status(self, status):
            if status == QMediaPlayer.EndOfMedia:
                self.play_next_if_available()
    
    # Format time from milliseconds to M:S or H:M:S
    def format_time(self, ms):
        seconds = int(ms / 1000)
        if seconds < 3600:
            return time.strftime('%M:%S', time.gmtime(seconds))
        else:
            return time.strftime('%H:%M:%S', time.gmtime(seconds))
    
    # ABOUT PAGE
    def show_about_dialog(self, event=None):
        dialog = AboutDialog(self)
        dialog.exec_()


    # Function to move slider
    def move_slider(self):
        if getattr(self, "stopped", False):
            return

        if self.player.state() == QMediaPlayer.PlayingState:
            self.music_slider.setMinimum(0)
            self.music_slider.setMaximum(self.player.duration())

            current_pos = self.player.position()
            self.music_slider.setValue(current_pos)

            elapsed = self.format_time(current_pos)
            total = self.format_time(self.player.duration())

            self.time_lable.setText(f"{elapsed} / {total}")

    # Seek to new slider position after dragging
    def seek_slider_release(self):
        self.stopped = False
        self.player.setPosition(self.music_slider.value())

    # Add songs
    def add_Songs(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, caption='Add audio files', directory='C:\\', 
            filter="Supported files (*.mp3 *.wav *.flac *.ogg *.m4a)"
        )
        
        if files:
            print(files) 
            for file in files:
                songs.current_song_list.append(file)
                self.listWidget.addItem(
                    QListWidgetItem(
                        QtGui.QIcon(':/img/utils/images/MusicListItem.png'), 
                        os.path.basename(file)
                    )
                )

    # Text marquee (scrolling label text)
    def start_marquee(self, label: QLabel):
        text = label.text()
        if len(text) <= 1:
            return  # Skip short text

        def scroll_text():
            current = label.text()
            label.setText(current[1:] + current[0])  # Rotate text left

        # Stop any existing timer if needed
        if hasattr(label, "_marquee_timer") and label._marquee_timer:
            label._marquee_timer.stop()

        timer = QTimer(self)
        timer.timeout.connect(scroll_text)
        timer.start(150)  # speed in milliseconds
        label._marquee_timer = timer

    # Play audio file
    def play_audio(self):
        try:
            current_selection = self.listWidget.currentRow()
            current_song = songs.current_song_list[current_selection]

            song_url = QMediaContent(QUrl.fromLocalFile(current_song))
            self.player.setMedia(song_url)
            self.player.play()

            self.Current_song_name.setText(os.path.basename(current_song))
            self.Current_song_path.setText(os.path.dirname(current_song))

            # Marquee function
            self.start_marquee(self.Current_song_name)
            self.start_marquee(self.Current_song_path)

            # Extract and display album art
            album_art = self.get_album_art_from_audio(current_song)
            if album_art:
                self.album_art_view.setPixmap(QPixmap.fromImage(album_art))
                self.set_album_art(current_song)
            else:
                default_pixmap = QPixmap("utils/images/No-album-art.png")
                self.album_art_view.setPixmap(default_pixmap)

        except Exception as e:
            print(f"Error playing audio: {e}")
    
    # Handle media status changes
    def toggle_shuffle_mode(self):
        self.shuffle_mode = not self.shuffle_mode
        print(f"Shuffle mode {'enabled' if self.shuffle_mode else 'disabled'}")


    def play_next_if_available(self):
        try:
            if not songs.current_song_list:
                return

            if self.shuffle_mode:
                import random
                next_index = random.randint(0, len(songs.current_song_list) - 1)
            else:
                current_index = self.listWidget.currentRow()
                next_index = current_index + 1

                if next_index >= len(songs.current_song_list):
                    if self.loop_playlist:
                        next_index = 0
                    else:
                        print("Reached end of playlist.")
                        return

            next_song = songs.current_song_list[next_index]

            song_url = QMediaContent(QUrl.fromLocalFile(next_song))
            self.player.setMedia(song_url)
            self.player.play()
            self.listWidget.setCurrentRow(next_index)

            self.Current_song_name.setText(os.path.basename(next_song))
            self.Current_song_path.setText(os.path.dirname(next_song))
            self.start_marquee(self.Current_song_name)
            self.start_marquee(self.Current_song_path)
            self.set_album_art(next_song)

        except Exception as e:
            print(f"Error in play_next_if_available: {e}")

    def get_album_art_from_audio(self, audio_file_path):
        """
        Extract album art from the audio file using Mutagen.
        Returns QImage or None if no album art is found.
        """
        try:
            # Open the audio file
            audio = MP3(audio_file_path, ID3=ID3)

            # Check for embedded album art (APIC frame)
            for tag in audio.tags.values():
                if isinstance(tag, APIC) and tag.type == 3:  # Type 3 is for front cover
                    album_art_data = tag.data
                    if album_art_data:
                        # Convert the album art binary data into a QImage
                        album_art_image = QImage()
                        album_art_image.loadFromData(album_art_data)
                        return album_art_image
        except Exception as e:
            print(f"Error extracting album art: {e}")

        # Return None if no album art is found
        return None
    
    def set_album_art(self, audio_file_path):
        """
        Gets album art from the audio file and displays it in albumArtLabel.
        Clears the label if no art is found.
        """
        album_art = self.get_album_art_from_audio(audio_file_path)
        if album_art:
            self.album_art_view.setPixmap(QPixmap.fromImage(album_art))
        else:
            default_pixmap = QPixmap("utils/images/No-album-art.png")
            self.album_art_view.setPixmap(default_pixmap)


    # Pause and unpause audio
    def pause_and_unpause(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()
    
    # Stop audio
    def stop_song(self):
        try:
            self.player.stop()
        except Exception as e:
            print(f"Error stopping audio: {e}")
    
    # Change volume
    def volume_changed(self, value):
        self.player.setVolume(value)
    
    #Default next song
    def default_next(self):
        try:
            song_index = self.listWidget.currentRow()
            next_index = song_index + 1
            next_song= songs.current_song_list[next_index]

            song_url = QMediaContent(QUrl.fromLocalFile(next_song))
            self.player.setMedia(song_url)
            self.player.play()
            self.listWidget.setCurrentRow(next_index)

            self.Current_song_name.setText(os.path.basename(next_song))
            self.Current_song_path.setText(os.path.dirname(next_song))
            
            # Marquee function
            self.start_marquee(self.Current_song_name)
            self.start_marquee(self.Current_song_path)

            # Extract and display album art
            album_art = self.get_album_art_from_audio(next_song)
            if album_art:
                self.album_art_view.setPixmap(QPixmap.fromImage(album_art))
                self.set_album_art(next_song)
            else:
                default_pixmap = QPixmap("utils/images/No-album-art.png")
                self.album_art_view.setPixmap(default_pixmap)
        except Exception as e:
            print(f"Default next song error: {e}")
    
    # Looped next song
    def looped_next(self):
        try:
            current_index = self.listWidget.currentRow()
            current_song = songs.current_song_list[current_index]

            song_url = QMediaContent(QUrl.fromLocalFile(current_song))
            self.player.setMedia(song_url)
            self.player.play()
            self.listWidget.setCurrentRow(current_index)  # Optional but safe

            self.Current_song_name.setText(os.path.basename(current_song))
            self.Current_song_path.setText(os.path.dirname(current_song))

            self.start_marquee(self.Current_song_name)
            self.start_marquee(self.Current_song_path)

            self.set_album_art(current_song)

        except Exception as e:
            print(f"Loop current song error: {e}")

    
    
    def shuffled_next(self):
        try:
            import random
            song_list = songs.current_song_list
            if not song_list:
                return

            random_song = random.choice(song_list)
            random_index = song_list.index(random_song)

            song_url = QMediaContent(QUrl.fromLocalFile(random_song))
            self.player.setMedia(song_url)
            self.player.play()
            self.listWidget.setCurrentRow(random_index)

            self.Current_song_name.setText(os.path.basename(random_song))
            self.Current_song_path.setText(os.path.dirname(random_song))

            self.start_marquee(self.Current_song_name)
            self.start_marquee(self.Current_song_path)

            self.set_album_art(random_song)

        except Exception as e:
            print(f"Shuffled next song error: {e}")

    
    #play_next song
    def next_song(self):
        try:
            song_index = self.listWidget.currentRow()
            next_index = song_index + 1
            next_song= songs.current_song_list[next_index]

            song_url = QMediaContent(QUrl.fromLocalFile(next_song))
            self.player.setMedia(song_url)
            self.player.play()
            self.listWidget.setCurrentRow(next_index)

            self.Current_song_name.setText(os.path.basename(next_song))
            self.Current_song_path.setText(os.path.dirname(next_song))
            
            # Marquee function
            self.start_marquee(self.Current_song_name)
            self.start_marquee(self.Current_song_path)

            # Extract and display album art
            album_art = self.get_album_art_from_audio(next_song)
            if album_art:
                self.album_art_view.setPixmap(QPixmap.fromImage(album_art))
                self.set_album_art(next_song)
            else:
                default_pixmap = QPixmap("utils/images/No-album-art.png")
                self.album_art_view.setPixmap(default_pixmap)

        except Exception as e:
            print(f"Error getting current song index: {e}")
            return
    
    #play_next song
    def previous_song(self):
        try:
            song_index = self.listWidget.currentRow()
            prev_index = song_index - 1
            prev_song= songs.current_song_list[prev_index]

            song_url = QMediaContent(QUrl.fromLocalFile(prev_song))
            self.player.setMedia(song_url)
            self.player.play()
            self.listWidget.setCurrentRow(prev_index)

            self.Current_song_name.setText(os.path.basename(prev_song))
            self.Current_song_path.setText(os.path.dirname(prev_song))
            
            # Marquee function
            self.start_marquee(self.Current_song_name)
            self.start_marquee(self.Current_song_path)
            
            # Extract and display album art
            album_art = self.get_album_art_from_audio(prev_song)
            if album_art:
                self.album_art_view.setPixmap(QPixmap.fromImage(album_art))
                self.set_album_art(prev_song)
            else:
                default_pixmap = QPixmap("utils/images/No-album-art.png")
                self.album_art_view.setPixmap(default_pixmap)

        except Exception as e:
            print(f"Error getting current song index: {e}")
            return
    # remove one somg
    def remove_one_song(self):
        try:
            current_selection = self.listWidget.currentRow()
            if current_selection != -1:
                self.listWidget.takeItem(current_selection)
                del songs.current_song_list[current_selection]
        except Exception as e:
            print(f"Error removing song: {e}")
    
    # remove all songs
    def remove_all_songs(self):
        try:
            self.listWidget.clear()
            songs.current_song_list.clear()
        except Exception as e:
            print(f"Error removing all songs: {e}")
    
    # songs list
    def song_list(self):
        try:
            self.listWidget.clear()
            for song in songs.current_song_list:
                self.listWidget.addItem(
                    QListWidgetItem(
                        QtGui.QIcon(':/img/utils/images/MusicListItem.png'), 
                        os.path.basename(song)
                    )
                )
        except Exception as e:
            print(f"Error displaying songs list: {e}")
    
    #playlist
    def show_playlist(self):
        try:
            self.listWidget.clear()
            for song in songs.current_song_list:
                self.listWidget.addItem(
                    QListWidgetItem(
                        QtGui.QIcon(':/img/utils/images/MusicListItem.png'), 
                        os.path.basename(song)
                    )
                )
        except Exception as e:
            print(f"Error displaying playlist: {e}")
    
    # favourite songs
    def show_favourite_songs(self):
        try:
            self.listWidget.clear()
            for song in songs.current_song_list:
                self.listWidget.addItem(
                    QListWidgetItem(
                        QtGui.QIcon(':/img/utils/images/MusicListItem.png'), 
                        os.path.basename(song)
                    )
                )
        except Exception as e:
            print(f"Error displaying favourite songs: {e}")
    
    # dealling with favorites & playlists

    def get_or_select_music_folder(self):
        config_path = "data/config.json"
        os.makedirs("data", exist_ok=True)

        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config = json.load(f)
                return config.get("music_folder", "")

        # Ask user to select a music folder
        folder = QFileDialog.getExistingDirectory(self, "Select Your Music Folder")
        if folder:
            with open(config_path, "w") as f:
                json.dump({"music_folder": folder}, f)
            return folder
        else:
            QMessageBox.warning(self, "No Folder Selected", "No folder was selected. Exiting app.")
            sys.exit()
    
    def load_tracks_from_folder(self, folder_path):
        supported_ext = ('.mp3', '.wav', '.flac', '.ogg', '.m4a')
        try:
            songs_in_folder = [
                os.path.join(folder_path, f)
                for f in os.listdir(folder_path)
                if f.lower().endswith(supported_ext)
            ]
            songs.current_song_list = songs_in_folder
            self.playlist()
        except Exception as e:
            print(f"Error loading songs from folder: {e}")


#DIALOGUE about page
class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About KGM Audio Player")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()

        # App logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("utils/images/KGM app logo1.png").scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)

        # App info text
        info_label = QLabel(
            "<h2>KGM Audio Player</h2>"
            "<p>Version: 1.0</p>"
            "<p>Developed by: Kisakye Gibreel</p>"
            "<p>Thank you for using this player!</p>"
            "<p>Copyright 2025</p>"
            "<p>Kampala,Uganda 🇺🇬</p>"
        )
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setWordWrap(True)

        # Add widgets to layout
        layout.addWidget(logo_label)
        layout.addWidget(info_label)

        self.setLayout(layout)

