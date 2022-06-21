import multiprocessing
from pathlib import Path
from time import time
from typing import List, Callable

import numpy as np
from PIL.Image import Image
from PyPDF2 import PdfFileReader
from numpy import ndarray
from pdf2image import convert_from_path
from rich.progress import track

from config import Config
from utils.console import console
from utils.file_utils import wait_until_file_is_unlocked
from utils.rectangle import Rectangle
from utils.save_config import SaveConfig


def convert_pdf_to_image(
        path_to_pdf: str, attempts: int = 5
) -> (List[Image], float, float, int, List[Rectangle]):
    """
    Converts each page of the given PDF to an image

    :param path_to_pdf: Path to the PDF file that should be converted
    :param attempts: How often it should be attempted to open the file
    :return list of all images and the width and height in pts
    """
    converted_images = None
    pdf_file_reader = None
    i = 0
    while i < attempts:
        try:
            wait_until_file_is_unlocked(path_to_pdf)
            with open(path_to_pdf, "rb") as f:
                pdf_file_reader = PdfFileReader(f)
                if pdf_file_reader is not None:
                    break
        except FileNotFoundError as e:
            console.log(e)
        i += 1

    if pdf_file_reader is None:
        console.log("[red]PDF konnte nicht gefunden werden")

    min_height = 99999999
    min_width = 99999999
    min_index = 0

    pts_dimensions = []

    file_name = Path(path_to_pdf).stem
    with open(path_to_pdf, "rb") as f:
        pdf_file_reader = PdfFileReader(f)
        for number in range(pdf_file_reader.getNumPages()):
            x, y, width, height = pdf_file_reader.getPage(number).mediaBox

            pts_dimensions.append(Rectangle(x, y, width, height))

            if width < min_width:
                min_width = width
                min_index = number
            if height < min_height:
                min_height = height

        start_time = time()
        console.log(f"{file_name} is being converted")
        try:

            console.log("Reading PDF with: ", SaveConfig.get_dpi_value())
            converted_images = convert_from_path(
                pdf_path=path_to_pdf,
                output_folder=Config.OCR_WORKING_DIR,
                poppler_path="./Poppler/Library/bin",
                thread_count=multiprocessing.cpu_count(),
                jpegopt=True,
                dpi=SaveConfig.get_dpi_value(),
            )
            console.log(
                f"Needed {time() - start_time} seconds to convert {file_name} to images"
            )
        except Exception as e:
            console.log(e, e)

    return converted_images, min_width, min_height, min_index, pts_dimensions


def convert_pil_images_to_cv2_format(
        pil_images: List[Image], progress_callback: Callable[[int], None]
) -> List[ndarray]:
    """
    Converts Image in PIL format to cv2 format

    :param pil_images: PIL Images to convert
    :param progress_callback: Callback for progress display
    :return List of all images in cv2 format
    """
    cv2_images = []
    for i, image in track(
            enumerate(pil_images),
            description="Converting image to cv2 format...".ljust(40),
            console=console,
            total=len(pil_images),
    ):
        progress = i / (len(pil_images) * 2)
        progress = round(progress, 2)
        progress_callback(progress * 100)
        cv2_images.append(convert_pil_to_cv2_format(image))
    return cv2_images


def convert_pil_to_cv2_format(pil_image: Image) -> ndarray:
    """
    Converts a Pillow image into the format needed by Opencv
    :param pil_image: The Pillow image that should be converted
    :return: Converted image
    """
    open_cv_image = np.array(pil_image)
    open_cv_image = open_cv_image[:, :, ::-1].copy()
    return open_cv_image
