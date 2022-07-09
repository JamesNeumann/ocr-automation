import math
from typing import List

import numpy as np
from PyQt6.QtGui import QImage

from ui.components.crop_amount_selection import CropAmountSelection
from utils.analysis_result import AnalysisResult
from utils.console import console
from utils.conversion import pts_to_pixel, convert_to_pts
from utils.offset import Offset
from utils.rectangle import Rectangle
from utils.save_config import SaveConfig


class CropAmountSelectionController:
    def __init__(self):
        self.analysis_result: AnalysisResult = AnalysisResult(
            images=[],
            crop_boxes=[],
            pts_width=0,
            pts_height=0,
            transformed_boxes=[],
            min_index=0,
            max_box=Rectangle(0, 0, 0, 0),
            pts_dimensions=[],
        )

        self.crop_amount_selection = CropAmountSelection(
            top_spin_box_callback=self.top_spin_box_changed,
            right_spin_box_callback=self.right_spin_box_changed,
            bottom_spin_box_callback=self.bottom_spin_box_changed,
            left_spin_box_callback=self.left_spin_box_changed,
            next_image_button_callback=self.next_image_button_clicked,
            previous_image_button_callback=self.previous_image_button_clicked,
            on_all_pages_toggled=self.all_pages_button_toggled,
            on_single_pages_toggled=self.single_pages_button_toggled,
        )

        self.current_image_index = 0
        self.q_images = []
        self.is_single_image_crop_mode = False

        self.default_offset = SaveConfig.get_default_crop_box_offset()
        self.crop_amount_selection.set_spin_box_values(self.default_offset)
        self.selected_offset = self.default_offset.copy()
        self.selected_single_page_offsets: List[Offset] = []
        self.selected_single_page_spin_box_values: List[Offset] = []

    def initialize_single_image_offsets(self):
        self.selected_single_page_spin_box_values = [
            self.default_offset.copy() for _ in self.analysis_result.images
        ]

        self.selected_single_page_offsets = [
            self.default_offset.copy() for _ in self.analysis_result.images
        ]

        for index, offset in enumerate(self.selected_single_page_spin_box_values):
            pts_size_y = self.analysis_result.pts_dimensions[index].height
            pts_size_x = self.analysis_result.pts_dimensions[index].width

            shape_width = self.analysis_result.images[index].shape[1]
            shape_height = self.analysis_result.images[index].shape[0]

            self.selected_single_page_offsets[index].top = pts_to_pixel(
                offset.top, pts_size_y / shape_height
            )
            self.selected_single_page_offsets[index].right = pts_to_pixel(
                offset.right, pts_size_x / shape_width
            )
            self.selected_single_page_offsets[index].bottom = pts_to_pixel(
                offset.bottom, pts_size_y / shape_height
            )
            self.selected_single_page_offsets[index].left = pts_to_pixel(
                offset.left, pts_size_x / shape_width
            )

    def change_visible_image(self):
        if self.current_image_index > len(self.q_images) - 1:
            self.create_q_image(self.current_image_index)

        if self.is_single_image_crop_mode:
            crop_box = self.analysis_result.transformed_box[self.current_image_index]
        else:
            crop_box = self.analysis_result.max_box

        self.crop_amount_selection.set_spin_box_values(
            self.selected_single_page_spin_box_values[self.current_image_index]
        )

        crop_box_with_offset = self.get_crop_box_pixel(
            crop_box,
            self.analysis_result.images[self.current_image_index],
            self.current_image_index,
        )

        self.crop_amount_selection.render_image(
            self.q_images[self.current_image_index], crop_box_with_offset
        )

    def update_image_button_state(self):
        if self.current_image_index == 0:
            self.crop_amount_selection.disable_previous_button()
        if self.current_image_index == len(self.analysis_result.images) - 1:
            self.crop_amount_selection.disable_next_button()
        if 0 < self.current_image_index < len(self.analysis_result.images) - 1:
            self.crop_amount_selection.enable_next_button()
            self.crop_amount_selection.enable_previous_button()

    def all_pages_button_toggled(self):
        self.is_single_image_crop_mode = False
        self.change_visible_image()

    def single_pages_button_toggled(self):
        self.is_single_image_crop_mode = True
        self.change_visible_image()

    def next_image_button_clicked(self):
        if self.current_image_index < len(self.analysis_result.images) - 1:
            self.current_image_index += 1
            self.change_visible_image()

        self.update_image_button_state()

    def previous_image_button_clicked(self):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.change_visible_image()
        self.update_image_button_state()

    def top_spin_box_changed(self, value: int):
        self.selected_single_page_spin_box_values[self.current_image_index].top = value
        self.update_selected_offset("top", value)
        self.change_visible_image()

    def right_spin_box_changed(self, value: int):
        self.selected_single_page_spin_box_values[
            self.current_image_index
        ].right = value
        self.update_selected_offset("right", value)
        self.change_visible_image()

    def bottom_spin_box_changed(self, value: int):
        self.selected_single_page_spin_box_values[
            self.current_image_index
        ].bottom = value
        self.update_selected_offset("bottom", value)
        self.change_visible_image()

    def left_spin_box_changed(self, value: int):
        self.selected_single_page_spin_box_values[self.current_image_index].left = value
        self.update_selected_offset("left", value)
        self.change_visible_image()

    def update_selected_offset(self, dimension: str, value: int):

        if dimension == "top" or dimension == "bottom":
            pts_size = self.analysis_result.pts_dimensions[
                self.current_image_index
            ].height
            shape_index = 0
        else:
            pts_size = self.analysis_result.pts_dimensions[
                self.current_image_index
            ].width
            shape_index = 1

        new_pixel_offset = pts_to_pixel(
            value,
            pts_size
            / self.analysis_result.images[self.current_image_index].shape[shape_index],
        )

        if self.is_single_image_crop_mode:
            self.selected_single_page_offsets[self.current_image_index][
                dimension
            ] = new_pixel_offset
        else:
            self.selected_offset[dimension] = new_pixel_offset

    def show(self):
        self.update_selected_offset("top", self.selected_offset.top)
        self.update_selected_offset("right", self.selected_offset.right)
        self.update_selected_offset("bottom", self.selected_offset.bottom)
        self.update_selected_offset("left", self.selected_offset.left)
        self.crop_amount_selection.show_ui()
        self.update_image_button_state()
        self.change_visible_image()

    def reset(self):
        self.current_image_index = 0
        self.q_images = []
        self.is_single_image_crop_mode = False

        self.default_offset = SaveConfig.get_default_crop_box_offset()
        self.crop_amount_selection.set_spin_box_values(self.default_offset)
        self.selected_offset = self.default_offset.copy()
        self.selected_single_page_offsets = []
        self.selected_single_page_spin_box_values = []
        self.update_image_button_state()
        self.crop_amount_selection.reset()

    def set_analysis_result(self, analysis_result: AnalysisResult):
        self.analysis_result = analysis_result
        self.update_spin_boxes_max_value()
        self.initialize_single_image_offsets()

    def update_spin_boxes_max_value(self):
        image_shape = self.analysis_result.images[self.analysis_result.min_index].shape
        width = image_shape[1]
        height = image_shape[0]
        pts_per_width = float(self.analysis_result.pts_width / width)
        pts_per_height = float(self.analysis_result.pts_height / height)

        crop_box = self.analysis_result.max_box
        max_top = convert_to_pts(pts_per_height * crop_box.y)

        right_diff = width - crop_box.width - crop_box.x
        if width < crop_box.width or right_diff < 0:
            right_diff = 0
        bottom_diff = height - crop_box.height - crop_box.y
        if height < crop_box.height or bottom_diff < 0:
            bottom_diff = 0

        max_right = convert_to_pts(pts_per_width * right_diff)
        max_bottom = convert_to_pts(pts_per_height * bottom_diff)
        max_left = convert_to_pts(pts_per_width * crop_box.x)

        self.crop_amount_selection.set_top_spin_box_max(math.floor(max_top))
        self.crop_amount_selection.set_right_spin_box_max(math.floor(max_right))
        self.crop_amount_selection.set_bottom_spin_box_max(math.floor(max_bottom))
        self.crop_amount_selection.set_left_spin_box_max(math.floor(max_left))

    def get_crop_box_pixel(
        self, crop_box: Rectangle, image: np.ndarray, index: int, relative=True
    ):
        offset = (
            self.selected_single_page_offsets[index]
            if self.is_single_image_crop_mode
            else self.selected_offset
        )
        x = max(crop_box.x - offset.left, 0)
        y = max(crop_box.y - offset.top, 0)
        width = min(
            crop_box.width
            + offset.left
            + offset.right
            - (0 if relative else crop_box.x),
            image.shape[1],
        )
        height = min(
            crop_box.height
            + offset.top
            + offset.bottom
            - (0 if relative else crop_box.y),
            image.shape[0],
        )
        return Rectangle(x, y, width, height)

    def get_crop_box_pts(
        self,
        crop_box: Rectangle,
        image: np.ndarray,
        pts_rectangle: Rectangle,
        index: int,
        relative=True,
    ):
        crop_box_pixel = self.get_crop_box_pixel(crop_box, image, index, relative)

        pts_per_width = float(pts_rectangle.width / image.shape[1])
        pts_per_height = float(pts_rectangle.height / image.shape[0])

        crop_box_pts = Rectangle(
            convert_to_pts(crop_box_pixel.x * pts_per_width),
            convert_to_pts(crop_box_pixel.y * pts_per_height),
            convert_to_pts(crop_box_pixel.width * pts_per_width),
            convert_to_pts(crop_box_pixel.height * pts_per_height),
        )

        return crop_box_pts

    def get_transformed_crop_boxes_pts(self):
        transformed_boxes_pts = []

        transformed_boxes = self.analysis_result.transformed_box
        for index, box in enumerate(transformed_boxes):
            box = self.get_crop_box_pts(
                box,
                self.analysis_result.images[index],
                self.analysis_result.pts_dimensions[index],
                index,
                True,
            )
            transformed_boxes_pts.append(box)

        return transformed_boxes_pts

    def get_max_crop_box_pts(self):
        return self.get_crop_box_pts(
            self.analysis_result.max_box,
            self.analysis_result.images[self.analysis_result.min_index],
            self.analysis_result.pts_dimensions[self.analysis_result.min_index],
            True,
        )

    def create_q_image(self, index: int):
        image = self.analysis_result.images[index]
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(
            image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888
        )
        self.q_images.append(q_image)
