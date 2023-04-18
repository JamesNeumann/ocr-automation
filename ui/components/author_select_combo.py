from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6.QtSql import QSqlQueryModel, QSqlDatabase

from ui.components.extended_combo import ExtendedCombo
from utils.db_connection import DBConnection


class AuthorSelectCombo(QWidget):
    def __init__(self, parent=None) -> None:
        super(AuthorSelectCombo, self).__init__(parent)
        self.combo = ExtendedCombo()
        self.con = DBConnection()

    def init(self):
        if not self.con.con.isOpen():
            self.con.con.open()
        model = QSqlQueryModel(self)
        model.setQuery(
            """SELECT IFNULL("Nachname", '?') || ', '  || IFNULL("Vorname", '?') || ' ' || CASE WHEN Geburtsjahr IS NULL AND Todesjahr IS NULL THEN '(?)' WHEN Todesjahr IS NULL THEN '(*' || Geburtsjahr || ')' WHEN Geburtsjahr IS NULL THEN '(† ' || Todesjahr || ')' ELSE '(' || Geburtsjahr || '-' || Todesjahr || ')' END || IFNULL(', ' || "Link", '') || IFNULL(' [' || "Zusatzinformationen (mit Semikolon trenn)" || ']', '') AS Gesamt FROM authors ORDER BY Gesamt;"""
        )

        self.combo.setModel(model)
        self.combo.setModelColumn(0)
