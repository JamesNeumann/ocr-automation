from PyQt6.QtWidgets import QMessageBox


def create_dialog(
    window_title: str,
    text: str,
    icon: QMessageBox.Icon,
    buttons: QMessageBox.StandardButton,
    parent,
):
    if parent:
        dialog = QMessageBox()
    else:
        dialog = QMessageBox(parent)
    dialog.setIcon(icon)
    dialog.setWindowTitle(window_title)
    dialog.setText(text)
    dialog.setStandardButtons(buttons)

    return dialog
