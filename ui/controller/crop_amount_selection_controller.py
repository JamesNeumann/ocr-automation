import re
from typing import List

import numpy as np
from PyQt6.QtGui import QImage

from automation.store import Store
from ui.components.crop_amount_selection import CropAmountSelection
from utils.crop_box_analysis_result import CropBoxAnalysisResult
from utils.conversion import pts_to_pixel, convert_to_pts
from utils.offset import Offset
from utils.rectangle import Rectangle
from utils.save_config import SaveConfig


def get_crop_box_pixel_including_offset(
    crop_box: Rectangle,
    offset: Offset,
    horizontal_offset: float,
    vertical_offset: float,
    image: np.ndarray,
    relative=True,
):
    # x = max(crop_box.x - offset.left + horizontal_offset, 0)
    # y = max(crop_box.y - offset.top + vertical_offset, 0)

    x = crop_box.x - offset.left + horizontal_offset
    y = crop_box.y - offset.top + vertical_offset

    calculated_width = (
        crop_box.width
        + offset.left
        + horizontal_offset
        + offset.right
        - horizontal_offset
        - (0 if relative else crop_box.x)
    )
    # width = min(
    #     calculated_width,
    #     image.shape[1],
    # )
    width = calculated_width

    calculated_height = (
        crop_box.height
        + offset.top
        + vertical_offset
        + offset.bottom
        - vertical_offset
        - (0 if relative else crop_box.y)
    )
    # height = min(
    #     calculated_height,
    #     image.shape[0],
    # )

    height = calculated_height

    return Rectangle(
        int(round(x)), int(round(y)), int(round(width)), int(round(height))
    )


def get_crop_box_pts(
    crop_box: Rectangle,
    offset: Offset,
    horizontal_offset: float,
    vertical_offset: float,
    image: np.ndarray,
    pts_rectangle: Rectangle,
    relative=True,
):
    crop_box_pixel = get_crop_box_pixel_including_offset(
        crop_box, offset, horizontal_offset, vertical_offset, image, relative
    )

    pts_per_width = float(pts_rectangle.width / image.shape[1])
    pts_per_height = float(pts_rectangle.height / image.shape[0])

    crop_box_pts = Rectangle(
        convert_to_pts(crop_box_pixel.x * pts_per_width),
        convert_to_pts(crop_box_pixel.y * pts_per_height),
        convert_to_pts(crop_box_pixel.width * pts_per_width),
        convert_to_pts(crop_box_pixel.height * pts_per_height),
    )

    return crop_box_pts


