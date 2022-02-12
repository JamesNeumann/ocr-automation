import os.path

from PyQt6.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot, QThreadPool

from automation.abby_automation import AbbyAutomation
from ui.steps.step import Step


class OpenAbbyWorkerSignals(QObject):
    finished = pyqtSignal()


class OpenAbbyWorker(QRunnable):

    def __init__(self, path_to_pdf: str):
        super(OpenAbbyWorker, self).__init__()
        self.path_to_pdf = path_to_pdf
        self.signals = OpenAbbyWorkerSignals()

    @pyqtSlot()
    def run(self) -> None:
        AbbyAutomation.open_abby_and_ocr_editor(path_to_pdf=self.path_to_pdf)
        self.signals.finished.emit()


class OpenAbbyStep(Step):
    finished_signal = pyqtSignal()

    def __init__(self, *, text: str, previous_text="Zurück", previous_callback=None, next_text="Weiter",
                 next_callback=None, detail: str = ""):
        super().__init__(text=text,
                         previous_text=previous_text,
                         previous_callback=previous_callback,
                         next_text=next_text,
                         next_callback=next_callback, detail=detail)
        self.path_to_pdf = ""
        self.worker = None
        self.threadpool = QThreadPool()

    def start(self):
        self.worker = OpenAbbyWorker(self.path_to_pdf)
        self.worker.signals.finished.connect(lambda: self.finished_signal.emit())
        self.threadpool.start(self.worker)

    def set_pdf_path(self, path_to_pdf: str):
        self.path_to_pdf = os.path.abspath(path_to_pdf)
