from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QRadioButton

from ui.components.checkable_combo_box import CheckableComboBox
from ui.steps.step import Step
from utils.ocr_languages import predefined_ocr_languages, custom_languages


class OcrLanguageSelectionStep(Step):
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
        self.container_layout = QVBoxLayout()

        self.pre_defined_languages_group_box = QGroupBox("Standard OCR-Sprachen")

        self.pre_defined_languages_layout = QVBoxLayout()

        # self.pre_defined_languages = ['Altdeutsch', 'Deutsch', 'Deutsch (Neue Rechtschreibung)', 'Englisch',
        #                               'Französisch', 'Italienisch', 'Spanisch']

        # deutsch = "Deutsch;Englisch;Französisch;Lateinisch;"
        # altdeutsch = "Altdeutsch;Englisch;Französisch;Lateinisch;"
        # france = "Französisch;Deutsch;Englisch;Lateinisch;"
        # deutsch_new = "Deutsch (Neue Rechtschreibung);Französisch;Englisch;Lateinisch;"
        # english = "Englisch;Französisch;Deutsch;Lateinisch;"
        # italian = "Italienisch;Englisch;Französisch;Deutsch;Lateinisch;"
        # spanish = "Spanisch;Englisch;Französisch;Deutsch;Lateinisch;"

        # self.pre_defined_languages = [deutsch, altdeutsch, france, deutsch_new, english, italian, spanish]

        self.pre_defined_languages = [
            ";".join(language) for language in predefined_ocr_languages
        ]

        for index, language in enumerate(self.pre_defined_languages):
            button = QRadioButton(language)
            if index == 0:
                button.setChecked(True)
            self.pre_defined_languages_layout.addWidget(button)

        self.pre_defined_languages_group_box.setLayout(
            self.pre_defined_languages_layout
        )

        self.container_layout.addWidget(self.pre_defined_languages_group_box)

        self.custom_language_selection_group_box = QGroupBox(
            "Wähle eine andere Sprachen"
        )
        self.custom_language_layout = QVBoxLayout()
        self.custom_languages = custom_languages

        self.checkable_combo_box = CheckableComboBox()
        self.checkable_combo_box.addItems(self.custom_languages)
        self.checkable_combo_box.item_checked.connect(
            lambda items: self.uncheck_predefined_languages()
            if len(items) > 0
            else self.check_first_predefined_language()
        )
        self.custom_language_layout.addWidget(self.checkable_combo_box)

        self.custom_language_selection_group_box.setLayout(self.custom_language_layout)
        self.container_layout.addWidget(self.custom_language_selection_group_box)
        self.layout.addLayout(self.container_layout, 2, 0, 2, 4)

    def uncheck_predefined_languages(self):
        for button in self.pre_defined_languages_group_box.findChildren(QRadioButton):
            button.setAutoExclusive(False)
            button.setChecked(False)
            button.setAutoExclusive(True)

    def check_first_predefined_language(self):
        button = self.pre_defined_languages_group_box.findChildren(QRadioButton)[0]
        button.setAutoExclusive(False)
        button.setChecked(True)
        button.setAutoExclusive(True)

    def get_selected_language(self):
        custom_languages = self.checkable_combo_box.currentData()
        if len(custom_languages) > 0:
            return ";".join(custom_languages) + ";"

        for button in self.pre_defined_languages_group_box.findChildren(QRadioButton):
            if button.isChecked():
                return button.text()

    def reset(self):
        self.checkable_combo_box.reset()
