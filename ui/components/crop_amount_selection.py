import math
from typing import List

from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton, QVBoxLayout, QGroupBox, QSpinBox
from numpy import ndarray

from utils.conversion import pts_to_pixel, convert_to_pts
from utils.rectangle import Rectangle


class CropAmountSelection(QWidget):
    DEFAULT_OFFSET_TOP = 5
    DEFAULT_OFFSET_BOTTOM = 15
    DEFAULT_OFFSET_LEFT = 5
    DEFAULT_OFFSET_RIGHT = 5

    def __init__(self):
        super().__init__()

        self.offset_top = 0
        self.offset_bottom = 0
        self.offset_left = 0
        self.offset_right = 0
        self.images = []
        self.curr_image_index = 0
        self.q_images = []
        self.rectangle = None
        self.rectangles = []
        self.pts_per_width = 0
        self.pts_per_height = 0
        self.width = 0
        self.height = 0
        self.set_default_offset()
        self.pen = QPen(Qt.GlobalColor.green)
        self.pen.setWidth(5)

        self.layout = QHBoxLayout()

        self.label = QLabel(self)
        self.next_image_button = QPushButton(">")
        self.previous_image_button = QPushButton("<")

        self.next_image_button.clicked.connect(self.next_image)
        self.previous_image_button.clicked.connect(self.previous_image)

        # image control layout
        self.image_control_layout = QVBoxLayout()
        self.image_control_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_control_layout.addWidget(self.label)
        self.layout.addLayout(self.image_control_layout)

        # button layout
        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.previous_image_button)
        self.button_layout.addWidget(self.next_image_button)
        self.image_control_layout.addLayout(self.button_layout)

        # adjustment layout
        self.crop_adjustment_box = QGroupBox()
        self.crop_adjustment_layout = QVBoxLayout()

        self.top_offset_box = QGroupBox("Oberer Rand:")
        self.top_offset_layout = QHBoxLayout()
        self.top_offset_spinbox = QSpinBox()
        self.top_offset_spinbox.setSuffix(" mm")
        self.top_offset_spinbox.setMinimum(-9999)
        self.top_offset_spinbox.setValue(CropAmountSelection.DEFAULT_OFFSET_TOP)
        self.top_offset_spinbox.valueChanged.connect(self.top_spinbox_changed)
        self.top_offset_layout.addWidget(self.top_offset_spinbox)
        self.top_offset_box.setLayout(self.top_offset_layout)

        self.bottom_offset_box = QGroupBox("Unterer Rand:")
        self.bottom_offset_layout = QHBoxLayout()
        self.bottom_offset_spinbox = QSpinBox()
        self.bottom_offset_spinbox.setSuffix(" mm")
        self.bottom_offset_spinbox.setMinimum(-9999)
        self.bottom_offset_spinbox.setValue(CropAmountSelection.DEFAULT_OFFSET_BOTTOM)
        self.bottom_offset_spinbox.valueChanged.connect(self.bottom_spinbox_changed)
        self.bottom_offset_layout.addWidget(self.bottom_offset_spinbox)
        self.bottom_offset_box.setLayout(self.bottom_offset_layout)

        self.left_offset_box = QGroupBox("Linker Rand:")
        self.left_offset_layout = QHBoxLayout()
        self.left_offset_spinbox = QSpinBox()
        self.left_offset_spinbox.setSuffix(" mm")
        self.left_offset_spinbox.setMinimum(-9999)
        self.left_offset_spinbox.setValue(CropAmountSelection.DEFAULT_OFFSET_LEFT)
        self.left_offset_spinbox.valueChanged.connect(self.left_spinbox_changed)
        self.left_offset_layout.addWidget(self.left_offset_spinbox)
        self.left_offset_box.setLayout(self.left_offset_layout)

        self.right_offset_box = QGroupBox("Rechter Rand:")
        self.right_offset_layout = QHBoxLayout()
        self.right_offset_spinbox = QSpinBox()
        self.right_offset_spinbox.setSuffix(" mm")
        self.right_offset_spinbox.setMinimum(-9999)
        self.right_offset_spinbox.valueChanged.connect(self.right_spinbox_changed)
        self.right_offset_spinbox.setValue(CropAmountSelection.DEFAULT_OFFSET_RIGHT)
        self.right_offset_layout.addWidget(self.right_offset_spinbox)
        self.right_offset_box.setLayout(self.right_offset_layout)

        self.crop_adjustment_layout.addWidget(self.top_offset_box)
        self.crop_adjustment_layout.addWidget(self.bottom_offset_box)
        self.crop_adjustment_layout.addWidget(self.left_offset_box)
        self.crop_adjustment_layout.addWidget(self.right_offset_box)
        self.crop_adjustment_box.setLayout(self.crop_adjustment_layout)

        self.layout.addWidget(self.crop_adjustment_box)

        self.setLayout(self.layout)

        self.update_button_state()

    def update_pixmap(self, index: int):
        if index > len(self.q_images) - 1:
            self.create_q_image(index)

        q_pixmap = QPixmap(self.q_images[index])
        painter_instance = QPainter(q_pixmap)
        painter_instance.setPen(self.pen)
        rect = QRect(
            max(self.rectangle.x - self.offset_left, 0),
            max(self.rectangle.y - self.offset_top, 0),
            min(self.rectangle.width - self.rectangle.x + self.offset_left + self.offset_right, self.width),
            min(self.rectangle.height - self.rectangle.y + self.offset_top + self.offset_bottom, self.height)
        )
        painter_instance.drawRect(rect)

        painter_instance.end()
        pixmap = q_pixmap.scaled(600, 600, Qt.AspectRatioMode.KeepAspectRatio)

        self.label.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())

    def create_q_image(self, index: int):
        image = self.images[index]
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        self.q_images.append(q_image)

    def next_image(self):
        if self.curr_image_index < len(self.images) - 1:
            self.curr_image_index += 1
            self.update_pixmap(self.curr_image_index)
        self.update_button_state()

    def previous_image(self):
        if self.curr_image_index > 0:
            self.curr_image_index -= 1
            self.update_pixmap(self.curr_image_index)
        self.update_button_state()

    def show_pix_map(self):
        if self.isHidden():
            self.show()
        self.update_pixmap(self.curr_image_index)

    def update_button_state(self):
        if self.curr_image_index == 0:
            self.previous_image_button.setDisabled(True)
        if self.curr_image_index == len(self.images) - 1:
            self.next_image_button.setDisabled(True)
        if 0 < self.curr_image_index < len(self.images) - 1:
            self.previous_image_button.setDisabled(False)
            self.next_image_button.setDisabled(False)

    def top_spinbox_changed(self, value: int):
        if self.pts_per_height:
            pixel = pts_to_pixel(value, self.pts_per_height)
            if self.rectangle.y - pixel > 0:
                self.offset_top = pixel
                self.update_pixmap(self.curr_image_index)

    def bottom_spinbox_changed(self, value: int):
        if self.pts_per_height:
            pixel = pts_to_pixel(value, self.pts_per_height)
            if self.rectangle.height + pixel < self.height:
                self.offset_bottom = pixel
                self.update_pixmap(self.curr_image_index)

    def left_spinbox_changed(self, value: int):
        if self.pts_per_width:
            pixel = pts_to_pixel(value, self.pts_per_width)
            if self.rectangle.x - pixel > 0:
                self.offset_left = pixel
                self.update_pixmap(self.curr_image_index)

    def right_spinbox_changed(self, value: int):
        if self.pts_per_width:
            pixel = pts_to_pixel(value, self.pts_per_width)
            if self.rectangle.width + pixel < self.width:
                self.offset_right = pixel
                self.update_pixmap(self.curr_image_index)

    def set_images(self, images: List[ndarray]) -> None:
        self.images = images

    def set_rectangle(self, rectangle: Rectangle) -> None:
        self.rectangle = rectangle

    def set_rectangles(self, rectangles: List[Rectangle]):
        self.rectangles = rectangles

    def set_width(self, width):
        self.width = width

    def set_height(self, height):
        self.height = height

    def set_pts_width_per_pixel(self, pts_per_width: float):
        self.pts_per_width = pts_per_width

    def set_pts_height_per_pixel(self, pts_per_height: float):
        self.pts_per_height = pts_per_height

    def set_spinner_max(self):
        max_left = convert_to_pts(float(self.pts_per_width) * self.rectangle.x)
        max_right = convert_to_pts((self.width - self.rectangle.width) * float(self.pts_per_width))
        max_top = convert_to_pts(float(self.pts_per_height) * self.rectangle.y)
        max_bottom = convert_to_pts(float(self.pts_per_height) * (self.height - self.rectangle.height))

        self.left_offset_spinbox.setMaximum(max(math.floor(max_left), 0))
        self.right_offset_spinbox.setMaximum(max(max_right, 0))
        self.top_offset_spinbox.setMaximum(max_top)
        self.bottom_offset_spinbox.setMaximum(max_bottom)

        if max_left < CropAmountSelection.DEFAULT_OFFSET_LEFT:
            self.left_offset_spinbox.setValue(self.offset_left)
        else:
            self.left_offset_spinbox.setValue(CropAmountSelection.DEFAULT_OFFSET_LEFT)
        if max_right < CropAmountSelection.DEFAULT_OFFSET_RIGHT:
            self.right_offset_spinbox.setValue(self.offset_right)
        else:
            self.right_offset_spinbox.setValue(CropAmountSelection.DEFAULT_OFFSET_RIGHT)
        if max_top < CropAmountSelection.DEFAULT_OFFSET_TOP:
            self.top_offset_spinbox.setValue(max_top)
        else:
            self.top_offset_spinbox.setValue(CropAmountSelection.DEFAULT_OFFSET_TOP)
        if max_bottom < CropAmountSelection.DEFAULT_OFFSET_BOTTOM:
            self.bottom_offset_spinbox.setValue(max_bottom)
        else:
            self.bottom_offset_spinbox.setValue(CropAmountSelection.DEFAULT_OFFSET_BOTTOM)

    def get_pts_rectangle(self):
        return Rectangle(
            convert_to_pts(max(self.rectangle.x - self.offset_left, 0) * self.pts_per_width),
            convert_to_pts(max(self.rectangle.y - self.offset_top, 0) * self.pts_per_height),
            convert_to_pts(min(self.rectangle.width - self.rectangle.x + self.offset_left + self.offset_right,
                               self.width) * self.pts_per_width),
            convert_to_pts(min(self.rectangle.height - self.rectangle.y + self.offset_top + self.offset_bottom,
                               self.height) * self.pts_per_height)
        )

    def get_pts_rectangles(self):
        pts_rectangles = []
        for rectangle in self.rectangles:
            temp_rectangle = Rectangle(
                convert_to_pts(rectangle.x * self.pts_per_width),
                convert_to_pts(rectangle.y * self.pts_per_height),
                convert_to_pts(rectangle.width * self.pts_per_width),
                convert_to_pts(rectangle.height * self.pts_per_height)
            )
            pts_rectangles.append(temp_rectangle)
        return pts_rectangles

    def reset(self):
        self.images = []
        self.curr_image_index = 0
        self.q_images = []
        self.rectangle = None
        self.pts_per_width = 0
        self.pts_per_height = 0
        self.width = 0
        self.height = 0
        self.set_default_offset()

        self.top_offset_spinbox.setValue(0)
        self.bottom_offset_spinbox.setValue(0)
        self.left_offset_spinbox.setValue(0)
        self.right_offset_spinbox.setValue(0)

    def set_default_offset(self):
        self.offset_top = 0
        self.offset_bottom = 0
        self.offset_left = 0
        self.offset_right = 0
