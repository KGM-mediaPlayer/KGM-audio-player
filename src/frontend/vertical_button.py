import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
import PyQt5.QtCore as qtc

class VerticalButton(qtw.QPushButton):
    """A custom QPushButton that rotates its text and icons 90 degrees clockwise."""
    
    def paintEvent(self, event):
        painter = qtg.QPainter(self)
        
        # Initialize style options to handle QSS drawing (border, background)
        option = qtw.QStyleOptionButton()
        self.initStyleOption(option)
        
        # Apply the rotation transformation for all content (text and icon)
        painter.translate(self.rect().center())
        painter.rotate(90)
        painter.translate(-self.rect().center())
        
        rect = self.rect()
        text_flags = qtc.Qt.AlignCenter | qtc.Qt.TextDontClip 
        
        # 1. Draw the icon (it will appear visually at the bottom, centered)
        if not option.icon.isNull():
            icon_size = option.iconSize
            
            # Position icon near the bottom edge (which is the right edge pre-rotation)
            icon_rect = qtc.QRect(
                (rect.width() - icon_size.width()) // 2,
                rect.height() - icon_size.height() - 5,
                icon_size.width(),
                icon_size.height()
            )
            
            # FIX: Use the 5-argument overload, including the QTC.Qt.AlignCenter flag.
            option.icon.paint(
                painter, 
                icon_rect, 
                qtc.Qt.AlignCenter,  
                qtg.QIcon.Normal, 
                qtg.QIcon.Off
            )

        # 2. Draw the rotated text ("About")
        painter.drawText(rect, text_flags, option.text)
        
        painter.end()
        
        # Call the base class paintEvent to draw borders/background defined in QSS
        super().paintEvent(event)