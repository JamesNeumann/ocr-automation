from PyQt6.QtWidgets import QDialog, QLineEdit, QDialogButtonBox, QFormLayout


class InputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.firstname = QLineEdit(self)
        self.lastname = QLineEdit(self)
        self.birth_year = QLineEdit(self)
        self.death_year = QLineEdit(self)
        self.link = QLineEdit(self)
        self.additional_information = QLineEdit(self)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )

        layout = QFormLayout(self)
        layout.addRow("Vorname", self.firstname)
        layout.addRow("Nachname", self.lastname)
        layout.addRow("Geburtsjahr", self.birth_year)
        layout.addRow("Todesjahr", self.death_year)
        layout.addRow("Link", self.link)
        layout.addRow("Zusatzinformationen", self.additional_information)
        self.resize(500, 200)
        layout.addWidget(button_box)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

    def get_inputs(self):
        return (
            self.firstname.text(),
            self.lastname.text(),
            self.birth_year.text(),
            self.death_year.text(),
            self.link.text(),
            self.additional_information.text(),
        )

    def is_valid(self):
        return self.firstname.text() != "" and self.lastname.text() != ""
