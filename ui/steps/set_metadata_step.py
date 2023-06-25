from PyQt6.QtWidgets import QFormLayout, QLineEdit

from ui.steps.step import Step
from utils.console import console
from utils.set_metadata import Metadata
from ui.components.author_select_combo import AuthorSelectCombo


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
        self.topic_field = QLineEdit()
        self.first_author_select = AuthorSelectCombo()
        self.second_author_select = AuthorSelectCombo(show_add_button=False)
        self.third_author_select = AuthorSelectCombo(show_add_button=False)

        self.first_author_select.callbacks.append(self.second_author_select.init)
        self.first_author_select.callbacks.append(self.third_author_select.init)

        self.form = QFormLayout()
        self.form.addRow("Titel", self.title_field)
        self.form.addRow("1. Verfasser", self.first_author_select.parent_layout)
        self.form.addRow("2. Verfasser", self.second_author_select.parent_layout)
        self.form.addRow("3. Verfasser", self.third_author_select.parent_layout)
        self.form.addRow("Thema", self.topic_field)
        self.layout.addLayout(self.form, 3, 0, 1, 4)

    def init(self):
        self.first_author_select.init()
        self.second_author_select.init()
        self.third_author_select.init()

    def reset(self):
        self.title_field.setText("")
        self.topic_field.setText("")

    def get_metadata(self):
        authors = []
        first_author = self.first_author_select.combo.currentText().strip()
        if first_author != "":
            authors.append(first_author)
        second_author = self.second_author_select.combo.currentText().strip()
        if second_author != "":
            authors.append(second_author)
        third_author = self.third_author_select.combo.currentText().strip()
        if third_author != "":
            authors.append(third_author)
        return Metadata(
            self.title_field.text(),
            "; ".join(authors),
            self.topic_field.text(),
        )

    def set_title(self, title: str):
        self.title_field.setText(title)
