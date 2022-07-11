import uuid
from typing import List, Callable

import cv2
from PIL import Image
from PyQt6.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool, pyqtSlot
from numpy import ndarray

from automation.ocr_automation import OcrAutomation
from config import Config
from ui.components.progress_bar import ProgressBar
from ui.steps.step import Step
from utils.analyze_pdf import crop_images_single_box, crop_images_multiple_boxes
from utils.console import console
from utils.rectangle import Rectangle


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
        crop_pages_single: bool,
        progress_callback: Callable,
    ):
        super(CropRunningWorker, self).__init__()
        self.signals = CropRunningSignals()
        self.path_to_pdf = path_to_pdf
        self.crop_rectangle = crop_rectangle
        self.crop_rectangles = crop_rectangles
        self.crop_pages_single = crop_pages_single
        self.images = images
        self.progress_callback = progress_callback

    @pyqtSlot()
    def run(self) -> None:
        max_x_center_diff = 0
        for crop_rect in self.crop_rectangles:
            for crop_rect_inner in self.crop_rectangles:
                x_center_diff = abs(crop_rect.center_x - crop_rect_inner.center_x)
                if x_center_diff > max_x_center_diff:
                    max_x_center_diff = x_center_diff

        if self.crop_pages_single:
            # OcrAutomation.crop_pdf_single_pages(
            #     path_to_pdf=self.path_to_pdf, crop_rectangles=self.crop_rectangles
            # )
            cropped_images = crop_images_multiple_boxes(
                self.images, self.crop_rectangles
            )
        else:
            # OcrAutomation.crop_pdf(
            #     path_to_pdf=self.path_to_pdf, crop_rectangle=self.crop_rectangle
            # )
            cropped_images = crop_images_single_box(self.images, self.crop_rectangle)

        pillow_images = []

        amount = len(cropped_images)
        for index, image in enumerate(cropped_images):
            img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image_pillow = Image.fromarray(img)
            pillow_images.append(image_pillow)
            self.signals.progress.emit((index / amount) * 100)

        temp_uuid = uuid.uuid4()
        path = f"{Config.OCR_WORKING_DIR}\\{temp_uuid}.pdf"

        console.log("Saving PDF")

        pillow_images[0].save(
            path,
            "PDF",
            resolution=100.0,
            save_all=True,
            append_images=pillow_images[1:],
        )

        self.signals.progress.emit(100)

        OcrAutomation.open_pdf_in_ocr_editor(path)

        # if max_x_center_diff < 5:
        #     OcrAutomation.crop_pdf(
        #         path_to_pdf=self.path_to_pdf, crop_rectangle=self.crop_rectangle
        #     )
        # else:
        #     OcrAutomation.crop_pdf_single_pages(
        #         path_to_pdf=self.path_to_pdf, crop_rectangles=self.crop_rectangles
        #     )

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
        crop_pages_single,
    ):
        self.worker = CropRunningWorker(
            file_path,
            rectangle,
            rectangles,
            images,
            crop_pages_single,
            self.update_progressbar,
        )
        self.worker.signals.finished.connect(self.finished.emit)
        self.worker.signals.progress.connect(self.update_progressbar)
        self.threadpool.start(self.worker)
