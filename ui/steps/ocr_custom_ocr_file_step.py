from PyQt6.QtWidgets import QSpacerItem, QSizePolicy

from automation.ocr_automation import OcrAutomation
from ui.components.file_selection import FileSelection
from ui.steps.step import Step

class OcrCustomOcrFileStep(Step):
    def __init__(
            self,
            *,
            text: str="Wähle die Frakturmusterdatei ",
            next_text="Fertig",
            next_callback=None,
            detail: str = ""
    ):
        super().__init__(
            text=text,
            next_text=next_text,
            next_callback=next_callback,
            detail=detail,
        )

        self.file_selection = FileSelection(file_type="FBT")
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
