from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QCheckBox, QVBoxLayout, QScrollArea

from ui.steps.step import Step
from utils.ocr_default_error_replacement import (
    load_all_ocr_default_error_replacement_maps,
)
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

        self.check_boxes = []

    def add_replacement_maps_check_boxes(self):
        if self.checkbox_added:
            return
        for replacement_map in load_all_ocr_default_error_replacement_maps():
            checkbox = QCheckBox(replacement_map["name"])
            checkbox.toggled.connect(self.check_changed)
            self.check_boxes.append(checkbox)
            self.checkbox_layout.addWidget(
                checkbox,
            )
        self.check_boxes[0].setChecked(True)

        self.scroll_container.setLayout(self.checkbox_layout)
        self.layout.addWidget(self.scroll_container, 2, 0, 1, 4)
        self.checkbox_added = True

    def check_changed(self, state):
        print(state)
        if state:
            for check_box in self.check_boxes:
                print(check_box == self.sender())
                if check_box != self.sender():
                    check_box.setChecked(False)



    def get_selected_replacement_maps(self):
        maps = load_all_ocr_default_error_replacement_maps()
        selected_maps = []
        items = (
            self.checkbox_layout.itemAt(i) for i in range(self.checkbox_layout.count())
        )
        for index, item in enumerate(items):
            if item.widget().isChecked():
                selected_maps.append(maps[index])
        return selected_maps
