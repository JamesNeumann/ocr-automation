from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QProgressBar


class ProgressBar(QProgressBar, QThread):
    def __init__(self, text_visible=True, parent=None):
        super().__init__(parent)
        self.setMaximum(100)
        self._active = False
        self.setTextVisible(text_visible)
        self.setValue(0)

    def update_bar(self, value):
        self.setValue(value)
