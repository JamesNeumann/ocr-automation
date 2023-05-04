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
    QLineEdit,
)

from config import Config
from ui.components.spin_boxes import create_mm_spinbox
from utils.offset import Offset
from utils.rectangle import Rectangle
from utils.save_config import SaveConfig


class CropAmountSelection(QWidget):
    def __init__(
        self,
        *,
        reset_callback: Callable,
        apply_all_pages_callback: Callable,
        apply_even_pages_callback: Callable,
        apply_odd_pages_callback: Callable,
        apply_specific_pages_callback: Callable,
        top_spin_box_callback: Callable,
        right_spin_box_callback: Callable,
        bottom_spin_box_callback: Callable,
        left_spin_box_callback: Callable,
        previous_image_button_callback: Callable,
        next_image_button_callback: Callable,
        horizontal_spin_box_callback: Callable,
        vertical_spin_box_callback: Callable,
    ):
        super().__init__()

        self.reset_callback = reset_callback
        self.apply_all_pages_callback = apply_all_pages_callback
        self.apply_even_pages_callback = apply_even_pages_callback
        self.apply_odd_pages_callback = apply_odd_pages_callback
        self.apply_specific_pages_callback = apply_specific_pages_callback

        self.top_spin_box_callback = top_spin_box_callback
        self.right_spin_box_callback = right_spin_box_callback
        self.bottom_spin_box_callback = bottom_spin_box_callback
        self.left_spin_box_callback = left_spin_box_callback

        self.horizontal_spin_box_callback = horizontal_spin_box_callback
        self.vertical_spin_box_callback = vertical_spin_box_callback

        self.next_image_button_callback = next_image_button_callback
        self.previous_image_button_callback = previous_image_button_callback

        self._create_ui()

        self.pen = QPen(Qt.GlobalColor.green)
        self.pen.setWidth(Config.map_dpi_to_pen_width(SaveConfig.get_dpi_value()))

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
        self.pen.setWidth(Config.map_dpi_to_pen_width(SaveConfig.get_dpi_value()))
        if self.isHidden():
            self.show()

    def update_page_label(self, text: str):
        self.page_label.setText(text)

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

    def set_spin_box_values(
        self, values: Offset, horizontal_value: int, vertical_value: int
    ):
        self.top_spin_box.blockSignals(True)
        self.right_spin_box.blockSignals(True)
        self.bottom_spin_box.blockSignals(True)
        self.left_spin_box.blockSignals(True)
        self.horizontal_spin_box.blockSignals(True)
        self.vertical_spin_box.blockSignals(True)

        self.top_spin_box.setValue(values.top)
        self.right_spin_box.setValue(values.right)
        self.bottom_spin_box.setValue(values.bottom)
        self.left_spin_box.setValue(values.left)
        self.horizontal_spin_box.setValue(horizontal_value)
        self.vertical_spin_box.setValue(vertical_value)

        self.top_spin_box.blockSignals(False)
        self.right_spin_box.blockSignals(False)
        self.bottom_spin_box.blockSignals(False)
        self.left_spin_box.blockSignals(False)
        self.horizontal_spin_box.blockSignals(False)
        self.vertical_spin_box.blockSignals(False)

    def reset(self):
        self.next_image_button.blockSignals(True)
        self.previous_image_button.blockSignals(True)

        self.next_image_button.setDisabled(False)
        self.previous_image_button.setDisabled(True)

        self.next_image_button.blockSignals(False)
        self.previous_image_button.blockSignals(False)

    def block_spinbox_signals(self, block: bool):
        self.top_spin_box.blockSignals(block)
        self.right_spin_box.blockSignals(block)
        self.bottom_spin_box.blockSignals(block)
        self.left_spin_box.blockSignals(block)
        self.horizontal_spin_box.blockSignals(block)
        self.vertical_spin_box.blockSignals(block)

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

        self.page_label = QLabel("")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.previous_image_button)
        button_layout.addWidget(self.next_image_button)
        button_layout.addWidget(self.page_label)
        return button_layout

    def _create_crop_box_layout(self):
        crop_information_container = QVBoxLayout()

        crop_information_container.addWidget(self._create_crop_actions())
        crop_information_container.addLayout(self._create_horizontal_vertical_spinbox())
        crop_information_container.addLayout(self._create_spin_boxes())
        crop_information_container.setStretch(2, 1)
        return crop_information_container

    def _create_crop_actions(self):
        crop_actions_group_box = QGroupBox("Aktionen")

        crop_actions_layout = QVBoxLayout()

        first_child_layout = QHBoxLayout()
        second_child_layout = QHBoxLayout()
        third_child_layout = QHBoxLayout()

        reset_crop_values_button = QPushButton("Aktuelle Seite zurücksetzen")
        reset_crop_values_button.setStyleSheet("padding: 8px;")
        reset_crop_values_button.clicked.connect(self.reset_callback)

        apply_to_all_pages_button = QPushButton("Auf alle Seiten anwenden")
        apply_to_all_pages_button.setStyleSheet("padding: 8px;")
        apply_to_all_pages_button.clicked.connect(self.apply_all_pages_callback)

        apply_to_even_pages_button = QPushButton("Auf gerade Seiten anwenden")
        apply_to_even_pages_button.setStyleSheet("padding: 8px;")
        apply_to_even_pages_button.clicked.connect(self.apply_even_pages_callback)

        apply_to_odd_pages_button = QPushButton("Auf ungerade Seiten anwenden")
        apply_to_odd_pages_button.setStyleSheet("padding: 8px;")
        apply_to_odd_pages_button.clicked.connect(self.apply_odd_pages_callback)

        first_child_layout.addWidget(reset_crop_values_button)
        first_child_layout.addWidget(apply_to_all_pages_button)

        second_child_layout.addWidget(apply_to_even_pages_button)
        second_child_layout.addWidget(apply_to_odd_pages_button)

        third_child_layout.addWidget(QLabel("Spezielle Seiten (bspw. 1,2-5,10):"))
        self.specific_pages_line_edit = QLineEdit()
        third_child_layout.addWidget(self.specific_pages_line_edit)

        apply_specific_pages_button = QPushButton("Anwenden")
        apply_specific_pages_button.setStyleSheet("padding: 8px;")
        apply_specific_pages_button.clicked.connect(self.apply_specific_pages_callback)
        third_child_layout.addWidget(apply_specific_pages_button)

        crop_actions_layout.addLayout(first_child_layout)
        crop_actions_layout.addLayout(second_child_layout)
        crop_actions_layout.addLayout(third_child_layout)

        crop_actions_group_box.setLayout(crop_actions_layout)

        return crop_actions_group_box

    def _create_horizontal_vertical_spinbox(self):
        (
            self.horizontal_spin_box_group_box,
            self.horizontal_spin_box,
        ) = self._create_spinbox(
            default_value=0,
            label="Horizontale Verschiebung",
            spin_box_callback=self.horizontal_spin_box_callback,
        )

        self.vertical_spin_box_group_box, self.vertical_spin_box = self._create_spinbox(
            default_value=0,
            label="Vertikale Verschiebung",
            spin_box_callback=self.vertical_spin_box_callback,
        )

        move_layout = QHBoxLayout()
        move_layout.addWidget(self.vertical_spin_box_group_box)
        move_layout.addWidget(self.horizontal_spin_box_group_box)
        return move_layout

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

        crop_adjustment_layout = QVBoxLayout()
        crop_adjustment_layout.addWidget(self.top_spin_box_group_box)
        crop_adjustment_layout.addWidget(self.right_spin_box_group_box)
        crop_adjustment_layout.addWidget(self.bottom_spin_box_group_box)
        crop_adjustment_layout.addWidget(self.left_spin_box_group_box)
        return crop_adjustment_layout

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
