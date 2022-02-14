from PyQt6.QtCore import QRunnable, pyqtSignal, pyqtSlot, QThreadPool, QObject

from automation.abby_automation import AbbyAutomation
from ui.steps.step import Step


class OcrRunningWorkerSignals(QObject):
    finished = pyqtSignal()


class OcrRunningWorker(QRunnable):
    def __init__(self, languages: str):
        super(OcrRunningWorker, self).__init__()
        self.signals = OcrRunningWorkerSignals()
        self.languages = languages

    @pyqtSlot()
    def run(self):
        AbbyAutomation.run_ocr(self.languages)
        self.signals.finished.emit()

class OcrRunningStep(Step):
    finished = pyqtSignal()

    def __init__(self, *, text: str, previous_text="Zurück", previous_callback=None, next_text="Weiter",
                 next_callback=None, detail: str = ""):
        super().__init__(
            text=text,
            previous_text=previous_text,
            previous_callback=previous_callback,
            next_text=next_text,
            next_callback=next_callback, detail=detail
        )
        self.threadpool = QThreadPool()
        self.worker = None

    def start(self, languages):
        self.worker = OcrRunningWorker(languages)
        self.worker.signals.finished.connect(lambda: self.finished.emit())
        self.threadpool.start(self.worker)
