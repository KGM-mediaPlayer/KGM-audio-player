import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
import PyQt5.QtCore as qtc 

class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("KGM Media Player")
        self.resize(900, 600) # Adjusted size to better fit the screenshot

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
        self.right_container_layout=qtw.QVBoxLayout(self.right_container)
        #self.right_widget.setContentsMargins(10, 10, 10, 10)
        self.right_container.setObjectName("rightWidget")

        self.main_layout.addWidget(self.right_container)

        # -----------------------------------------------------------
        ## 1. Right container Stack top to bottom
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
        self.playBackTimer_frame_layout.addWidget(self.rightPlaybackTimer)

        self.playBackSlider=qtw.QSlider()
        self.playBackSlider.setObjectName("playBackSlider")

        self.playBackFooter_frame=qtw.QFrame()
        self.playBackFooter_frame_layout=qtw.QHBoxLayout(self.playBackFooter_frame)
        self.playBackTimer_frame.setObjectName("playBackFooterFrame")

        #playBack footer Contents
        self.albumArt_frame=qtw.QFrame()
        self.albumArt_frame_layout=qtw.QHBoxLayout(self.albumArt_frame)

        self.mediaTitle_frame=qtw.QFrame()
        self.mediaTitle_frame_layout=qtw.QVBoxLayout(self.mediaTitle_frame)

        #labels to go in media title frame
        self.songLabel=qtw.QLabel("Song Label")
        self.artistName=qtw.QLabel("Artist Name")
        self.albumtName=qtw.QLabel("Album Name")

        #playBackControl frame
        self.playBackControl_outerframe=qtw.QFrame()
        self.playBackControl_outerframe_layout=qtw.QVBoxLayout(self.playBackControl_outerframe)

        self.mainPlayBackControl_frame=qtw.QFrame()
        self.mainPlayBackControl_frame_layout=qtw.QVBoxLayout(self.mainPlayBackControl_frame)
        self.mainPlayBackControl_frame.setObjectName("mainPlaybackControlFrame")

        self.secondaryPlayBackControl_frame=qtw.QFrame()
        self.secondaryPlayBackControl_frame_layout=qtw.QVBoxLayout(self.secondaryPlayBackControl_frame)
        self.secondaryPlayBackControl_frame.setObjectName("secondaryPlaybackControlFrame")

        #adding componenets to rightcontainer
        self.right_container.addWidget(self.top_label_frame)
        self.right_container.addWidget(self.listObject)
        self.right_container.addWidget(self.playBackTimer_frame)
        self.right_container.addWidget(self.playBackFooter_frame)
        




        


