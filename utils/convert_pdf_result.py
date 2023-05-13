from typing import List

import numpy as np

from utils.rectangle import Rectangle


class ConvertPdfResult:
    """
    Class for storing the results of a PDF-analysis after converting to images
    """

    def __init__(
        self,
        *,
        path_to_pdf: str,
        images: List[np.ndarray],
        pts_width: float,
        pts_height: float,
        pts_dimensions: List[Rectangle],
    ):
        self.path_to_pdf = path_to_pdf
        self.images = images
        self.pts_width = pts_width
        self.pts_height = pts_height
        self.pts_dimensions = pts_dimensions
