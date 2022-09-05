from typing import Dict

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget,
    QGridLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QStackedLayout,
    QTextEdit,
    QLineEdit,
)

from ui.components.default_error_replacement_table import DefaultErrorReplacementTable
from utils.console import console
from utils.save_config import SaveConfig


class ReplacementListItem(QWidget):
    def __init__(
        self,
        replacement_map: Dict,
        parent=None,
        edit_pressed_callback=None,
        delete_pressed_callback=None,
    ):
        super(ReplacementListItem, self).__init__(parent)

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


class DefaultErrorReplacementEdit(QWidget):
    def __init__(self, back_callback=None, save_callback=None):
        super(DefaultErrorReplacementEdit, self).__init__()
        self.layout = QGridLayout()

        header_layout = QHBoxLayout()
        self.header_label = QLineEdit()

        font = self.header_label.font()
        font.setPointSize(15)
        self.header_label.setFont(font)

        header_layout.addWidget(self.header_label)

        self.layout.addLayout(header_layout, 0, 1, 1, 1)
        self.setLayout(self.layout)

        self.table = DefaultErrorReplacementTable()
        self.layout.addWidget(self.table, 1, 1, 1, 1)

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


class DefaultErrorReplacementList(QWidget):
    def __init__(self, parent_callback=None):
        super(DefaultErrorReplacementList, self).__init__()
        self.layout = QGridLayout()

        header_layout = QHBoxLayout()
        header_label = QLabel("<h1>Standardfehlerlisten</h1>")
        add_new_replacement_button = QPushButton("Neue Standardfehlerliste hinzufügen")
        header_layout.addWidget(header_label)
        header_layout.addWidget(add_new_replacement_button)

        self.layout.addLayout(header_layout, 0, 1, 1, 1)

        self.setLayout(self.layout)

        self.error_list = QListWidget()

        for replacement_map in SaveConfig.get_default_error_replacement_maps():
            item = QListWidgetItem(self.error_list)
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.error_list.addItem(item)
            row = ReplacementListItem(
                replacement_map,
                edit_pressed_callback=self.edit_button_pressed,
                delete_pressed_callback=self.delete_button_pressed,
            )
            item.setSizeHint(row.minimumSizeHint())
            self.error_list.setItemWidget(item, row)

        self.layout.addWidget(self.error_list, 1, 1, 1, 1)

        self.parent_callback = parent_callback

    def edit_button_pressed(self, replacement_map: Dict):
        self.parent_callback(replacement_map)

    def delete_button_pressed(self, replacement_map: Dict):
        console.log("Delete pressed", replacement_map)


class DefaultErrorReplacementSettings(QWidget):
    def __init__(self):
        super().__init__()
        self.parent_layout = QStackedLayout()

        self.list = DefaultErrorReplacementList(self.change_to_edit)
        self.edit = DefaultErrorReplacementEdit(
            self.edit_back_button_pressed, self.edit_save_button_pressed
        )

        self.parent_layout.addWidget(self.list)
        self.parent_layout.addWidget(self.edit)

        self.setLayout(self.parent_layout)

    def change_to_edit(self, replacement_map):
        self.edit.set_replacement_map(replacement_map)
        self.parent_layout.setCurrentIndex(1)

    def edit_back_button_pressed(self):
        self.parent_layout.setCurrentIndex(0)

    def edit_save_button_pressed(self, replacement_map: Dict):
        console.log(replacement_map)
        self.parent_layout.setCurrentIndex(0)
