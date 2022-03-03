from PyQt6.QtCore import pyqtSignal, QObject, QRunnable, pyqtSlot, QThreadPool

from automation.finereader_automation import FineReaderAutomation
from ui.components.progress_bar import ProgressBar
from ui.steps.step import Step
from utils.analyze_pdf import analyze_pdf_orientation


class CheckPdfOrientationSignals(QObject):
    progress = pyqtSignal(float)
    finished = pyqtSignal(list, str)


class CheckPdfOrientationWorker(QRunnable):
    def __init__(self, path_to_pdf: str):
        super(CheckPdfOrientationWorker, self).__init__()
        self.signals = CheckPdfOrientationSignals()
        self.path_to_pdf = path_to_pdf

    @pyqtSlot()
    def run(self) -> None:
        landscaped, portraits = analyze_pdf_orientation(
            self.path_to_pdf, lambda value: self.signals.progress.emit(value)
        )

        len_landscaped = len(landscaped)
        len_portraits = len(portraits)
        result_indices = []
        if len_landscaped > 0 and len_portraits > 0:
            result_indices = portraits if len_landscaped > len_portraits else landscaped
        if len(result_indices) > 0:
            FineReaderAutomation.open_pdf_in_ocr_editor(self.path_to_pdf)

        self.signals.finished.emit(result_indices, self.path_to_pdf)


class CheckPdfOrientationRunningStep(Step):
    finished = pyqtSignal(list, str)

    def __init__(self, *, text: str, previous_text="Zurück", previous_callback=None, next_text="Weiter",
                 next_callback=None, detail: str = ""):
        super().__init__(
            text=text,
            previous_text=previous_text,
            previous_callback=previous_callback,
            next_text=next_text,
            next_callback=next_callback, detail=detail
        )

        self.progress_bar = ProgressBar(text_visible=True)
        self.layout.addWidget(self.progress_bar, 2, 0, 2, 4)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)

        self.threadpool = QThreadPool()
        self.worker = None

    def start(self, path_to_pdf):
        self.worker = CheckPdfOrientationWorker(path_to_pdf)
        self.worker.signals.finished.connect(lambda indices, path: self.finished.emit(indices, path))
        self.worker.signals.progress.connect(lambda value: self.progress_bar.setValue(int(value * 100)))
        self.threadpool.start(self.worker)

    def reset(self):
        self.progress_bar.setValue(0)
