from PyQt6.QtCore import pyqtSignal, QRunnable, pyqtSlot, QThreadPool, QObject

from ui.crop_amount_selection import CropAmountSelection
from ui.progress_bar import ProgressBar
from ui.steps.step import Step
from utils.analyze_pdf import get_pdf_pages_as_images, get_crop_box_pixel
from utils.console import console
from utils.rectangle import Rectangle


class CropWorkerSignals(QObject):
    finished = pyqtSignal(list, float, float, Rectangle)
    progress = pyqtSignal(int)


class CropWorker(QRunnable):
    def __init__(self, path_to_pdf: str):
        super(CropWorker, self).__init__()
        self.path_to_pdf = path_to_pdf
        self.signals = CropWorkerSignals()

    @pyqtSlot()
    def run(self):
        images, pts_width, pts_height = get_pdf_pages_as_images(self.path_to_pdf,
                                                                lambda value: self.signals.progress.emit(value))
        crop_box = get_crop_box_pixel(images, lambda value: self.signals.progress.emit(50 + value))
        console.log(crop_box)
        self.signals.finished.emit(images, pts_width, pts_height, crop_box)


class CropAmountStep(Step):
    def __init__(self, *, text: str, previous_text="Zurück", previous_callback=None, next_text="Weiter",
                 next_callback=None, detail: str = ""):
        super().__init__(
            text=text,
            previous_text=previous_text,
            previous_callback=previous_callback,
            next_text=next_text,
            next_callback=next_callback, detail=detail
        )
        self.crop_amount_selection = CropAmountSelection()

        self.progress_bar = ProgressBar()
        self.layout.addWidget(self.progress_bar, 2, 0, 2, 4)
        self.layout.addWidget(self.crop_amount_selection, 2, 0, 2, 4)
        self.threadpool = QThreadPool()
        self.worker = None
        self.path_to_pdf = ""

    def open_pdf_pages(self, path_to_pdf: str) -> None:
        self.path_to_pdf = path_to_pdf
        if self.crop_amount_selection.isVisible():
            self.crop_amount_selection.hide()
        self.progress_bar.setValue(0)
        if self.progress_bar.isHidden():
            self.progress_bar.show()
        self.worker = CropWorker(path_to_pdf)
        self.worker.signals.finished.connect(self.update_ui)
        self.worker.signals.progress.connect(lambda value: self.progress_bar.setValue(value))
        self.threadpool.start(self.worker)

    def update_ui(self, images: list, pts_width: int, pts_height: int, crop_box: Rectangle):
        self.crop_amount_selection.reset()
        self.label.setText("<h1>Wie soll die PDF zugeschnitten werden?")
        self.crop_amount_selection.set_images(images)
        self.crop_amount_selection.set_width(images[0].shape[1])
        self.crop_amount_selection.set_height(images[0].shape[0])
        self.crop_amount_selection.set_rectangle(crop_box)
        self.crop_amount_selection.set_pts_width_per_pixel(pts_width / images[0].shape[1])
        self.crop_amount_selection.set_pts_height_per_pixel(pts_height / images[0].shape[0])
        self.crop_amount_selection.set_spinner_max()
        self.crop_amount_selection.show_pix_map()
        self.progress_bar.hide()
        self.window().activateWindow()

    def reset(self):
        self.crop_amount_selection.reset()
