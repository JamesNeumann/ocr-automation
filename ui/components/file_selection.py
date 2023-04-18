import os

from PyQt6.QtWidgets import QFileDialog, QWidget, QHBoxLayout, QPushButton, QLabel
from enum import IntEnum
from typing import Callable, Optional

from automation.store import Store
from utils.save_config import SaveConfig


class FileType(IntEnum):
    PDF = 0
    FBT = 1
    XLSX = 2


class FileSelection(QWidget):
    def __init__(
        self,
        file_type: FileType = FileType.PDF,
        button_text="Auswahl...",
        select_callback: Optional[Callable[[str], None]] = None,
    ):
        super().__init__()

        self.selected_file_name = ""
        self.file_folder = ""
        self.file_type = file_type
        self.select_callback = select_callback

        self.layout = QHBoxLayout()
        self.dialogButton = QPushButton(button_text)
        self.dialogButton.clicked.connect(self.get_file)

        self.layout.addWidget(self.dialogButton)
        self.selected_file_label = QLabel()
        self.layout.addWidget(self.selected_file_label)
        self.setLayout(self.layout)

    def get_file(self):
        if self.file_type == FileType.PDF:
            full_file_path = self.get_pdf_file()
        elif self.file_type == FileType.FBT:
            full_file_path = self.get_fbt_file()
        else:
            full_file_path = self.get_xlsx_file()

        if self.select_callback is not None:
            self.select_callback(full_file_path)

    def get_xlsx_file(self):
        path = SaveConfig.get_default_save_location()
        full_file_path = QFileDialog.getOpenFileName(
            self,
            directory=path,
            caption="Wähle eine Excel-Datei",
            filter="Excel-Dateien (*.xlsx)",
        )
        return full_file_path[0]

    def get_pdf_file(self):
        path = SaveConfig.get_default_save_location()
        full_file_path = QFileDialog.getOpenFileName(
            self, directory=path, caption="Wähle eine PDF", filter="PDF-Dateien (*.pdf)"
        )[0]
        if full_file_path != "":
            self.selected_file_name = os.path.basename(full_file_path)
            self.file_folder = os.path.dirname(full_file_path)
            # SaveConfig.save_folder_path(self.file_folder)
            SaveConfig.update_default_save_location(self.file_folder)
            self.selected_file_label.setText(self.selected_file_name)

        Store.SELECTED_FILE_PATH = os.path.abspath(self.file_path())
        return full_file_path

    def get_fbt_file(self):
        path = os.path.join(os.path.abspath(os.curdir), "Fraktur")
        full_file_path = QFileDialog.getOpenFileName(
            self, directory=path, caption="Wähle die Frakturmuster Datei"
        )[0]
        if full_file_path != "":
            self.selected_file_name = os.path.basename(full_file_path)
            self.file_folder = os.path.dirname(full_file_path)
            self.selected_file_label.setText(self.selected_file_name)

        Store.FBT_FILE_PATH = os.path.abspath(self.file_path())
        return full_file_path

    def file_path(self):
        return self.file_folder + "/" + self.selected_file_name

    def reset(self):
        self.selected_file_name = ""
        self.file_folder = ""
        self.selected_file_label.setText("")
