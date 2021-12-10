import glob
import tempfile
from typing import List, Any
import numpy as np
from PIL.Image import Image
from numpy import ndarray

from pdf2image import convert_from_path

from utils.console import console


def convert_pdf_to_image(path_to_pdf: str) -> List[Image]:
    converted_images = None
    console.log(f"{path_to_pdf} is being converted")
    try:
        with tempfile.TemporaryDirectory() as path:
            converted_images = convert_from_path(
                pdf_path=path_to_pdf,
                output_folder=path,
            )
    except Exception as e:
        print(e)

    return converted_images


def convert_pdfs_to_images() -> List[List[Image]]:
    result_images = []
    files_to_convert = glob.glob('./files/*.pdf')
    for file in files_to_convert:
        result_images.append(convert_pdf_to_image(file))
    return result_images


def convert_pil_images_to_cv2_format(pil_images: List[Image]) -> List[ndarray]:
    cv2_images = []
    for image in pil_images:
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