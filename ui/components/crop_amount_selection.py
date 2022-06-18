from typing import Callable

from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QImage, QPixmap, QPen, QPainter
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QGroupBox,
    QSpinBox,
    QGridLayout,
    QRadioButton,
)

from ui.components.mm_spinbox import create_mm_spinbox
from utils.offset import Offset
from utils.rectangle import Rectangle


class CropAmountSelection(QWidget):
    def __init__(
        self,
        top_spin_box_callback: Callable,
        right_spin_box_callback: Callable,
        bottom_spin_box_callback: Callable,
        left_spin_box_callback: Callable,
        previous_image_button_callback: Callable,
        next_image_button_callback: Callable,
        on_all_pages_toggled: Callable,
        on_single_pages_toggled: Callable,
    ):
        super().__init__()

        self.top_spin_box_callback = top_spin_box_callback
        self.right_spin_box_callback = right_spin_box_callback
        self.bottom_spin_box_callback = bottom_spin_box_callback
        self.left_spin_box_callback = left_spin_box_callback

        self.next_image_button_callback = next_image_button_callback
        self.previous_image_button_callback = previous_image_button_callback

        self.on_all_pages_toggled = on_all_pages_toggled
        self.on_single_pages_toggled = on_single_pages_toggled

        self._create_ui()

        self.pen = QPen(Qt.GlobalColor.green)
        self.pen.setWidth(20)

    def render_image(self, image: QImage, box: Rectangle):
        pixmap = QPixmap(image)
        painter_instance = QPainter(pixmap)
        painter_instance.setPen(self.pen)

        painter_instance.drawRect(QRect(box.x, box.y, box.width, box.height))

        painter_instance.end()
        pixmap = pixmap.scaled(
            600,
            600,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.image_container.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())

    def show_ui(self):
        if self.isHidden():
            self.show()

    def enable_previous_button(self):
        if not self.previous_image_button.isEnabled():
            self.previous_image_button.setDisabled(False)

    def disable_previous_button(self):
        if self.previous_image_button.isEnabled():
            self.previous_image_button.setDisabled(True)

    def enable_next_button(self):
        if not self.next_image_button.isEnabled():
            self.next_image_button.setDisabled(False)

    def disable_next_button(self):
        if self.next_image_button.isEnabled():
            self.next_image_button.setDisabled(True)

    def set_top_spin_box_max(self, max_value: int):
        self.top_spin_box.setMaximum(max_value)

    def set_right_spin_box_max(self, max_value: int):
        self.right_spin_box.setMaximum(max_value)

    def set_bottom_spin_box_max(self, max_value: int):
        self.bottom_spin_box.setMaximum(max_value)

    def set_left_spin_box_max(self, max_value: int):
        self.left_spin_box.setMaximum(max_value)

    def set_spin_box_values(self, values: Offset):
        self.top_spin_box.blockSignals(True)
        self.right_spin_box.blockSignals(True)
        self.bottom_spin_box.blockSignals(True)
        self.left_spin_box.blockSignals(True)

        self.top_spin_box.setValue(values.top)
        self.right_spin_box.setValue(values.right)
        self.bottom_spin_box.setValue(values.bottom)
        self.left_spin_box.setValue(values.left)

        self.top_spin_box.blockSignals(False)
        self.right_spin_box.blockSignals(False)
        self.bottom_spin_box.blockSignals(False)
        self.left_spin_box.blockSignals(False)

    def _create_ui(self):
        self.main_layout = QHBoxLayout()

        self.main_layout.addLayout(self._create_image_controls())
        self.main_layout.addLayout(self._create_crop_box_layout())
        self.setLayout(self.main_layout)

    def _create_image_controls(self):
        self.image_container = QLabel(self)
        image_control_layout = QVBoxLayout()
        image_control_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_control_layout.addWidget(self.image_container)
        image_control_layout.addLayout(self._create_image_control_buttons())
        return image_control_layout

    def _create_image_control_buttons(self):
        self.next_image_button = QPushButton(">")
        self.next_image_button.clicked.connect(self.next_image_button_callback)

        self.previous_image_button = QPushButton("<")
        self.previous_image_button.clicked.connect(self.previous_image_button_callback)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.previous_image_button)
        button_layout.addWidget(self.next_image_button)
        return button_layout

    def _create_crop_box_layout(self):
        crop_information_container = QVBoxLayout()

        crop_information_layout = QHBoxLayout()
        crop_information_layout.addStretch(1)

        crop_information_container.addLayout(crop_information_layout)
        crop_information_layout.addLayout(self._create_crop_mode_buttons())
        crop_information_container.addWidget(self._create_spin_boxes())
        crop_information_container.setStretch(1, 5)
        return crop_information_container

    def _create_crop_mode_buttons(self):
        grid_layout = QGridLayout()
        radio_button_all_pages = QRadioButton("Alle Seiten zusammen beschneiden")
        radio_button_all_pages.setChecked(True)
        radio_button_all_pages.toggled.connect(self.on_all_pages_toggled)

        grid_layout.addWidget(radio_button_all_pages, 0, 0)

        radio_button_single_pages = QRadioButton("Seiten einzeln beschneiden")
        radio_button_single_pages.setChecked(False)
        radio_button_single_pages.toggled.connect(self.on_single_pages_toggled)
        grid_layout.addWidget(radio_button_single_pages, 0, 1)
        return grid_layout

    def _create_spin_boxes(self):
        self.top_spin_box_group_box, self.top_spin_box = self._create_spinbox(
            default_value=0,
            label="Oberer Rand:",
            spin_box_callback=self.top_spin_box_callback,
        )

        self.right_spin_box_group_box, self.right_spin_box = self._create_spinbox(
            default_value=0,
            label="Rechter Rand:",
            spin_box_callback=self.right_spin_box_callback,
        )

        self.bottom_spin_box_group_box, self.bottom_spin_box = self._create_spinbox(
            default_value=0,
            label="Unterer Rand:",
            spin_box_callback=self.bottom_spin_box_callback,
        )

        self.left_spin_box_group_box, self.left_spin_box = self._create_spinbox(
            default_value=0,
            label="Linker Rand:",
            spin_box_callback=self.left_spin_box_callback,
        )

        crop_adjustment_box = QGroupBox()
        crop_adjustment_layout = QVBoxLayout()
        crop_adjustment_layout.addWidget(self.top_spin_box_group_box)
        crop_adjustment_layout.addWidget(self.right_spin_box_group_box)
        crop_adjustment_layout.addWidget(self.bottom_spin_box_group_box)
        crop_adjustment_layout.addWidget(self.left_spin_box_group_box)
        crop_adjustment_box.setLayout(crop_adjustment_layout)
        return crop_adjustment_box

    @staticmethod
    def _create_spinbox(
        *, default_value: int, label: str, spin_box_callback: Callable
    ) -> (QHBoxLayout, QSpinBox):
        offset_box = QGroupBox(label)
        crop_box_layout = QHBoxLayout()
        crop_box_spinner = create_mm_spinbox(default_value=default_value)
        crop_box_spinner.valueChanged.connect(spin_box_callback)
        offset_box.setLayout(crop_box_layout)
        crop_box_layout.addWidget(crop_box_spinner)

        return offset_box, crop_box_spinner
