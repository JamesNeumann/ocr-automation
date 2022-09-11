import uuid
from typing import List, Callable

import cv2
import img2pdf
from PyQt6.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool, pyqtSlot
from numpy import ndarray

from automation.ocr_automation import OcrAutomation
from config import Config
from ui.components.progress_bar import ProgressBar
from ui.steps.step import Step
from utils.analyze_pdf import crop_images_multiple_boxes
from utils.console import console
from utils.conversion import convert_to_pts
from utils.rectangle import Rectangle
from utils.save_config import SaveConfig
from PyPDF2 import PdfReader, PdfWriter

from utils.translate import translate


class CropRunningSignals(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)


class CropRunningWorker(QRunnable):
    def __init__(
        self,
        path_to_pdf: str,
        crop_rectangle: Rectangle,
        crop_rectangles: List[Rectangle],
        images: List[ndarray],
        progress_callback: Callable,
        pts_rectangles: List[Rectangle],
    ):
        super(CropRunningWorker, self).__init__()
        self.signals = CropRunningSignals()
        self.path_to_pdf = path_to_pdf
        self.crop_rectangle = crop_rectangle
        self.crop_rectangles = crop_rectangles
        self.images = images
        self.progress_callback = progress_callback
        self.pts_rectangles = pts_rectangles

    @pyqtSlot()
    def run(self) -> None:
        max_x_center_diff = 0
        for crop_rect in self.crop_rectangles:
            for crop_rect_inner in self.crop_rectangles:
                x_center_diff = abs(crop_rect.center_x - crop_rect_inner.center_x)
                if x_center_diff > max_x_center_diff:
                    max_x_center_diff = x_center_diff

        pdf = PdfReader(self.path_to_pdf)
        out = PdfWriter()
        amount = len(self.images)
        for index, page in enumerate(pdf.pages):

            image_height = self.images[index].shape[0]
            image_width = self.images[index].shape[1]

            pts_width, pts_height = page.mediabox.getUpperRight()

            pts_x, pts_y = page.mediabox.getLowerLeft()

            pts_x = float(pts_x)
            pts_y = float(pts_y)

            pts_width = float(pts_width)
            pts_height = float(pts_height)

            crop_rectangle = self.crop_rectangles[index]

            y_diff = image_height - crop_rectangle.height - crop_rectangle.y
            height_diff = y_diff + crop_rectangle.height

            x_trans = translate(crop_rectangle.x, 0, image_width, pts_x, pts_width)
            y_trans = translate(y_diff, 0, image_height, abs(pts_y), pts_height)
            width_trans = translate(
                crop_rectangle.width + crop_rectangle.x,
                0,
                image_width,
                pts_x,
                pts_width,
            )
            height_trans = translate(
                height_diff, 0, image_height, abs(pts_y), pts_height
            )

            page.mediabox.upper_right = (width_trans, height_trans)
            page.mediabox.lower_left = (x_trans, y_trans)

            out.addPage(page)
            self.signals.progress.emit((index / amount) * 100)

        temp_uuid = uuid.uuid4()
        path = f"{Config.OCR_WORKING_DIR}\\{temp_uuid}.pdf"
        out.write(path)
        console.log("Saving PDF")

        self.signals.progress.emit(100)

        OcrAutomation.open_pdf_in_ocr_editor(path)

        self.signals.finished.emit()


class CropRunningStep(Step):
    finished = pyqtSignal()

    def __init__(
        self,
        *,
        text: str,
        previous_text="Zurück",
        previous_callback=None,
        next_text="Weiter",
        next_callback=None,
        detail: str = "",
    ):
        super().__init__(
            text=text,
            previous_text=previous_text,
            previous_callback=previous_callback,
            next_text=next_text,
            next_callback=next_callback,
            detail=detail,
        )

        self.progress_bar = ProgressBar(text_visible=True)
        self.layout.addWidget(self.progress_bar, 2, 0, 2, 4)
        self.progress_bar.setValue(0)

        self.worker = None
        self.threadpool = QThreadPool()

    def update_progressbar(self, value: int):
        self.progress_bar.setValue(value)

    def start(
        self,
        file_path: str,
        rectangle: Rectangle,
        rectangles: List[Rectangle],
        images: List[ndarray],
        pts_rectangles: List[Rectangle],
    ):
        self.worker = CropRunningWorker(
            file_path,
            rectangle,
            rectangles,
            images,
            self.update_progressbar,
            pts_rectangles,
        )
        self.worker.signals.finished.connect(self.finished.emit)
        self.worker.signals.progress.connect(self.update_progressbar)
        self.threadpool.start(self.worker)
