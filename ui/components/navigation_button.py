from PyQt6 import QtCore
from PyQt6.QtWidgets import QPushButton


class NavigationButton(QPushButton):
    def __init__(self, text: str, x: int, y: int, width: int, height: int):
        super().__init__(text)

        self.setGeometry(QtCore.QRect(x, y, width, height))
