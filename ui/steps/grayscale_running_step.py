from PyQt6.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool, pyqtSlot

from automation.ocr_automation import OcrAutomation
from ui.steps.step import Step


class GrayscaleSignal(QObject):
    finished = pyqtSignal()


class GrayscaleWorker(QRunnable):
    def __init__(self):
        super(GrayscaleWorker, self).__init__()
        self.signals = GrayscaleSignal()

    @pyqtSlot()
    def run(self) -> None:
        OcrAutomation.convert_pdf_to_binary()
        self.signals.finished.emit()


class GrayscaleRunning(Step):
    finished = pyqtSignal()

    def __init__(
        self,
        *,
        text: str,
        previous_text="",
        previous_callback=None,
        next_text="",
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

        self.worker = None
        self.threadpool = QThreadPool()

    def start(self):
        self.worker = GrayscaleWorker()
        self.worker.signals.finished.connect(self.finished.emit)
        self.threadpool.start(self.worker)
