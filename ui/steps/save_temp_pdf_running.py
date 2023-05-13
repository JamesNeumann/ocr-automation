import os.path
import time

from PyQt6.QtCore import pyqtSignal, QObject, QRunnable, pyqtSlot, QThreadPool

from automation.ocr_automation import OcrAutomation
from automation.procedures.general_procedures import GeneralProcedures
from ui.components.progress_bar import ProgressBar
from ui.steps.step import Step
from utils.keyboard_util import press_key


class SaveTempPdfRunningSignals(QObject):
    finished = pyqtSignal(str)


class SaveTempPdfRunningWorker(QRunnable):
    def __init__(self):
        super(SaveTempPdfRunningWorker, self).__init__()
        self.signals = SaveTempPdfRunningSignals()

    @pyqtSlot()
    def run(self):
        press_key(key_combination="alt+tab")
        path, name = GeneralProcedures.save_temp_pdf()
        time.sleep(1)
        OcrAutomation.close_ocr_project(False)
        # Store.FILE_PATH_AFTER_ORIENTATION_SAVE = os.path.abspath(os.path.join(path, str(name) + ".pdf"))
        self.signals.finished.emit(
            os.path.abspath(os.path.join(path, str(name) + ".pdf"))
        )


class SaveTempPdfRunningStep(Step):
    finished = pyqtSignal(str)

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

    def start(self):
        self.worker = SaveTempPdfRunningWorker()
        self.worker.signals.finished.connect(self.finished.emit)
        self.threadpool.start(self.worker)
