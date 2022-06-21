from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QGroupBox,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QSpinBox,
)

from config import Config
from ui.components.spin_boxes import create_mm_spinbox, create_spinbox
from ui.steps.step import Step
from utils.console import console
from utils.offset import Offset
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

        self.crop_group_box = QGroupBox("Standardwerte für das Zuschneiden")

        (
            self.crop_box_top_layout,
            self.crop_box_top_spinner,
        ) = SettingsStep._create_spinbox(default_value=0, label="Oberer Rand:")

        (
            self.crop_box_right_layout,
            self.crop_box_right_spinner,
        ) = SettingsStep._create_spinbox(default_value=0, label="Rechter Rand:")

        (
            self.crop_box_bottom_layout,
            self.crop_box_bottom_spinner,
        ) = SettingsStep._create_spinbox(default_value=0, label="Unterer Rand:")

        (
            self.crop_box_left_layout,
            self.crop_box_left_spinner,
        ) = SettingsStep._create_spinbox(default_value=0, label="Linker Rand:")

        self.crop_box_parent_layout = QVBoxLayout()
        self.crop_box_parent_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.crop_box_parent_layout.setSpacing(20)
        self.crop_box_parent_layout.addLayout(self.crop_box_top_layout)
        self.crop_box_parent_layout.addLayout(self.crop_box_right_layout)
        self.crop_box_parent_layout.addLayout(self.crop_box_bottom_layout)
        self.crop_box_parent_layout.addLayout(self.crop_box_left_layout)

        self.crop_group_box.setLayout(self.crop_box_parent_layout)

        self.dpi_group_box = QGroupBox("DPI für das Analysieren von Bildern")
        self.dpi_layout, self.dpi_spinner = SettingsStep._create_spinbox(default_value=0,
                                                                         label="DPI", is_mm=False, label_min_width=30)
        self.dpi_parent_layout = QVBoxLayout()
        self.dpi_parent_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.dpi_parent_layout.setSpacing(0)
        self.dpi_parent_layout.addLayout(self.dpi_layout)
        self.dpi_group_box.setLayout(self.dpi_parent_layout)

        self.y_axis_threshold_group_box = QGroupBox(
            "Dieser Wert bestimmt ab wann der Beschneidungskasten für jede Seite auch entlang der vertikalen Achse angewendet wird")
        self.y_axis_threshold_layout, self.y_axis_threshold_spinner = SettingsStep._create_spinbox(
            default_value=int(0 * 100),
            label="Schwellenwert",
            unit='%',
            is_mm=False,
            label_min_width=90,
            maximum=100,
            minimum=0
        )
        self.y_axis_threshold_parent_layout = QVBoxLayout()
        self.y_axis_threshold_parent_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.y_axis_threshold_parent_layout.setSpacing(0)
        self.y_axis_threshold_parent_layout.addLayout(self.y_axis_threshold_layout)
        self.y_axis_threshold_group_box.setLayout(self.y_axis_threshold_parent_layout)

        self.layout.addWidget(self.crop_group_box, 2, 0, 1, 4)
        self.layout.addWidget(self.dpi_group_box, 3, 0, 1, 4)
        self.layout.addWidget(self.y_axis_threshold_group_box, 4, 0, 1, 4)

    def update_crop_box(self, crop_box: Offset):
        self.crop_box_top_spinner.setValue(crop_box.top)
        self.crop_box_right_spinner.setValue(crop_box.right)
        self.crop_box_bottom_spinner.setValue(crop_box.bottom)
        self.crop_box_left_spinner.setValue(crop_box.left)

    def update_dpi(self, dpi: int):
        self.dpi_spinner.setValue(dpi)

    def update_y_axis_threshold(self, value: int):
        self.y_axis_threshold_spinner.setValue(value)

    @staticmethod
    def _create_spinbox(*, default_value: int, label: str, is_mm=True, label_min_width=80, unit='',
                        minimum=Config.MIN_DPI, maximum=Config.MAX_DPI) -> (QHBoxLayout, QSpinBox):
        crop_box_layout = QHBoxLayout()
        crop_box_label = QLabel(label)
        crop_box_label.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        )
        crop_box_label.setMinimumWidth(label_min_width)

        if is_mm:
            crop_box_spinner = create_mm_spinbox(default_value=default_value)
        else:
            crop_box_spinner = create_spinbox(
                default_value=default_value,
                unit=unit,
                minimum=minimum,
                maximum=maximum,
            )
        crop_box_spinner.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        )
        crop_box_spinner.setMinimumWidth(100)

        crop_box_layout.addWidget(crop_box_label)
        crop_box_layout.addWidget(crop_box_spinner)
        return crop_box_layout, crop_box_spinner

    def get_crop_box(self) -> Offset:
        return Offset(
            self.crop_box_top_spinner.value(),
            self.crop_box_right_spinner.value(),
            self.crop_box_bottom_spinner.value(),
            self.crop_box_left_spinner.value(),
        )

    def get_dpi_value(self) -> int:
        return self.dpi_spinner.value()

    def get_y_axis_threshold(self) -> int:
        return self.y_axis_threshold_spinner.value()
