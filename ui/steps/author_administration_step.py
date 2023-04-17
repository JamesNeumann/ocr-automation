from config import Config
from ui.steps.step import Step
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel
from PyQt6.QtWidgets import (
    QMessageBox,
    QTableView,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QLabel,
    QPushButton,
)
from utils.console import console
from PyQt6.QtCore import Qt, QSortFilterProxyModel, QModelIndex, QTimer
import os

from utils.save_config import SaveConfig


class FilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._filter_value = None

        self.sourceModelChanged.connect(self.on_source_model_changed)

    @property
    def filter_value(self):
        return self._filter_value

    @filter_value.setter
    def filter_value(self, value):
        self._filter_value

    def on_source_model_changed(self) -> None:
        self.fetchMore(QModelIndex())

    def fetchMore(self, parent: QModelIndex) -> None:
        if not self.sourceModel().canFetchMore(parent):
            return
        self.sourceModel().fetchMore(parent)
        self.fetchMore(parent)

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        if self.filter_value is None:
            return super().filterAcceptsRow(source_row, source_parent)
        # if self.filterKeyColumn() >= 0:
        #     value = (
        #         self.sourceModel()
        #         .index(source_row, self.filterKeyColumn(), source_parent)
        #         .data(self.filterRole())
        #     )
        #     return value == self.filter_value
        for column in range(self.columnCount()):
            value = (
                self.sourceModel()
                .index(source_row, column, source_parent)
                .data(self.filterRole())
            )
            if value == self.filter_value:
                return True
        return False


class AuthorAdministrationStep(Step):
    def __init__(
        self,
        *,
        text: str,
        previous_text="Zurück",
        previous_callback=None,
        next_text="Weiter",
        next_callback=None,
        detail: str = ""
    ):
        super().__init__(
            text=text,
            previous_text=previous_text,
            previous_callback=previous_callback,
            next_text=next_text,
            next_callback=next_callback,
            detail=detail,
        )
        self.con = QSqlDatabase.addDatabase("QSQLITE")

    def init(self):
        author_folder_path = SaveConfig.get_author_db_path()

        if author_folder_path == "" or not os.path.exists(author_folder_path):
            QMessageBox.critical(
                None,
                "Fehler",
                "Ordner für die Autoren Datebank existiert nicht. Bitte in den Einstellungen ändern",
            )
            return

        author_db_path = os.path.join(author_folder_path, Config.AUTHOR_DB_NAME)

        self.con.setDatabaseName(author_db_path)

        if not self.con.open():
            QMessageBox.critical(
                None,
                "Fehler",
                "Datenbank Fehler: %s" % self.con.lastError().databaseText(),
            )

        self.model = QSqlTableModel(self)
        self.model.setTable("authors")
        self.model.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)

        self.model.setHeaderData(0, Qt.Orientation.Horizontal, "ID")
        self.model.setHeaderData(1, Qt.Orientation.Horizontal, "Vorname")
        self.model.setHeaderData(2, Qt.Orientation.Horizontal, "Nachname")
        self.model.setHeaderData(3, Qt.Orientation.Horizontal, "Geburtsjahr")
        self.model.setHeaderData(4, Qt.Orientation.Horizontal, "Todesjahr")
        self.model.setHeaderData(5, Qt.Orientation.Horizontal, "Link")
        self.model.setHeaderData(6, Qt.Orientation.Horizontal, "Zusatzinformationen")
        self.model.select()
        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.setColumnHidden(0, True)
        self.view.resizeColumnsToContents()

        self.proxy = FilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.proxy.setFilterKeyColumn(-1)
        self.view.setModel(self.proxy)

        self.author_search_layout = QHBoxLayout()
        self.author_search_label = QLabel("Suche:")

        self.author_search_input = QLineEdit()
        self.author_search_input.textEdited.connect(self.on_line_edit)

        self.author_search_layout.addWidget(self.author_search_label)
        self.author_search_layout.addWidget(self.author_search_input)

        self.author_actions_layout = QHBoxLayout()
        self.author_add_button = QPushButton("Autor hinzufügen")
        self.author_add_button.clicked.connect(self.add_row)
        self.author_delete_button = QPushButton("Ausgewählte Autoren löschen")
        self.author_delete_button.clicked.connect(self.delete_row)
        self.author_actions_layout.addWidget(self.author_add_button)
        self.author_actions_layout.addWidget(self.author_delete_button)

        self.author_layout = QVBoxLayout()
        self.author_layout.addLayout(self.author_search_layout)
        self.author_layout.addWidget(self.view)
        self.author_layout.addLayout(self.author_actions_layout)
        self.layout.addLayout(self.author_layout, 1, 0, 1, 5)

    def on_line_edit(self, value: str):
        self.proxy.setFilterFixedString(self.author_search_input.text())

    def add_row(self):
        ret = self.model.insertRow(self.model.rowCount())
        print(ret)
        if ret:
            count = self.model.rowCount() - 1
            print(count)
            self.view.selectRow(count)
            item = self.view.selectedIndexes()[0]
            self.model.setData(item, str(count))

    def delete_row(self):
        selected = self.view.selectionModel().selectedRows()
        for index in selected:
            self.model.removeRow(index.row())
        self.model.select()
        self.view.selectRow(0)

    def close(self):
        super().close()
        self.con.commit()
        self.con.close()
