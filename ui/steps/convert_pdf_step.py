from PyQt6.QtCore import pyqtSignal, QRunnable, pyqtSlot, QThreadPool, QObject

from automation.store import Store
from ui.components.progress_bar import ProgressBar
from ui.steps.step import Step
from utils.convert_pdf_result import ConvertPdfResult
from utils.analyse_pdf import get_pdf_pages_as_images, is_greyscale


class ConvertWorkerSignals(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)


class ConvertWorker(QRunnable):
    def __init__(self, path_to_pdf: str):
        super(ConvertWorker, self).__init__()
        self.convert_pdf_result = None
        self.path_to_pdf = path_to_pdf
        self.signals = ConvertWorkerSignals()

    @pyqtSlot()
    def run(self):
        images, pts_width, pts_height, index, pts_dimensions = get_pdf_pages_as_images(
            self.path_to_pdf, self.signals.progress.emit
        )

        self.convert_pdf_result = ConvertPdfResult(
            path_to_pdf=self.path_to_pdf,
            images=images,
            pts_width=pts_width,
            pts_height=pts_height,
            pts_dimensions=pts_dimensions,
        )

        # self.convert_pdf_result.is_greyscale = is_greyscale(images)

        Store.CONVERT_PDF_RESULT = self.convert_pdf_result

        self.signals.finished.emit()


class ConvertPdfStep(Step):
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
        self.progress_bar = ProgressBar()
        self.layout.addWidget(self.progress_bar, 2, 0, 2, 4)
        self.threadpool = QThreadPool()
        self.worker = None
        self.path_to_pdf = ""

    def convert_pdf_pages(self, path_to_pdf: str) -> None:
        self.label.setText("<h1>Die PDF wird analysiert</h1>")
        self.path_to_pdf = path_to_pdf
        self.progress_bar.setValue(0)
        if self.progress_bar.isHidden():
            self.progress_bar.show()
        self.worker = ConvertWorker(path_to_pdf)
        self.worker.signals.finished.connect(self.finished.emit)
        self.worker.signals.progress.connect(self.progress_bar.setValue)
        self.threadpool.start(self.worker)

    def reset(self):
        self.label.setText(f"<h1>{self.text}</h1>")
