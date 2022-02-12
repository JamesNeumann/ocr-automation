from PyQt6.QtCore import pyqtSignal

from ui.file_selection import FileSelection
from ui.progress_bar import ProgressBar
from ui.steps.step import Step


class FileSelectionStep(Step):
    def __init__(self, *, text: str, previous_text="Zurück", previous_callback=None, next_text="Weiter",
                 next_callback=None, detail: str = ""):
        super().__init__(text=text,
                         previous_text=previous_text,
                         previous_callback=previous_callback,
                         next_text=next_text,
                         next_callback=next_callback, detail=detail)

        self.file_selection = FileSelection()
        self.layout.addWidget(self.file_selection, 2, 0, 2, 4)
        self.progress_bar = ProgressBar()
        self.progress_bar.hide()
        self.layout.addWidget(self.progress_bar, 3, 0, 3, 4)
