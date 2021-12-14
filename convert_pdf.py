import glob
import multiprocessing
import tempfile
from time import time
from typing import List, Any
import numpy as np
from PIL.Image import Image
from PyPDF2 import PdfFileReader
from numpy import ndarray

from pdf2image import convert_from_path
from rich.progress import  track
from utils.console import console


def convert_pdf_to_image(path_to_pdf: str) -> (List[Image], float, float):
    converted_images = None

    pdf_file_reader = PdfFileReader(open(path_to_pdf, "rb"))
    _, _, upper_left, upper_right = pdf_file_reader.getPage(0).mediaBox
    start_time = time()
    console.log(f"{path_to_pdf} is being converted")
    try:
        with tempfile.TemporaryDirectory() as path:
            converted_images = convert_from_path(
                pdf_path=path_to_pdf,
                output_folder=path,
                poppler_path="./Poppler/Library/bin",
                thread_count=multiprocessing.cpu_count(),
            )
        console.log(f"Needed {time() - start_time} seconds to convert {path_to_pdf} to images")
    except Exception as e:
        print(e)

    return converted_images, upper_left, upper_right


def convert_pdfs_to_images() -> (List[List[Image]], float, float):
    result_images = []
    files_to_convert = glob.glob('./files/*.pdf')
    for file in files_to_convert:
        images, pts_width, pts_height = convert_pdf_to_image(file)
        result_images.append([images, pts_width, pts_width])
    return result_images


def convert_pil_images_to_cv2_format(pil_images: List[Image]) -> List[ndarray]:
    cv2_images = []
    for image in track(pil_images, description="Converting image to cv2 format..."):
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
