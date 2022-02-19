from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFileDialog, QLabel


class FolderSelection(QWidget):
    def __init__(self):
        super().__init__()

        self.selected_folder = ""

        self.layout = QHBoxLayout()
        self.dialogButton = QPushButton("Wähle Ordner...")
        self.dialogButton.clicked.connect(self.get_folder)

        self.layout.addWidget(self.dialogButton)
        self.selected_folder_label = QLabel()
        self.layout.addWidget(self.selected_folder_label)
        self.setLayout(self.layout)

    def get_folder(self):
        self.selected_folder = QFileDialog.getExistingDirectory(self, "Wähle einen Ordner")
        self.selected_folder_label.setText(self.selected_folder)

