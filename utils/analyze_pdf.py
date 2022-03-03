from typing import List, Callable

import cv2
from PyPDF2 import PdfFileReader
from numpy import ndarray
from rich.progress import track

from utils.console import console
from utils.convert_pdf import convert_pdf_to_image, convert_pil_images_to_cv2_format
from utils.rectangle import Rectangle


def get_pdf_pages_as_images(path_to_pdf: str, progress_callback: Callable[[int], None]) -> (
        List[ndarray], float, float):
    """
    Returns the pages of the given PDF as images. Also returns the width and height in pts
    :param path_to_pdf: Path to the PDF that should be converted
    :param progress_callback: Callback to visualize progress
    :return: PDF pages as images, width in pts, height in pts
    """
    images, pts_width, pts_height, index = convert_pdf_to_image(path_to_pdf)
    cv2_images = convert_pil_images_to_cv2_format(images, progress_callback)
    return cv2_images, pts_width, pts_height, index


def get_crop_box_pixel(images: List[ndarray], progress_callback: Callable[[int], None]) -> Rectangle:
    """
    Calculates the crop box in pixel dimension
    :param images: Images to analyze
    :param progress_callback: Callback to visualize progress
    :return: The crop box rectangle
    """

    height = 999999
    width = 999999
    for image in images:
        if image.shape[0] < height:
            height = image.shape[0]
        if image.shape[1] < width:
            width = image.shape[1]

    global_min_x = width
    global_min_y = height
    global_max_x = 0
    global_max_y = 0

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

    global_min_x = max(0, global_min_x)
    global_min_y = max(0, global_min_y)
    global_max_x = min(width, global_max_x)
    global_max_y = min(height, global_max_y)
    progress_callback(50)
    return Rectangle(global_min_x, global_min_y, global_max_x, global_max_y)


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


def analyze_pdf_orientation(path_to_pdf: str, progress_callback: Callable[[float], None]) -> (List[int], List[int]):
    """
    Analyzes PDF orientation

    :param path_to_pdf: Path to the PDF
    :param progress_callback: Callback for execution progress
    :return: (Amount of landscaped images, Amount of portraits images)
    """
    with open(path_to_pdf, "rb") as f:
        pdf_file_reader = PdfFileReader(f)

        landscaped = []
        portraits = []

        num_pdf_files = pdf_file_reader.getNumPages()

        for index in range(num_pdf_files):
            box = pdf_file_reader.getPage(index).mediaBox
            if box.getUpperRight_x() - box.getUpperLeft_x() > box.getUpperRight_y() - box.getLowerRight_y():
                landscaped.append(index)
            else:
                portraits.append(index)
            progress_callback(index / num_pdf_files)

        progress_callback(1)
    return landscaped, portraits
