import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
import PyQt5.QtCore as qtc 
from .theme_manager import ThemeManager
from .asset_loader import create_svg_icon, load_and_scale_image

import os

class VideoWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()

        #image loading func
        def get_asset_path(self, filename):
            """Resolves the absolute path for an asset file."""
            # __file__ is the path to kgm_media_player.py
            base_dir = os.path.dirname(__file__) 
            return os.path.join(base_dir, 'assets', filename)


        self.setWindowTitle("Video Player")
        self.resize(900, 750) # Adjusted size to better fit the screenshot

        self.theme_manager = ThemeManager(__file__) #Instantiate the ThemeManager
        self.theme_manager.load_and_apply_theme() #Load the theme (This sets all QSS)

        #Central widget
        self.central_container = qtw.QWidget()
        self.setCentralWidget(self.central_container)

        self.main_layout = qtw.QVBoxLayout(self.central_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0) # Remove margin for full-bleed sidebar/content
        self.main_layout.setSpacing(0) # No space between sidebar and main content

        self.leftPlayBackTimer_frame=qtw.QFrame()
        self.leftPlayBackTimer_frame_layout=qtw.QHBoxLayout(self.leftPlayBackTimer_frame)
        self.leftPlayBackTimer_frame.setObjectName("playBackTimer_frame")
        self.leftPlayBackTimer_frame.setContentsMargins(0, 0, 0, 0)
        #self.playBackTimer_frame.setMaximumHeight(10)

        self.rightPlayBackTimer_frame=qtw.QFrame()
        self.rightPlayBackTimer_frame_layout=qtw.QHBoxLayout(self.rightPlayBackTimer_frame)
        self.rightPlayBackTimer_frame.setObjectName("playBackTimer_frame")
        self.rightPlayBackTimer_frame.setContentsMargins(0, 0, 0, 0)

        self.leftPlaybackTimer=qtw.QLabel("00:00")
        self.leftPlaybackTimer.setObjectName("playBackTimer")
        self.rightPlaybackTimer=qtw.QLabel("00:00")
        self.rightPlaybackTimer.setObjectName("playBackTimer")
        

        self.playBackSlider=qtw.QSlider(qtc.Qt.Horizontal)
        self.playBackSlider.setObjectName("playBackSlider")
        self.playBackSlider.setContentsMargins(0, 0, 0, 0)

        self.leftPlayBackTimer_frame_layout.addWidget(self.leftPlaybackTimer)
        self.rightPlayBackTimer_frame_layout.addWidget(self.rightPlaybackTimer)
        

        self.playBackFooter_frame=qtw.QFrame()
        self.playBackFooter_frame_layout=qtw.QHBoxLayout(self.playBackFooter_frame)
        self.playBackFooter_frame_layout.setObjectName("playBackFooterFrame")
        self.playBackFooter_frame.setMaximumHeight(100)

        #playBack footer Contents
        

        #playBackControl frame
        self.playBackControl_outerframe=qtw.QFrame()
        self.playBackControl_outerframe_layout=qtw.QVBoxLayout(self.playBackControl_outerframe)
        self.playBackControl_outerframe.setObjectName("playBackControl_outerframe")
        self.playBackControl_outerframe.setContentsMargins(0, 0, 0, 0)
        self.playBackControl_outerframe.setMaximumWidth(280)
        
        

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
        playPause_btnIcon=create_svg_icon(__file__, "play_alt.png", size=30)
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
        self.playBackFooter_frame_layout.addWidget(self.rightPlaybackTimer)
        self.playBackFooter_frame_layout.addStretch()
        self.playBackFooter_frame_layout.addWidget(self.playBackControl_outerframe)
        self.playBackFooter_frame_layout.addStretch()
        self.playBackFooter_frame_layout.addWidget(self.leftPlaybackTimer)
        #self.playBackFooter_frame_layout.addWidget(self.volumeIcon)
        #self.playBackFooter_frame_layout.addWidget(self.volumeSlider)

        
        #adding componenets to rightcontainer
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.playBackSlider)
        #self.main_layout.addWidget(self.playBackTimer_frame)
        self.main_layout.addWidget(self.playBackFooter_frame)


        self.show()