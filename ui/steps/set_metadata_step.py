from PyQt6.QtWidgets import QFormLayout, QLineEdit

from ui.steps.step import Step
from utils.set_metadata import Metadata


class SetMetadataStep(Step):
    def __init__(
        self,
        *,
        text: str,
        previous_text="Zurück",
        previous_callback=None,
        next_text="Weiter",
        next_callback=None,
        detail: str = ""
    ):
        super().__init__(
            text=text,
            previous_text=previous_text,
            previous_callback=previous_callback,
            next_text=next_text,
            next_callback=next_callback,
            detail=detail,
        )

        self.title_field = QLineEdit()
        self.create_field = QLineEdit()
        self.theme_field = QLineEdit()

        self.form = QFormLayout()
        self.form.addRow("Titel", self.title_field)
        self.form.addRow("Verfasser", self.create_field)
        self.form.addRow("Thema", self.theme_field)
        self.layout.addLayout(self.form, 3, 0, 1, 4)

    def reset(self):
        self.title_field.setText("")
        self.create_field.setText("")
        self.theme_field.setText("")

    def get_metadata(self):
        return Metadata(
            self.title_field.text(), self.create_field.text(), self.theme_field.text()
        )

    def set_title(self, title: str):
        self.title_field.setText(title)
