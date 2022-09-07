from typing import List, Any, Dict

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QTableView,
    QStyledItemDelegate,
    QAbstractItemView,
    QPushButton,
)


class PushButtonDelegate(QStyledItemDelegate):
    clicked = pyqtSignal(QModelIndex)

    def paint(self, painter, option, index):
        if (
            isinstance(self.parent(), QAbstractItemView)
            and self.parent().model() is index.model()
        ):
            self.parent().openPersistentEditor(index)

    def createEditor(self, parent, option, index):
        button = QPushButton(parent)
        button.clicked.connect(lambda *args, ix=index: self.clicked.emit(ix))
        return button

    def setEditorData(self, editor: QPushButton, index):
        # editor.setIcon(QIcon().fromTheme("edit-delete"))
        editor.setText(index.data(Qt.ItemDataRole.DisplayRole))

    def setModelData(self, editor, model, index):
        pass


class DefaultErrorReplacementModel(QAbstractTableModel):
    def __init__(self, data: List):
        super().__init__()
        self._data = data
        self.header_items = ["Suchen nach", "Ersetzen mit", "Aktion"]

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = ...
    ) -> Any:
        if (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DisplayRole
        ):
            return self.header_items[section]

    def insertRowAtEnd(self):
        row = len(self._data)
        index = self.index(row, 0)
        self.insertRows(row, 1, index)

    def insertRows(self, row: int, count: int, parent: QModelIndex = ...) -> bool:
        self.beginInsertRows(parent, row, row + count - 1)
        default_row = ["", "", "Löschen"]
        for i in range(count):
            self._data.insert(row, default_row)
        self.endInsertRows()
        self.layoutChanged.emit()
        return True

    def removeRows(self, row: int, count: int, parent: QModelIndex = ...) -> bool:
        self.beginRemoveRows(parent, row, row + count - 1)
        for i in range(count):
            del self._data[row]
        self.endRemoveRows()
        self.layoutChanged.emit()
        return True

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return 3

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if index.isValid():
            if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                column = index.column()
                row = index.row()
                value = ""
                if row < len(self._data):
                    value = self._data[row][column]
                return str(value)

    def setData(self, index: QModelIndex, value: Any, role: int = ...) -> bool:
        if role == Qt.ItemDataRole.EditRole:
            column = index.column()
            row = index.row()
            self._data[row][column] = value
            return True
        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        return (
            Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsEditable
        )


class OcrDefaultErrorReplacementTable(QTableView):
    def __init__(self):
        super().__init__()
        self.default_replacement_model = None
        self.delete_button_delegate = None

    def update_model(self, replacement_map: Dict):
        data = []
        for item in replacement_map["map"]:
            item.append("Löschen")
            data.append(item)
        self.default_replacement_model = DefaultErrorReplacementModel(data)
        self.setModel(self.default_replacement_model)

        self.delete_button_delegate = PushButtonDelegate(self)
        self.delete_button_delegate.clicked.connect(self.button_delegate_clicked)
        self.setItemDelegateForColumn(2, self.delete_button_delegate)

    def get_replacement_map_values(self):
        data = []
        for row in range(self.default_replacement_model.rowCount()):
            data.append([])
            for column in range(self.default_replacement_model.columnCount()):
                index = self.default_replacement_model.index(row, column)
                # We suppose data are strings
                data[row].append(
                    self.default_replacement_model.data(
                        index, role=Qt.ItemDataRole.DisplayRole
                    )
                )
        return data

    def button_delegate_clicked(self, index):
        self.model().removeRows(index.row(), 1, index)

    def insert_row(self):
        self.model().insertRowAtEnd()
