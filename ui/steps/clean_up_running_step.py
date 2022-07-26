from PyQt6.QtCore import pyqtSignal, QObject, QRunnable, pyqtSlot, QThreadPool

from automation.ocr_automation import OcrAutomation
from automation.store import Store
from ui.components.progress_bar import ProgressBar
from ui.steps.step import Step
from utils.console import console


class CleanUpRunningSignals(QObject):
    finished = pyqtSignal()


class CleanUpRunningWorker(QRunnable):
    def __init__(self):
        super(CleanUpRunningWorker, self).__init__()
        self.signals = CleanUpRunningSignals()

    @pyqtSlot()
    def run(self) -> None:
        OcrAutomation.clean_up()
        Store.reset()
        self.signals.finished.emit()
        console.log("Abgeshlossen")


class CleanUpRunningStep(Step):
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
        self.worker = None
        self.threadpool = QThreadPool()

    def start(self):
        self.worker = CleanUpRunningWorker()
        self.worker.signals.finished.connect(self.finished.emit)
        self.threadpool.start(self.worker)
