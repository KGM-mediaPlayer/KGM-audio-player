import sys
import vlc
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon
from music import Ui_MainWindow
import database
import sqlite3
import os
from mutagen import File
import urllib.parse
from EQ import EqualizerWindow

class MusicPlayer(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # Set up the GUI from music.py

        # VLC setup
        self.vlc_instance = vlc.Instance('--no-xlib')  # '--no-xlib' for Linux, can be omitted on Windows/macOS
        self.player = self.vlc_instance.media_player_new()
        self.eq_window = EqualizerWindow(self.player)
        self.eq_window.show()
        
        #remove title bar
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        # Slider timer
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1000)  # update every 1 second
        self.timer.timeout.connect(self.update_slider_position)
        
        # Window move
        self.ui.menu_bar.mouseMoveEvent = self.move_window
        self.ui.menu_bar.mousePressEvent = self.start_move
        self.ui.menu_bar.mouseReleaseEvent = self.stop_move
        self.start_pos = None
        self.is_moving = False

        # database
        database.create_tables()
        db_table=self.removal_db_selection()

        # Load songs from the database
        database.get_all_songs('music_library')
        
        #drag and drop
        self.ui.play_list_widget.setAcceptDrops(True)
        self.ui.play_list_widget.setDragDropMode(QtWidgets.QAbstractItemView.DropOnly)


        self.ui.pause_btn.clicked.connect(self.toggle_play_pause)
        self.ui.next_btn.clicked.connect(self.next_track)
        self.ui.prev_btn.clicked.connect(self.prev_track)
        self.ui.all_songs_btn.clicked.connect(self.load_songs)
        self.ui.favourite_btn.clicked.connect(self.favourite_songs)
        self.ui.back_to_home.clicked.connect(self.switch_page)
        self.ui.back_to_list.clicked.connect(self.switch_page)
        self.ui.make_favourite_btn.clicked.connect(self.add_to_favourites)
        self.ui.add_songs_to_library_btn.clicked.connect(self.add_songs_to_library)
        self.ui.remove_all_songs_btn.clicked.connect(self.remove_songs_from_library)
        self.ui.remove_current_selection_btn.clicked.connect(self.remove_current_selection)
        self.ui.app_logo_2.clicked.connect(self.show_about_dialog)
        self.ui.duration_slider.sliderMoved.connect(self.set_slider_position)
        self.ui.play_list_widget.itemDoubleClicked.connect(self.play_selected_song)
        self.ui.play_list_btn.clicked.connect(self.playlist)
        self.ui.video_view_2.clicked.connect(self.switch_page)
        # Eq button
        self.ui.more_options_btn.clicked.connect(self.show_equalizer)
        
    connect = sqlite3.connect('music_library.db')
    connect.row_factory = sqlite3.Row  # Enable dict-style access
    cursor = connect.cursor()

    def show_about_dialog(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec_()
    
    #windows move functions
    def start_move(self, event):
        self.start_pos = event.globalPos()
        self.is_moving = True
        event.accept()
    def stop_move(self, event):
        self.is_moving = False
        event.accept()
    def move_window(self, event):
        if self.is_moving:
            self.move(self.pos() + event.globalPos() - self.start_pos)
            self.start_pos = event.globalPos()
        event.accept()
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
        metadata = File(file_path, easy=True)

        if metadata is None:
            # File not supported or unreadable
            title = os.path.basename(file_path)
            artist = "Unknown Artist"
            album = "Unknown Album"
        else:
            title = metadata.get("title", [os.path.basename(file_path)])[0]
            artist = metadata.get("artist", ["Unknown Artist"])[0]
            album = metadata.get("album", ["Unknown Album"])[0]

        return title, artist, album
    
    def load_songs(self):
        self.ui.center_stackedWidget.setCurrentIndex(2)
        self.ui.page_label.setText("All Songs")
        songs = database.get_all_songs('music_library')
        self.ui.play_list_widget.clear()
        for song in songs:
            title, artist, album, path = song  # unpack tuple
            item = QtWidgets.QListWidgetItem(f"{title} - {artist}")
            item.setIcon(QtGui.QIcon("UI_V2/MusicListItem.png"))
            item.setData(QtCore.Qt.UserRole, {
                "title": title,
                "artist": artist,
                "album": album,
                "path": path
            })
            self.ui.play_list_widget.addItem(item)
        
        if self.player.is_playing():
            current_media_path = self.player.get_media().get_mrl().replace("file://", "")  # Strip URI prefix
            for i in range(self.ui.play_list_widget.count()):
                item = self.ui.play_list_widget.item(i)
                song_data = item.data(QtCore.Qt.UserRole)
                if song_data["path"] == current_media_path:
                    self.ui.play_list_widget.setCurrentRow(i)
                    break

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

    
    def favourite_songs(self):
        self.ui.center_stackedWidget.setCurrentIndex(2)
        self.ui.page_label.setText("Favourites")
        songs = database.get_all_songs('favourites')
        self.ui.play_list_widget.clear()
        for song in songs:
            title, artist, album, path = song  # unpack tuple
            item = QtWidgets.QListWidgetItem(f"{title} - {artist}")
            item.setIcon(QtGui.QIcon("UI_V2/like.png"))
            item.setData(QtCore.Qt.UserRole, {
                "title": title,
                "artist": artist,
                "album": album,
                "path": path
            })
            self.ui.play_list_widget.addItem(item)
        
        if self.player.is_playing():
            current_media_path = self.player.get_media().get_mrl().replace("file://", "")  # Strip URI prefix
            for i in range(self.ui.play_list_widget.count()):
                item = self.ui.play_list_widget.item(i)
                song_data = item.data(QtCore.Qt.UserRole)
                if song_data["path"] == current_media_path:
                    self.ui.play_list_widget.setCurrentRow(i)
                    break
        
    
    def switch_page(self):
        sender = self.sender()
        if sender == self.ui.back_to_home:
            self.ui.center_stackedWidget.setCurrentIndex(0)
        elif sender == self.ui.video_view_2:
            self.ui.center_stackedWidget.setCurrentIndex(1)
        elif sender == self.ui.back_to_list:
            self.ui.center_stackedWidget.setCurrentIndex(2)

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
    
    def play_selected_song(self, selected_item=None):
        if selected_item is None:
            selected_item = self.ui.play_list_widget.currentItem()
        
        if selected_item:
            song_data = selected_item.data(QtCore.Qt.UserRole)
            song_data = {
                "title": song_data["title"],
                "artist": song_data["artist"],
                "album": song_data["album"],
                "path": song_data["path"]
            }
            self.play_media(song_data["path"])

            
    # playing function
    
    def toggle_play_pause(self):
        if self.player.is_playing():
            self.player.pause()
            self.ui.pause_btn.setIcon(QIcon(":/resc/UI_V2/play_alt.png"))
        else:
            self.player.play()
            self.ui.pause_btn.setIcon(QIcon(":/resc/UI_V2/play_btn.png"))

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

    def play_media(self, file_path):
        media = self.vlc_instance.media_new(file_path)
        self.player.set_media(media)
        # Parse media synchronously to ensure metadata is available
        media.parse()

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

        media.parse()  # Optional: may help retrieve metadata
        self.player.play()

        # Wait briefly before setting duration (ensures VLC loads media)
        QtCore.QTimer.singleShot(500, self.set_duration)
        self.timer.start()
    
    def get_album_art_from_audio(self, audio_file_path):
        """
        Extracts album art from MP3/ID3 tags using mutagen.
        Returns a QImage or None if not found.
        """
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
        """
        Gets album art from the audio file and displays it in albumArtLabel.
        Clears the label if no art is found.
        """
        album_art = self.get_album_art_from_audio(audio_file_path)
        if album_art and not album_art.isNull():
            self.ui.Album_art.setPixmap(QPixmap.fromImage(album_art))
        else:
            default_pixmap = QPixmap("UI_V2/No-album-art.png")
            self.ui.Album_art.setPixmap(default_pixmap)

    def set_track_info(self, media):
        """
        Sets the track information in the UI.
        """
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


#DIALOGUE about page
class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About KGM Audio Player")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()

        # App logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("UI_V2/app.png").scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)

        # App info text
        info_label = QLabel(
            "<h2>KGM Audio Player</h2>"
            "<p>Version: 2.0.0</p>"
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