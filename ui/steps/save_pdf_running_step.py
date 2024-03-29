from typing import Dict

from PyQt6.QtCore import pyqtSignal, QObject, QRunnable, pyqtSlot, QThreadPool

from automation.ocr_automation import OcrAutomation
from ui.components.progress_bar import ProgressBar
from ui.steps.step import Step
from utils.file_utils import wait_until_file_is_unlocked
from utils.keyboard_util import press_key
from utils.set_metadata import set_standard_metadata, Metadata


class SavePDFRunningSignals(QObject):
    finished = pyqtSignal()


class SavePDFRunningWorker(QRunnable):
    def __init__(self, pdf_path: str, enable_precise_scan: bool, metadata: Metadata):
        super(SavePDFRunningWorker, self).__init__()
        self.signals = SavePDFRunningSignals()
        self.pdf_path = pdf_path
        self.enable_precise_scan = enable_precise_scan
        self.metadata = metadata

    @pyqtSlot()
    def run(self) -> None:
        press_key(key_combination="alt+tab")
        OcrAutomation.save_pdf(self.pdf_path, self.enable_precise_scan)
        wait_until_file_is_unlocked(self.pdf_path)
        set_standard_metadata(self.pdf_path, self.metadata)
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

    def start(self, path_to_pdf: str, enable_precise_scan: bool, metadata: Metadata):
        self.worker = SavePDFRunningWorker(path_to_pdf, enable_precise_scan, metadata)
        self.worker.signals.finished.connect(self.finished.emit)
        self.threadpool.start(self.worker)
