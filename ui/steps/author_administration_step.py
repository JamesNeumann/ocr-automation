import os
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
from PyQt6.QtCore import Qt, QSortFilterProxyModel, QModelIndex, QTimer

from utils.db_connection import DBConnection
from utils.save_config import SaveConfig
from utils.dialog import create_dialog
from config import Config
from ui.steps.step import Step
from ui.components.file_selection import FileSelection, FileType
from utils.import_authors import import_authors


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

    def init(self):
        self.con = DBConnection()
        author_folder_path = SaveConfig.get_author_db_path()

        if author_folder_path == "" or not os.path.exists(author_folder_path):
            QMessageBox.critical(
                None,
                "Fehler",
                "Ordner für die Autoren Datebank existiert nicht. Bitte in den Einstellungen ändern",
            )
            return

        author_db_path = os.path.join(author_folder_path, Config.AUTHOR_DB_NAME)

        self.con.con.setDatabaseName(author_db_path)

        if not self.con.con.open():
            QMessageBox.critical(
                None,
                "Fehler",
                "Datenbank Fehler: %s" % self.con.con.lastError().databaseText(),
            )

        self.model = QSqlTableModel(self)
        self.model.setTable("authors")
        self.model.setSort(1, Qt.SortOrder.AscendingOrder)
        self.model.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)

        self.model.setHeaderData(0, Qt.Orientation.Horizontal, "ID")
        self.model.setHeaderData(2, Qt.Orientation.Horizontal, "Vorname")
        self.model.setHeaderData(1, Qt.Orientation.Horizontal, "Nachname")
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
        # self.view.setSortingEnabled(True)
        # self.view.sortByColumn(1, Qt.SortOrder.AscendingOrder)

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

        self.author_import_file_select = FileSelection(
            file_type=FileType.XLSX,
            button_text="Autoren importieren",
            select_callback=self.excel_file_selected,
        )

        self.author_layout = QVBoxLayout()
        self.author_layout.addLayout(self.author_search_layout)
        self.author_layout.addWidget(self.view)
        self.author_layout.addLayout(self.author_actions_layout)
        self.author_layout.addWidget(self.author_import_file_select)
        self.layout.addLayout(self.author_layout, 1, 0, 1, 5)

    def excel_file_selected(self, full_file_path: str):
        if full_file_path == "":
            return
        dialog = create_dialog(
            window_title="Importieren - Achtung",
            text="Alle Autoren in der Datenbank werden gelöscht und mit den Autoren in der Excel-Datei überschrieben. Fortfahren?",
            icon=QMessageBox.Icon.Warning,
            buttons=QMessageBox.StandardButton.Abort | QMessageBox.StandardButton.Ok,
            parent=self,
        )
        button = dialog.exec()
        if button == QMessageBox.StandardButton.Ok:
            import_authors(excel_path=full_file_path, db_path=self.con.get_db_path())
            self.init()
        else:
            self.author_import_file_select.reset()

    def on_line_edit(self, value: str):
        self.proxy.setFilterFixedString(self.author_search_input.text())

    def add_row(self):
        ret = self.model.insertRow(self.model.rowCount())
        if ret:
            count = self.model.rowCount() - 1
            self.view.selectRow(count)
            item = self.view.selectedIndexes()[0]
            self.model.setData(item, str(count))

    def delete_row(self):
        selected = self.view.selectionModel().selectedRows()
        selection_x = [self.view.model().mapToSource(index) for index in selected]
        for index in selection_x:
            self.model.removeRow(index.row())
        self.author_search_input.setText("")
        self.proxy.setFilterFixedString(self.author_search_input.text())

        self.model.select()
        self.proxy.fetchMore(QModelIndex())
        self.view.selectRow(0)

    def close(self):
        super().close()
        self.con.con.commit()
        self.con.con.close()
