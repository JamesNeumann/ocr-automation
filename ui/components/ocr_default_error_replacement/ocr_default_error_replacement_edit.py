from typing import Dict

from PyQt6.QtWidgets import QWidget, QGridLayout, QPushButton, QHBoxLayout, QLineEdit

from ui.components.ocr_default_error_replacement.ocr_default_error_replacement_table import (
    OcrDefaultErrorReplacementTable,
)


class OcrDefaultErrorReplacementEdit(QWidget):
    def __init__(self, back_callback=None, save_callback=None):
        super(OcrDefaultErrorReplacementEdit, self).__init__()
        self.layout = QGridLayout()

        header_layout = QHBoxLayout()
        self.header_label = QLineEdit()

        font = self.header_label.font()
        font.setPointSize(15)
        self.header_label.setFont(font)

        header_layout.addWidget(self.header_label)

        self.layout.addLayout(header_layout, 0, 1, 1, 1)
        self.setLayout(self.layout)

        self.table_layout = QHBoxLayout()
        self.add_row_button = QPushButton("Eintrag hinzufügen")
        self.add_row_button.clicked.connect(self.add_row)
        self.table = OcrDefaultErrorReplacementTable()
        self.table_layout.addWidget(self.table)
        self.table_layout.addWidget(self.add_row_button)
        self.layout.addLayout(self.table_layout, 1, 1, 1, 1)

        self.button_layout = QHBoxLayout()

        self.save_button = QPushButton("Speichern")
        self.save_button.clicked.connect(
            lambda: save_callback(self.get_updated_replacement_map())
        )

        self.back_button = QPushButton("Zurück")
        self.back_button.clicked.connect(back_callback)

        self.button_layout.addWidget(self.back_button)
        self.button_layout.addWidget(self.save_button)
        self.layout.addLayout(self.button_layout, 2, 1, 1, 1)

        self.current_replacement_map = None

    def set_replacement_map(self, replacement_map: Dict):
        self.current_replacement_map = replacement_map
        self.header_label.setText(self.current_replacement_map["name"])
        self.table.update_model(self.current_replacement_map)

    def get_updated_replacement_map(self):
        self.current_replacement_map["name"] = self.header_label.text()
        self.current_replacement_map["map"] = self.table.get_replacement_map_values()
        return self.current_replacement_map

    def add_row(self):
        self.table.insert_row()
