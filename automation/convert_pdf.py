import multiprocessing
import shutil
import tempfile
from time import time
from typing import List

import numpy as np
from PIL.Image import Image
from PyPDF2 import PdfFileReader
from numpy import ndarray
from pdf2image import convert_from_path
from rich.progress import track

from ui.progress_bar import ProgressBar
from utils.console import console


def convert_pdf_to_image(path_to_pdf: str) -> (List[Image], float, float):
    """
    Converts each page of the given PDF to an image
    :param path_to_pdf: Path to the PDF file that should be converted
    :return list of all images and the width and height in pts
    """
    converted_images = None

    pdf_file_reader = PdfFileReader(open(path_to_pdf, "rb"))
    _, _, upper_left, upper_right = pdf_file_reader.getPage(0).mediaBox
    start_time = time()
    console.log(f"{path_to_pdf} is being converted")
    try:
        temp_path = None
        with tempfile.TemporaryDirectory() as path:
            temp_path = path
            # console.log(temp_path)
            converted_images = convert_from_path(
                pdf_path=path_to_pdf,
                output_folder=path,
                poppler_path="./Poppler/Library/bin",
                thread_count=multiprocessing.cpu_count(),
            )

        try:
            shutil.rmtree(temp_path)
        except Exception as e:
            console.log(e)
        console.log(f"Needed {time() - start_time} seconds to convert {path_to_pdf} to images")
    except Exception as e:
        console.log(e, e)

    return converted_images, upper_left, upper_right


def convert_pil_images_to_cv2_format(pil_images: List[Image], progress_bar: ProgressBar) -> List[ndarray]:
    """
    Converts Image in PIL format to cv2 format
    :param pil_images: PIL Images to convert
    :return List of all images in cv2 format
    """
    cv2_images = []
    for i, image in track(enumerate(pil_images), description="Converting image to cv2 format...".ljust(40),
                          console=console, total=len(pil_images)):
        progress = i / (len(pil_images) * 2)
        progress = round(progress, 2)
        if progress_bar:
            progress_bar.setValue(progress * 100)
        cv2_images.append(convert_pil_to_cv2_format(image))
    if progress_bar:
        progress_bar.setValue(50)
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
