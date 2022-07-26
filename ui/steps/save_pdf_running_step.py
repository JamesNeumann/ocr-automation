from PyQt6.QtCore import pyqtSignal, QObject, QRunnable, pyqtSlot, QThreadPool

from automation.ocr_automation import OcrAutomation
from automation.store import Store
from ui.components.progress_bar import ProgressBar
from ui.steps.step import Step
from utils.set_standard_metadata import set_standard_metadata
from utils.file_utils import wait_until_file_is_unlocked


class SavePDFRunningSignals(QObject):
    finished = pyqtSignal()


class SavePDFRunningWorker(QRunnable):
    def __init__(self, pdf_path: str, enable_precise_scan: bool):
        super(SavePDFRunningWorker, self).__init__()
        self.signals = SavePDFRunningSignals()
        self.pdf_path = pdf_path
        self.enable_precise_scan = enable_precise_scan

    @pyqtSlot()
    def run(self) -> None:
        OcrAutomation.save_pdf(self.pdf_path, self.enable_precise_scan)
        wait_until_file_is_unlocked(self.pdf_path)
        set_standard_metadata(self.pdf_path)
        OcrAutomation.open_pdf_in_default_program(self.pdf_path)
        self.signals.finished.emit()


class SavePDFRunningStep(Step):
    finished = pyqtSignal()

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

        self.progress_bar = ProgressBar(text_visible=False)
        self.layout.addWidget(self.progress_bar, 2, 0, 2, 4)
        self.progress_bar.setValue(100)

        self.threadpool = QThreadPool()
        self.worker = None

    def start(self, path_to_pdf: str, enable_precise_scan: bool):
        self.worker = SavePDFRunningWorker(path_to_pdf, enable_precise_scan)
        self.worker.signals.finished.connect(self.finished.emit)
        self.threadpool.start(self.worker)
