import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
import PyQt5.QtCore as qtc 
from .theme_manager import ThemeManager

class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()

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

        self.main_layout.addWidget(self.sidebar_container)


        # -----------------------------------------------------------
        ## 1. Right container (Right Panel)
        # -----------------------------------------------------------
        self.right_container=qtw.QStackedWidget()
        #self.right_widget.setContentsMargins(10, 10, 10, 10)
        self.right_container.setObjectName("rightWidget")

        self.playlist_page = qtw.QWidget()
        self.playlist_page_layout = qtw.QVBoxLayout(self.playlist_page)
        self.playlist_page_layout.setContentsMargins(0, 0, 0, 0) # Use this layout to stack components

        self.main_layout.addWidget(self.right_container)
        

        # -----------------------------------------------------------
        ##  Right container Stack top to bottom
        # -----------------------------------------------------------
        self.top_label_frame=qtw.QFrame()
        self.top_label_frame_layout=qtw.QHBoxLayout(self.top_label_frame)
        self.top_label_frame.setObjectName("topLabel")

        self.listObject=qtw.QListWidget()
        self.top_label_frame.setObjectName("lisObject")

        self.playBackTimer_frame=qtw.QFrame()
        self.playBackTimer_frame_layout=qtw.QHBoxLayout(self.playBackTimer_frame)
        self.playBackTimer_frame.setObjectName("playBackTimerFrame")

        self.leftPlaybackTimer=qtw.QLabel("00:00")
        self.rightPlaybackTimer=qtw.QLabel("00:00")
        self.playBackTimer_frame_layout.addWidget(self.leftPlaybackTimer)
        self.playBackTimer_frame_layout.addStretch()
        self.playBackTimer_frame_layout.addWidget(self.rightPlaybackTimer)

        self.playBackSlider=qtw.QSlider(qtc.Qt.Horizontal)
        self.playBackSlider.setObjectName("playBackSlider")

        self.playBackFooter_frame=qtw.QFrame()
        self.playBackFooter_frame_layout=qtw.QHBoxLayout(self.playBackFooter_frame)
        self.playBackTimer_frame.setObjectName("playBackFooterFrame")

        #playBack footer Contents
        self.albumArt_frame=qtw.QFrame()
        self.albumArt_frame_layout=qtw.QHBoxLayout(self.albumArt_frame)

        self.albumArt_view=qtw.QLabel()
        self.albumArt_view.setObjectName("albumArtView")
        self.albumArt_frame_layout.addWidget(self.albumArt_view)

        self.mediaTitle_frame=qtw.QFrame()
        self.mediaTitle_frame_layout=qtw.QVBoxLayout(self.mediaTitle_frame)

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

        self.mainPlayBackControl_frame=qtw.QFrame()
        self.mainPlayBackControl_frame_layout=qtw.QVBoxLayout(self.mainPlayBackControl_frame)
        self.mainPlayBackControl_frame.setObjectName("mainPlaybackControlFrame")

        self.secondaryPlayBackControl_frame=qtw.QFrame()
        self.secondaryPlayBackControl_frame_layout=qtw.QVBoxLayout(self.secondaryPlayBackControl_frame)
        self.secondaryPlayBackControl_frame.setObjectName("secondaryPlaybackControlFrame")

        #adding componets to footer
        self.playBackFooter_frame_layout.addWidget(self.albumArt_frame)
        self.playBackFooter_frame_layout.addStretch()
        self.playBackFooter_frame_layout.addWidget(self.playBackControl_outerframe)
        self.playBackFooter_frame_layout.addStretch()

        #adding componenets to rightcontainer
        self.playlist_page_layout.addWidget(self.top_label_frame)
        self.playlist_page_layout.addWidget(self.listObject)
        self.playlist_page_layout.addWidget(self.playBackTimer_frame)
        self.playlist_page_layout.addWidget(self.playBackSlider)
        self.playlist_page_layout.addWidget(self.playBackFooter_frame)

        self.right_container.addWidget(self.playlist_page)

        self.show()

    