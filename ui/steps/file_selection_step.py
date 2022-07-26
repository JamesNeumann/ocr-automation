from PyQt6.QtWidgets import QSpacerItem, QSizePolicy

from ui.components.file_selection import FileSelection
from ui.components.special_pdf_actions import SpecialPdfActions
from ui.steps.step import Step


class FileSelectionStep(Step):
    def __init__(
        self,
        *,
        text: str,
        previous_text="Zurück",
        previous_callback=None,
        next_text="Weiter",
        next_callback=None,
        detail: str = "",
        set_metadata_callback=None,
        read_ocr_callback=None,
        optional_button_callback=None
    ):
        super().__init__(
            text=text,
            previous_text=previous_text,
            previous_callback=previous_callback,
            next_text=next_text,
            next_callback=next_callback,
            optional_button_text="Metadaten setzen und speichern",
            optional_button_callback=optional_button_callback,
            detail=detail,
        )

        self.file_selection = FileSelection()
        self.layout.addWidget(self.file_selection, 2, 0, 2, 4)
        self.layout.addItem(
            QSpacerItem(
                10, 100, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum
            ),
            3,
            0,
            1,
            4,
        )

        self.special_pdf_actions = SpecialPdfActions(
            set_metadata_callback, read_ocr_callback
        )
        self.layout.addWidget(self.special_pdf_actions, 4, 0, 1, 4)
        self.layout.addItem(
            QSpacerItem(
                10, 100, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum
            ),
            5,
            0,
            1,
            4,
        )

    def reset(self):
        self.file_selection.reset()
