import sys
import os
import vlc
import sqlite3
import urllib.parse
from pathlib import Path
import random
import resc_rc
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt,QTimer
from PyQt5.QtWidgets import QWidget,QMessageBox
from mutagen import File as MutagenFile
from mutagen.mp3 import HeaderNotFoundError

from music import Ui_MainWindow
from EQ import EqualizerWindow
import database

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and py2app/pyinstaller bundles."""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller / py2app frozen environment
        return os.path.join(sys._MEIPASS, relative_path)
    elif getattr(sys, 'frozen', False):
        # macOS app bundle, typical py2app case
        return os.path.join(os.path.dirname(sys.executable), '..', 'Resources', relative_path)
    else:
        # Normal dev mode
        return os.path.join(os.path.abspath("."), relative_path)


class MusicPlayer(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # Set up the GUI from music.py
        
        self.video_fullscreen = False

        # VLC setup
        self.vlc_instance = vlc.Instance('--no-xlib')  # '--no-xlib' for Linux, can be omitted on Windows/macOS
        self.player = self.vlc_instance.media_player_new()
        self.eq_window = EqualizerWindow(self.player)
        
        
        #remove title bar
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        
        # Slider timer
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1000)  # update every 1 second
        self.timer.timeout.connect(self.update_slider_position)
        
        # Window move
        self.ui.menu_bar.installEventFilter(self)

        self.ui.menu_bar.mousePressEvent = self.start_move
        self.ui.menu_bar.mouseMoveEvent = self.move_window
        self.ui.menu_bar.mouseReleaseEvent = self.stop_move

        

        self.setMouseTracking(True)
        self._drag_active = False
        self._drag_start_pos = None
        self.resize_dir = None
        self.is_resizing = False
        self.is_moving = False



        self.video_fullscreen = False
        self.original_video_parent = self.ui.video_view.parent()
        self.ui.video_view.installEventFilter(self)

        # database
        database.create_tables()
        db_table=self.removal_db_selection()

        # Load songs from the database
        database.get_all_songs('music_library')
        
        #play next if available
        self.shuffle = False
        self.looping = False
        self.original_playlist_data = []  # full list of (text, metadata)
        self.playback_order = []          # list of indices like [0, 1, 2, 3]
        self.current_play_index = 0       # position in playback_order

        self.event_manager = self.player.event_manager()
        self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.on_track_end)

        self.original_playlist = [self.ui.play_list_widget.item(i).text()
                          for i in range(self.ui.play_list_widget.count())]
        
        self.ui.play_list_widget.clear()
        for text, metadata in self.original_playlist_data:
            item = QtWidgets.QListWidgetItem(text)
            item.setData(QtCore.Qt.UserRole, metadata)
            self.ui.play_list_widget.addItem(item)




        self.ui.pause_btn.clicked.connect(self.toggle_play_pause)
        self.ui.next_btn.clicked.connect(self.next_track)
        self.ui.prev_btn.clicked.connect(self.prev_track)
        self.ui.all_songs_btn.clicked.connect(self.load_songs)
        self.ui.favourite_btn.clicked.connect(self.favourite_songs)
        self.ui.back_to_home.clicked.connect(self.switch_page)
        self.ui.search_bar.textChanged.connect(self.search_play_list)
        self.ui.make_favourite_btn.clicked.connect(self.add_to_favourites)
        self.ui.add_songs_to_library_btn.clicked.connect(self.add_songs_to_library)
        self.ui.remove_all_songs_btn.clicked.connect(self.remove_songs_from_library)
        self.ui.remove_current_selection_btn.clicked.connect(self.remove_current_selection)
        self.ui.app_logo_2.clicked.connect(self.show_about_dialog)
        self.ui.duration_slider.sliderMoved.connect(self.set_slider_position)
        self.ui.play_list_widget.itemDoubleClicked.connect(self.play_selected_song)
        self.ui.play_list_btn.clicked.connect(self.playlist)
        self.ui.video_view_2.clicked.connect(self.switch_page)
        self.ui.video_view.mouseDoubleClickEvent = self.set_full_screen
        self.ui.loop_btn.clicked.connect(self.toggle_loop)
        self.ui.shuffle_btn.clicked.connect(self.toggle_shuffle)
        self.ui.about_track_btn.clicked.connect(self.show_track_info)


        #seek slider
        self.ui.duration_slider.sliderPressed.connect(self.pause_for_seek)
        self.ui.duration_slider.sliderReleased.connect(self.resume_after_seek)

        self.event_manager.event_attach(
            vlc.EventType.MediaParsedChanged, self.on_media_parsed
        )

        # Eq button
        self.ui.more_options_btn.clicked.connect(self.show_equalizer)

           
    connect = sqlite3.connect('music_library.db')
    connect.row_factory = sqlite3.Row  # Enable dict-style access
    cursor = connect.cursor()

    
    def show_about_dialog(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec_()
    
    def eventFilter(self, obj, event):
            if obj == self.ui.menu_bar:
                if event.type() == QtCore.QEvent.MouseButtonPress and event.button() == QtCore.Qt.LeftButton:
                    self._drag_active = True
                    self._drag_start_pos = event.globalPos() - self.frameGeometry().topLeft()
                    return True

                elif event.type() == QtCore.QEvent.MouseMove and self._drag_active:
                    self.move(event.globalPos() - self._drag_start_pos)
                    return True

                elif event.type() == QtCore.QEvent.MouseButtonRelease:
                    self._drag_active = False
                    return True

            return super().eventFilter(obj, event)
    
    def toggle_fullscreen_on_double_click(self, event):
        if event.type() == QtCore.QEvent.MouseButtonDblClick and event.source() == self.ui.video_view:
            if getattr(self, "video_fullscreen", False):
                # Restore to embedded view
                self.ui.video_view.setParent(self.original_video_parent)
                self.ui.video_view.setWindowFlags(Qt.Widget)
                self.original_video_parent.layout().addWidget(self.ui.video_view)
                self.ui.video_view.showNormal()
                self.ui.stackedWidget.setCurrentWidget(self.ui.video_view)
                self.overlay_ui.hide_overlay()
                self.video_fullscreen = False
            else:
                # Make fullscreen
                self.ui.video_view.setParent(None)
                self.ui.video_view.setWindowFlags(Qt.Window)
                self.ui.video_view.showFullScreen()
                self.overlay_ui.show_on_video(self.ui.video_view)
                self.video_fullscreen = True
            event.accept()

    def show_on_video(self, video_widget):
        self.setParent(video_widget)
        self.resize(video_widget.size())
        self.move(0, video_widget.height() - self.height())  # align to bottom
        self.show()
        self.raise_()  # make sure overlay is on top


    def eventFilter(self, obj, event):
        if obj == self.ui.video_view and event.type() == QtCore.QEvent.MouseButtonDblClick:
            self.toggle_fullscreen_on_double_click(event)
            return True
        return super().eventFilter(obj, event)


    def set_full_screen(self, event):
        if self.video_fullscreen:
            # Exit fullscreen
            self.ui.video_view.setParent(self.original_video_parent)
            self.ui.video_view.setWindowFlags(Qt.Widget)
            self.original_video_parent.layout().addWidget(self.ui.video_view)
            self.ui.video_view.showNormal()
            self.ui.center_stackedWidget.setCurrentWidget(self.ui.video_view)
            self.video_fullscreen = False
        else:
            # Enter fullscreen
            self.ui.video_view.setParent(None)
            self.ui.video_view.setWindowFlags(Qt.Window)
            self.ui.video_view.showFullScreen()

            self.video_fullscreen = True

        event.accept()

    
    def on_video_resized(self, event):
        self.overlay_ui.resize(self.ui.video_view.size())
        event.accept()

        # Attach the handler
        self.ui.video_view.resizeEvent = self.on_video_resized
    
    #windows move functions
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.start_pos = event.globalPos()
            self.start_rect = self.geometry()

            if self.resize_dir:
                self.is_resizing = True
            else:
                # Only allow move if mouse is in the title bar region
                if self.childAt(event.pos()) == self.ui.menu_bar:
                    self.is_moving = True

            event.accept()


    def mouseReleaseEvent(self, event):
        self.is_moving = False
        self.is_resizing = False
        event.accept()

    def start_move(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.start_pos = event.globalPos()
            self.is_moving = True
            event.accept()

    def move_window(self, event):
        if self.is_moving:
            delta = event.globalPos() - self.start_pos
            self.move(self.pos() + delta)
            self.start_pos = event.globalPos()
        event.accept()

    def stop_move(self, event):
        self.is_moving = False
        event.accept()

    def move_window(self, event):
        if self.is_moving:
            self.move(self.pos() + event.globalPos() - self.start_pos)
            self.start_pos = event.globalPos()
        event.accept()
    
    def update_cursor(self, event):
        pos = event.pos()
        rect = self.rect()
        margin = self.EDGE_MARGIN

        x, y, w, h = pos.x(), pos.y(), rect.width(), rect.height()

        if x <= margin and y <= margin:
            self.setCursor(QtCore.Qt.SizeFDiagCursor)
            self.resize_dir = 'top_left'
        elif x >= w - margin and y <= margin:
            self.setCursor(QtCore.Qt.SizeBDiagCursor)
            self.resize_dir = 'top_right'
        elif x <= margin and y >= h - margin:
            self.setCursor(QtCore.Qt.SizeBDiagCursor)
            self.resize_dir = 'bottom_left'
        elif x >= w - margin and y >= h - margin:
            self.setCursor(QtCore.Qt.SizeFDiagCursor)
            self.resize_dir = 'bottom_right'
        elif x <= margin:
            self.setCursor(QtCore.Qt.SizeHorCursor)
            self.resize_dir = 'left'
        elif x >= w - margin:
            self.setCursor(QtCore.Qt.SizeHorCursor)
            self.resize_dir = 'right'
        elif y <= margin:
            self.setCursor(QtCore.Qt.SizeVerCursor)
            self.resize_dir = 'top'
        elif y >= h - margin:
            self.setCursor(QtCore.Qt.SizeVerCursor)
            self.resize_dir = 'bottom'
        else:
            self.setCursor(QtCore.Qt.ArrowCursor)
            self.resize_dir = None

    def resize_window(self, event):
        if not self.start_pos or not self.start_rect:
            return

        delta = event.globalPos() - self.start_pos
        rect = self.start_rect

        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()

        if self.resize_dir == 'right':
            self.setGeometry(x, y, w + delta.x(), h)
        elif self.resize_dir == 'bottom':
            self.setGeometry(x, y, w, h + delta.y())
        elif self.resize_dir == 'bottom_right':
            self.setGeometry(x, y, w + delta.x(), h + delta.y())
        elif self.resize_dir == 'left':
            self.setGeometry(x + delta.x(), y, w - delta.x(), h)
        elif self.resize_dir == 'top':
            self.setGeometry(x, y + delta.y(), w, h - delta.y())
        elif self.resize_dir == 'top_left':
            self.setGeometry(x + delta.x(), y + delta.y(), w - delta.x(), h - delta.y())
        elif self.resize_dir == 'top_right':
            self.setGeometry(x, y + delta.y(), w + delta.x(), h - delta.y())
        elif self.resize_dir == 'bottom_left':
            self.setGeometry(x + delta.x(), y, w - delta.x(), h + delta.y())

    
    def add_songs_to_library(self):
        # Create a file dialog to choose files
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Audio Files (*.mp3 *.wav *.flac *.ogg *.m4a *.aac);;Video Files (*.mp4 *.avi *.mkv *.mov *.flv)")
        file_dialog.setViewMode(QtWidgets.QFileDialog.List)

        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            
            for file_path in selected_files:
                if os.path.isfile(file_path):
                    # Check if it's a video or audio file
                    if file_path.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.flv')):
                        # It's a video, add to playlist only
                        title, artist, album = self.get_song_metadata(file_path)
                        database.add_song('playlist', title, artist, album, file_path)  # Add to playlist
                    else:
                        # It's an audio file, add to music_library
                        title, artist, album = self.get_song_metadata(file_path)
                        database.add_song('music_library', title, artist, album, file_path)  # Add to music_library

    # Full screen
   

    def pause_for_seek(self):
        self.was_playing = self.player.is_playing()
        self.player.pause()

    def resume_after_seek(self):
        value = self.ui.duration_slider.value()
        self.player.set_time(value)
        if self.was_playing:
            self.player.play()

    def removal_db_selection(self):
        page_text = self.ui.page_label.text()
        if page_text == "All Songs":
            db_table = 'music_library'
        elif page_text == 'Favourites':
            db_table = 'favourites'
        elif page_text == 'Playlist':
            db_table = 'playlist'
        else:
            db_table = None  # Default to None or another value if necessary
        return db_table

    def remove_songs_from_library(self):
        db_table = self.removal_db_selection()
        if db_table:
            database.remove_all_songs(db_table)
            QtWidgets.QMessageBox.information(self, "Removed", f"All songs removed from {db_table}!")
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "Unknown page, no songs removed.")

    def remove_current_selection(self):
        db_table = self.removal_db_selection()
        if db_table:
            selected_item = self.ui.play_list_widget.currentItem()
            if selected_item:
                song_data = selected_item.data(QtCore.Qt.UserRole)
                path = song_data["path"]  # Use path as the unique identifier
                title = song_data["title"]

                database.remove_song(db_table, path)  # Pass path instead of title

                self.ui.play_list_widget.takeItem(self.ui.play_list_widget.row(selected_item))
                QtWidgets.QMessageBox.information(self, "Removed", f"'{title}' removed from {db_table}!")
            else:
                QtWidgets.QMessageBox.warning(self, "No Selection", "Please select a song to remove.")
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "Unknown page, no songs removed.")
   
    def set_slider_position(self, position):
        self.player.set_time(position)  # Seek to the specified time in ms
        self.ui.duration_slider.setValue(position)
        current_time = position / 1000  # ms to seconds
        self.ui.current_time_label.setText(self.format_time(current_time))

    def update_slider_position(self):
        current_time = self.player.get_time()  # in milliseconds
        self.ui.duration_slider.blockSignals(True)  # prevent triggering signals while updating
        self.ui.duration_slider.setValue(current_time)
        self.ui.duration_slider.blockSignals(False)
        self.ui.current_time_label.setText(self.format_time(current_time / 1000))

    def format_time(self, seconds):
        minutes, seconds = divmod(seconds, 60)
        return f"{int(minutes):02}:{int(seconds):02}"
    
    def set_duration(self):
        # Try to get the duration from the player
        duration = self.player.get_length()
        
        # Fallback to media duration if unavailable
        if duration <= 0:
            media = self.player.get_media()
            if media:
                duration = media.get_duration()
        
        # Ensure non-negative and convert to seconds
        duration = max(0, duration) / 1000

        # Setup slider
        self.ui.duration_slider.setRange(0, int(duration * 1000))  # use ms
        self.ui.duration_slider.setValue(0)
        self.ui.duration_slider.setPageStep(1000)
        self.ui.duration_slider.setSingleStep(1000)
        self.ui.duration_slider.setTracking(True)

        # Set total duration label only once
        self.ui.total_time_label.setText(self.format_time(duration))


    def get_song_metadata(self, file_path):
        try:
            audio = MutagenFile(file_path, easy=True)
            if not audio:
                raise ValueError("Unsupported or unrecognized file format")

            title = audio.get("title", [os.path.basename(file_path)])[0]
            artist = audio.get("artist", ["Unknown Artist"])[0]
            album = audio.get("album", ["Unknown Album"])[0]
            return title, artist, album

        except (HeaderNotFoundError, ValueError, Exception) as e:
            print(f"Skipping {file_path}: {e}")
            return os.path.basename(file_path), "Unknown Artist", "Unknown Album"

    
    def load_songs(self):
        self.ui.center_stackedWidget.setCurrentIndex(2)
        self.ui.page_label.setText("All Songs")
        songs = database.get_all_songs('music_library')
        self.ui.play_list_widget.clear()
        for song in songs:
            title, artist, album, path = song  # unpack tuple
            item = QtWidgets.QListWidgetItem(f"{title} - {artist}")
            item.setIcon(QtGui.QIcon(resource_path("UI_V2/MusicListItem.png")))
            item.setData(QtCore.Qt.UserRole, {
                "title": title,
                "artist": artist,
                "album": album,
                "path": path
            })
            self.ui.play_list_widget.addItem(item)
        self.select_currently_playing_song()
        
    def playlist(self):
        self.ui.center_stackedWidget.setCurrentIndex(2)
        self.ui.page_label.setText("Playlist")
        songs = database.get_all_songs('playlist')
        self.ui.play_list_widget.clear()
        for song in songs:
            title, artist, album, path = song
            item = QtWidgets.QListWidgetItem(f"{title} - {artist}")
            item.setData(QtCore.Qt.UserRole, {
                "title": title,
                "artist": artist,
                "album": album,
                "path": path
            })
            self.ui.play_list_widget.addItem(item)
        self.select_currently_playing_song()

    
    def favourite_songs(self):
        self.ui.center_stackedWidget.setCurrentIndex(2)
        self.ui.page_label.setText("Favourites")
        songs = database.get_all_songs('favourites')
        self.ui.play_list_widget.clear()
        for song in songs:
            title, artist, album, path = song  # unpack tuple
            item = QtWidgets.QListWidgetItem(f"{title} - {artist}")
            item.setIcon(QtGui.QIcon(resource_path("UI_V2/like.png")))
            item.setData(QtCore.Qt.UserRole, {
                "title": title,
                "artist": artist,
                "album": album,
                "path": path
            })
            self.ui.play_list_widget.addItem(item)
        self.select_currently_playing_song()

    def search_play_list(self):
        search_text = self.ui.search_bar.text().strip().lower()

        for i in range(self.ui.play_list_widget.count()):
            item = self.ui.play_list_widget.item(i)
            item_text = item.text().lower()

            if search_text in item_text or not search_text:
                item.setHidden(False)
            else:
                item.setHidden(True)


    def show_track_info(self):
        current_item = self.ui.play_list_widget.currentItem()
        if not current_item:
            QtWidgets.QMessageBox.warning(self, "No Track Selected", "Please select a track first.")
            return

        file_info = current_item.data(QtCore.Qt.UserRole)
        print("file_info from UserRole:", file_info, type(file_info))

        if not isinstance(file_info, dict):
            QtWidgets.QMessageBox.warning(self, "Invalid Track Metadata", "Metadata is not in expected format.")
            return

        file_path = file_info.get('path')  # match by path, or use title depending on your DB
        print("Looking up path:", file_path)

        from database import get_song_by_filepath
        song = get_song_by_filepath('music_library', file_path)

        if not song:
            QtWidgets.QMessageBox.information(self, "Track Info", f"Metadata not found for:\n{file_path}")
            return

        title = song.get('title', 'Unknown Title')
        artist = song.get('artist', 'Unknown Artist')
        album = song.get('album', 'Unknown Album')
        path = song.get('path', '')

        dialog = TrackInfoDialog(title, artist, album, path, parent=self)
        dialog.exec_()


    def switch_page(self):
        sender = self.sender()
        if sender == self.ui.back_to_home:
            self.ui.center_stackedWidget.setCurrentIndex(0)
            self.select_currently_playing_song()
        elif sender == self.ui.video_view_2:
            self.ui.center_stackedWidget.setCurrentIndex(1)
            self.select_currently_playing_song()
        elif sender == self.ui.back_to_list:
            self.ui.center_stackedWidget.setCurrentIndex(2)
            self.select_currently_playing_song()

    def add_to_favourites(self):
        selected_item = self.ui.play_list_widget.currentItem()
        if selected_item:
            song = selected_item.data(QtCore.Qt.UserRole)
            if song:  # make sure song is valid
                title = song['title']
                artist = song['artist']
                album = song['album']
                path = song['path']

                # Add to database
                database.add_song('favourites', title, artist, album, path)

                QtWidgets.QMessageBox.information(self, "Success", f"{title} added to favourites.")
            else:
                QtWidgets.QMessageBox.warning(self, "Error", "Invalid song data.")
        else:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Select a song to add to favourites.")


    def add_current_song_to_favourites(self):
        if hasattr(self,'current_song')and self.current_song:
            self.add_to_favourites(self.current_song)
        else:
            QtWidgets.QMessageBox.warning(self, "No Song", "No song is currently playing.")
    
    def play_next_song(self, event=None):
        if self.current_index + 1 < len(self.playlist):
            self.current_index += 1
            self.play_song(self.playlist[self.current_index])

    def play_selected_song(self, selected_item=None):
        if selected_item is None:
            selected_item = self.ui.play_list_widget.currentItem()

        if selected_item:
            song_data = selected_item.data(QtCore.Qt.UserRole)
            if not song_data:
                print("❌ Error: No song data found in selected item.")
                return
            required_keys = {"title", "artist", "album", "path"}
            if not all(key in song_data for key in required_keys):
                print(f"❌ Error: Incomplete song data: {song_data}")
                return
            song_data = {
                "title": song_data["title"],
                "artist": song_data["artist"],
                "album": song_data["album"],
                "path": song_data["path"]
            }
            file_path = song_data["path"]
            if not os.path.exists(file_path):
                print(f"❌ Error: File does not exist at path: {file_path}")
                return
            print(f"▶️ Now playing: {song_data['title']} - {song_data['artist']} [{file_path}]")
            self.play_media(file_path)

            if database.song_exists('favourites', file_path):
                self.ui.make_favourite_btn.setIcon(QIcon(resource_path("UI_V2/favourite_btn.png")))
            else:
                self.ui.make_favourite_btn.setIcon(QIcon(resource_path("UI_V2/fav_btn_1.png")))
        
        else:
            print("❌ Error: No item selected in playlist.")

    def select_currently_playing_song(self):
        title = self.ui.song_label.text().strip()
        artist = self.ui.artist_name_label.text().strip()
        current_name = f"{title} - {artist}"
        print(f"Looking for: {current_name}")

        self.ui.play_list_widget.clearSelection()

        for row in range(self.ui.play_list_widget.count()):
            item = self.ui.play_list_widget.item(row)
            item_name = item.text().strip()
            print(f"Checking: {item_name}")

            if item_name == current_name:
                item.setSelected(True)
                self.ui.play_list_widget.setCurrentRow(row)
                self.ui.play_list_widget.scrollToItem(item)
                print(f"Selected and highlighted row {row}")
                return

        print("Currently playing song not found by name.")

    
    # playing function
    
    def toggle_play_pause(self):
        if self.player.is_playing():
            self.player.pause()
            self.ui.pause_btn.setIcon(QIcon(resource_path("UI_V2/play_alt.png")))
        else:
            self.player.play()
            self.ui.pause_btn.setIcon(QIcon(resource_path("UI_V2/play_btn.png")))

    def next_track(self):
        label_text = self.ui.page_label.text()
        self.set_track_info(self.player.get_media())
        if label_text in ["All Songs", "Favourites"]:  # optionally add more page names
            current_row = self.ui.play_list_widget.currentRow()
            if current_row < self.ui.play_list_widget.count() - 1:
                next_row = current_row + 1
                self.ui.play_list_widget.setCurrentRow(next_row)
                next_item = self.ui.play_list_widget.item(next_row)
                self.play_selected_song(next_item)
        
    def prev_track(self):
        label_text = self.ui.page_label.text()
        self.set_track_info(self.player.get_media())
        if label_text in ["All Songs", "Favourites"]:
            current_row = self.ui.play_list_widget.currentRow()
            if current_row > 0:
                prev_row = current_row - 1
                self.ui.play_list_widget.setCurrentRow(prev_row)
                prev_item = self.ui.play_list_widget.item(prev_row)
                self.play_selected_song(prev_item)
    
    def on_media_parsed(self, event):
        QtCore.QMetaObject.invokeMethod(self, self.set_duration, QtCore.Qt.QueuedConnection)

    def play_media(self, file_path):
        # Stop current playback if necessary
        if self.player.is_playing():
            self.player.stop()
        media = self.vlc_instance.media_new(file_path)
        self.player.set_media(media)
        
        # Parse media synchronously to ensure metadata is available
        

        self.set_track_info(self.player.get_media())
        has_video = False
        tracks = media.tracks_get()
        if tracks:
            for track in tracks:
                if track.type == vlc.TrackType.video:
                    has_video = True
                    break

        if has_video:
            self.ui.center_stackedWidget.setCurrentIndex(1)
            self.ui.video_view.show()
            self.attach_vlc_video_output()
        else:
            self.ui.video_view.hide()

        self.player.play()

        # Wait briefly before setting duration (ensures VLC loads media)
        QtCore.QTimer.singleShot(500, self.set_duration)
        self.timer.start()

        
    def toggle_loop(self):
        self.looping = not self.looping

        if self.looping:
            self.ui.loop_btn.setIcon(QIcon(resource_path("UI_V2/loop-one.png")))  # or loop-one.png if looping a single track
        else:
            self.ui.loop_btn.setIcon(QIcon(resource_path("UI_V2/loop.png")))

        self.ui.loop_btn.setChecked(self.looping)



    
    def toggle_shuffle(self):
        self.shuffle = not self.shuffle

        self.ui.shuffle_btn.setIcon(
            QIcon(resource_path("UI_V2/suffle_btn.png")) if self.shuffle else QIcon(resource_path("UI_V2/play_all_btn.png"))
        )
        self.ui.shuffle_btn.setChecked(self.shuffle)

        if self.shuffle:
            self.playback_order = random.sample(range(len(self.original_playlist_data)), len(self.original_playlist_data))
        else:
            self.playback_order = list(range(len(self.original_playlist_data)))

        self.current_play_index = 0  # reset to beginning (or keep current?)





    def on_track_end(self, event):
        QTimer.singleShot(0, self.handle_track_end)

    def handle_track_end(self):
        current_row = self.ui.play_list_widget.currentRow()
        total_rows = self.ui.play_list_widget.count()

        if current_row < 0:
            return  # No item selected

        if self.looping:
            item = self.ui.play_list_widget.item(current_row)

        elif self.shuffle:
            if not self.playback_order:
                print("Shuffle is ON but playback_order is empty. Resetting playback order.")
                self.playback_order = list(range(total_rows))  # fallback
            next_row = random.choice(self.playback_order)
            self.ui.play_list_widget.setCurrentRow(next_row)
            item = self.ui.play_list_widget.item(next_row)

        elif current_row + 1 < total_rows:
            self.ui.play_list_widget.setCurrentRow(current_row + 1)
            item = self.ui.play_list_widget.item(current_row + 1)
        else:
            return

        # Get file path from item's metadata
        metadata = item.data(QtCore.Qt.UserRole)
        if isinstance(metadata, dict) and "path" in metadata:
            file_path = metadata["path"]
            self.play_media(file_path)
        else:
            print("Invalid metadata or missing path.")


        # Get file path from item's UserRole data
        metadata = item.data(QtCore.Qt.UserRole)
        if isinstance(metadata, dict) and "path" in metadata:
            file_path = metadata["path"]
            self.play_media(file_path)
        else:
            print("Invalid metadata or missing path.")


    def get_album_art_from_audio(self, audio_file_path):
        try:
            from mutagen.id3 import ID3, APIC
            decoded_path = urllib.parse.unquote(audio_file_path)

            tags = ID3(decoded_path)
            for tag in tags.values():
                if isinstance(tag, APIC):  # Covers APIC: tag
                    return QtGui.QImage.fromData(tag.data)
        except Exception as e:
            print(f"Album art extraction error: {e}")
        return None

    def set_album_art(self, audio_file_path):
        album_art = self.get_album_art_from_audio(audio_file_path)
        if album_art and not album_art.isNull():
            self.ui.Album_art.setPixmap(QPixmap.fromImage(album_art))
        else:
            default_pixmap = QPixmap(resource_path("UI_V2/No-album-art.png"))
            self.ui.Album_art.setPixmap(default_pixmap)

    def set_track_info(self, media):
        media.parse()  # Ensure metadata is loaded
        title = media.get_meta(vlc.Meta.Title) or "Unknown Title"
        artist = media.get_meta(vlc.Meta.Artist) or "Unknown Artist"
        album = media.get_meta(vlc.Meta.Album) or "Unknown Album"
        path = media.get_mrl().replace("file://", "")

        self.ui.song_label.setText(title)
        self.ui.song_label_2.setText(title)
        self.ui.album_label_2.setText(album)
        self.ui.artist_name_label.setText(artist)
        self.ui.artist_name_label_2.setText(artist)
        self.ui.album_label.setText(album)
        self.ui.album_label_2.setText(album)
        self.set_album_art(path)

        self.setup_marquee(self.ui.song_label_2, title, self.ui.frame_5.width())

    def setup_marquee(self, label, text, max_width):
        fm = QtGui.QFontMetrics(label.font())
        text_width = fm.horizontalAdvance(text)

        # If text fits, stop marquee and set plain text
        if text_width <= max_width:
            if hasattr(self, 'marquee_timer') and self.marquee_timer.isActive():
                self.marquee_timer.stop()
            label.setText(text)
            label.setAlignment(QtCore.Qt.AlignCenter)  # Optional: align center for shorter text
            self.marquee_text = ""
            return

        label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.marquee_offset = 0
        self.marquee_text = text
        self.marquee_label = label
        self.marquee_width = text_width

        if hasattr(self, 'marquee_timer') and self.marquee_timer.isActive():
            self.marquee_timer.stop()

        self.marquee_timer = QtCore.QTimer()
        self.marquee_timer.timeout.connect(self.scroll_marquee)
        self.marquee_timer.start(100)

    def scroll_marquee(self):
        offset = self.marquee_offset
        display_text = self.marquee_text[offset:] + '   ' + self.marquee_text[:offset]
        self.marquee_label.setText(display_text)
        self.marquee_offset = (self.marquee_offset + 1) % len(self.marquee_text)


    # EQ implimentation
    def apply_equalizer(self):
        gains = [self.ui.slider_band1.value(), self.ui.slider_band2.value(), ..., self.ui.slider_band10.value()]
        eq = vlc.AudioEqualizer()

        for i, gain in enumerate(gains):
            eq.set_amp_at_index(gain, i)

        if self.player:
            self.player.set_equalizer(eq)

    def save_preset(self, name):
        gains = [self.ui.slider_band1.value(), ..., self.ui.slider_band10.value()]
        with sqlite3.connect("music_library.db") as conn:
            c = conn.cursor()
            c.execute("REPLACE INTO equalizer_presets (name, band1, band2, band3, band4, band5, band6, band7, band8, band9, band10) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (name, *gains))
            conn.commit()

    def load_preset(self, name):
        with sqlite3.connect("music_library.db") as conn:
            c = conn.cursor()
            c.execute("SELECT band1, band2, band3, band4, band5, band6, band7, band8, band9, band10 FROM equalizer_presets WHERE name=?", (name,))
            row = c.fetchone()
            if row:
                sliders = [self.ui.slider_band1, ..., self.ui.slider_band10]
                for slider, value in zip(sliders, row):
                    slider.setValue(value)
                self.apply_equalizer()

    def reset_equalizer(self):
        for slider in [self.ui.slider_band1, ..., self.ui.slider_band10]:
            slider.setValue(0)
        self.apply_equalizer()

    def attach_vlc_video_output(self):
        win_id = int(self.ui.video_view.winId())
        if sys.platform.startswith("linux"):
            self.player.set_xwindow(win_id)
        elif sys.platform == "win32":
            self.player.set_hwnd(win_id)
        elif sys.platform == "darwin":
            self.player.set_nsobject(win_id)
    
    # hooking EQ to UI
    def show_equalizer(self):
        self.eq_window = EqualizerWindow(self.player)
        self.eq_window.show()

    def update_preset_list(self):
        with sqlite3.connect("music_library.db") as conn:
            c = conn.cursor()
            c.execute("SELECT name FROM equalizer_presets")
            presets = [row[0] for row in c.fetchall()]
            self.ui.preset_combo.clear()
            self.ui.preset_combo.addItems(presets)

## Track Info Dialog
class TrackInfoDialog(QtWidgets.QDialog):
    def __init__(self, title, artist, album, path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Track Information")
        self.setMinimumWidth(400)

        layout = QtWidgets.QVBoxLayout(self)

        # Create labels with icons (you can replace emojis with QIcons if you want)
        title_label = QtWidgets.QLabel(f"🎵 Title: <b>{title}</b>")
        artist_label = QtWidgets.QLabel(f"🎤 Artist: <b>{artist}</b>")
        album_label = QtWidgets.QLabel(f"💽 Album: <b>{album}</b>")
        path_label = QtWidgets.QLabel(f"📁 File Path: <i>{path}</i>")

        # Set word wrap for path in case it's long
        path_label.setWordWrap(True)

        # Add all labels to the layout
        layout.addWidget(title_label)
        layout.addWidget(artist_label)
        layout.addWidget(album_label)
        layout.addWidget(path_label)

        # Add Close button
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(self.accept)  # closes the dialog
        layout.addWidget(close_btn)

        self.setLayout(layout)

#DIALOGUE about page
class AboutDialog(QDialog):
    def __init__(self, MusicPlayer, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About KGM Media Player")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()

        # Use resource path from passed-in provider
        logo_label = QLabel()
        logo_pixmap = QPixmap(resource_path("UI_V2/app.png")).scaled(
            70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setPixmap(logo_pixmap)

        # App info text
        info_label = QLabel(
            "<h2>KGM Media Player</h2>"
            "<p>Version: 2.0.0</p>"
            "<p>Developed by: Kisakye Gibreel</p>"
            "<p>Thank you for using this player!</p>"
            "<p>Copyright 2025</p>"
            "<p>Kampala, Uganda 🇺🇬</p>"
        )
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setWordWrap(True)

        layout.addWidget(logo_label)
        layout.addWidget(info_label)
        self.setLayout(layout)
