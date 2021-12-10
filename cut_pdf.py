import uuid

import cv2
from numpy import ndarray
from pathlib import Path

from convert_pdf import convert_pdf_to_image, convert_pil_images_to_cv2_format
from utils.console import console


def cut_pdf(path_to_pdf: str):
    images = convert_pdf_to_image(path_to_pdf)
    cv2_images = convert_pil_images_to_cv2_format(images)
    file_id = uuid.uuid4()
    Path(f"./converted_files/{file_id}").mkdir(parents=True, exist_ok=True)

    global_max_x = 0
    global_min_x = 999999999
    global_max_y = 0
    global_min_y = 999999999

    for i, image in enumerate(cv2_images):
        console.log(f"Detect text of page {i} of {len(images)}")

        width = images[i].width
        height = images[i].height

        gray_scale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        ret, threshold = cv2.threshold(gray_scale_image, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))

        dilation = cv2.dilate(threshold, rect_kernel, iterations=1)

        contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

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
        cv2.rectangle(image, (global_min_x, global_min_y), (global_max_x, global_max_y), (0, 255, 0), 2)
        cv2.imwrite(f"./converted_files/{file_id}/{i}.png", image)


def find_text_on_image(image: ndarray) -> None:
    pass
