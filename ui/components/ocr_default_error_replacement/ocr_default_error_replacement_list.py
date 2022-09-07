from typing import Dict

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
)

from ui.components.ocr_default_error_replacement.ocr_default_error_replacement_list_item import (
    OcrDefaultErrorReplacementListItem,
)
from utils.save_config import SaveConfig


class OcrDefaultErrorReplacementList(QWidget):
    def __init__(
        self, edit_callback=None, delete_callback=None, create_new_callback=None
    ):
        super(OcrDefaultErrorReplacementList, self).__init__()

        self.edit_callback = edit_callback
        self.delete_callback = delete_callback
        self.create_new_callback = create_new_callback

        self.layout = QGridLayout()

        header_layout = QHBoxLayout()
        header_label = QLabel("<h1>Standardfehlerlisten</h1>")
        add_new_replacement_button = QPushButton("Neue Standardfehlerliste hinzufügen")
        add_new_replacement_button.clicked.connect(create_new_callback)
        header_layout.addWidget(header_label)
        header_layout.addWidget(add_new_replacement_button)

        self.layout.addLayout(header_layout, 0, 1, 1, 1)

        self.error_list = QListWidget()
        self._generate_list()
        self.layout.addWidget(self.error_list, 1, 1, 1, 1)
        self.setLayout(self.layout)

    def _generate_list(self):
        for replacement_map in SaveConfig.get_default_error_replacement_maps():
            item = QListWidgetItem(self.error_list)
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.error_list.addItem(item)

            row = OcrDefaultErrorReplacementListItem(
                replacement_map,
                edit_pressed_callback=self.edit_button_pressed,
                delete_pressed_callback=self.delete_button_pressed,
            )
            item.setSizeHint(row.minimumSizeHint())
            self.error_list.setItemWidget(item, row)

    def reload(self):
        self.error_list.clear()
        self._generate_list()

    def edit_button_pressed(self, replacement_map: Dict):
        self.edit_callback(replacement_map)

    def delete_button_pressed(self, replacement_map: Dict):
        self.delete_callback(replacement_map)
