import uuid
from pathlib import Path
from time import time
from typing import List, Callable

import cv2
from numpy import ndarray
from rich.progress import track

from utils.console import console
from utils.conversion import convert_to_pts
from utils.convert_pdf import convert_pdf_to_image, convert_pil_images_to_cv2_format
from utils.rectangle import Rectangle


def get_pdf_pages_as_images(path_to_pdf: str, progress_callback: Callable[[int], None]) -> (
        List[ndarray], float, float):
    images, pts_width, pts_height = convert_pdf_to_image(path_to_pdf)
    cv2_images = convert_pil_images_to_cv2_format(images, progress_callback)
    return cv2_images, pts_width, pts_height


def get_crop_box_pixel(images: List[ndarray], progress_callback: Callable[[int], None]) -> Rectangle:

    global_max_x = 0
    global_min_x = 999999999
    global_max_y = 0
    global_min_y = 999999999

    width = images[0].shape[0]
    height = images[0].shape[0]

    for i, image in track(enumerate(images), description="Detecting text...".ljust(40), total=len(images),
                          console=console):

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
                    # cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    global_min_x = max(0, global_min_x)
    global_min_y = max(0, global_min_y)
    global_max_x = min(width, global_max_x)
    global_max_y = min(height, global_max_y)
    progress_callback(50)
    return Rectangle(global_min_x, global_min_y, global_max_x, global_max_y)


def get_crop_box(path_to_pdf: str, offsetLeft: int = 0,
                 offsetRight: int = 0, offsetTop: int = 0, offsetBottom: int = 0) -> (Rectangle, List[ndarray]):
    """
    Calculates the crop box for the given PDF

    :param path_to_pdf: The path to the PDF
    :param offset: The offset to add to the resulting crop box
    :return: The calculated crop box
    """

    images, pts_width, pts_height = convert_pdf_to_image(path_to_pdf)
    cv2_images = convert_pil_images_to_cv2_format(images)
    file_id = uuid.uuid4()
    Path(f"./converted_files/{file_id}").mkdir(parents=True, exist_ok=True)

    start_time = time()

    global_max_x = 0
    global_min_x = 999999999
    global_max_y = 0
    global_min_y = 999999999

    width = images[0].width
    height = images[0].height

    for i, image in track(enumerate(cv2_images), description="Detecting text...".ljust(40), total=len(cv2_images),
                          console=console):

        progress = i / (len(cv2_images) * 2)
        progress = round(progress, 2)

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
                    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    global_min_x = max(0, global_min_x - offsetLeft)
    global_min_y = max(0, global_min_y - offsetTop)
    global_max_x = min(width, global_max_x + offsetRight)
    global_max_y = min(height, global_max_y + offsetBottom)

    # for i, image in track(enumerate(cv2_images), description="Saving images...".ljust(40), total=len(cv2_images),
    #                       console=console):
    #     cv2.rectangle(image, (global_min_x, global_min_y), (global_max_x, global_max_y), (255, 0, 0), 2)
    #     copped_image = image[global_min_y:global_max_y, global_min_x:global_max_x]
    #     cv2.imwrite(f"./converted_files/{file_id}/{i}.png", copped_image)

    console.log(f"Needed {time() - start_time} seconds to convert {len(images)} PDF-files")

    pts_per_width = pts_width / width
    pts_per_height = pts_height / height

    min_x_mm = convert_to_pts(float(pts_per_width) * global_min_x)
    min_y_mm = convert_to_pts(float(pts_per_width) * global_min_y)

    max_x_mm = convert_to_pts(float(pts_per_height) * global_max_x)
    max_y_mm = convert_to_pts(float(pts_per_height) * global_max_y)

    min_x_mm = max(min_x_mm, 0)
    min_y_mm = max(min_y_mm, 0)

    max_x_mm = min(max_x_mm - min_x_mm, convert_to_pts(float(pts_width)))
    max_y_mm = min(max_y_mm - min_y_mm, convert_to_pts(float(pts_height)))

    return Rectangle(min_x_mm, min_y_mm, max_x_mm, max_y_mm), cv2_images


def find_contours_on_image(image: ndarray):
    """
    Find all contours on the given image

    :param image: Image to find contours on
    :return: The found contours and the hierarchy
    """
    gray_scale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray_scale_image, (7, 7), 0)
    ret, threshold = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (16, 16))

    dilation = cv2.dilate(threshold, rect_kernel, iterations=1)

    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    return contours, hierarchy
