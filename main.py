import sys

from PyQt6.QtWidgets import QApplication
from rich.traceback import install

from ui.main import MainWindow

if __name__ == '__main__':
    install(show_locals=True)

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
