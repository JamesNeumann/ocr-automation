from typing import List, Any, Dict

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt6.QtWidgets import QTableView


class DefaultErrorReplacementModel(QAbstractTableModel):
    def __init__(self, data: List):
        super().__init__()
        self._data = data
        self.header_items = ["Suchen nach", "Ersetzen mit"]

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = ...
    ) -> Any:
        if (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DisplayRole
        ):
            return self.header_items[section]

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return 2

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if index.isValid():
            if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                column = index.column()
                row = index.row()
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

    def update_model(self, replacement_map: Dict):
        self.default_replacement_model = DefaultErrorReplacementModel(
            replacement_map["map"]
        )
        self.setModel(self.default_replacement_model)

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
