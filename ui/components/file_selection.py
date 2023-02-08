import os

from PyQt6.QtWidgets import QFileDialog, QWidget, QHBoxLayout, QPushButton, QLabel

from automation.store import Store
from utils.save_config import SaveConfig


class FileSelection(QWidget):
    def __init__(self, file_type="PDF"):
        super().__init__()

        self.selected_file_name = ""
        self.file_folder = ""

        self.layout = QHBoxLayout()
        self.dialogButton = QPushButton("Auswahl...")
        self.dialogButton.clicked.connect(self.get_pdf_file if file_type == "PDF" else self.get_fbt_file)

        self.layout.addWidget(self.dialogButton)
        self.selected_file_label = QLabel()
        self.layout.addWidget(self.selected_file_label)
        self.setLayout(self.layout)

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

    def file_path(self):
        return self.file_folder + "/" + self.selected_file_name

    def reset(self):
        self.selected_file_name = ""
        self.file_folder = ""
        self.selected_file_label.setText("")
