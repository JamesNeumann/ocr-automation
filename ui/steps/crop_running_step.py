from PyQt6.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool, pyqtSlot

from automation.abby_automation import AbbyAutomation
from ui.progress_bar import ProgressBar
from ui.steps.step import Step
from utils.rectangle import Rectangle


class CropRunningSignals(QObject):
    finished = pyqtSignal()


class CropRunningWorker(QRunnable):

    def __init__(self, path_to_pdf: str, crop_rectangle: Rectangle):
        super(CropRunningWorker, self).__init__()
        self.signals = CropRunningSignals()
        self.path_to_pdf = path_to_pdf
        self.crop_rectangle = crop_rectangle

    @pyqtSlot()
    def run(self) -> None:
        AbbyAutomation.crop_pdf(path_to_pdf=self.path_to_pdf, crop_rectangle=self.crop_rectangle)
        self.signals.finished.emit()


class CropRunningStep(Step):
    finished = pyqtSignal()

    def __init__(self, *, text: str, previous_text="Zurück", previous_callback=None, next_text="Weiter",
                 next_callback=None, detail: str = ""):
        super().__init__(text=text,
                         previous_text=previous_text,
                         previous_callback=previous_callback,
                         next_text=next_text,
                         next_callback=next_callback, detail=detail)

        self.progress_bar = ProgressBar(text_visible=False)
        self.layout.addWidget(self.progress_bar, 2, 0, 2, 4)
        self.progress_bar.setValue(100)

        self.worker = None
        self.threadpool = QThreadPool()

    def start(self, file_path, rectangle):
        self.worker = CropRunningWorker(file_path, rectangle)
        self.worker.signals.finished.connect(lambda: self.finished.emit())
        self.threadpool.start(self.worker)
