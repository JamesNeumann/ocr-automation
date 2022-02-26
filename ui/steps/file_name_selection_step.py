import os.path

from PyQt6.QtWidgets import QFormLayout, QLineEdit

from ui.components.folder_selection import FolderSelection
from ui.steps.step import Step


class FileNameSelectionStep(Step):
    def __init__(self, *, text: str, previous_text="Zurück", previous_callback=None, next_text="Weiter",
                 next_callback=None, detail: str = ""):
        super().__init__(text=text,
                         previous_text=previous_text,
                         previous_callback=previous_callback,
                         next_text=next_text,
                         next_callback=next_callback, detail=detail)

        self.folder_selection = FolderSelection()
        self.layout.addWidget(self.folder_selection, 2, 0, 1, 4)

        self.file_name_field = QLineEdit()

        self.form = QFormLayout()
        self.form.addRow("Dateiname", self.file_name_field)
        self.layout.addLayout(self.form, 4, 0, 1, 4)

        self.previous_name = ""

    def reset(self):
        self.folder_selection.reset()
        self.file_name_field.setText("")

    def set_previous_name(self, name: str):
        self.previous_name = name
        self.file_name_field.setText(os.path.splitext(self.previous_name)[0])
