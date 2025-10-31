import sys
import os
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QSlider, 
    QLabel, QPushButton, QSizePolicy, QGraphicsView, QGraphicsScene, QApplication,
    QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize

# --- VLC and macOS Dependencies ---
try:
    # Attempt to import VLC and the necessary PyQt utilities
    import vlc
    from PyQt5.sip import unwrapinstance
    VLC_AVAILABLE = True
except ImportError:
    vlc = None
    unwrapinstance = None
    VLC_AVAILABLE = False
    print("VLC or PyQt5.sip not fully available. Video playback will be simulated.")

# --- MOCK DEPENDENCIES FOR INDEPENDENT EXECUTION ---

# Placeholder asset_loader functions to prevent ImportError when running standalone
def create_svg_icon(file_path, svg_filename, size=40):
    """Placeholder for loading SVG icons."""
    return QIcon() 

def load_and_scale_image(file_path, image_filename, size=40, round_radius=0):
    """Placeholder for loading PNG/image icons."""
    return QIcon()

# --- VIDEO PLAYER WINDOW CLASS ---

class VideoPlayerWindow(QMainWindow):
    """
    Defines the modular UI for the Video Player as a separate QMainWindow,
    using QGraphicsView as the video display surface.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("KGM Video Player (Standalone Test)")
        self.setMinimumSize(800, 600)
        self.setObjectName("VideoPlayerWindow")
        
        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # --- Main Layout ---
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 1. Video Display Surface (QGraphicsView)
        self.video_view = QGraphicsView() 
        self.video_view.setObjectName("video_view")
        self.video_view.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.video_view.setFrameShadow(QtWidgets.QFrame.Plain)
        self.video_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Set up a necessary QGraphicsScene
        self.video_scene = QGraphicsScene(self)
        self.video_view.setScene(self.video_scene)
        
        # Optimization for video: turn off scrollbars
        self.video_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.video_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Add the graphics view to the layout
        self.main_layout.addWidget(self.video_view)

        # 2. Control Overlay Container
        self.controls_overlay_container = QFrame()
        self.controls_overlay_container.setObjectName("controls_overlay_container")
        self.controls_overlay_container.setMaximumHeight(150)
        self.controls_layout = QVBoxLayout(self.controls_overlay_container)
        self.controls_layout.setContentsMargins(10, 5, 10, 5)
        self.controls_layout.setSpacing(5)
        
        # 3. Playback Timer and Slider Frame (Reusable Element 1)
        self.playBackTimer_frame = QFrame()
        self.playBackTimer_frame.setObjectName("playBackTimer_frame")
        self.playBackTimer_frame.setMinimumHeight(40) 
        self.playBackTimer_frame.setMaximumHeight(40)
        self.playBackTimer_frame.setLayout(self._setup_timer_slider_layout())
        self.controls_layout.addWidget(self.playBackTimer_frame)

        # 4. Playback Controls Buttons Frame (Reusable Element 2)
        self.playBackControl_outerframe = QFrame()
        self.playBackControl_outerframe.setObjectName("playBackControl_outerframe")
        self.playBackControl_outerframe.setMinimumHeight(70)
        self.playBackControl_outerframe.setMaximumHeight(70)
        self.playBackControl_outerframe.setLayout(self._setup_playback_buttons_layout())
        self.controls_layout.addWidget(self.playBackControl_outerframe)

        # Add control overlay to the bottom of the video view
        self.main_layout.addWidget(self.controls_overlay_container)

        self.controls_overlay_container.show()

    def _setup_timer_slider_layout(self):
        """Sets up the layout for the timer labels and slider."""
        timer_slider_layout = QHBoxLayout()
        timer_slider_layout.setContentsMargins(0, 0, 0, 0)
        timer_slider_layout.setSpacing(5)

        # Left Timer Label
        self.leftPlaybackTimer = QLabel("00:00")
        self.leftPlaybackTimer.setObjectName("leftPlaybackTimer")
        self.leftPlaybackTimer.setMinimumWidth(50)
        self.leftPlaybackTimer.setMaximumWidth(50)
        timer_slider_layout.addWidget(self.leftPlaybackTimer)

        # Playback Slider
        self.playBackSlider = QSlider(Qt.Horizontal)
        self.playBackSlider.setObjectName("playBackSlider")
        self.playBackSlider.setRange(0, 100)
        timer_slider_layout.addWidget(self.playBackSlider)

        # Right Timer Label
        self.rightPlaybackTimer = QLabel("00:00")
        self.rightPlaybackTimer.setObjectName("rightPlaybackTimer")
        self.rightPlaybackTimer.setMinimumWidth(50)
        timer_slider_layout.addWidget(self.rightPlaybackTimer)

        return timer_slider_layout

    def _setup_playback_buttons_layout(self):
        """Sets up the layout for the playback control buttons."""
        
        playback_controls_layout = QVBoxLayout()
        playback_controls_layout.setContentsMargins(10, 5, 10, 5)
        playback_controls_layout.setSpacing(5)

        # --- Top Row (Prev/Play/Next) ---
        top_row = QHBoxLayout()
        top_row.setSpacing(15)

        # 1. Previous Track Button
        self.prev_track_btn = QPushButton()
        self.prev_track_btn.setIcon(create_svg_icon(__file__, "prev_btn.svg", size=40))
        top_row.addWidget(self.prev_track_btn)

        # 2. Play/Pause Button
        self.playPause_track_btn = QPushButton()
        self.playPause_track_btn.setIcon(load_and_scale_image(__file__,'play_btn.png',size=40)) 
        top_row.addWidget(self.playPause_track_btn)

        # 3. Next Track Button
        self.next_track_btn = QPushButton()
        self.next_track_btn.setIcon(create_svg_icon(__file__, "next_btn.svg", size=40))
        top_row.addWidget(self.next_track_btn)
        
        # Center the top row buttons
        top_row_frame = QFrame()
        top_row_frame.setLayout(top_row)
        top_row.setAlignment(Qt.AlignCenter)
        playback_controls_layout.addWidget(top_row_frame)


        # --- Bottom Row (Extra Options) ---
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(15)

        # 1. Repeat Button
        self.repeatOptions_btn = QPushButton()
        self.repeatOptions_btn.setIcon(load_and_scale_image(__file__,'loop.png',size=10))
        bottom_row.addWidget(self.repeatOptions_btn)

        # 2. Favourite Button
        self.makeFavourite_btn = QPushButton()
        self.makeFavourite_btn.setIcon(load_and_scale_image(__file__, "fav_btn.png", size=20,round_radius=40))
        bottom_row.addWidget(self.makeFavourite_btn)

        # 3. Shuffle Button
        self.shuffle_btn = QPushButton()
        self.shuffle_btn.setIcon(load_and_scale_image(__file__,'play_all_btn.png',size=10))
        bottom_row.addWidget(self.shuffle_btn)

        # 4. Info Button (Track Info)
        self.trackInfo_btn = QPushButton()
        self.trackInfo_btn.setIcon(load_and_scale_image(__file__,'information.png',size=15))
        bottom_row.addWidget(self.trackInfo_btn)

        # Center the bottom row buttons
        bottom_row_frame = QFrame()
        bottom_row_frame.setLayout(bottom_row)
        bottom_row.setAlignment(Qt.AlignCenter)
        playback_controls_layout.addWidget(bottom_row_frame)
        
        return playback_controls_layout

# --- INDEPENDENT EXECUTION BLOCK ---

if __name__ == '__main__':
    # --- CONFIGURATION ---
    TARGET_VIDEO_PATH = "/Users/gibreel/Downloads/DJ Khaled - I'm On One (Explicit Version) ft. Drake, Rick Ross, Lil Wayne.mp4"
    
    # 1. Setup
    app = QApplication(sys.argv)
    window = VideoPlayerWindow(parent=None)
    
    # 2. Mock VLC and Playback Logic
    if VLC_AVAILABLE:
        try:
            # a. Initialize VLC with macOS-stable options to prevent SegFault/Bus Error
            instance = vlc.Instance('--vout=macosx', '--no-sub-autodetect-file', '--no-video-title-show')
            player = instance.media_player_new()

            # b. Define the playback function
            def start_playback():
                if player.is_playing():
                    player.pause()
                    return

                if not os.path.exists(TARGET_VIDEO_PATH):
                    QMessageBox.critical(window, "File Not Found", f"Video file not found at: {TARGET_VIDEO_PATH}")
                    return

                # i. Attach VLC output (The macOS FIX)
                # Ensure the window is shown and events processed for a valid native handle
                window.show()
                QtWidgets.QApplication.instance().processEvents() 

                video_widget = window.video_view
                
                if sys.platform == 'darwin': # macOS
                    # Use sip.unwrapinstance to get the raw C++ NSView pointer
                    native_handle = unwrapinstance(video_widget)
                    player.set_nsobject(native_handle)
                elif sys.platform == 'win32': # Windows
                    player.set_hwnd(video_widget.winId())
                elif sys.platform.startswith('linux'): # Linux
                    player.set_xwindow(video_widget.winId())
                
                # ii. Set and Play Media
                media = instance.media_new(TARGET_VIDEO_PATH)
                player.set_media(media)
                player.play()
                
            # c. Connect Play/Pause button to start playback
            window.playPause_track_btn.clicked.connect(start_playback)
            
        except Exception as e:
            QMessageBox.critical(window, "VLC Initialization Error", f"Failed to initialize VLC: {e}. Showing UI only.")
            
    # 3. Show Window and Start Loop
    window.show()
    sys.exit(app.exec_())