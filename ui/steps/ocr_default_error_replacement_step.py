from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGroupBox, QCheckBox, QVBoxLayout, QScrollArea

from ui.steps.step import Step
from utils.save_config import SaveConfig


class OcrDefaultErrorReplacementStep(Step):
    def __init__(
        self,
        *,
        text: str,
        previous_text="Nein",
        previous_callback=None,
        next_text="Ja",
        next_callback=None,
        detail: str = "",
    ):
        super().__init__(
            text=text,
            previous_text=previous_text,
            previous_callback=previous_callback,
            next_text=next_text,
            next_callback=next_callback,
            detail=detail,
        )
        self.checkbox_layout = QVBoxLayout()
        self.scroll_container = QScrollArea()
        self.scroll_container.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.scroll_container.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_container.setWidgetResizable(True)
        self.checkbox_added = False

    def add_replacement_maps_check_boxes(self):
        if self.checkbox_added:
            return
        for replacement_map in SaveConfig.get_default_error_replacement_maps():
            checkbox = QCheckBox(replacement_map["name"])
            self.checkbox_layout.addWidget(
                checkbox,
            )

        self.scroll_container.setLayout(self.checkbox_layout)
        self.layout.addWidget(self.scroll_container, 2, 0, 1, 4)
        self.checkbox_added = True

    def get_selected_replacement_maps(self):
        maps = SaveConfig.get_default_error_replacement_maps()
        selected_maps = []
        items = (
            self.checkbox_layout.itemAt(i) for i in range(self.checkbox_layout.count())
        )
        for index, item in enumerate(items):
            if item.widget().isChecked():
                selected_maps.append(maps[index])
        return selected_maps
