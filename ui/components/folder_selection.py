from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFileDialog, QLabel

from utils.save_config import SaveConfig


class FolderSelection(QWidget):
    def __init__(self, default_folder: str):
        super().__init__()

        self.selected_folder = default_folder

        self.layout = QHBoxLayout()
        self.dialogButton = QPushButton("Wähle Ordner...")
        self.dialogButton.clicked.connect(self.get_folder)

        self.layout.addWidget(self.dialogButton)
        self.selected_folder_label = QLabel(self.selected_folder)
        self.layout.addWidget(self.selected_folder_label)
        self.setLayout(self.layout)

    def get_folder(self):
        self.selected_folder = QFileDialog.getExistingDirectory(
            self,
            directory=SaveConfig.get_default_save_location(),
            caption="Wähle einen Ordner",
        )
        self.selected_folder_label.setText(self.selected_folder)

    def set_folder(self, folder):
        self.selected_folder = folder
        self.selected_folder_label.setText(folder)

    def reset(self):
        self.selected_folder = ""
        self.selected_folder_label.setText("")
