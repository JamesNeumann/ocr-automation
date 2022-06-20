from PyQt6.QtCore import pyqtSignal, QRunnable, pyqtSlot, QThreadPool, QObject

from config import Config
from ui.components.progress_bar import ProgressBar
from ui.controller.crop_amount_selection_controller import CropAmountSelectionController
from ui.steps.step import Step
from utils.analysis_result import AnalysisResult
from utils.analyze_pdf import (
    get_pdf_pages_as_images,
    get_crop_boxes,
)
from utils.console import console


class CropWorkerSignals(QObject):
    finished = pyqtSignal(AnalysisResult)
    progress = pyqtSignal(int)


class CropWorker(QRunnable):
    def __init__(self, path_to_pdf: str):
        super(CropWorker, self).__init__()
        self.path_to_pdf = path_to_pdf
        self.signals = CropWorkerSignals()

    @pyqtSlot()
    def run(self):
        images, pts_width, pts_height, index, pts_dimensions = get_pdf_pages_as_images(
            self.path_to_pdf, self.signals.progress.emit
        )

        crop_boxes, max_box, max_index = get_crop_boxes(
            images,
            lambda value: self.signals.progress.emit(50 + value),
            render_debug_lines=True,
            save_images=False,
        )

        transformed_boxes = []

        max_box_area = max_box.area()
        for rectangle in crop_boxes:
            transformed = rectangle.move_to_center(max_box)
            transformed.x = int(transformed.x)
            console.log("Area:", rectangle.area(), max_box_area, rectangle.area() / max_box_area)
            if rectangle.area() < max_box_area * Config.CROP_Y_AXIS_THRESHOLD:
                transformed.y = max_box.y
            transformed_boxes.append(transformed)

        # console.log("Maximum crop box", max_box)
        # console.log("Boxes of individual pages", [str(box) for box in crop_boxes])
        # console.log(
        #     "Boxes of transformed pages", [str(box) for box in transformed_boxes]
        # )

        analysis_result = AnalysisResult(
            images=images,
            pts_width=pts_width,
            pts_height=pts_height,
            min_index=max_index,
            max_box=max_box,
            crop_boxes=crop_boxes,
            transformed_boxes=transformed_boxes,
            pts_dimensions=pts_dimensions,
        )

        self.signals.finished.emit(analysis_result)


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

        self.progress_bar = ProgressBar()
        self.layout.addWidget(self.progress_bar, 2, 0, 2, 4)
        self.layout.addWidget(
            self.crop_amount_selection_controller.crop_amount_selection, 2, 0, 2, 4
        )
        self.threadpool = QThreadPool()
        self.worker = None
        self.path_to_pdf = ""

    def open_pdf_pages(self, path_to_pdf: str) -> None:
        self.label.setText("<h1>Die PDF wird analysiert</h1>")
        self.path_to_pdf = path_to_pdf
        if self.crop_amount_selection_controller.crop_amount_selection.isVisible():
            self.crop_amount_selection_controller.crop_amount_selection.hide()
        self.progress_bar.setValue(0)
        if self.progress_bar.isHidden():
            self.progress_bar.show()
        self.worker = CropWorker(path_to_pdf)
        self.worker.signals.finished.connect(self.update_ui)
        self.worker.signals.progress.connect(self.progress_bar.setValue)
        self.threadpool.start(self.worker)

    def update_ui(self, analysis_result: AnalysisResult):
        self.crop_amount_selection_controller.reset()
        self.label.setText("<h1>Wie soll die PDF zugeschnitten werden?")

        self.crop_amount_selection_controller.set_analysis_result(analysis_result)
        self.crop_amount_selection_controller.show()

        # self.crop_amount_selection.set_images(images)
        # self.crop_amount_selection.set_width(images[0].shape[1])
        # self.crop_amount_selection.set_height(images[0].shape[0])
        # self.crop_amount_selection.set_rectangle(crop_box)
        # self.crop_amount_selection.set_transformed_rectangles(crop_boxes)
        # self.crop_amount_selection.set_pts_width_per_pixel(
        #     pts_width / images[0].shape[1]
        # )
        # self.crop_amount_selection.set_pts_height_per_pixel(
        #     pts_height / images[0].shape[0]
        # )

        # self.crop_amount_selection.set_spinner_max()
        # self.crop_amount_selection.show_pix_map()
        # self.crop_amount_selection.update_default_offset()
        # self.crop_amount_selection.show_crop_hint()
        self.progress_bar.hide()
        self.window().activateWindow()

    def reset(self):
        self.crop_amount_selection_controller.reset()
