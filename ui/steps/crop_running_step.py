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

        cropped_images = crop_images_multiple_boxes(self.images, self.crop_rectangles)

        pillow_images = []
        saved_images = []

        # amount = len(cropped_images)
        # for index, image in enumerate(cropped_images):
        #     img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        #     height, width = img.shape[:2]
        #
        #     current_dpi = SaveConfig.get_dpi_value()
        #     new_dpi = 200
        #     new_width = round(width * new_dpi / current_dpi)
        #     new_height = round(height * new_dpi / current_dpi)
        #     img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
        #     image_id = uuid.uuid4()
        #     file_path = f"{Config.OCR_WORKING_DIR}\\{image_id}.jpg"
        #     cv2.imwrite(file_path, img, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        #
        #     saved_images.append(file_path)
        #
        #     # encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 60]
        #     # result, encimg = cv2.imencode('.jpg', img, encode_param)
        #
        #     # image_pillow = Image.fromarray(img)
        #     # image_pillow.resize((round))
        #     # pillow_images.append(image_pillow)
        #
        #     self.signals.progress.emit((index / amount) * 100)

        amount = len(cropped_images)
        pdf = PdfReader(self.path_to_pdf)
        out = PdfWriter()
        for index, page in enumerate(pdf.pages):
            console.log("Media Box", page.mediabox)

            # pixel_per_pts_width = self.images[index].shape[0] / page.mediabox.getUpperRight_x()
            # pixel_per_pts_height = self.images[index].shape[1] / page.mediabox.getLowerRight_y()

            x = convert_to_pts(self.crop_rectangles[index].x)
            y = convert_to_pts(self.crop_rectangles[index].y)

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
            height_diff =  y_diff + crop_rectangle.height

            x_trans = self.translate(crop_rectangle.x, 0, image_width, pts_x, pts_width)
            y_trans = self.translate(y_diff, 0, image_height, abs(pts_y), pts_height)
            width_trans = self.translate(crop_rectangle.width + crop_rectangle.x, 0, image_width, pts_x, pts_width)
            height_trans = self.translate(height_diff, 0, image_height, abs(pts_y), pts_height)

            console.log("Pts Box", pts_width, pts_height)
            console.log("Translated", x_trans, y_trans, width_trans, height_trans)

            width = convert_to_pts(self.crop_rectangles[index].width) + x
            height = convert_to_pts(self.crop_rectangles[index].height) + y

            # console.log("New Box", x, y, width, height)

            page.mediabox.upper_right = (width_trans, height_trans)
            page.mediabox.lower_left = (x_trans, y_trans)
            # page.mediabox.upper_left = (x, y)
            # page.mediabox.lower_right = (width, height)

            console.log("New Mediabox", page.mediabox)
            out.addPage(page)
            self.signals.progress.emit((index / amount) * 100)

        out.write("out.pdf")

        temp_uuid = uuid.uuid4()
        path = f"{Config.OCR_WORKING_DIR}\\{temp_uuid}.pdf"
        out.write(path)
        console.log("Saving PDF")

        # with open(path, "wb") as f:
        #     f.write(img2pdf.convert(saved_images))

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

    def translate(sekf, value, leftMin, leftMax, rightMin, rightMax):
        # Figure out how 'wide' each range is
        leftSpan = leftMax - leftMin
        rightSpan = rightMax - rightMin

        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value - leftMin) / float(leftSpan)

        # Convert the 0-1 range into a value in the right range.
        return rightMin + (valueScaled * rightSpan)


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
