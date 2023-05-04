from typing import List, Callable

import cv2
import numpy
from PyPDF2 import PdfReader
from numpy import ndarray
import numpy as np
from rich.progress import track

from config import Config
from utils.console import console
from utils.convert_pdf import convert_pdf_to_image, convert_pil_images_to_cv2_format
from utils.rectangle import Rectangle
from utils.save_config import SaveConfig


def get_pdf_pages_as_images(
    path_to_pdf: str, progress_callback: Callable[[int], None]
) -> (List[ndarray], float, float, int, List[Rectangle]):
    """
    Returns the pages of the given PDF as images. Also returns the width and height in pts
    :param path_to_pdf: Path to the PDF that should be converted
    :param progress_callback: Callback to visualize progress
    :return: PDF pages as images, width in pts, height in pts
    """
    images, pts_width, pts_height, index, pts_dimensions = convert_pdf_to_image(
        path_to_pdf
    )
    cv2_images = convert_pil_images_to_cv2_format(images, progress_callback)
    return cv2_images, pts_width, pts_height, index, pts_dimensions


def get_crop_box_pixel(
    images: List[ndarray], progress_callback: Callable[[int], None]
) -> Rectangle:
    """
    Calculates the crop box in pixel dimension
    :param images: Images to analyze
    :param progress_callback: Callback to visualize progress
    :return: The crop box rectangle
    """

    width, height = get_max_image_size(images)

    crop_box = get_maximum_crop_box(images, width, height, progress_callback)
    for i, image in track(
        enumerate(images),
        description="Saving images...".ljust(55),
        total=len(images),
        console=console,
    ):
        cv2.rectangle(
            image,
            (crop_box.x, crop_box.width),
            (crop_box.y, crop_box.height),
            (255, 0, 0),
            2,
        )
        # cropped_image = image[global_min_y:global_max_y, global_min_x:global_max_x]
        cv2.imwrite(f"converted_files/{i}.png", image)

    progress_callback(50)
    return crop_box


def get_max_image_size(images: List[ndarray]) -> (float, float):
    """
    Returns the maximum width and height of the given images
    :param images: Images to analyze for maximum width and height
    :return: Width, Height
    """
    height = 999999
    width = 999999
    for image in images:
        if image.shape[0] < height:
            height = image.shape[0]
        if image.shape[1] < width:
            width = image.shape[1]

    return width, height


def get_maximum_crop_box(
    images: List[ndarray],
    width: float,
    height: float,
    progress_callback: Callable[[int], None],
) -> Rectangle:
    global_min_x = width
    global_min_y = height
    global_max_x = 0
    global_max_y = 0

    for i, image in track(
        enumerate(images),
        description="Text wird erkannt...".ljust(55),
        total=len(images),
        console=console,
    ):
        progress = i / (len(images) * 2)
        progress = round(progress, 2)

        progress_callback(progress * 100)

        contours, hierarchy = find_contours_on_image(image)
        for j, cnt in enumerate(contours):
            if hierarchy[0][j][2] == -1:
                if cv2.contourArea(cnt) > 1000:
                    x, y, w, h = cv2.boundingRect(cnt)
                    if x < global_min_x:
                        global_min_x = x
                    if x + w > global_max_x:
                        global_max_x = x + w
                    if y < global_min_y:
                        global_min_y = y
                    if y + h > global_max_y:
                        global_max_y = y + h
                    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 6)

    global_min_x = max(0, global_min_x)
    global_min_y = max(0, global_min_y)
    global_max_x = min(width, global_max_x)
    global_max_y = min(height, global_max_y)

    return Rectangle(global_min_x, global_min_y, global_max_x, global_max_y)


def get_crop_boxes(
    images: List[ndarray],
    progress_callback: Callable[[int], None],
    *,
    render_debug_lines: bool = False,
    save_images: bool = False,
) -> (List[Rectangle], Rectangle, int):
    """
    Calculates the crop box in pixel dimension
    :param images: Images to analyze
    :param progress_callback: Callback to visualize progress
    :param render_debug_lines: If debug lines should be rendered on the image
    :param save_images: If the images should be saved
    :return: The crop box rectangle
    """
    image_crop_boxes = []
    max_crop_box = Rectangle(0, 0, 0, 0)
    max_index = 0
    # width, height = get_max_image_size(images)

    stroke_width = int(Config.map_dpi_to_pen_width(SaveConfig.get_dpi_value()))
    for i, image in track(
        enumerate(images),
        description="Text wird erkannt...".ljust(55),
        total=len(images),
        console=console,
    ):
        progress = i / (len(images))
        progress = round(progress, 2)
        progress_callback(int(progress * 100))

        image_crop_box = get_image_crop_box(image)
        image_crop_boxes.append(image_crop_box)

        if image_crop_box.area() > max_crop_box.area():
            max_crop_box = image_crop_box
            max_index = i

        if image.shape[1] < max_crop_box.width:
            max_crop_box.x = 0
            max_crop_box.width = image.shape[1]
            max_index = i

        if image.shape[0] < max_crop_box.height:
            max_crop_box.y = 0
            max_crop_box.height = image.shape[0]
            max_index = i

        if render_debug_lines:
            cv2.rectangle(
                image,
                (image_crop_box.x, image_crop_box.y),
                (
                    image_crop_box.width + image_crop_box.x,
                    image_crop_box.height + image_crop_box.y,
                ),
                (0, 0, 255),
                stroke_width,
            )

    if save_images:
        for i, image in track(
            enumerate(images),
            description="Saving images...".ljust(55),
            total=len(images),
            console=console,
        ):
            cv2.rectangle(
                image,
                (max_crop_box.x, max_crop_box.y),
                (
                    max_crop_box.width + max_crop_box.x,
                    max_crop_box.height + max_crop_box.y,
                ),
                (0, 255, 255),
                10,
            )
            # cv2.rectangle(image, (max_crop_box.x, max_crop_box.y), (max_crop_box.width, max_crop_box.height), (255, 0, 0),
            #               2)
            # cropped_image = image[global_min_y:global_max_y, global_min_x:global_max_x]
            cv2.imwrite(f"converted_files/{i}.png", image)

    return image_crop_boxes, max_crop_box, max_index


