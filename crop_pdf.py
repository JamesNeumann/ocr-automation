import uuid
from time import time

import cv2
from numpy import ndarray
from pathlib import Path

from convert_pdf import convert_pdf_to_image, convert_pil_images_to_cv2_format
from utils.console import console
from rich.progress import track


def get_crop_box(path_to_pdf: str) -> (float, float, float, float):
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

    for i, image in track(enumerate(cv2_images), description="Detecting text...", total=len(cv2_images)):

        contours, _ = find_contours_on_image(image)

        for cnt in contours:
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

    for i, image in enumerate(cv2_images):
        cv2.rectangle(image, (global_min_x, global_min_y), (global_max_x, global_max_y), (255, 0, 0), 2)
        cv2.imwrite(f"./converted_files/{file_id}/{i}.png", image)

    console.log(f"Needed {time() - start_time}s to convert {len(images)} PDF-files")

    pts_constant = 0.352778

    pts_per_width = pts_width / width
    pts_per_height = pts_height / height

    min_x_mm = float(pts_per_width) * global_min_x * pts_constant
    min_y_mm = float(pts_per_width) * global_min_y * pts_constant

    max_x_mm = float(pts_per_height) * global_max_x * pts_constant
    max_y_mm = float(pts_per_height) * global_max_y * pts_constant

    return min_x_mm, min_y_mm, max_x_mm - min_x_mm, max_y_mm - min_y_mm


def find_contours_on_image(image: ndarray):
    gray_scale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    ret, threshold = cv2.threshold(gray_scale_image, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))

    dilation = cv2.dilate(threshold, rect_kernel, iterations=1)

    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    return contours, hierarchy
