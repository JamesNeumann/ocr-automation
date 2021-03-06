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
from utils.rectangle import Rectangle
from utils.save_config import SaveConfig


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
    ):
        super(CropRunningWorker, self).__init__()
        self.signals = CropRunningSignals()
        self.path_to_pdf = path_to_pdf
        self.crop_rectangle = crop_rectangle
        self.crop_rectangles = crop_rectangles
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

        cropped_images = crop_images_multiple_boxes(self.images, self.crop_rectangles)

        pillow_images = []
        saved_images = []

        amount = len(cropped_images)
        for index, image in enumerate(cropped_images):
            img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            height, width = img.shape[:2]

            current_dpi = SaveConfig.get_dpi_value()
            new_dpi = 200
            new_width = round(width * new_dpi / current_dpi)
            new_height = round(height * new_dpi / current_dpi)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
            image_id = uuid.uuid4()
            file_path = f"{Config.OCR_WORKING_DIR}\\{image_id}.jpg"
            cv2.imwrite(file_path, img, [int(cv2.IMWRITE_JPEG_QUALITY), 90])

            saved_images.append(file_path)

            # encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 60]
            # result, encimg = cv2.imencode('.jpg', img, encode_param)

            # image_pillow = Image.fromarray(img)
            # image_pillow.resize((round))
            # pillow_images.append(image_pillow)

            self.signals.progress.emit((index / amount) * 100)

        temp_uuid = uuid.uuid4()
        path = f"{Config.OCR_WORKING_DIR}\\{temp_uuid}.pdf"

        console.log("Saving PDF")

        with open(path, "wb") as f:
            f.write(img2pdf.convert(saved_images))

        # pillow_images[0].save(
        #     path,
        #     "PDF",
        #     resolution=100.0,
        #     save_all=True,
        #     append_images=pillow_images[1:],
        # )

        self.signals.progress.emit(100)

        OcrAutomation.open_pdf_in_ocr_editor(path)

        self.signals.finished.emit()


class CropRunningStep(Step):
    finished = pyqtSignal()

    def __init__(
        self,
        *,
        text: str,
        previous_text="Zur??ck",
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
    ):
        self.worker = CropRunningWorker(
            file_path,
            rectangle,
            rectangles,
            images,
            self.update_progressbar,
        )
        self.worker.signals.finished.connect(self.finished.emit)
        self.worker.signals.progress.connect(self.update_progressbar)
        self.threadpool.start(self.worker)