def get_image_crop_box(image: ndarray) -> Rectangle:
    """
    Calculates the crop box for the given image, so that the hole text is contained in the box.
    The returned box contains the width and height relative to the x and y coordinates.
    Therefore, (x + width, y) results in the top right pixel coordinate
    :param image: Image to analyze
    :return: Resulting crop box
    """
    image_crop_box = Rectangle(99999, 99999, 0, 0)

    contours, hierarchy = find_contours_on_image(image)
    for j, cnt in enumerate(contours):
        if hierarchy[0][j][2] == -1:
            if cv2.contourArea(cnt) > 1000:
                x, y, w, h = cv2.boundingRect(cnt)
                # console.log("x : ", x, "y: ", y, "w: ", w, "h: ", h)
                if x < image_crop_box.x:
                    image_crop_box.x = x
                if x + w > image_crop_box.width:
                    image_crop_box.width = w + x
                if y < image_crop_box.y:
                    image_crop_box.y = y
                # console.log(y + h)
                if y + h > image_crop_box.height:
                    image_crop_box.height = y + h

    image_crop_box.width = image_crop_box.width - image_crop_box.x
    image_crop_box.height = image_crop_box.height - image_crop_box.y

    return image_crop_box


def find_contours_on_image(image: ndarray):
    """
    Find all contours on the given image

    :param image: Image to find contours on
    :return: The found contours and the hierarchy
    """
    gray_scale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray_scale_image, (7, 7), 0)
    ret, threshold = cv2.threshold(
        blur, 20, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (16, 16))

    dilation = cv2.dilate(threshold, rect_kernel, iterations=1)

    contours, hierarchy = cv2.findContours(
        dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )

    return contours, hierarchy


def analyze_pdf_orientation(
    path_to_pdf: str, progress_callback: Callable[[float], None]
) -> (List[int], List[int]):
    """
    Analyzes PDF orientation

    :param path_to_pdf: Path to the PDF
    :param progress_callback: Callback for execution progress
    :return: (Amount of landscaped images, Amount of portraits images)
    """
    pdf_file_reader = PdfReader(path_to_pdf)

    landscaped = []
    portraits = []

    num_pdf_files = pdf_file_reader.getNumPages()

    for index in range(num_pdf_files):
        box = pdf_file_reader.getPage(index).mediabox
        if (
            box.getUpperRight_x() - box.getUpperLeft_x()
            > box.getUpperRight_y() - box.getLowerRight_y()
        ):
            landscaped.append(index)
        else:
            portraits.append(index)
        progress_callback(index / num_pdf_files)
    progress_callback(1)
    return landscaped, portraits


def crop_images_single_box(images: List[ndarray], crop_box: Rectangle) -> List[ndarray]:
    """
    Crops the images with the given crop box
    :param images: Images to crop
    :param crop_box: Rectangle for cropping the images
    :return: Cropped images
    """
    return [crop_image(image, crop_box) for image in images]


def crop_images_multiple_boxes(images: List[ndarray], crop_boxes: List[Rectangle]):
    """
    Crops the images with the given crop boxes
    :param images: Images to crop
    :param crop_boxes: Rectangles for cropping the images
    :return: Cropped images
    """
    if len(images) != len(crop_boxes):
        raise ValueError("The number of images and crop_boxes have to be equal")

    cropped_images = []
    for index, image in enumerate(images):
        cropped_image = crop_image(image, crop_boxes[index])
        cropped_shape = cropped_image.shape
        image_shape = image.shape
        cropped_images.append(cropped_image)

    return cropped_images


def crop_image(image: ndarray, crop_box: Rectangle) -> ndarray:
    return image[
        crop_box.y : crop_box.y + crop_box.height,
        crop_box.x : crop_box.x + crop_box.width,
    ]


def is_grayscale(images: ndarray):
    print(images.shape)


def should_pdf_pages_be_cropped_individual(crop_boxes: Rectangle) -> bool:
    return True
