from PyQt6.QtCore import QRunnable, pyqtSignal, pyqtSlot, QThreadPool, QObject

from automation.ocr_automation import OcrAutomation
from automation.store import Store
from config import Config
from ui.components.progress_bar import ProgressBar
from ui.steps.step import Step


class OcrRunningWorkerSignals(QObject):
    finished = pyqtSignal()


class OcrFromFileRunningWorker(QRunnable):
    def __init__(self, open_ocr_editor):
        super(OcrFromFileRunningWorker, self).__init__()
        self.signals = OcrRunningWorkerSignals()
        self.open_ocr_editor = open_ocr_editor

    @pyqtSlot()
    def run(self):
        if self.open_ocr_editor:
            OcrAutomation.open_pdf_in_ocr_editor(Store.SELECTED_FILE_PATH, True)
        OcrAutomation.run_ocr_with_ocr_from_text()
        self.signals.finished.emit()


class OcrFromFileRunningStep(Step):
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

    def start(self, open_pdf_editor=False):
        Config.STOP_STUCK_RUNNING = False
        self.worker = OcrFromFileRunningWorker(open_pdf_editor)
        self.worker.autoDelete()
        self.worker.signals.finished.connect(self.finished.emit)
        self.threadpool.start(self.worker)

    def stop(self):
        Config.STOP_STUCK_RUNNING = True
