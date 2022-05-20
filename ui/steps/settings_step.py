from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QGroupBox,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QSpinBox,
)

from ui.components.mm_spinbox import create_mm_spinbox
from ui.steps.step import Step
from utils.console import console
from utils.save_config import SaveConfig


class SettingsStep(Step):
    def __init__(
        self,
        *,
        text: str,
        previous_text="Schließen",
        previous_callback=None,
        next_text="Speichern",
        next_callback=None,
        detail: str = ""
    ):
        super().__init__(
            text=text,
            previous_text=previous_text,
            previous_callback=previous_callback,
            next_text=next_text,
            next_callback=next_callback,
            detail=detail,
        )

        top, right, bottom, left = SaveConfig.get_default_crop_box_offset()

        self.crop_group_box = QGroupBox("Standardwerte für das Zuschneiden")

        (
            self.crop_box_top_layout,
            self.crop_box_top_spinner,
        ) = SettingsStep._create_spinbox(default_value=top, label="Oberer Rand:")

        (
            self.crop_box_right_layout,
            self.crop_box_right_spinner,
        ) = SettingsStep._create_spinbox(default_value=right, label="Rechter Rand:")

        (
            self.crop_box_bottom_layout,
            self.crop_box_bottom_spinner,
        ) = SettingsStep._create_spinbox(default_value=bottom, label="Unterer Rand:")

        (
            self.crop_box_left_layout,
            self.crop_box_left_spinner,
        ) = SettingsStep._create_spinbox(default_value=left, label="Linker Rand:")

        self.crop_box_parent_layout = QVBoxLayout()
        self.crop_box_parent_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.crop_box_parent_layout.setSpacing(20)
        self.crop_box_parent_layout.addLayout(self.crop_box_top_layout)
        self.crop_box_parent_layout.addLayout(self.crop_box_right_layout)
        self.crop_box_parent_layout.addLayout(self.crop_box_bottom_layout)
        self.crop_box_parent_layout.addLayout(self.crop_box_left_layout)

        self.crop_group_box.setLayout(self.crop_box_parent_layout)

        self.layout.addWidget(self.crop_group_box, 2, 0, 2, 4)

    def update_values(self):
        top, right, bottom, left = SaveConfig.get_default_crop_box_offset()
        self.crop_box_top_spinner.setValue(top)
        self.crop_box_right_spinner.setValue(right)
        self.crop_box_bottom_spinner.setValue(bottom)
        self.crop_box_left_spinner.setValue(left)

    @staticmethod
    def _create_spinbox(*, default_value: int, label: str) -> (QHBoxLayout, QSpinBox):
        crop_box_layout = QHBoxLayout()
        crop_box_label = QLabel(label)
        crop_box_label.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        )
        crop_box_label.setMinimumWidth(80)

        crop_box_spinner = create_mm_spinbox(default_value=default_value)
        crop_box_spinner.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        )
        crop_box_spinner.setMinimumWidth(100)

        crop_box_layout.addWidget(crop_box_label)
        crop_box_layout.addWidget(crop_box_spinner)
        return crop_box_layout, crop_box_spinner

    def get_crop_box(self) -> (int, int, int, int):
        return (
            self.crop_box_top_spinner.value(),
            self.crop_box_right_spinner.value(),
            self.crop_box_bottom_spinner.value(),
            self.crop_box_left_spinner.value(),
        )
