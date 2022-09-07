from PyQt6.QtWidgets import QWidget, QStackedLayout

from ui.components.ocr_default_error_replacement.ocr_default_error_replacement_edit import (
    OcrDefaultErrorReplacementEdit,
)
from ui.components.ocr_default_error_replacement.ocr_default_error_replacement_list import (
    OcrDefaultErrorReplacementList,
)


class OcrDefaultErrorReplacementSettings(QWidget):
    def __init__(
        self,
        edit_callback,
        delete_callback,
        edit_back_callback,
        edit_save_callback,
        delete_entry_callback,
        create_new_callback,
    ):
        super(OcrDefaultErrorReplacementSettings, self).__init__()

        self.layout = QStackedLayout()

        self.list = OcrDefaultErrorReplacementList(
            edit_callback, delete_callback, create_new_callback
        )
        self.edit = OcrDefaultErrorReplacementEdit(
            edit_back_callback, edit_save_callback, delete_entry_callback
        )

        self.layout.addWidget(self.list)
        self.layout.addWidget(self.edit)

        self.setLayout(self.layout)
