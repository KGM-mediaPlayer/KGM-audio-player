import sys
import os
import vlc
import sqlite3
import urllib.parse
from pathlib import Path
import random
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QMessageBox, QWidget, QMenu
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt,QTimer
from PyQt5.QtWidgets import QWidget,QMessageBox
from mutagen import File as MutagenFile
from mutagen.mp3 import HeaderNotFoundError

from src.frontend.kgm_media_player import MainWindow
from src.frontend.old.EQ import EqualizerWindow
import src.backend.database as database
from src.frontend.asset_loader import create_svg_icon, load_and_scale_image
from src.frontend.aboutDialogue import AboutDialog


class MediaPlayer(QtCore.QObject):
    def __init__(self, main_window_instance):
        super().__init__()
        self.ui = main_window_instance
        
        self.video_fullscreen = False

        # VLC setup
        self.vlc_instance = vlc.Instance('--no-xlib')  # '--no-xlib' for Linux, can be omitted on Windows/macOS
        self.player = self.vlc_instance.media_player_new()
        
        
        # Slider timer
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1000)  # update every 1 second
        self.timer.timeout.connect(self.update_slider_position)

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

        """self.original_playlist = [self.ui.listObject.item(i).text()
                          for i in range(self.ui.playlist_page.count())]"""
        
        self.ui.listObject.clear()
        for text, metadata in self.original_playlist_data:
            item = QtWidgets.QListWidgetItem(text)
            item.setData(QtCore.Qt.UserRole, metadata)
            self.ui.listObject.addItem(item)


        # --- Context Menu setup (UI Connection in Backend Object) ---
        self.ui.listObject.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.listObject.customContextMenuRequested.connect(self.show_context_menu)
        # -------------------------------------------------------------

        self.ui.playPause_track_btn.clicked.connect(self.toggle_play_pause)
        self.ui.next_track_btn.clicked.connect(self.next_track)
        self.ui.prev_track_btn.clicked.connect(self.prev_track)
        #self.ui.all_songs_btn.clicked.connect(self.load_songs)
        self.ui.favourites_btn.clicked.connect(self.favourite_songs)
        #self.ui.back_to_home.clicked.connect(self.switch_page)
        self.ui.searchInput.textChanged.connect(self.search_play_list)
        self.ui.makeFavourite_btn.clicked.connect(self.add_to_favourites)
        #self.ui.add_songs_to_library_btn.clicked.connect(self.add_songs_to_library)
        #self.ui.remove_all_songs_btn.clicked.connect(self.remove_songs_from_library)
        #self.ui.remove_current_selection_btn.clicked.connect(self.remove_current_selection)
        self.ui.about_btn.clicked.connect(self.show_about_dialog)
        self.ui.listObject.itemDoubleClicked.connect(self.play_selected_song)
        self.ui.music_btn.clicked.connect(self.load_songs)
        self.ui.playlist_btn.clicked.connect(self.playlist)
        #self.ui.video_view_2.clicked.connect(self.switch_page)
        self.ui.repeatOptions_btn.clicked.connect(self.toggle_loop)
        self.ui.shuffle_btn.clicked.connect(self.toggle_shuffle)
        self.ui.trackInfo_btn.clicked.connect(self.show_track_info)


        #seek slider
        self.ui.playBackSlider.sliderPressed.connect(self.pause_for_seek)
        self.ui.playBackSlider.sliderReleased.connect(self.resume_after_seek)

        self.event_manager.event_attach(
            vlc.EventType.MediaParsedChanged, self.on_media_parsed
        )

        # Eq button
        #self.ui.more_options_btn.clicked.connect(self.show_equalizer)

           
    connect = sqlite3.connect('music_library.db')
    connect.row_factory = sqlite3.Row  # Enable dict-style access
    cursor = connect.cursor()

    def show_context_menu(self, position):
        """
        Builds and displays the context menu on right-click. 
        It supports both item-specific actions (like remove) and global actions (like add or delete all).
        """
        
        selected_item = self.ui.listObject.itemAt(position)
        
        context_menu = QMenu(self.ui)
        
        current_page = self.ui.page_label.text()
        
        action_add_library = context_menu.addAction("Add Item(s) to Library...")
        action_add_library.setIcon(QIcon(load_and_scale_image(__file__, "add_icon.png", size=30))) 
        action_add_library.triggered.connect(self.add_songs_to_library) 

        context_menu.addSeparator() 
        
        action_add_fav = context_menu.addAction("Add to Favourites")
        action_add_fav.setIcon(QIcon(load_and_scale_image(__file__, "fav_btn_1.png", size=30))) 
        action_add_fav.triggered.connect(self.add_current_selection_to_favourites)
        action_add_fav.setEnabled(selected_item is not None) 

        remove_text = "Remove Selected Item"
        if current_page == "Music Library":
            remove_text = "Remove Selected from Library"
        elif current_page == "Favourites":
            remove_text = "Remove Selected from Favourites"
        elif current_page == "Playlist(s)":
            remove_text = "Remove Selected from Playlist"
            
        action_remove = context_menu.addAction(remove_text)
        action_remove.setIcon(QIcon(load_and_scale_image(__file__, "delete.png", size=30)))
        action_remove.triggered.connect(self.remove_current_selection)
        action_remove.setEnabled(selected_item is not None) 

        context_menu.addSeparator() 
        
        action_delete_all = context_menu.addAction(f"Delete ALL from {current_page}")
        action_delete_all.setIcon(QIcon(load_and_scale_image(__file__, "clear_all.png", size=30))) 
        action_delete_all.triggered.connect(self.remove_current_selection)
        
        context_menu.exec_(self.ui.listObject.mapToGlobal(position))

    # --- Context Menu Action Handlers (Backend Logic) ---
    # ... Existing handlers (add_current_selection_to_favourites, remove_current_selection) go here ...

    # --- Placeholder methods for new actions ---
    # def add_items_to_library(self):
    #     pass

    # def delete_all_items_in_current_view(self):
    #     pass


    def add_current_selection_to_favourites(self):
        """Logic to add the currently selected song from the listObject to the 'favourites' database table."""
        selected_item = self.ui.listObject.currentItem()
        if selected_item:
            song = selected_item.data(QtCore.Qt.UserRole)
            if song and all(key in song for key in ['title', 'artist', 'album', 'path']):
                title = song['title']
                artist = song['artist']
                album = song['album']
                path = song['path']

                database.add_song('favourites', title, artist, album, path)

                QtWidgets.QMessageBox.information(self.ui, "Success", f"'{title}' added to favourites.")
            else:
                QtWidgets.QMessageBox.warning(self.ui, "Error", "Invalid song data.")
        else:
            QtWidgets.QMessageBox.warning(self.ui, "No Selection", "Please select a song first.")
    # ---------------------------------------------------
    
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
            # Assuming 'self.original_video_parent' and proper container management
            # self.ui.video_view.setParent(self.original_video_parent) 
            self.ui.video_view.setWindowFlags(Qt.Widget)
            # self.original_video_parent.layout().addWidget(self.ui.video_view) 
            self.ui.video_view.showNormal()
            self.ui.right_container.setCurrentWidget(self.ui.video_view)
            self.video_fullscreen = False
        else:
            # Enter fullscreen
            self.ui.video_view.setParent(None)
            self.ui.video_view.setWindowFlags(Qt.Window)
            self.ui.video_view.showFullScreen()

            self.video_fullscreen = True

        event.accept()

    
    def on_video_resized(self, event):
        # self.overlay_ui.resize(self.ui.video_view.size()) # Assuming overlay_ui exists
        event.accept()

        # Attach the handler
        self.ui.video_view.resizeEvent = self.on_video_resized
    

    
    def add_songs_to_library(self):
        # Create a file dialog to choose files
        file_dialog = QtWidgets.QFileDialog(self.ui) # Use self.ui as parent
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
            
            # Refresh the list if currently on the Music Library page
            if self.ui.page_label.text() == "Music Library":
                self.load_songs()


    # Full screen
   

    def pause_for_seek(self):
        self.was_playing = self.player.is_playing()
        self.player.pause()

    def resume_after_seek(self):
        # Assuming ui.playBackSlider is the correct slider
        value = self.ui.playBackSlider.value() 
        self.player.set_time(value)
        if self.was_playing:
            self.player.play()

    def removal_db_selection(self):
        page_text = self.ui.page_label.text()
        if page_text == "Music Library":
            db_table = 'music_library'
        elif page_text == 'Favourites':
            db_table = 'favourites'
        elif page_text == 'Playlist(s)':
            db_table = 'playlist'
        else:
            db_table = None  # Default to None or another value if necessary
        return db_table

    def remove_songs_from_library(self):
        db_table = self.removal_db_selection()
        if db_table:
            database.remove_all_songs(db_table)
            self.ui.listObject.clear() # Clear the visible list
            QtWidgets.QMessageBox.information(self.ui, "Removed", f"All songs removed from {db_table}!")
        else:
            QtWidgets.QMessageBox.warning(self.ui, "Error", "Unknown page, no songs removed.")

    def remove_current_selection(self):
        db_table = self.removal_db_selection()
        if db_table:
            # Note: currentItem() is used, which works for both context menu and dedicated button click
            selected_item = self.ui.listObject.currentItem() 
            if selected_item:
                song_data = selected_item.data(QtCore.Qt.UserRole)
                path = song_data["path"]  # Use path as the unique identifier
                title = song_data["title"]

                database.remove_song(db_table, path)  # Pass path instead of title

                # Remove item from the QListWidget
                self.ui.listObject.takeItem(self.ui.listObject.row(selected_item))
                QtWidgets.QMessageBox.information(self.ui, "Removed", f"'{title}' removed from {db_table}!")
            else:
                QtWidgets.QMessageBox.warning(self.ui, "No Selection", "Please select a song to remove.")
        else:
            QtWidgets.QMessageBox.warning(self.ui, "Error", "Unknown page, no songs removed.")
   
    def set_slider_position(self, position):
        self.player.set_time(position)  # Seek to the specified time in ms
        self.ui.playBackSlider.setValue(position)
        current_time = position / 1000  # ms to seconds
        self.ui.leftPlaybackTimer.setText(self.format_time(current_time))

    def update_slider_position(self):
        current_time = self.player.get_time()  # in milliseconds
        self.ui.playBackSlider.blockSignals(True)  # prevent triggering signals while updating
        self.ui.playBackSlider.setValue(current_time)
        self.ui.playBackSlider.blockSignals(False)
        self.ui.leftPlaybackTimer.setText(self.format_time(current_time / 1000))

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
        self.ui.playBackSlider.setRange(0, int(duration * 1000))  # use ms
        self.ui.playBackSlider.setValue(0)
        self.ui.playBackSlider.setPageStep(1000)
        self.ui.playBackSlider.setSingleStep(1000)
        self.ui.playBackSlider.setTracking(True)

        # Set total duration label only once
        self.ui.rightPlaybackTimer.setText(self.format_time(duration))


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
        self.ui.right_container.setCurrentIndex(0)
        self.ui.page_label.setText("Music Library")
        songs = database.get_all_songs('music_library')
        self.ui.listObject.clear()
        for song in songs:
            title, artist, album, path = song  # unpack tuple
            item = QtWidgets.QListWidgetItem(f"{title} - {artist}")
            item.setIcon(QtGui.QIcon(load_and_scale_image(__file__, "MusicListItem.png", size=30)))
            item.setData(QtCore.Qt.UserRole, {
                "title": title,
                "artist": artist,
                "album": album,
                "path": path
            })
            self.ui.listObject.addItem(item)
        self.select_currently_playing_song()
        
    def playlist(self):
        self.ui.right_container.setCurrentIndex(0)
        self.ui.page_label.setText("Playlist(s)")
        songs = database.get_all_songs('playlist')
        self.ui.listObject.clear()
        for song in songs:
            title, artist, album, path = song
            item = QtWidgets.QListWidgetItem(f"{title} - {artist}")
            item.setData(QtCore.Qt.UserRole, {
                "title": title,
                "artist": artist,
                "album": album,
                "path": path
            })
            self.ui.listObject.addItem(item)
        self.select_currently_playing_song()

    
    def favourite_songs(self):
        self.ui.right_container.setCurrentIndex(2)
        self.ui.page_label.setText("Favourites")
        songs = database.get_all_songs('favourites')
        self.ui.listObject.clear()
        for song in songs:
            title, artist, album, path = song  # unpack tuple
            item = QtWidgets.QListWidgetItem(f"{title} - {artist}")
            item.setIcon(QtGui.QIcon(load_and_scale_image(__file__, "like.png", size=30)))
            item.setData(QtCore.Qt.UserRole, {
                "title": title,
                "artist": artist,
                "album": album,
                "path": path
            })
            self.ui.listObject.addItem(item)
        self.select_currently_playing_song()

    def search_play_list(self):
        search_text = self.ui.searchInput.text().strip().lower()

        for i in range(self.ui.listObject.count()):
            item = self.ui.listObject.item(i)
            item_text = item.text().lower()

            if search_text in item_text or not search_text:
                item.setHidden(False)
            else:
                item.setHidden(True)


    def show_track_info(self):
        current_item = self.ui.listObject.currentItem()
        if not current_item:
            QtWidgets.QMessageBox.warning(self.ui, "No Track Selected", "Please select a track first.")
            return

        file_info = current_item.data(QtCore.Qt.UserRole)
        print("file_info from UserRole:", file_info, type(file_info))

        if not isinstance(file_info, dict):
            QtWidgets.QMessageBox.warning(self.ui, "Invalid Track Metadata", "Metadata is not in expected format.")
            return

        file_path = file_info.get('path')  # match by path, or use title depending on your DB
        print("Looking up path:", file_path)

        from src.backend.database import get_song_by_filepath
        song = get_song_by_filepath('music_library', file_path)

        if not song:
            QtWidgets.QMessageBox.information(self.ui, "Track Info", f"Metadata not found for:\n{file_path}")
            return

        title = song.get('title', 'Unknown Title')
        artist = song.get('artist', 'Unknown Artist')
        album = song.get('album', 'Unknown Album')
        path = song.get('path', '')

        # Since TrackInfoDialog is not defined here, using QMessageBox as a fallback
        QtWidgets.QMessageBox.information(self.ui, "Track Info", 
                                          f"Title: {title}\nArtist: {artist}\nAlbum: {album}\nPath: {path}")


    def switch_page(self):
        sender = self.sender()
        if sender == self.ui.back_to_home:
            self.ui.right_container.setCurrentIndex(0)
            self.select_currently_playing_song()
        elif sender == self.ui.video_view_2:
            self.ui.right_container.setCurrentIndex(1)
            self.select_currently_playing_song()
        elif sender == self.ui.back_to_list:
            self.ui.right_container.setCurrentIndex(2)
            self.select_currently_playing_song()

    def add_to_favourites(self):
        # This is likely connected to a button, which is why it uses currentItem()
        selected_item = self.ui.listObject.currentItem()
        if selected_item:
            song = selected_item.data(QtCore.Qt.UserRole)
            if song:  # make sure song is valid
                title = song['title']
                artist = song['artist']
                album = song['album']
                path = song['path']

                # Add to database
                database.add_song('favourites', title, artist, album, path)

                QtWidgets.QMessageBox.information(self.ui, "Success", f"{title} added to favourites.")
            else:
                QtWidgets.QMessageBox.warning(self.ui, "Error", "Invalid song data.")
        else:
            QtWidgets.QMessageBox.warning(self.ui, "No Selection", "Select a song to add to favourites.")


    def add_current_song_to_favourites(self):
        if hasattr(self,'current_song')and self.current_song:
            self.add_to_favourites(self.current_song)
        else:
            QtWidgets.QMessageBox.warning(self.ui, "No Song", "No song is currently playing.")
    
    def play_next_song(self, event=None):
        if self.current_index + 1 < len(self.playlist):
            self.current_index += 1
            self.play_song(self.playlist[self.current_index])

    def play_selected_song(self, selected_item=None):
        if selected_item is None:
            selected_item = self.ui.listObject.currentItem()

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
                self.ui.makeFavourite_btn.setIcon(QIcon(load_and_scale_image(__file__, "favourite_btn.png", size=30)))
            else:
                self.ui.makeFavourite_btn.setIcon(QIcon(load_and_scale_image(__file__, "fav_btn_1.png", size=30)))
        
        else:
            print("❌ Error: No item selected in playlist.")

    def select_currently_playing_song(self):
        title = self.ui.songLabel.text().strip()
        artist = self.ui.artistName.text().strip()
        current_name = f"{title} - {artist}"
        print(f"Looking for: {current_name}")

        #self.ui.playlist_page.clearSelection()

        for row in range(self.ui.listObject.count()):
            item = self.ui.listObject.item(row)
            item_name = item.text().strip()
            print(f"Checking: {item_name}")

            if item_name == current_name:
                item.setSelected(True)
                self.ui.listObject.setCurrentRow(row)
                self.ui.listObject.scrollToItem(item)
                print(f"Selected and highlighted row {row}")
                return

        print("Currently playing song not found by name.")

    
    # playing function
    
    def toggle_play_pause(self):
        if self.player.is_playing():
            self.player.pause()
            # Assuming an icon update is needed here
            self.ui.playPause_track_btn.setIcon(QIcon(load_and_scale_image(__file__,'play_btn.png',size=40))) 
        else:
            self.player.play()
            self.ui.playPause_track_btn.setIcon(QIcon(create_svg_icon(__file__, "playPause_btn.svg", size=50)))

    def next_track(self):
        label_text = self.ui.page_label.text()
        self.set_track_info(self.player.get_media())
        if label_text in ["Music Library", "Favourites", "Playlist(s)"]:  # optionally add more page names
            current_row = self.ui.listObject.currentRow()
            if current_row < self.ui.listObject.count() - 1:
                next_row = current_row + 1
                self.ui.listObject.setCurrentRow(next_row)
                next_item = self.ui.listObject.item(next_row)
                self.play_selected_song(next_item)
        
    def prev_track(self):
        label_text = self.ui.page_label.text()
        self.set_track_info(self.player.get_media())
        if label_text in ["Music Library", "Favourites", "Playlist(s)"]:
            current_row = self.ui.listObject.currentRow()
            if current_row > 0:
                prev_row = current_row - 1
                self.ui.listObject.setCurrentRow(prev_row)
                prev_item = self.ui.listObject.item(prev_row)
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
            self.ui.right_container.setCurrentIndex(1)
            self.ui.video_view.show()
            self.attach_vlc_video_output()
        '''else:
            self.ui.video_view.hide()'''

        self.player.play()

        # Wait briefly before setting duration (ensures VLC loads media)
        QtCore.QTimer.singleShot(500, self.set_duration)
        self.timer.start()

        
    def toggle_loop(self):
        self.looping = not self.looping

        if self.looping:
            # Assuming loop-one.png is for enabled loop
            self.ui.repeatOptions_btn.setIcon(QIcon(load_and_scale_image(__file__,'loop-one.png',size=10)))  
        else:
            # Assuming loop.png is for disabled loop
            self.ui.repeatOptions_btn.setIcon(QIcon(load_and_scale_image(__file__,'loop.png',size=10)))

        self.ui.repeatOptions_btn.setChecked(self.looping)


    
    def toggle_shuffle(self):
        self.shuffle = not self.shuffle

        self.ui.shuffle_btn.setIcon(
            QIcon(load_and_scale_image(__file__,'shuffle_btn.png',size=10)) if self.shuffle else QIcon(load_and_scale_image(__file__,'play_all_btn.png',size=10))
        )
        self.ui.shuffle_btn.setChecked(self.shuffle)

        if self.shuffle:
            # Recreate playback order if shuffle is turned ON
            self.playback_order = random.sample(range(len(self.original_playlist_data)), len(self.original_playlist_data))
        else:
            # Reset to sequential order if shuffle is turned OFF
            self.playback_order = list(range(len(self.original_playlist_data)))

        self.current_play_index = 0  # reset to beginning (or keep current?)


    def on_track_end(self, event):
        QTimer.singleShot(0, self.handle_track_end)

    def handle_track_end(self):
        current_row = self.ui.listObject.currentRow()
        total_rows = self.ui.listObject.count()

        if current_row < 0:
            return  # No item selected

        item = None
        if self.looping:
            item = self.ui.listObject.item(current_row)

        elif self.shuffle:
            if not self.playback_order:
                print("Shuffle is ON but playback_order is empty. Resetting playback order.")
                self.playback_order = list(range(total_rows))  # fallback
            next_row = random.choice(self.playback_order)
            self.ui.listObject.setCurrentRow(next_row)
            item = self.ui.listObject.item(next_row)

        elif current_row + 1 < total_rows:
            self.ui.listObject.setCurrentRow(current_row + 1)
            item = self.ui.listObject.item(current_row + 1)
        else:
            return

        # Get file path from item's metadata
        if item:
            metadata = item.data(QtCore.Qt.UserRole)
            if isinstance(metadata, dict) and "path" in metadata:
                file_path = metadata["path"]
                self.play_media(file_path)
            else:
                print("Invalid metadata or missing path for next track.")


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
            self.ui.albumArt_view.setPixmap(QPixmap.fromImage(album_art).scaled(
                self.ui.albumArt_view.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            default_pixmap = QPixmap(load_and_scale_image(__file__, "No-album-art.png", size=60))
            self.ui.albumArt_view.setPixmap(default_pixmap.scaled(
                self.ui.albumArt_view.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))


    def set_track_info(self, media):
        media.parse()  # Ensure metadata is loaded
        title = media.get_meta(vlc.Meta.Title) or "Unknown Title"
        artist = media.get_meta(vlc.Meta.Artist) or "Unknown Artist"
        album = media.get_meta(vlc.Meta.Album) or "Unknown Album"
        # media resource locator needs proper decoding and path stripping
        mrl = media.get_mrl()
        path = urllib.parse.unquote(mrl.removeprefix("file:///")) if mrl.startswith("file:///") else mrl

        self.ui.songLabel.setText(title)
        self.ui.artistName.setText(artist)
        self.ui.albumName.setText(album)
        self.set_album_art(path)

        self.setup_marquee(self.ui.songLabel, title, self.ui.mediaTitle_frame.width()) # If marquee is needed
        self.setup_marquee(self.ui.artistName, title, self.ui.mediaTitle_frame.width()) # If marquee is needed
        self.setup_marquee(self.ui.albumName, title, self.ui.mediaTitle_frame.width()) # If marquee is needed


    def setup_marquee(self, label, text, max_width):
        fm = QtGui.QFontMetrics(label.font())
        text_width = fm.horizontalAdvance(text)

        if text_width <= max_width:
            if hasattr(self, 'marquee_timer') and self.marquee_timer.isActive():
                self.marquee_timer.stop()
            label.setText(text)
            label.setAlignment(QtCore.Qt.AlignCenter)  
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
        # Placeholder for EQ sliders
        gains = [0] * 10
        try:
            eq = vlc.AudioEqualizer()
        except AttributeError:
            print("VLC AudioEqualizer not initialized or available.")
            return

        for i, gain in enumerate(gains):
            eq.set_amp_at_index(gain, i)

        if self.player:
            self.player.set_equalizer(eq)

    def save_preset(self, name):
        # Placeholder for EQ sliders
        gains = [0] * 10
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
                # Need actual slider names/references here
                # sliders = [self.ui.slider_band1, ..., self.ui.slider_band10]
                # for slider, value in zip(sliders, row):
                #     slider.setValue(value)
                self.apply_equalizer()

    def reset_equalizer(self):
        # Need actual slider names/references here
        # for slider in [self.ui.slider_band1, ..., self.ui.slider_band10]:
        #     slider.setValue(0)
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
        # Assuming EqualizerWindow exists and takes self.player
        self.eq_window = EqualizerWindow(self.player)
        self.eq_window.show()

    def update_preset_list(self):
        with sqlite3.connect("music_library.db") as conn:
            c = conn.cursor()
            c.execute("SELECT name FROM equalizer_presets")
            presets = [row[0] for row in c.fetchall()]
            # Logic to update a QComboBox or similar UI element with presets goes here
            # e.g., self.ui.preset_combo.clear(); self.ui.preset_combo.addItems(presets)
            return presets # Returning the list for potential use
            
