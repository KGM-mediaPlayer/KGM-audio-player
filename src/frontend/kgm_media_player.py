import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
import PyQt5.QtCore as qtc 
from .theme_manager import ThemeManager
from .asset_loader import create_svg_icon, load_and_scale_image
from ..backend import database
import os
import sys

class MarqueeLabel(qtw.QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._scroll_offset = 0
        self._full_text = text
        self._timer = qtc.QTimer(self)
        self._timer.timeout.connect(self._update_scroll)
        self.setAlignment(qtc.Qt.AlignLeft | qtc.Qt.AlignVCenter)

    def setText(self, text):
        self._full_text = text
        self._scroll_offset = 0
        self._timer.stop()
        super().setText(text)
        qtc.QTimer.singleShot(100, self.check_should_scroll)

    def check_should_scroll(self):
        fm = self.fontMetrics()
        if fm.horizontalAdvance(self._full_text) > self.width() and self.width() > 10:
            self.setAlignment(qtc.Qt.AlignLeft | qtc.Qt.AlignVCenter)
            self._timer.start(150)
        else:
            self._timer.stop()
            self.setAlignment(qtc.Qt.AlignCenter)
            super().setText(self._full_text)

    def _update_scroll(self):
        self._scroll_offset += 1
        if self._scroll_offset > len(self._full_text) + 3:
            self._scroll_offset = 0
        
        display_text = self._full_text[self._scroll_offset:] + "   " + self._full_text[:self._scroll_offset]
        super().setText(display_text)


class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        
        database.create_tables()

        self.themes = ["default_dark.json", "ocean_blue.json", "light_theme.json"]
        self.current_theme = database.get_setting("theme", "default_dark.json")

        self.setWindowTitle("KGM Media Player")
        self.resize(1000, 750)

        self.theme_manager = ThemeManager()
        self.theme_manager.load_and_apply_theme(self.current_theme)

        self.central_container = qtw.QWidget()
        self.setCentralWidget(self.central_container)
        self.main_layout = qtw.QHBoxLayout(self.central_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.sidebar_container = qtw.QWidget()
        self.sidebar_container_layout = qtw.QVBoxLayout(self.sidebar_container)
        self.sidebar_container_layout.setContentsMargins(10, 10, 10, 10)
        self.sidebar_container_layout.setSpacing(5)
        self.sidebar_container.setObjectName("Sidebar") 

        self.appLogo = qtw.QLabel("")
        LogoIcon = load_and_scale_image("app.png", size=32)
        self.appLogo.setPixmap(LogoIcon)

        self.playlist_btn = qtw.QPushButton("")
        playListIcon = create_svg_icon("playlist_btn.svg", size=35)
        self.playlist_btn.setIcon(playListIcon)
        self.playlist_btn.setToolTip("Video playlist")

        self.music_btn = qtw.QPushButton("")
        music_btnIcon = create_svg_icon("music_btn.svg", size=35)
        self.music_btn.setIcon(music_btnIcon)
        self.music_btn.setToolTip("music library")

        self.effects_btn = qtw.QPushButton("")
        effects_btnIcon = create_svg_icon("effects_btn.svg", size=40)
        self.effects_btn.setIcon(effects_btnIcon)
        self.effects_btn.setToolTip("Special Effects")

        self.favourites_btn = qtw.QPushButton("")
        favIcon = create_svg_icon("favourite_btn.png", size=40)
        self.favourites_btn.setIcon(favIcon)
        self.favourites_btn.setToolTip("Favourites")

        self.settings_btn = qtw.QPushButton("")
        settings_btnIcon = create_svg_icon("settings_btn.svg", size=35)
        self.settings_btn.setIcon(settings_btnIcon)
        self.settings_btn.setToolTip("Settings")

        self.theme_btn = qtw.QPushButton("")
        themeIcon = create_svg_icon("theme_btn.svg", size=35)
        self.theme_btn.setIcon(themeIcon)
        self.theme_btn.setToolTip("Interface Themes")
        self.theme_btn.clicked.connect(self.switch_theme)

        self.about_btn = qtw.QPushButton("")
        self.about_btn.setObjectName("about_btn")
        about_btntIcon = create_svg_icon("about_btn.svg")
        self.about_btn.setIcon(about_btntIcon)
        self.about_btn.setToolTip("About KGM MediaPlayer")

        self.sidebar_container_layout.addWidget(self.appLogo, alignment=qtc.Qt.AlignCenter)
        self.sidebar_container_layout.addWidget(self.music_btn)
        self.sidebar_container_layout.addWidget(self.favourites_btn)
        self.sidebar_container_layout.addStretch()
        self.sidebar_container_layout.addWidget(self.theme_btn)
        self.sidebar_container_layout.addWidget(self.about_btn)
        self.main_layout.addWidget(self.sidebar_container)

        self.right_container = qtw.QStackedWidget()
        self.right_container.setObjectName("rightWidget")
        self.playlist_page = qtw.QWidget()
        self.playlist_page_layout = qtw.QVBoxLayout(self.playlist_page)
        self.playlist_page_layout.setContentsMargins(0, 0, 0, 0) 
        self.main_layout.addWidget(self.right_container)
        
        self.top_label_frame = qtw.QFrame()
        self.top_label_frame_layout = qtw.QHBoxLayout(self.top_label_frame)
        self.top_label_frame.setObjectName("topLabel")

        self.pageIcon = qtw.QLabel("PlayIcon")
        pageIcon_btn = load_and_scale_image("playPause_btn.svg", size=30)
        self.pageIcon.setPixmap(pageIcon_btn)
        
        self.page_label = qtw.QLabel("Playlist")
        self.page_label.setContentsMargins(0, 0, 0, 0)
        self.page_label.setObjectName("pageLabel")

        self.searchIcon = qtw.QLabel("SearchIcon")
        self.searchIcon.setObjectName("searchIcon")
        self.searchIcon.setContentsMargins(0, 0, 0, 0)
        searchIcon_btn = load_and_scale_image("searchIcon_btn.svg", size=24)
        self.searchIcon.setPixmap(searchIcon_btn)

        self.searchInput = qtw.QLineEdit("")
        self.searchInput.setContentsMargins(0, 0, 0, 0)
        self.searchInput.setObjectName("searchInput")

        self.top_label_frame_layout.addWidget(self.pageIcon)
        self.top_label_frame_layout.addWidget(self.page_label)
        self.top_label_frame_layout.addStretch()
        self.top_label_frame_layout.addWidget(self.searchIcon)
        self.top_label_frame_layout.addWidget(self.searchInput)

        self.centerframe = qtw.QFrame()
        self.centerframe_layout = qtw.QHBoxLayout(self.centerframe)
        self.centerframe.setObjectName("centerFrame")
        self.centerframe.setContentsMargins(0, 0, 0, 0)

        self.listObject = qtw.QListWidget()
        self.listObject.setObjectName("lisObject")
        self.listObject.setViewportMargins(0, 0, 0, 0)
        self.centerframe_layout.addWidget(self.listObject)

        self.playBackTimer_frame = qtw.QFrame()
        self.playBackTimer_frame_layout = qtw.QHBoxLayout(self.playBackTimer_frame)
        self.playBackTimer_frame.setObjectName("playBackTimer_frame")
        self.playBackTimer_frame.setContentsMargins(0, 0, 0, 0)

        self.leftPlaybackTimer = qtw.QLabel("00:00")
        self.leftPlaybackTimer.setObjectName("playBackTimer")
        self.rightPlaybackTimer = qtw.QLabel("00:00")
        self.rightPlaybackTimer.setObjectName("playBackTimer")
        
        self.playBackSlider = qtw.QSlider(qtc.Qt.Horizontal)
        self.playBackSlider.setObjectName("playBackSlider")
        self.playBackSlider.setContentsMargins(0, 0, 0, 0)

        self.playBackTimer_frame_layout.addWidget(self.leftPlaybackTimer)
        self.playBackTimer_frame_layout.addStretch()
        self.playBackTimer_frame_layout.addWidget(self.rightPlaybackTimer)
        
        self.playBackFooter_frame = qtw.QFrame()
        self.playBackFooter_frame_layout = qtw.QHBoxLayout(self.playBackFooter_frame)
        self.playBackFooter_frame_layout.setObjectName("playBackFooterFrame")
        self.playBackFooter_frame.setMaximumHeight(100)

        self.albumArt_frame = qtw.QFrame()
        self.albumArt_frame_layout = qtw.QHBoxLayout(self.albumArt_frame)
        self.albumArt_frame_layout.setContentsMargins(10, 5, 10, 5)
        self.albumArt_frame_layout.setSpacing(12)
        self.albumArt_frame.setObjectName("albumArtFrame")
        self.albumArt_frame.setMaximumWidth(200)

        self.albumArt_view = qtw.QLabel()
        self.albumArt_view.setObjectName("albumArtView")
        self.albumArt_view.setFixedSize(70, 70)
        self.albumArt_view.setAlignment(qtc.Qt.AlignCenter)

        small_scaled_pixmap = load_and_scale_image("No-album-art.png", size=70, round_radius=10)
        self.albumArt_view.setPixmap(small_scaled_pixmap)

        self.mediaTitle_frame = qtw.QFrame()
        self.mediaTitle_frame_layout = qtw.QVBoxLayout(self.mediaTitle_frame)
        self.mediaTitle_frame.setObjectName("mediaTitle_frame")

        self.songLabel = MarqueeLabel("Song Label")
        self.artistName = MarqueeLabel("Artist Name")
        self.albumName = MarqueeLabel("Album Name")
        self.mediaTitle_frame_layout.addWidget(self.songLabel)
        self.mediaTitle_frame_layout.addWidget(self.artistName)
        self.mediaTitle_frame_layout.addWidget(self.albumName)

        self.albumArt_frame_layout.addWidget(self.albumArt_view)
        self.albumArt_frame_layout.addWidget(self.mediaTitle_frame)

        self.playBackControl_outerframe = qtw.QFrame()
        self.playBackControl_outerframe_layout = qtw.QVBoxLayout(self.playBackControl_outerframe)
        self.playBackControl_outerframe.setObjectName("playBackControl_outerframe")
        self.playBackControl_outerframe.setContentsMargins(0, 0, 0, 0)
        self.playBackControl_outerframe.setMaximumWidth(280)
        
        self.mainPlayBackControl_frame = qtw.QFrame()
        self.mainPlayBackControl_frame_layout = qtw.QHBoxLayout(self.mainPlayBackControl_frame)
        self.mainPlayBackControl_frame.setObjectName("mainPlaybackControlFrame")
        self.mainPlayBackControl_frame.setContentsMargins(0, 0, 0, 0)
        
        self.secondaryPlayBackControl_frame = qtw.QFrame()
        self.secondaryPlayBackControl_frame_layout = qtw.QHBoxLayout(self.secondaryPlayBackControl_frame)
        self.secondaryPlayBackControl_frame.setObjectName("secondaryPlaybackControlFrame")
        self.secondaryPlayBackControl_frame.setContentsMargins(0, 0, 0, 0)
        self.secondaryPlayBackControl_frame_layout.setAlignment(qtc.Qt.AlignHCenter) 

        self.prev_track_btn = qtw.QPushButton("")
        prev_track_btnIcon = create_svg_icon("prev_track_btn.png", size=20)
        self.prev_track_btn.setToolTip("Prev track")
        self.prev_track_btn.setIcon(prev_track_btnIcon)

        self.playPause_track_btn = qtw.QPushButton("")
        playPause_btnIcon = create_svg_icon("play_alt.png", size=30)
        self.playPause_track_btn.setToolTip("play/Pause")
        self.playPause_track_btn.setObjectName("playpause_btn")
        self.playPause_track_btn.setIcon(playPause_btnIcon)

        self.next_track_btn = qtw.QPushButton("")
        next_track_btnIcon = create_svg_icon("next_track_btn.png", size=20)
        self.next_track_btn.setToolTip("Next track")
        self.next_track_btn.setIcon(next_track_btnIcon)

        self.mainPlayBackControl_frame_layout.addWidget(self.prev_track_btn)
        self.mainPlayBackControl_frame_layout.addWidget(self.playPause_track_btn)
        self.mainPlayBackControl_frame_layout.addWidget(self.next_track_btn)

        self.repeatOptions_btn = qtw.QPushButton("")
        repeatIcon = create_svg_icon("loop.png", size=10)
        self.repeatOptions_btn.setIcon(repeatIcon)
        self.repeatOptions_btn.setToolTip("Repeat Options")

        self.makeFavourite_btn = qtw.QPushButton("")
        favBtnIcon = create_svg_icon("fav_btn.png", size=10)
        self.makeFavourite_btn.setIcon(favBtnIcon)
        self.makeFavourite_btn.setToolTip("Add to Favourites")

        self.shuffle_btn = qtw.QPushButton("")
        shuffleIcon = create_svg_icon("shuffle_btn.png", size=10)
        self.shuffle_btn.setIcon(shuffleIcon)
        self.shuffle_btn.setToolTip("Shuffle Playlist")

        self.trackInfo_btn = qtw.QPushButton("")
        infoIcon = create_svg_icon("track_info_btn.png", size=10)
        self.trackInfo_btn.setIcon(infoIcon)
        self.trackInfo_btn.setToolTip("Track Information")
        
        self.secondaryPlayBackControl_frame_layout.addStretch()
        self.secondaryPlayBackControl_frame_layout.addWidget(self.repeatOptions_btn)
        self.secondaryPlayBackControl_frame_layout.addWidget(self.makeFavourite_btn)
        self.secondaryPlayBackControl_frame_layout.addWidget(self.shuffle_btn)
        self.secondaryPlayBackControl_frame_layout.addWidget(self.trackInfo_btn)
        self.secondaryPlayBackControl_frame_layout.addStretch()

        self.playBackControl_outerframe_layout.addWidget(self.mainPlayBackControl_frame)
        self.playBackControl_outerframe_layout.addStretch() 
        self.playBackControl_outerframe_layout.addWidget(self.secondaryPlayBackControl_frame)
        self.playBackControl_outerframe_layout.addStretch() 

        self.volumeSlider = qtw.QSlider(qtc.Qt.Horizontal)
        self.volumeSlider.setObjectName("volumeSlider")
        self.volumeSlider.setToolTip("Volume Slider")
        self.volumeSlider.setMaximumWidth(120)
        self.volumeSlider.setMinimumWidth(120)

        self.volumeIcon = qtw.QLabel("")
        volumeIcon_img = load_and_scale_image("speaker_btn.svg", size=14)
        self.volumeIcon.setPixmap(volumeIcon_img)

        self.playBackFooter_frame_layout.addWidget(self.albumArt_frame)
        self.playBackFooter_frame_layout.addStretch()
        self.playBackFooter_frame_layout.addWidget(self.playBackControl_outerframe)
        self.playBackFooter_frame_layout.addStretch()
        self.playBackFooter_frame_layout.addWidget(self.volumeIcon)
        self.playBackFooter_frame_layout.addWidget(self.volumeSlider)

        self.playlist_page_layout.addWidget(self.top_label_frame)
        self.playlist_page_layout.addWidget(self.centerframe)
        self.playlist_page_layout.addWidget(self.playBackTimer_frame)
        self.playlist_page_layout.addWidget(self.playBackSlider)
        self.playlist_page_layout.addWidget(self.playBackFooter_frame)

        self.right_container.addWidget(self.playlist_page)
        self.show()

    def resizeEvent(self, event):
        self.songLabel.check_should_scroll()
        self.artistName.check_should_scroll()
        self.albumName.check_should_scroll()
        super().resizeEvent(event)

    def switch_theme(self):
        index = self.themes.index(self.current_theme)
        next_index = (index + 1) % len(self.themes)
        self.current_theme = self.themes[next_index]
        
        self.theme_manager.load_and_apply_theme(self.current_theme)
        database.save_setting("theme", self.current_theme)