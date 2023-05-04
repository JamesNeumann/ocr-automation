from typing import List

import numpy as np

from utils.rectangle import Rectangle


class AnalysisResult:
    """
    Class for storing the results of an PDF-analysis for the optimal crop box
    """

    def __init__(
        self,
        *,
        images: List[np.ndarray],
        pts_width: float,
        pts_height: float,
        min_index: int,
        max_box: Rectangle,
        crop_boxes: List[Rectangle],
        transformed_boxes: List[Rectangle],
        pts_dimensions: List[Rectangle],
        is_grayscale: bool = False
    ):
        self.images = images
        self.pts_width = pts_width
        self.pts_height = pts_height
        self.min_index = min_index
        self.max_box = max_box
        self.crop_boxes = crop_boxes
        self.transformed_box = transformed_boxes
        self.pts_dimensions = pts_dimensions
        self.is_grayscale = is_grayscale
