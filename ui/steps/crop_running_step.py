from typing import List

from PyQt6.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool, pyqtSlot

from automation.ocr_automation import OcrAutomation
from ui.components.progress_bar import ProgressBar
from ui.steps.step import Step
from utils.console import console
from utils.rectangle import Rectangle


class CropRunningSignals(QObject):
    finished = pyqtSignal()


class CropRunningWorker(QRunnable):

    def __init__(self, path_to_pdf: str, crop_rectangle: Rectangle, crop_rectangles: List[Rectangle]):
        super(CropRunningWorker, self).__init__()
        self.signals = CropRunningSignals()
        self.path_to_pdf = path_to_pdf
        self.crop_rectangle = crop_rectangle
        self.crop_rectangles = crop_rectangles

    @pyqtSlot()
    def run(self) -> None:
        max_x_center_diff = 0
        for crop_rect in self.crop_rectangles:
            for crop_rect_inner in self.crop_rectangles:
                x_center_diff = abs(crop_rect.center_x - crop_rect_inner.center_x)
                if x_center_diff > max_x_center_diff:
                    max_x_center_diff = x_center_diff

        console.log("Max center x diff", max_x_center_diff)

        if max_x_center_diff < 5:
            OcrAutomation.crop_pdf(path_to_pdf=self.path_to_pdf, crop_rectangle=self.crop_rectangle)
        else:
            OcrAutomation.crop_pdf_single_pages(path_to_pdf=self.path_to_pdf, crop_rectangles=self.crop_rectangles)
        self.signals.finished.emit()


class CropRunningStep(Step):
    finished = pyqtSignal()

    def __init__(self, *, text: str, previous_text="Zurück", previous_callback=None, next_text="Weiter",
                 next_callback=None, detail: str = ""):
        super().__init__(text=text,
                         previous_text=previous_text,
                         previous_callback=previous_callback,
                         next_text=next_text,
                         next_callback=next_callback, detail=detail)

        self.progress_bar = ProgressBar(text_visible=False)
        self.layout.addWidget(self.progress_bar, 2, 0, 2, 4)
        self.progress_bar.setValue(100)

        self.worker = None
        self.threadpool = QThreadPool()

    def start(self, file_path, rectangle, rectangles):
        self.worker = CropRunningWorker(file_path, rectangle, rectangles)
        self.worker.signals.finished.connect(lambda: self.finished.emit())
        self.threadpool.start(self.worker)
