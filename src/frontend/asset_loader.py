import PyQt5.QtGui as qtg
import PyQt5.QtCore as qtc
import os

# --- Path Resolution ---
def get_asset_path(calling_file_path, filename):
    """
    Resolves the absolute path for an asset file relative to the caller's directory.
    
    :param calling_file_path: Pass __file__ from the importing module (e.g., kgm_media_player.py).
    :param filename: The name of the file inside the 'assets' folder (e.g., 'play.svg').
    :return: Absolute path string.
    """
    base_dir = os.path.dirname(calling_file_path) 
    return os.path.join(base_dir, 'assets', filename)

# --- Icon Creation ---
def create_svg_icon(calling_file_path, svg_filename, size=24):
    """
    Creates a QIcon from an SVG file, handling path resolution and size.
    """
    try:
        path = get_asset_path(calling_file_path, svg_filename)
        pixmap = qtg.QPixmap(path)
        
        if pixmap.isNull():
            print(f"Warning: Could not load SVG from {path}. Check file path.")
            return qtg.QIcon()
        
        # Scale the pixmap before creating the icon
        scaled_pixmap = pixmap.scaled(
            size, size,
            qtc.Qt.KeepAspectRatio,
            qtc.Qt.SmoothTransformation
        )
        
        return qtg.QIcon(scaled_pixmap)

    except Exception as e:
        print(f"Error creating icon {svg_filename}: {e}")
        return qtg.QIcon()

# In src/frontend/asset_loader.py

def create_rounded_pixmap(pixmap, radius):
    """
    Takes a square QPixmap and clips it to a rounded shape using QPainter.
    
    :param pixmap: The source QPixmap (already scaled to the final size).
    :param radius: The border radius in pixels (e.g., 10 for 10px rounded corners).
    :return: A new QPixmap with rounded corners.
    """
    if pixmap.isNull():
        return qtg.QPixmap()

    size = pixmap.size()
    
    # 1. Create a new pixmap with transparency
    # We use a format that supports the alpha channel
    rounded = qtg.QPixmap(size)
    rounded.fill(qtc.Qt.transparent)
    
    # 2. Set up the painter
    painter = qtg.QPainter(rounded)
    painter.setRenderHint(qtg.QPainter.Antialiasing, True)
    painter.setRenderHint(qtg.QPainter.SmoothPixmapTransform, True)
    
    # 3. Define the rounded rectangle clip path
    path = qtg.QPainterPath()
    rect = qtc.QRectF(0, 0, size.width(), size.height())
    path.addRoundedRect(rect, radius, radius)
    
    # 4. Apply the path as a clip mask
    painter.setClipPath(path)
    
    # 5. Draw the original pixmap onto the new rounded pixmap
    painter.drawPixmap(0, 0, pixmap)
    
    # 6. Finalize painting
    painter.end()
    
    return rounded

# --- Image Loading (for Album Art) ---
# In src/frontend/asset_loader.py (Modified load_and_scale_image)

def load_and_scale_image(calling_file_path, filename, size=60, round_radius=0):
    """
    Loads, scales, and returns a QPixmap. Optionally rounds the corners.
    
    :param round_radius: Radius for clipping, set > 0 to enable clipping.
    """
    path = get_asset_path(calling_file_path, filename)
    pixmap = qtg.QPixmap(path)
    
    if not pixmap.isNull():
        # Scale first
        scaled_pixmap = pixmap.scaled(
            size, size,
            qtc.Qt.KeepAspectRatio,
            qtc.Qt.SmoothTransformation
        )
        
        # New: Clip and round the corners if a radius is provided
        if round_radius > 0:
            return create_rounded_pixmap(scaled_pixmap, round_radius)
            
        return scaled_pixmap
    else:
        print(f"Error: Could not load image from {path}.")
        return qtg.QPixmap()