import ctypes
import sys

from PyQt6 import QtCore
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from rich.traceback import install

from config import initialize_directories
from ui.main import MainWindow
from utils.save_config import SaveConfig
from utils.screen import Screen

if __name__ == '__main__':
    install(show_locals=True)

    myappid = u'jamesneumann.FineReaderAutomation.v1.0'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    SaveConfig.init()

    Screen.set_screen_resolution_string()
    initialize_directories()
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('./images/icon.ico'))
    window = MainWindow()
    MainWindow.setWindowFlags(window,
                              QtCore.Qt.WindowType.WindowCloseButtonHint |
                              QtCore.Qt.WindowType.WindowMinimizeButtonHint
                              )

    window.show()

    app.exec()
