from PyQt6.QtSql import QSqlDatabase
from utils.save_config import SaveConfig, Config
from PyQt6.QtWidgets import QMessageBox
import os


class DBConnection(object):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBConnection, cls).__new__(cls)
            cls.con = QSqlDatabase.addDatabase("QSQLITE")
            author_folder_path = SaveConfig.get_author_db_path()

            if author_folder_path == "" or not os.path.exists(author_folder_path):
                QMessageBox.critical(
                    None,
                    "Fehler",
                    "Ordner für die Autoren Datebank existiert nicht. Bitte in den Einstellungen ändern",
                )
                return

            author_db_path = os.path.join(author_folder_path, Config.AUTHOR_DB_NAME)

            cls.con.setDatabaseName(author_db_path)

            if not cls.con.open():
                QMessageBox.critical(
                    None,
                    "Fehler",
                    "Datenbank Fehler: %s" % cls.con.lastError().databaseText(),
                )
        return cls._instance
