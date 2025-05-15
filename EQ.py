from PyQt5 import QtWidgets, uic
import vlc

class EqualizerWindow(QtWidgets.QWidget):
    def __init__(self, vlc_player):
        super().__init__()
        uic.loadUi("EQ.ui", self)
        self.player = vlc_player  # store vlc player instance

        self.sliders = [
            self.slider_60, self.slider_170, self.slider_310, self.slider_600,
            self.slider_1000, self.slider_3000, self.slider_6000,
            self.slider_12000, self.slider_14000, self.slider_16000,
        ]

        self.apply_btn.clicked.connect(self.apply_eq)
        self.reset_btn.clicked.connect(self.reset_eq)
        self.save_btn.clicked.connect(self.save_preset)
        self.load_btn.clicked.connect(self.load_preset)

    def apply_eq(self):
        eq = vlc.AudioEqualizer()
        for i, slider in enumerate(self.sliders):
            val = slider.value()
            eq.set_amp_at_index(float(val), i)
        self.player.set_equalizer(eq)

    def reset_eq(self):
        for s in self.sliders:
            s.setValue(0)
        self.apply_eq()  # apply reset immediately

    def save_preset(self):
        from database import save_eq_preset
        values = [s.value() for s in self.sliders]
        name, ok = QtWidgets.QInputDialog.getText(self, "Save Preset", "Preset name:")
        if ok and name:
            save_eq_preset(name, values)

    def load_preset(self):
        from database import get_eq_presets
        presets = get_eq_presets()
        if not presets:
            return
        name, ok = QtWidgets.QInputDialog.getItem(self, "Load Preset", "Select preset:", presets.keys(), 0, False)
        if ok and name in presets:
            for slider, val in zip(self.sliders, presets[name]):
                slider.setValue(int(round(val)))
            self.apply_eq()  # apply loaded preset immediately
