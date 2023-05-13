from typing import Optional

from PyQt6.QtCore import pyqtSignal, QRunnable, pyqtSlot, QThreadPool, QObject

from automation.store import Store
from ui.components.grayscale_info import GrayscaleInfo
from ui.components.progress_bar import ProgressBar
from ui.controller.crop_amount_selection_controller import CropAmountSelectionController
from ui.steps.step import Step
from utils.crop_box_analysis_result import CropBoxAnalysisResult
from utils.analyse_pdf import (
    get_pdf_pages_as_images,
    get_crop_boxes,
)
from utils.convert_pdf_result import ConvertPdfResult
from utils.save_config import SaveConfig


class CropWorkerSignals(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)


class CropWorker(QRunnable):
    def __init__(self):
        super(CropWorker, self).__init__()
        self.signals = CropWorkerSignals()

    @pyqtSlot()
    def run(self):
        # images, pts_width, pts_height, index, pts_dimensions = get_pdf_pages_as_images(
        #     self.path_to_pdf, self.signals.progress.emit
        # )

        crop_boxes, max_box, max_index = get_crop_boxes(
            Store.CONVERT_PDF_RESULT.images,
            self.signals.progress.emit,
            render_debug_lines=False,
            save_images=False,
        )

        transformed_boxes = []

        max_box_area = max_box.area()
        y_axis_threshold = SaveConfig.get_y_axis_threshold()
        for rectangle in crop_boxes:
            transformed = rectangle.move_to_center(max_box)
            transformed.x = int(transformed.x)
            if rectangle.area() < max_box_area * y_axis_threshold:
                transformed.y = max_box.y
            transformed_boxes.append(transformed)

        analysis_result = CropBoxAnalysisResult(
            min_index=max_index,
            max_box=max_box,
            crop_boxes=crop_boxes,
            transformed_boxes=transformed_boxes,
        )
        Store.CROP_BOX_ANALYSIS_RESULT = analysis_result

        self.signals.finished.emit()


class CropAmountStep(Step):
    def __init__(
        self,
        *,
        text: str,
        previous_text="Zurück",
        previous_callback=None,
        next_text="Weiter",
        next_callback=None,
        detail: str = ""
    ):
        super().__init__(
            text=text,
            previous_text=previous_text,
            previous_callback=previous_callback,
            next_text=next_text,
            next_callback=next_callback,
            detail=detail,
        )

        self.crop_amount_selection_controller = CropAmountSelectionController()
        # self.grayscale_info = GrayscaleInfo(
        #     next_callback=self.convert_image_to_binary, previous_callback=self.update_ui
        # )
        self.progress_bar = ProgressBar()
        self.layout.addWidget(self.progress_bar, 2, 0, 2, 4)
        self.layout.addWidget(
            self.crop_amount_selection_controller.crop_amount_selection, 2, 0, 2, 4
        )
        # self.layout.addWidget(self.grayscale_info)
        self.threadpool = QThreadPool()
        self.worker = None
        self.convert_pdf_result: Optional[ConvertPdfResult] = None
        self.analysis_result = None

    def open_pdf_pages(self) -> None:
        self.label.setText("<h1>Zuschneidungsboxen werden berechnet</h1>")
        if self.crop_amount_selection_controller.crop_amount_selection.isVisible():
            self.crop_amount_selection_controller.crop_amount_selection.hide()
        self.crop_amount_selection_controller.crop_amount_selection.hide()
        self.progress_bar.setValue(0)
        if self.progress_bar.isHidden():
            self.progress_bar.show()
        self.worker = CropWorker()
        self.worker.signals.finished.connect(self.update_ui)
        self.worker.signals.progress.connect(self.progress)
        self.threadpool.start(self.worker)

    def progress(self, progress: int):
        self.progress_bar.setValue(progress)

    def update_ui(self):
        self.crop_amount_selection_controller.reset()
        self.label.setText("<h1>Wie soll die PDF zugeschnitten werden?")
        self.crop_amount_selection_controller.set_analysis_result()
        self.crop_amount_selection_controller.show()
        self.progress_bar.hide()
        self.window().activateWindow()

    def reset(self):
        self.crop_amount_selection_controller.reset()
