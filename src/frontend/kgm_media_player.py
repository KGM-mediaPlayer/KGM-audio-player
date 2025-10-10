import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
import PyQt5.QtCore as qtc 
from .theme_manager import ThemeManager
from .asset_loader import create_svg_icon, load_and_scale_image
from .vertical_button import VerticalButton
import os

class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()

        #image loading func
        def get_asset_path(self, filename):
            """Resolves the absolute path for an asset file."""
            # __file__ is the path to kgm_media_player.py
            base_dir = os.path.dirname(__file__) 
            return os.path.join(base_dir, 'assets', filename)


        self.setWindowTitle("KGM Media Player")
        self.resize(900, 600) # Adjusted size to better fit the screenshot

        self.theme_manager = ThemeManager(__file__) #Instantiate the ThemeManager
        self.theme_manager.load_and_apply_theme() #Load the theme (This sets all QSS)

        #Central widget
        self.central_container = qtw.QWidget()
        self.setCentralWidget(self.central_container)

        self.main_layout = qtw.QHBoxLayout(self.central_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0) # Remove margin for full-bleed sidebar/content
        self.main_layout.setSpacing(0) # No space between sidebar and main content


        # -----------------------------------------------------------
        ## 1. Sidebar Setup (Left Panel)
        # -----------------------------------------------------------
        self.sidebar_container = qtw.QWidget()
        self.sidebar_container_layout = qtw.QVBoxLayout(self.sidebar_container)
        self.sidebar_container_layout.setContentsMargins(10, 10, 10, 10)
        self.sidebar_container_layout.setSpacing(5) # Reduced spacing
        self.sidebar_container.setObjectName("Sidebar") 

        #sidebar buttons
        self.appLogo=qtw.QLabel("")
        LogoIcon = load_and_scale_image(__file__, "app.png", size=32)
        self.appLogo.setPixmap(LogoIcon)

        self.playlist_btn=qtw.QPushButton("")
        playListIcon=create_svg_icon(__file__, "playlist_btn.svg", size=35)
        self.playlist_btn.setIcon(playListIcon)
        self.playlist_btn.setToolTip("View and manage your playlist")


        self.music_btn=qtw.QPushButton("")
        music_btnIcon=create_svg_icon(__file__, "music_btn.svg", size=35)
        self.music_btn.setIcon(music_btnIcon)
        self.music_btn.setToolTip("music library")

        self.effects_btn=qtw.QPushButton("")
        effects_btnIcon=create_svg_icon(__file__, "effects_btn.svg", size=40)
        self.effects_btn.setIcon(effects_btnIcon)
        self.effects_btn.setToolTip("Special Effects")

        self.settings_btn=qtw.QPushButton("")
        settings_btnIcon=create_svg_icon(__file__, "settings_btn.svg", size=35)
        self.settings_btn.setIcon(settings_btnIcon)
        self.settings_btn.setToolTip("Settings")

        self.theme_btn=qtw.QPushButton("")
        themeIcon=create_svg_icon(__file__, "theme_btn.svg", size=35)
        self.theme_btn.setIcon(themeIcon)
        self.theme_btn.setToolTip("Interface Themes")


        self.about_btn=qtw.QPushButton("")
        self.about_btn.setObjectName("about_btn")
        about_btntIcon=create_svg_icon(__file__, "about_btn.svg")
        self.about_btn.setIcon(about_btntIcon)
        self.about_btn.setToolTip("About KGM MediaPlayer")

        #Add buttons to side bar
        self.sidebar_container_layout.addWidget(self.appLogo, alignment=qtc.Qt.AlignCenter)
        self.sidebar_container_layout.addWidget(self.playlist_btn)
        self.sidebar_container_layout.addWidget(self.music_btn)
        self.sidebar_container_layout.addWidget(self.effects_btn)
        self.sidebar_container_layout.addWidget(self.settings_btn)
        self.sidebar_container_layout.addStretch()
        self.sidebar_container_layout.addWidget(self.theme_btn)
        self.sidebar_container_layout.addWidget(self.about_btn)

        self.main_layout.addWidget(self.sidebar_container)


        # -----------------------------------------------------------
        ## 1. Right container (Right Panel)
        # -----------------------------------------------------------
        self.right_container=qtw.QStackedWidget()
        #self.right_widget.setContentsMargins(10, 10, 10, 10)
        self.right_container.setObjectName("rightWidget")

        self.playlist_page = qtw.QWidget()
        self.playlist_page_layout = qtw.QVBoxLayout(self.playlist_page)
        self.playlist_page_layout.setContentsMargins(0, 0, 0, 0) 

        self.main_layout.addWidget(self.right_container)
        

        # -----------------------------------------------------------
        ##  Right container Stack top to bottom
        # -----------------------------------------------------------
        self.top_label_frame=qtw.QFrame()
        self.top_label_frame_layout=qtw.QHBoxLayout(self.top_label_frame)
        self.top_label_frame.setObjectName("topLabel")

        #top label componets
        self.pageIcon=qtw.QLabel("PlayIcon")
        pageIcon_btn=load_and_scale_image(__file__, "playPause_btn.svg", size=30)
        self.pageIcon.setPixmap(pageIcon_btn)
        
        self.page_label=qtw.QLabel("Playlist")
        self.page_label.setContentsMargins(0, 0, 0, 0)
        self.page_label.setObjectName("pageLabel")

        self.searchIcon=qtw.QLabel("SearchIcon")
        self.searchIcon.setObjectName("searchIcon")
        self.searchIcon.setContentsMargins(0, 0, 0, 0)
        searchIcon_btn=load_and_scale_image(__file__, "searchIcon_btn.svg", size=24)
        self.searchIcon.setPixmap(searchIcon_btn)

        self.searchInput=qtw.QLineEdit("Search")
        self.searchInput.setContentsMargins(0, 0, 0, 0)
        self.searchInput.setObjectName("searchInput")

        #add items to top label frame
        self.top_label_frame_layout.addWidget(self.pageIcon)
        self.top_label_frame_layout.addWidget(self.page_label)
        self.top_label_frame_layout.addStretch()
        self.top_label_frame_layout.addWidget(self.searchIcon)
        self.top_label_frame_layout.addWidget(self.searchInput)

        self.centerframe=qtw.QFrame()
        self.centerframe_layout=qtw.QHBoxLayout(self.centerframe)
        self.centerframe.setObjectName("centerFrame")

        self.listObject=qtw.QListWidget()
        self.listObject.setObjectName("lisObject")
        self.centerframe_layout.addWidget(self.listObject)

        self.playBackTimer_frame=qtw.QFrame()
        self.playBackTimer_frame_layout=qtw.QHBoxLayout(self.playBackTimer_frame)
        self.playBackTimer_frame.setObjectName("playBackTimer_frame")
        self.playBackTimer_frame.setContentsMargins(0, 0, 0, 0)
        #self.playBackTimer_frame.setMaximumHeight(10)

        self.leftPlaybackTimer=qtw.QLabel("00:00")
        self.leftPlaybackTimer.setObjectName("playBackTimer")
        self.rightPlaybackTimer=qtw.QLabel("00:00")
        self.rightPlaybackTimer.setObjectName("playBackTimer")
        

        self.playBackSlider=qtw.QSlider(qtc.Qt.Horizontal)
        self.playBackSlider.setObjectName("playBackSlider")
        self.playBackSlider.setContentsMargins(0, 0, 0, 0)

        self.playBackTimer_frame_layout.addWidget(self.leftPlaybackTimer)
        #self.playBackTimer_frame_layout.addWidget(self.playBackSlider)
        self.playBackTimer_frame_layout.addStretch()
        self.playBackTimer_frame_layout.addWidget(self.rightPlaybackTimer)
        

        self.playBackFooter_frame=qtw.QFrame()
        self.playBackFooter_frame_layout=qtw.QHBoxLayout(self.playBackFooter_frame)
        self.playBackFooter_frame_layout.setObjectName("playBackFooterFrame")
        self.playBackFooter_frame.setMaximumHeight(100)

        #playBack footer Contents
        self.albumArt_frame=qtw.QFrame()
        self.albumArt_frame_layout=qtw.QHBoxLayout(self.albumArt_frame)
        self.albumArt_frame_layout.setContentsMargins(0, 0, 0, 0) # Tidy up layout
        self.albumArt_frame.setObjectName("albumArtFrame")

        self.albumArt_view=qtw.QLabel()
        self.albumArt_view.setObjectName("albumArtView")
        self.albumArt_view.setFixedSize(70, 70)


        small_scaled_pixmap = load_and_scale_image(__file__, "No-album-art.png", size=60,round_radius=10)
        self.albumArt_view.setPixmap(small_scaled_pixmap)

        self.albumArt_frame_layout.addWidget(self.albumArt_view)

        self.mediaTitle_frame=qtw.QFrame()
        self.mediaTitle_frame_layout=qtw.QVBoxLayout(self.mediaTitle_frame)
        self.mediaTitle_frame.setObjectName("mediaTitle_frame")

        #labels to go in media title frame
        self.songLabel=qtw.QLabel("Song Label")
        self.artistName=qtw.QLabel("Artist Name")
        self.albumName=qtw.QLabel("Album Name")
        self.mediaTitle_frame_layout.addWidget(self.songLabel)
        self.mediaTitle_frame_layout.addWidget(self.artistName)
        self.mediaTitle_frame_layout.addWidget(self.albumName)

        #Adding componets to media title frame
        self.albumArt_frame_layout.addWidget(self.albumArt_view)
        self.albumArt_frame_layout.addWidget(self.mediaTitle_frame)

        #playBackControl frame
        self.playBackControl_outerframe=qtw.QFrame()
        self.playBackControl_outerframe_layout=qtw.QVBoxLayout(self.playBackControl_outerframe)
        self.playBackControl_outerframe.setObjectName("playBackControl_outerframe")
        self.playBackControl_outerframe.setContentsMargins(0, 0, 0, 0)
        
        

        self.mainPlayBackControl_frame=qtw.QFrame()
        self.mainPlayBackControl_frame_layout=qtw.QHBoxLayout(self.mainPlayBackControl_frame)
        self.mainPlayBackControl_frame.setObjectName("mainPlaybackControlFrame")
        self.mainPlayBackControl_frame.setContentsMargins(0, 0, 0, 0)
        #self.mainPlayBackControl_frame_layout.setAlignment(qtc.Qt.AlignHCenter)
        

        self.secondaryPlayBackControl_frame=qtw.QFrame()
        self.secondaryPlayBackControl_frame_layout=qtw.QHBoxLayout(self.secondaryPlayBackControl_frame)
        self.secondaryPlayBackControl_frame.setObjectName("secondaryPlaybackControlFrame")
        self.secondaryPlayBackControl_frame.setContentsMargins(0, 0, 0, 0)
        self.secondaryPlayBackControl_frame_layout.setAlignment(qtc.Qt.AlignHCenter) 



        #playback control. buttons
        self.prev_track_btn=qtw.QPushButton("")
        prev_track_btnIcon=create_svg_icon(__file__, "prev_track_btn.png", size=20)
        self.prev_track_btn.setContentsMargins(0, 0, 0, 0)
        self.prev_track_btn.setIcon(prev_track_btnIcon)
        self.prev_track_btn.setToolTip("previous item")

        self.playPause_track_btn=qtw.QPushButton("")
        self.playPause_track_btn.setToolTip("Play / Pause")
        playPause_btnIcon=create_svg_icon(__file__, "playPause_btn.svg", size=40)
        self.playPause_track_btn.setObjectName("playpause_btn")
        self.playPause_track_btn.setContentsMargins(0, 0, 0, 0)
        self.playPause_track_btn.setIcon(playPause_btnIcon)

        self.next_track_btn=qtw.QPushButton("")
        self.next_track_btn.setToolTip("next item")
        next_track_btnIcon=create_svg_icon(__file__, "next_track_btn.png", size=20)
        self.next_track_btn.setContentsMargins(0, 0, 0, 0)
        self.next_track_btn.setIcon(next_track_btnIcon)

        #add to respective frame
        self.mainPlayBackControl_frame_layout.addWidget(self.prev_track_btn)
        self.mainPlayBackControl_frame_layout.addWidget(self.playPause_track_btn)
        self.mainPlayBackControl_frame_layout.addWidget(self.next_track_btn)

        self.repeatOptions_btn=qtw.QPushButton("")
        self.repeatOptions_btn.setToolTip("repeat options")
        repeatOpyins_btnIcon=create_svg_icon(__file__, "loop.png", size=10)
        self.repeatOptions_btn.setIcon(repeatOpyins_btnIcon)

        self.makeFavourite_btn=qtw.QPushButton("")
        self.makeFavourite_btn.setToolTip("add/remove from favourites")
        makefavourites_btnIcon=create_svg_icon(__file__, "fav_btn.png", size=10)
        self.makeFavourite_btn.setIcon(makefavourites_btnIcon)

        self.shuffle_btn=qtw.QPushButton("")
        self.shuffle_btn.setToolTip("shuffle")
        shuffle_btnIcon=create_svg_icon(__file__, "shuffle_btn.png", size=10)
        self.shuffle_btn.setIcon(shuffle_btnIcon)

        self.trackInfo_btn=qtw.QPushButton("")
        self.trackInfo_btn.setToolTip("track Info")
        trackInfo_btnIcon=create_svg_icon(__file__, "track_info_btn.png", size=10)
        self.trackInfo_btn.setIcon(trackInfo_btnIcon)
        
        #add to respective frame
        self.secondaryPlayBackControl_frame_layout.addStretch()
        self.secondaryPlayBackControl_frame_layout.addWidget(self.repeatOptions_btn)
        self.secondaryPlayBackControl_frame_layout.addWidget(self.makeFavourite_btn)
        self.secondaryPlayBackControl_frame_layout.addWidget(self.shuffle_btn)
        self.secondaryPlayBackControl_frame_layout.addWidget(self.trackInfo_btn)
        self.secondaryPlayBackControl_frame_layout.addStretch()

        #add both playback control frames
        #self.playBackControl_outerframe_layout.addStretch() 
        self.playBackControl_outerframe_layout.addWidget(self.mainPlayBackControl_frame)
        self.playBackControl_outerframe_layout.addStretch() 
        self.playBackControl_outerframe_layout.addWidget(self.secondaryPlayBackControl_frame)
        self.playBackControl_outerframe_layout.addStretch() 


        # ----------------- Volume Control -----------------
        self.volumeSlider = qtw.QSlider(qtc.Qt.Horizontal)
        self.volumeSlider.setObjectName("volumeSlider")
        self.volumeSlider.setMaximumWidth(120)
        self.volumeSlider.setMinimumWidth(120)

        self.volumeIcon = qtw.QLabel("")
        self.volumeIcon.setMinimumWidth(15)
        self.volumeIcon.setMinimumHeight(15)
        volumeIcon_btn=load_and_scale_image(__file__, "speaker_btn.svg", size=14)
        self.volumeIcon.setPixmap(volumeIcon_btn)


        #adding componets to footer
        self.playBackFooter_frame_layout.addWidget(self.albumArt_frame)
        self.playBackFooter_frame_layout.addStretch()
        self.playBackFooter_frame_layout.addWidget(self.playBackControl_outerframe)
        self.playBackFooter_frame_layout.addStretch()
        self.playBackFooter_frame_layout.addWidget(self.volumeIcon)
        self.playBackFooter_frame_layout.addWidget(self.volumeSlider)

        
        #adding componenets to rightcontainer
        self.playlist_page_layout.addWidget(self.top_label_frame)
        self.playlist_page_layout.addWidget(self.centerframe)
        self.playlist_page_layout.addWidget(self.playBackTimer_frame)
        self.playlist_page_layout.addWidget(self.playBackSlider)
        self.playlist_page_layout.addWidget(self.playBackFooter_frame)

        self.right_container.addWidget(self.playlist_page)

        self.show()

    