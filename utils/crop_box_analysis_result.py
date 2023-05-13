from typing import List

import numpy as np

from utils.rectangle import Rectangle


class CropBoxAnalysisResult:
    """
    Class for storing the results of an PDF-analysis for the optimal crop box
    """

    def __init__(
        self,
        *,
        min_index: int,
        max_box: Rectangle,
        crop_boxes: List[Rectangle],
        transformed_boxes: List[Rectangle],
    ):
        self.min_index = min_index
        self.max_box = max_box
        self.crop_boxes = crop_boxes
        self.transformed_box = transformed_boxes
