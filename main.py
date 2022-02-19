import sys

from PyQt6.QtWidgets import QApplication
from rich.traceback import install

from ui.main import MainWindow
from utils.screen import Screen

if __name__ == '__main__':
    install(show_locals=True)

    Screen.set_screen_resolution_string()
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
