from PyQt5.QtWidgets import *
from music import Ui_MusicApp
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QUrl, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtCore import Qt
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from db_function import *
import time
import os
import songs
from db_function import *
import random

class ModernMusicApp(QMainWindow, Ui_MusicApp):
    def __init__(self):
        super().__init__()
        self.wondow = QMainWindow
        self.setupUi(self)

        # Remove title bar
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowTitle("KGM audio player")
        self.setWindowIcon(QIcon(":/img/utils/images/KGM app logo.png"))

        # Globals (Consider using instance attributes instead)
        self.stopped = False
        self.looped = False
        self.is_shuffled = False

        # DB STUFF
        create_database_or_database_table("favorites")

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

        # listViews
        self._views = {
            'all': self.song_listWidget,
            'favourites': self.playlist_Widget_2,
            'playlist': self.playlist_Widget,
        }
        # Songlists
        self._song_list = {
            'all': songs.current_song_list,
            'favourites': songs.favorite_songs_list,
            'playlist': songs.playlist_songs_list,
        }

        self._active_view = 'all'
        self._active_widget = self._views[self._active_view]
        self._active_list = self._song_list[self._active_view]

        for view in self._views.values():
            view.itemDoubleClicked.connect(self._play_selected_audio)

        # Connections
        self.add_songs_btn.clicked.connect(self.add_Songs)
        self.play_btn.clicked.connect(self._toggle_play)
        self.pause_btn.clicked.connect(self.pause_and_unpause)
        self.stop_btn.clicked.connect(self.stop_song)
        self.next_btn.clicked.connect(self._play_next_song)
        self.prev_btn.clicked.connect(self._play_previous_song)
        self.loop_btn.clicked.connect(self.toggle_loop)
        self.shuffle_songs_btn.clicked.connect(self.toggle_shuffle_mode)
        self.delete_selected_btn.clicked.connect(self._remove_one_song)
        self.delete_all_songs_btn.clicked.connect(self._remove_all_songs)
        self.App_logo.clicked.connect(self.show_about_dialog)
        self.song_list_btn.clicked.connect(self.show_all_songs_page)
        self.favourites_btn.clicked.connect(self.show_favourites_page)
        self.playlist_btn.clicked.connect(self.show_playlist_page)

        self.add_Songs()

        # loop/suffle/playback
        self.player.mediaStatusChanged.connect(self._handle_media_status)
        self.loop_playlist = False
        self.shuffle_mode = False

        # data storage
        os.makedirs("data", exist_ok=True)
        self.favourites_list = songs.favorite_songs_list
        self.playlist_list = songs.playlist_songs_list
        self.song_listWidget = self._views['all']

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

        # FAVOURITES PAGE

        self.show()

    # active page
    def _activate(self, key):
        self._active_view = key
        self._active_widget = self._views[key]
        self._active_list = self._song_list[key]


    def _handle_media_status(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self._play_next_if_available()

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
        if self.stopped:
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
                self.song_listWidget.addItem(
                       QListWidgetItem(
                         QtGui.QIcon(':/img/utils/images/MusicListItem.png'),
                          os.path.basename(file)
                    )
                )

    # Text marquee (scrolling label text)
    def start_marquee(self, label: QLabel):
        text = label.text()
        if len(text) <= 1:
            return

        def scroll_text():
            current = label.text()
            label.setText(current[1:] + current[0])

        if hasattr(label, "_marquee_timer") and label._marquee_timer:
            label._marquee_timer.stop()

        timer = QTimer(self)
        timer.timeout.connect(scroll_text)
        timer.start(150)
        label._marquee_timer = timer

    def _play_selected_audio(self, item=None):
        idx = self._active_widget.currentRow()
        if idx < 0 or idx >= len(self._active_list):
            return

        current_song = self._active_list[idx]
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(current_song)))
        self.player.play()

        self.Current_song_name.setText(os.path.basename(current_song))
        self.Current_song_path.setText(os.path.dirname(current_song))
        self.start_marquee(self.Current_song_name)
        self.start_marquee(self.Current_song_path)
        self._set_album_art(current_song)

    def _toggle_play(self):
        if self.player.media().isNull():
            self._play_selected_audio(self._active_widget.currentItem())
        elif self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    # Handle media status changes
    def toggle_shuffle_mode(self):
        self.shuffle_mode = not self.shuffle_mode
        print(f"Shuffle mode {'enabled' if self.shuffle_mode else 'disabled'}")

    def toggle_loop(self):
        self.loop_playlist = not self.loop_playlist
        print(f"Loop mode {'enabled' if self.loop_playlist else 'disabled'}")

    def _play_next_if_available(self):
        try:
            if not self._active_list:
                return

            current_index = self._active_widget.currentRow()
            next_index = -1

            if self.shuffle_mode:
                next_index = random.randint(0, len(self._active_list) - 1)
            else:
                next_index = current_index + 1
                if next_index >= len(self._active_list):
                    if self.loop_playlist and len(self._active_list) > 0:
                        next_index = 0
                    else:
                        print("Reached end of playlist.")
                        return

            if 0 <= next_index < len(self._active_list):
                next_song = self._active_list[next_index]
                self._play_song_at_index(next_index, next_song)

        except Exception as e:
            print(f"Error in play_next_if_available: {e}")

    def _play_song_at_index(self, index, song_path):
        song_url = QMediaContent(QUrl.fromLocalFile(song_path))
        self.player.setMedia(song_url)
        self.player.play()
        self._active_widget.setCurrentRow(index)
        self.Current_song_name.setText(os.path.basename(song_path))
        self.Current_song_path.setText(os.path.dirname(song_path))
        self.start_marquee(self.Current_song_name)
        self.start_marquee(self.Current_song_path)
        self._set_album_art(song_path)

    def get_album_art_from_audio(self, audio_file_path):

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

    def _set_album_art(self, audio_file_path):
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

    # Play next song
    def _play_next_song(self):
        self._play_next_if_available()

    # Play previous song

    def _play_previous_song(self):
        try:
            current_index = self._active_widget.currentRow()
            prev_index = current_index - 1
            if 0 <= prev_index < len(self._active_list):
                prev_song = self._active_list[prev_index]
                self._play_song_at_index(prev_index, prev_song)
            elif self.loop_playlist and len(self._active_list) > 0:
                prev_index = len(self._active_list) - 1
                prev_song = self._active_list[prev_index]
                self._play_song_at_index(prev_index, prev_song)
        except Exception as e:
            print(f"Error playing previous song: {e}")

    # remove one song
    def _remove_one_song(self):
        current_selection = self._active_widget.currentRow()
        if current_selection != -1:
            item_text = self._active_widget.item(current_selection).text()

            item = self._active_widget.takeItem(current_selection)

            if self._active_view == 'all':
                if 0 <= current_selection < len(songs.current_song_list):
                    del songs.current_song_list[current_selection]
            elif self._active_view == 'favourites':
                song_path_to_remove = None
                for song_path in songs.favorite_songs_list:
                    if os.path.basename(song_path) == item_text:
                        song_path_to_remove = song_path
                        break

                if song_path_to_remove:
                    if song_path_to_remove in songs.favorite_songs_list:
                        songs.favorite_songs_list.remove(song_path_to_remove)

                    delete_song_from_database_table(song=song_path_to_remove, table='favorites')
                else:
                    print(f"Warning: Could not find song path matching '{item_text}' in favorites list.")

            elif self._active_view == 'playlist':
                if 0 <= current_selection < len(songs.playlist_songs_list):
                    del songs.playlist_songs_list[current_selection]


    # remove all songs
    def _remove_all_songs(self):
        if self._active_view == 'all':
            self._views['all'].clear()
            songs.current_song_list.clear()
        elif self._active_view == 'favourites':
            self._views['favourites'].clear()
            songs.favorite_songs_list.clear()
            delete_all_song_from_database_table(table='favorites')
        elif self._active_view == 'playlist':
            self._views['playlist'].clear()
            songs.playlist_songs_list.clear()


    # songs list (not directly called in the provided snippet)
    def song_list(self):
        try:
            self._views['all'].clear()
            for song in songs.current_song_list:
                self._views['all'].addItem(
                    QListWidgetItem(
                        QtGui.QIcon(':/img/utils/images/MusicListItem.png'),
                        os.path.basename(song)
                    )
                )
        except Exception as e:
            print(f"Error displaying")


    def show_all_songs_page(self):
        self._activate('all')
        self.stackedWidget.setCurrentWidget(self.song_listWidget)


    def show_favourites_page(self):
        self._activate('favourites')
        self.stackedWidget.setCurrentWidget(self.playlist_Widget_2)
        songs.favorite_songs_list = fetch_all_songs_from_database_table(table='favorites')
        self._views['favourites'].clear()
        for song_path in songs.favorite_songs_list:
             self._views['favourites'].addItem(
                 QListWidgetItem(
                     QtGui.QIcon(':/img/utils/images/MusicListItem.png'),
                     os.path.basename(song_path)
                 )
             )


    def show_playlist_page(self):
        self._activate('playlist')
        self.stackedWidget.setCurrentWidget(self.playlist_Widget)


#DIALOGUE about page
class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About KGM Audio Player")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()

        # App logo
        logo_label = QLabel()
        logo_pixmap = QPixmap(":/img/utils/images/KGM app logo1.png").scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
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