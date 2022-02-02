from PyQt6.QtWidgets import QProgressBar


class ProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximum(100)
        self._active = False

    def update_bar(self, value):
        self.setValue(value)
