import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
import os
import json

class ThemeManager:
    def __init__(self, ui_file_path):
        """
        Initializes the ThemeManager, storing the path to the UI file 
        (kgm_media_player.py) to resolve relative paths for QSS and JSON.
        """
        self.base_dir = os.path.dirname(ui_file_path)

    def _hex_to_rgb(self, hex_color):
        """Helper to convert #RRGGBB to an (R, G, B) tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def load_and_apply_theme(self, theme_json_filename="default_light.json"):
        
        app = qtw.QApplication.instance()
        if not app: 
            print("ERROR: QApplication instance not available.")
            return

        # Define the file paths using the stored base_dir
        qss_template_path = os.path.join(self.base_dir, 'styles.qss')
        theme_file_path = os.path.join(self.base_dir, 'themes', theme_json_filename)
        
        try:
            # 1. Read Theme Colors (JSON)
            with open(theme_file_path, 'r') as f:
                theme_data = json.load(f)
            
            # 2. Read QSS Template
            with open(qss_template_path, 'r') as f:
                qss_content = f.read()

            colors = theme_data['colors']
            final_qss = qss_content
            
            # 3. Perform Substitution
            for key, value in colors.items():
                final_qss = final_qss.replace(f"__{key.upper()}__", value)
                
                # Handle special transparent color for highlights
                if key == "highlight_color":
                    r, g, b = self._hex_to_rgb(value)
                    rgba_val = f"rgba({r}, {g}, {b}, 0.15)"
                    final_qss = final_qss.replace(f"__{key.upper()}_TRANSPARENT__", rgba_val)

            # 4. Apply Final Styles
            app.setStyleSheet(final_qss)
            
            # 5. Apply QPalette for system consistency (e.g., dialogs)
            dark_palette = qtg.QPalette()
            dark_palette.setColor(qtg.QPalette.Window, qtg.QColor(colors['theme_background']))
            dark_palette.setColor(qtg.QPalette.Text, qtg.QColor(colors['text_color']))
            dark_palette.setColor(qtg.QPalette.Highlight, qtg.QColor(colors['highlight_color']))
            dark_palette.setColor(qtg.QPalette.Highlight, qtg.QColor(colors['sidebar_background']))
            dark_palette.setColor(qtg.QPalette.Highlight, qtg.QColor(colors['content_background']))
            dark_palette.setColor(qtg.QPalette.Highlight, qtg.QColor(colors['foreground_color']))
            dark_palette.setColor(qtg.QPalette.Highlight, qtg.QColor(colors['highlight_color']))
            dark_palette.setColor(qtg.QPalette.Highlight, qtg.QColor(colors['text_color']))
            app.setPalette(dark_palette)


        except (FileNotFoundError, KeyError) as e:
            print(f"Error loading theme: {e}. Theme files required for loading.")
            # Do NOT exit. Allow the app to start with system default look.