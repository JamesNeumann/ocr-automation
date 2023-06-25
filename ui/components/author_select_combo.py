from PyQt6.QtWidgets import QWidget, QPushButton, QHBoxLayout
from PyQt6.QtSql import QSqlQueryModel, QSqlQuery
from typing import Optional

from ui.components.author_input_dialog import InputDialog
from ui.components.extended_combo import ExtendedCombo
from utils.db_connection import DBConnection
from utils.console import console


class AuthorSelectCombo(QWidget):
    def __init__(self, show_add_button: bool = True, parent=None) -> None:
        super(AuthorSelectCombo, self).__init__(parent)

        self.parent_layout = QHBoxLayout()

        self.combo = ExtendedCombo()
        self.parent_layout.addWidget(self.combo)

        if show_add_button:
            self.open_dialog_button = QPushButton("Autor hinzufügen")
            self.input_dialog = InputDialog()
            self.open_dialog_button.clicked.connect(self.open_dialog)
            self.parent_layout.addWidget(self.open_dialog_button)
        self.con = DBConnection()
        self.model: Optional[QSqlQueryModel] = None
        self.callbacks = []

    def open_dialog(self):
        if self.input_dialog.exec():
            if self.input_dialog.is_valid():
                (
                    firstname,
                    lastname,
                    birth_year,
                    death_year,
                    link,
                    additional_information,
                ) = self.input_dialog.get_inputs()
                query = QSqlQuery()
                query.prepare(
                    """INSERT INTO authors ("Nachname", "Vorname", "Geburtsjahr", "Todesjahr", "Link", 
                "Zusatzinformationen (mit Semikolon trenn)") VALUES (:lastname, :firstname, :birth_year,
                :death_year, :link, :additional_information)"""
                )
                query.bindValue(":lastname", None if lastname == "" else lastname)
                query.bindValue(":firstname", None if firstname == "" else firstname)
                query.bindValue(":birth_year", None if birth_year == "" else birth_year)
                query.bindValue(":death_year", None if death_year == "" else death_year)
                query.bindValue(":link", None if link == "" else link)
                query.bindValue(
                    ":additional_information",
                    None if additional_information == "" else additional_information,
                )
                query.exec()
                if query.lastError().text() != "":
                    console.log(query.lastError().text())
                self.init()
                for callback in self.callbacks:
                    callback()
                # if self.model is not None:
                #    self.model.setQuery(self.model.query())

    def init(self):
        if not self.con.con.isOpen():
            self.con.con.open()
        self.model = QSqlQueryModel(self)
        self.model.setQuery(
            """SELECT IFNULL("Nachname", '?') || ', '  || IFNULL("Vorname", '?') || ' ' || CASE WHEN Geburtsjahr IS 
            NULL AND Todesjahr IS NULL THEN '(?)' WHEN Todesjahr IS NULL THEN '(*' || Geburtsjahr || ')' WHEN 
            Geburtsjahr IS NULL THEN '(† ' || Todesjahr || ')' ELSE '(' || Geburtsjahr || '-' || Todesjahr || ')' END 
            || IFNULL(', ' || "Link", '') || IFNULL(' [' || "Zusatzinformationen (mit Semikolon trenn)" || ']', 
            '') AS Gesamt FROM authors ORDER BY Gesamt;"""
        )

        self.combo.setModel(self.model)
        self.combo.setModelColumn(0)
