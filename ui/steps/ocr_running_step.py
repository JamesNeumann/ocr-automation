from PyQt6.QtCore import QRunnable, pyqtSignal, pyqtSlot, QThreadPool, QObject

from automation.finereader_automation import FineReaderAutomation
from ui.components.progress_bar import ProgressBar
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
        FineReaderAutomation.run_ocr(self.languages)
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

        self.progress_bar = ProgressBar(text_visible=False)
        self.layout.addWidget(self.progress_bar, 2, 0, 2, 4)
        self.progress_bar.setValue(100)

        self.threadpool = QThreadPool()
        self.worker = None

    def start(self, languages):
        self.worker = OcrRunningWorker(languages)
        self.worker.signals.finished.connect(lambda: self.finished.emit())
        self.threadpool.start(self.worker)
