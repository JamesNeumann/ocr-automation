from typing import Callable

from PyQt6.QtWidgets import QWidget, QGroupBox, QHBoxLayout, QPushButton, QVBoxLayout

from migrate_ocr_default_error import migrate


class SpecialPdfActions(QWidget):
    def __init__(self, set_metadata_callback: Callable, read_ocr_callback: Callable):
        super().__init__()
        self.parent_layout = QVBoxLayout()

        self.group_box = QGroupBox("Spezielle Aktionen")

        self.hbox_layout = QHBoxLayout()

        self.set_metadata_button = QPushButton("Metadaten setzen und speichern")
        self.set_metadata_button.clicked.connect(set_metadata_callback)
        self.set_metadata_button.setStyleSheet("padding: 10px;")

        self.read_ocr_button = QPushButton("OCR aus PDF einlesen")
        self.read_ocr_button.clicked.connect(read_ocr_callback)
        self.read_ocr_button.setStyleSheet("padding: 10px;")

        self.hbox_layout.addWidget(self.set_metadata_button)
        self.hbox_layout.addWidget(self.read_ocr_button)

        self.group_box.setLayout(self.hbox_layout)

        self.parent_layout.addWidget(self.group_box)
        self.setLayout(self.parent_layout)
