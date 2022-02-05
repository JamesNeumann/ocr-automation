import os

from PyQt6.QtWidgets import QFileDialog, QWidget, QHBoxLayout, QPushButton, QLabel


class FileSelection(QWidget):

    def __init__(self):
        super().__init__()

        self.selected_file_name = ""
        self.file_folder = ""

        self.layout = QHBoxLayout()
        self.dialogButton = QPushButton("Auswahl...")
        self.dialogButton.clicked.connect(self.get_pdf_file)

        self.layout.addWidget(self.dialogButton)
        self.selected_file_label = QLabel()
        self.layout.addWidget(self.selected_file_label)
        self.setLayout(self.layout)

    def get_pdf_file(self):
        path = self.file_folder if self.file_folder != "" else 'c:\\'
        full_file_path = QFileDialog.getOpenFileName(self, path, "*.pdf")[0]
        if full_file_path != "":
            self.selected_file_name = os.path.basename(full_file_path)
            self.file_folder = os.path.dirname(full_file_path)
            self.selected_file_label.setText(self.selected_file_name)

    def file_path(self):
        return self.file_folder + "/" + self.selected_file_name