class CropAmountSelectionController:
    def __init__(self):
        self.crop_amount_selection = CropAmountSelection(
            reset_callback=self.reset_button_clicked,
            apply_all_pages_callback=self.apply_all_pages_button_clicked,
            apply_even_pages_callback=self.apply_even_pages_button_clicked,
            apply_odd_pages_callback=self.apply_odd_pages_button_clicked,
            apply_specific_pages_callback=self.apply_specific_pages_button_clicked,
            top_spin_box_callback=self.top_spin_box_changed,
            right_spin_box_callback=self.right_spin_box_changed,
            bottom_spin_box_callback=self.bottom_spin_box_changed,
            left_spin_box_callback=self.left_spin_box_changed,
            next_image_button_callback=self.next_image_button_clicked,
            previous_image_button_callback=self.previous_image_button_clicked,
            horizontal_spin_box_callback=self.horizontal_spinbox_changed,
            vertical_spin_box_callback=self.vertical_spinbox_changed,
        )

        self.current_image_index = 0
        self.q_images = []

        self.default_offset = SaveConfig.get_default_crop_box_offset()
        self.crop_amount_selection.set_spin_box_values(self.default_offset, 0, 0)

        self.pages_offsets: List[Offset] = []
        self.pages_spinbox_values: List[Offset] = []

        self.horizontal_spinbox_values: List[int] = []
        self.horizontal_pages_offsets: List[float] = []

        self.vertical_spinbox_values: List[int] = []
        self.vertical_pages_offsets: List[float] = []

        self.specific_page_regex = r"\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*"

    def initialize_single_image_offsets(self):
        self.pages_spinbox_values = [
            self.default_offset.copy() for _ in Store.CONVERT_PDF_RESULT.images
        ]

        self.pages_offsets = [
            self.default_offset.copy() for _ in Store.CONVERT_PDF_RESULT.images
        ]

        self.horizontal_spinbox_values = [0 for _ in Store.CONVERT_PDF_RESULT.images]
        self.horizontal_pages_offsets = [0 for _ in Store.CONVERT_PDF_RESULT.images]

        self.vertical_spinbox_values = [0 for _ in Store.CONVERT_PDF_RESULT.images]
        self.vertical_pages_offsets = [0 for _ in Store.CONVERT_PDF_RESULT.images]

        for index, offset in enumerate(self.pages_spinbox_values):
            pts_size_y = Store.CONVERT_PDF_RESULT.pts_dimensions[index].height
            pts_size_x = Store.CONVERT_PDF_RESULT.pts_dimensions[index].width

            shape_width = Store.CONVERT_PDF_RESULT.images[index].shape[1]
            shape_height = Store.CONVERT_PDF_RESULT.images[index].shape[0]

            self.pages_offsets[index].top = pts_to_pixel(
                offset.top, pts_size_y / shape_height
            )
            self.pages_offsets[index].right = pts_to_pixel(
                offset.right, pts_size_x / shape_width
            )
            self.pages_offsets[index].bottom = pts_to_pixel(
                offset.bottom, pts_size_y / shape_height
            )
            self.pages_offsets[index].left = pts_to_pixel(
                offset.left, pts_size_x / shape_width
            )

    def change_visible_image(self):
        if self.current_image_index > len(self.q_images) - 1:
            self.create_q_image(self.current_image_index)

        crop_box = Store.CROP_BOX_ANALYSIS_RESULT.transformed_box[
            self.current_image_index
        ]
        self.crop_amount_selection.set_spin_box_values(
            self.pages_spinbox_values[self.current_image_index],
            self.horizontal_spinbox_values[self.current_image_index],
            self.vertical_spinbox_values[self.current_image_index],
        )

        crop_box_with_offset = get_crop_box_pixel_including_offset(
            crop_box,
            self.pages_offsets[self.current_image_index],
            self.horizontal_pages_offsets[self.current_image_index],
            self.vertical_pages_offsets[self.current_image_index],
            Store.CONVERT_PDF_RESULT.images[self.current_image_index],
        )

        self.crop_amount_selection.render_image(
            self.q_images[self.current_image_index], crop_box_with_offset
        )

    def reset_button_clicked(self):
        self.update_page_offset(
            self.current_image_index, self.default_offset.copy(), 0, 0
        )
        self.pages_spinbox_values[self.current_image_index] = self.default_offset.copy()

        self.vertical_spinbox_values = [0 for _ in Store.CONVERT_PDF_RESULT.images]
        self.vertical_pages_offsets = [0 for _ in Store.CONVERT_PDF_RESULT.images]

        self.horizontal_spinbox_values = [0 for _ in Store.CONVERT_PDF_RESULT.images]
        self.horizontal_pages_offsets = [0 for _ in Store.CONVERT_PDF_RESULT.images]

        self.update_spin_boxes_max_value()

        self.update_spin_boxes()
        self.change_visible_image()

    def apply_all_pages_button_clicked(self):
        for index in range(len(Store.CONVERT_PDF_RESULT.images)):
            if index == self.current_image_index:
                continue
            self.pages_offsets[index] = self.pages_offsets[
                self.current_image_index
            ].copy()
            self.pages_spinbox_values[index] = self.pages_spinbox_values[
                self.current_image_index
            ].copy()

    def apply_even_pages_button_clicked(self):
        for index in range(len(Store.CONVERT_PDF_RESULT.images)):
            if index == self.current_image_index:
                continue
            if (index + 1) % 2 != 0:
                continue
            self.pages_offsets[index] = self.pages_offsets[
                self.current_image_index
            ].copy()
            self.pages_spinbox_values[index] = self.pages_spinbox_values[
                self.current_image_index
            ].copy()

    def apply_odd_pages_button_clicked(self):
        for index in range(len(Store.CONVERT_PDF_RESULT.images)):
            if index == self.current_image_index:
                continue
            if (index + 1) % 2 == 0:
                continue
            self.pages_offsets[index] = self.pages_offsets[
                self.current_image_index
            ].copy()
            self.pages_spinbox_values[index] = self.pages_spinbox_values[
                self.current_image_index
            ].copy()

    def apply_specific_pages_button_clicked(self):
        specific_pages_value = (
            self.crop_amount_selection.specific_pages_line_edit.text()
        )
        specific_pages_value = specific_pages_value.replace(" ", "")
        match = re.match(self.specific_page_regex, specific_pages_value)
        if match:
            selected_pages = set[int]()
            page_selectors = specific_pages_value.split(",")
            for page in page_selectors:
                if "-" in page:
                    range_page = page.split("-")
                    start = int(range_page[0])
                    end = int(range_page[1]) + 1
                    for i in range(start, end):
                        selected_pages.add(i)
                else:
                    selected_pages.add(int(page))

            for page in selected_pages:
                image_page_index = page - 1
                if image_page_index < len(self.pages_offsets):
                    self.pages_offsets[image_page_index] = self.pages_offsets[
                        self.current_image_index
                    ].copy()
                    self.pages_spinbox_values[
                        image_page_index
                    ] = self.pages_spinbox_values[self.current_image_index].copy()

    def update_image_button_state(self):
        if self.current_image_index == 0:
            self.crop_amount_selection.disable_previous_button()
        if Store.CONVERT_PDF_RESULT is None:
            return
        if self.current_image_index == len(Store.CONVERT_PDF_RESULT.images) - 1:
            self.crop_amount_selection.disable_next_button()
        if 0 < self.current_image_index < len(Store.CONVERT_PDF_RESULT.images) - 1:
            self.crop_amount_selection.enable_next_button()
            self.crop_amount_selection.enable_previous_button()

        self.crop_amount_selection.update_page_label(
            f"Seite {self.current_image_index + 1} / {len(Store.CONVERT_PDF_RESULT.images) or 0}"
        )

    def next_image_button_clicked(self):
        if self.current_image_index < len(Store.CONVERT_PDF_RESULT.images) - 1:
            self.current_image_index += 1
            self.change_visible_image()
            self.update_spin_boxes()

        self.update_image_button_state()

    def previous_image_button_clicked(self):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.change_visible_image()
            self.update_spin_boxes()
        self.update_image_button_state()

    def horizontal_spinbox_changed(self, value: int):
        self._update_spin_box("horizontal", value)
        self.update_page_offset_dimension(self.current_image_index, "horizontal", value)
        self.change_visible_image()

    def vertical_spinbox_changed(self, value: int):
        self._update_spin_box("vertical", value)
        self.update_page_offset_dimension(self.current_image_index, "vertical", value)
        self.change_visible_image()

    def top_spin_box_changed(self, value: int):
        self._update_spin_box("top", value)
        self.update_page_offset_dimension(self.current_image_index, "top", value)
        self.change_visible_image()

    def right_spin_box_changed(self, value: int):
        self._update_spin_box("right", value)
        self.update_page_offset_dimension(self.current_image_index, "right", value)
        self.change_visible_image()

    def bottom_spin_box_changed(self, value: int):
        self._update_spin_box("bottom", value)
        self.update_page_offset_dimension(self.current_image_index, "bottom", value)
        self.change_visible_image()

    def left_spin_box_changed(self, value: int):
        self._update_spin_box("left", value)
        self.update_page_offset_dimension(self.current_image_index, "left", value)
        self.change_visible_image()

    def update_spin_boxes(self):
        self._update_spin_box(
            "top", int(self.pages_spinbox_values[self.current_image_index].top)
        )
        self._update_spin_box(
            "right", int(self.pages_spinbox_values[self.current_image_index].right)
        )
        self._update_spin_box(
            "bottom", int(self.pages_spinbox_values[self.current_image_index].bottom)
        )
        self._update_spin_box(
            "left", int(self.pages_spinbox_values[self.current_image_index].left)
        )
        self._update_spin_box(
            "horizontal", self.horizontal_spinbox_values[self.current_image_index]
        )
        self._update_spin_box(
            "vertical", self.vertical_spinbox_values[self.current_image_index]
        )

    def _update_spin_box(self, dimension: str, value: int):
        self.crop_amount_selection.block_spinbox_signals(True)
        if dimension == "horizontal":
            old_val = self.horizontal_spinbox_values[self.current_image_index]
            diff = value - old_val
            if diff != 0:
                self.left_spinbox().setMaximum(self.left_spinbox().maximum() + diff)
                self.right_spinbox().setMaximum(self.right_spinbox().maximum() - diff)
            self.horizontal_spinbox_values[self.current_image_index] = value
        elif dimension == "vertical":
            old_val = self.vertical_spinbox_values[self.current_image_index]
            diff = value - old_val
            if diff != 0:
                self.top_spinbox().setMaximum(self.top_spinbox().maximum() + diff)
                self.bottom_spinbox().setMaximum(self.bottom_spinbox().maximum() - diff)
            self.vertical_spinbox_values[self.current_image_index] = value
        else:
            if dimension == "top":
                old_val = self.pages_spinbox_values[self.current_image_index].top
                diff = value - old_val
                if diff != 0:
                    self.vertical_spinbox().setMinimum(
                        self.vertical_spinbox().minimum() + diff
                    )
            elif dimension == "bottom":
                old_val = self.pages_spinbox_values[self.current_image_index].bottom
                diff = value - old_val
                if diff != 0:
                    self.vertical_spinbox().setMaximum(
                        self.vertical_spinbox().maximum() - diff
                    )
            elif dimension == "left":
                old_val = self.pages_spinbox_values[self.current_image_index].left
                diff = value - old_val
                if diff != 0:
                    self.horizontal_spinbox().setMinimum(
                        self.horizontal_spinbox().minimum() + diff
                    )
            else:
                old_val = self.pages_spinbox_values[self.current_image_index].right
                diff = value - old_val
                if diff != 0:
                    self.horizontal_spinbox().setMaximum(
                        self.horizontal_spinbox().maximum() - diff
                    )
            self.pages_spinbox_values[self.current_image_index][dimension] = value
        self.crop_amount_selection.block_spinbox_signals(False)

    def update_page_offset(
        self, index: int, offset: Offset, horizontal_offset: int, vertical_offset: int
    ):
        self.update_page_offset_dimension(index, "top", int(offset.top))
        self.update_page_offset_dimension(index, "right", int(offset.right))
        self.update_page_offset_dimension(index, "bottom", int(offset.bottom))
        self.update_page_offset_dimension(index, "left", int(offset.left))
        self.update_page_offset_dimension(index, "horizontal", horizontal_offset)
        self.update_page_offset_dimension(index, "vertical", vertical_offset)

    def update_page_offset_dimension(self, index: int, dimension: str, value: int):
        new_pixel_offset = self.pts_to_pixel(index, dimension, value)

        if dimension == "horizontal":
            self.horizontal_pages_offsets[index] = new_pixel_offset
        elif dimension == "vertical":
            self.vertical_pages_offsets[index] = new_pixel_offset
        else:
            self.pages_offsets[index][dimension] = new_pixel_offset

    def pts_to_pixel(self, index: int, dimension: str, value: int):
        if dimension == "top" or dimension == "bottom":
            pts_size = Store.CONVERT_PDF_RESULT.pts_dimensions[index].height
            shape_index = 0
        else:
            pts_size = Store.CONVERT_PDF_RESULT.pts_dimensions[index].width
            shape_index = 1

        return pts_to_pixel(
            value,
            pts_size / Store.CONVERT_PDF_RESULT.images[index].shape[shape_index],
        )

    def show(self):
        self.update_page_offset(self.current_image_index, self.default_offset, 0, 0)
        self.crop_amount_selection.show_ui()
        self.update_image_button_state()
        self.change_visible_image()

    def reset(self):
        self.current_image_index = 0
        self.q_images = []

        self.default_offset = SaveConfig.get_default_crop_box_offset()
        self.crop_amount_selection.set_spin_box_values(self.default_offset, 0, 0)
        self.pages_offsets = []
        self.pages_spinbox_values = []
        self.update_image_button_state()
        self.crop_amount_selection.reset()

    def set_analysis_result(self):
        self.initialize_single_image_offsets()
        self.update_spin_boxes_max_value()

    def update_spin_boxes_max_value(self):
        # crop_box = self.analysis_result.transformed_box[self.current_image_index]
        #
        # image_shape = self.analysis_result.images[self.current_image_index].shape
        # width = image_shape[1]
        # height = image_shape[0]
        #
        # page_offset = self.pages_offsets[self.current_image_index]
        #
        # crop_box_including_offset = get_crop_box_pixel_including_offset(
        #     crop_box,
        #     page_offset,
        #     self.horizontal_pages_offsets[self.current_image_index],
        #     self.vertical_pages_offsets[self.current_image_index],
        #     self.analysis_result.images[self.current_image_index],
        # )
        #
        # pts_per_width = float(
        #     self.analysis_result.pts_dimensions[self.current_image_index].width / width
        # )
        # pts_per_height = float(
        #     self.analysis_result.pts_dimensions[self.current_image_index].height
        #     / height
        # )
        #
        # minimal_vertical_value = convert_to_pts(
        #     crop_box_including_offset.y * pts_per_height
        # )
        #
        # maximal_vertical_value = convert_to_pts(
        #     (height - crop_box_including_offset.y - crop_box_including_offset.height)
        #     * pts_per_height
        # )
        #
        # minimal_horizontal_value = convert_to_pts(
        #     crop_box_including_offset.x * pts_per_width
        # )
        #
        # maximal_horizontal_value = convert_to_pts(
        #     (width - crop_box_including_offset.x - crop_box_including_offset.width)
        #     * pts_per_width
        # )
        #
        # vertical_spinbox = self.vertical_spinbox()
        # horizontal_spinbox = self.horizontal_spinbox()
        # top_spinbox = self.top_spinbox()
        # right_spinbox = self.right_spinbox()
        # bottom_spinbox = self.bottom_spinbox()
        # left_spinbox = self.left_spinbox()
        #
        # if minimal_vertical_value > 0:
        #     vertical_spinbox.setMinimum(-minimal_vertical_value)
        #     top_spinbox.setMaximum(
        #         minimal_vertical_value
        #         + convert_to_pts(page_offset.top * pts_per_height)
        #     )
        # else:
        #     vertical_spinbox.setMinimum(0)
        #     top_spinbox.setMaximum(0)
        #
        # height_pts = convert_to_pts(height * pts_per_height)
        #
        # if maximal_vertical_value < height_pts:
        #     vertical_spinbox.setMaximum(maximal_vertical_value)
        #     bottom_spinbox.setMaximum(
        #         maximal_vertical_value
        #         + convert_to_pts(page_offset.bottom * pts_per_height)
        #     )
        # else:
        #     vertical_spinbox.setMaximum(height_pts)
        #     bottom_spinbox.setMaximum(height_pts)
        #
        # if minimal_horizontal_value > 0:
        #     horizontal_spinbox.setMinimum(-minimal_horizontal_value)
        #     left_spinbox.setMaximum(
        #         minimal_horizontal_value
        #         + convert_to_pts(page_offset.left * pts_per_height)
        #     )
        # else:
        #     horizontal_spinbox.setMinimum(0)
        #     left_spinbox.setMaximum(0)
        #
        # width_pts = convert_to_pts(width * pts_per_width)
        #
        # if maximal_horizontal_value < width_pts:
        #     horizontal_spinbox.setMaximum(maximal_horizontal_value)
        #     right_spinbox.setMaximum(
        #         maximal_horizontal_value
        #         + convert_to_pts(page_offset.right * pts_per_width)
        #     )
        # else:
        #     horizontal_spinbox.setMaximum(width_pts)
        #     right_spinbox.setMaximum(width_pts)

        self.top_spinbox().setMaximum(9999)
        self.right_spinbox().setMaximum(9999)
        self.bottom_spinbox().setMaximum(9999)
        self.left_spinbox().setMaximum(9999)

    def get_transformed_crop_boxes_pts(self):
        transformed_boxes_pts = []

        transformed_boxes = self.analysis_result.transformed_box
        for index, box in enumerate(transformed_boxes):
            box = get_crop_box_pts(
                box,
                self.pages_offsets[index],
                self.horizontal_pages_offsets[index],
                self.vertical_pages_offsets[index],
                Store.CONVERT_PDF_RESULT.images[index],
                Store.CONVERT_PDF_RESULT.pts_dimensions[index],
                True,
            )
            transformed_boxes_pts.append(box)

        return transformed_boxes_pts

    def get_max_crop_box_pts(self):
        return get_crop_box_pts(
            Store.CROP_BOX_ANALYSIS_RESULT.max_box,
            self.pages_offsets[Store.CROP_BOX_ANALYSIS_RESULT.min_index],
            self.horizontal_pages_offsets[Store.CROP_BOX_ANALYSIS_RESULT.min_index],
            self.vertical_pages_offsets[Store.CROP_BOX_ANALYSIS_RESULT.min_index],
            Store.CONVERT_PDF_RESULT.images[Store.CROP_BOX_ANALYSIS_RESULT.min_index],
            Store.CONVERT_PDF_RESULT.pts_dimensions[
                Store.CROP_BOX_ANALYSIS_RESULT.min_index
            ],
            True,
        )

    def get_transformed_crop_boxes_pixel(self):
        transformed_boxes = []
        for index, box in enumerate(Store.CROP_BOX_ANALYSIS_RESULT.transformed_box):
            transformed_boxes.append(
                get_crop_box_pixel_including_offset(
                    box,
                    self.pages_offsets[index],
                    self.horizontal_pages_offsets[index],
                    self.vertical_pages_offsets[index],
                    Store.CONVERT_PDF_RESULT.images[index],
                    True,
                )
            )
        return transformed_boxes

    def get_transformed_crop_boxes_pts(self):
        transformed_boxes = []
        for index, box in enumerate(Store.CROP_BOX_ANALYSIS_RESULT.transformed_box):
            transformed_boxes.append(
                get_crop_box_pts(
                    box,
                    self.pages_offsets[index],
                    self.horizontal_pages_offsets[index],
                    self.vertical_pages_offsets[index],
                    Store.CONVERT_PDF_RESULT.images[index],
                    Store.CONVERT_PDF_RESULT.pts_dimensions[index],
                    True,
                )
            )
        return transformed_boxes

    def get_max_crop_box_pixel(self):
        return get_crop_box_pixel_including_offset(
            Store.CROP_BOX_ANALYSIS_RESULT.max_box,
            self.pages_offsets[Store.CROP_BOX_ANALYSIS_RESULT.min_index],
            self.horizontal_pages_offsets[Store.CROP_BOX_ANALYSIS_RESULT.min_index],
            self.vertical_pages_offsets[Store.CROP_BOX_ANALYSIS_RESULT.min_index],
            Store.CONVERT_PDF_RESULT.images[Store.CROP_BOX_ANALYSIS_RESULT.min_index],
            True,
        )

    def create_q_image(self, index: int):
        image = Store.CONVERT_PDF_RESULT.images[index]
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(
            image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888
        )
        self.q_images.append(q_image)

    def horizontal_spinbox(self):
        return self.crop_amount_selection.horizontal_spin_box

    def vertical_spinbox(self):
        return self.crop_amount_selection.vertical_spin_box

    def top_spinbox(self):
        return self.crop_amount_selection.top_spin_box

    def right_spinbox(self):
        return self.crop_amount_selection.right_spin_box

    def bottom_spinbox(self):
        return self.crop_amount_selection.bottom_spin_box

    def left_spinbox(self):
        return self.crop_amount_selection.left_spin_box
