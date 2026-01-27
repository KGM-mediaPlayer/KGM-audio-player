import PyQt5.QtGui as qtg
import PyQt5.QtCore as qtc
import os
import sys

def get_asset_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, 'assets', filename)
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'frontend', 'assets', filename)

def create_svg_icon(svg_filename, size=24):
    try:
        path = get_asset_path(svg_filename)
        pixmap = qtg.QPixmap(path)
        
        if pixmap.isNull():
            print(f"Warning: Could not load icon from {path}")
            return qtg.QIcon()
        
        scaled_pixmap = pixmap.scaled(
            size, size,
            qtc.Qt.KeepAspectRatio,
            qtc.Qt.SmoothTransformation
        )
        return qtg.QIcon(scaled_pixmap)
    except Exception as e:
        print(f"Error creating icon {svg_filename}: {e}")
        return qtg.QIcon()

def load_and_scale_image(filename, size=60, round_radius=0):
    path = get_asset_path(filename)
    pixmap = qtg.QPixmap(path)
    
    if not pixmap.isNull():
        scaled_pixmap = pixmap.scaled(
            size, size,
            qtc.Qt.KeepAspectRatio,
            qtc.Qt.SmoothTransformation
        )
        if round_radius > 0:
            return create_rounded_pixmap(scaled_pixmap, round_radius)
        return scaled_pixmap
    else:
        print(f"Error: Could not load image from {path}.")
        return qtg.QPixmap()

def create_rounded_pixmap(pixmap, radius):
    if pixmap.isNull():
        return qtg.QPixmap()
    size = pixmap.size()
    rounded = qtg.QPixmap(size)
    rounded.fill(qtc.Qt.transparent)
    painter = qtg.QPainter(rounded)
    painter.setRenderHint(qtg.QPainter.Antialiasing, True)
    painter.setRenderHint(qtg.QPainter.SmoothPixmapTransform, True)
    path = qtg.QPainterPath()
    rect = qtc.QRectF(0, 0, size.width(), size.height())
    path.addRoundedRect(rect, radius, radius)
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, pixmap)
    painter.end()
    return rounded