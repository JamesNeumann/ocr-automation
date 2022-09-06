from typing import Dict

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton


class OcrDefaultErrorReplacementListItem(QWidget):
    def __init__(
        self,
        replacement_map: Dict,
        parent=None,
        edit_pressed_callback=None,
        delete_pressed_callback=None,
    ):
        super(OcrDefaultErrorReplacementListItem, self).__init__(parent)

        self.row = QHBoxLayout()

        self.name_label = QLabel(replacement_map["name"])
        self.element_amount_label = QLabel(
            str(len(replacement_map["map"])) + " Elemente"
        )

        self.button_layout = QHBoxLayout()

        self.edit_button = QPushButton("Bearbeiten")
        self.edit_button.clicked.connect(lambda: edit_pressed_callback(replacement_map))

        self.delete_button = QPushButton("Löschen")
        self.delete_button.clicked.connect(
            lambda: delete_pressed_callback(replacement_map)
        )

        self.button_layout.addWidget(self.edit_button)
        self.button_layout.addWidget(self.delete_button)

        self.row.addWidget(self.name_label)
        self.row.addWidget(self.element_amount_label)
        self.row.addLayout(self.button_layout)

        self.setLayout(self.row)
