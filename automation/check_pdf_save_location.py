from PyQt6.QtWidgets import QMessageBox
from typing import Callable
import os

from automation.store import Store
from utils.dialog import create_dialog


def check_pdf_save_location(parent):
    dialog = None
    if Store.SELECTED_FILE_PATH == Store.SAVE_FILE_PATH:
        dialog = create_dialog(
            window_title="Achtung",
            text="Die Originaldatei würde überschrieben werden",
            buttons=QMessageBox.StandardButton.Abort | QMessageBox.StandardButton.Ok,
            icon=QMessageBox.Icon.Warning,
            parent=parent,
        )
    if os.path.exists(Store.SAVE_FILE_PATH):
        dialog = create_dialog(
            window_title="Achtung",
            text="Es existiert bereits eine Datei mit diesem Namen",
            buttons=QMessageBox.StandardButton.Abort | QMessageBox.StandardButton.Ok,
            icon=QMessageBox.Icon.Warning,
            parent=parent,
        )

    if dialog is None:
        return True

    button = dialog.exec()

    if button == QMessageBox.StandardButton.Ok:
        dialog.close()
        return True
    if button == QMessageBox.StandardButton.Abort:
        dialog.close()
        return False
    return True
