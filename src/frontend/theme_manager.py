import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
import PyQt5.QtCore as qtc
import os
import json
import sys

class ThemeManager:
    def __init__(self):
        if hasattr(sys, '_MEIPASS'):
            self.base_dir = sys._MEIPASS
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def load_and_apply_theme(self, theme_json_filename="default_dark.json"):
        app = qtw.QApplication.instance()
        if not app: 
            return

        if hasattr(sys, '_MEIPASS'):
            qss_template_path = os.path.join(self.base_dir, 'styles.qss')
            theme_file_path = os.path.join(self.base_dir, 'themes', theme_json_filename)
        else:
            qss_template_path = os.path.join(self.base_dir, 'styles.qss')
            theme_file_path = os.path.join(self.base_dir, 'themes', theme_json_filename)
        
        try:
            with open(theme_file_path, 'r') as f:
                theme_data = json.load(f)
            
            with open(qss_template_path, 'r') as f:
                qss_content = f.read()

            colors = theme_data['colors']
            final_qss = qss_content
            
            for key, value in colors.items():
                final_qss = final_qss.replace(f"__{key.upper()}__", value)
                
                if key == "highlight_color":
                    r, g, b = self._hex_to_rgb(value)
                    rgba_val = f"rgba({r}, {g}, {b}, 0.15)"
                    final_qss = final_qss.replace(f"__{key.upper()}_TRANSPARENT__", rgba_val)

            app.setStyleSheet(final_qss)
            
            dark_palette = qtg.QPalette()
            dark_palette.setColor(qtg.QPalette.Window, qtg.QColor(colors['theme_background']))
            dark_palette.setColor(qtg.QPalette.WindowText, qtg.QColor(colors['text_color']))
            dark_palette.setColor(qtg.QPalette.Base, qtg.QColor(colors['content_background']))
            dark_palette.setColor(qtg.QPalette.AlternateBase, qtg.QColor(colors['sidebar_background']))
            dark_palette.setColor(qtg.QPalette.ToolTipBase, qtg.QColor(colors['text_color']))
            dark_palette.setColor(qtg.QPalette.ToolTipText, qtg.QColor(colors['text_color']))
            dark_palette.setColor(qtg.QPalette.Text, qtg.QColor(colors['text_color']))
            dark_palette.setColor(qtg.QPalette.Button, qtg.QColor(colors['sidebar_background']))
            dark_palette.setColor(qtg.QPalette.ButtonText, qtg.QColor(colors['text_color']))
            dark_palette.setColor(qtg.QPalette.BrightText, qtc.Qt.red)
            dark_palette.setColor(qtg.QPalette.Link, qtg.QColor(colors['highlight_color']))
            dark_palette.setColor(qtg.QPalette.Highlight, qtg.QColor(colors['highlight_color']))
            dark_palette.setColor(qtg.QPalette.HighlightedText, qtc.Qt.black)
            app.setPalette(dark_palette)

        except (FileNotFoundError, KeyError) as e:
            print(f"Error loading theme: {e}")