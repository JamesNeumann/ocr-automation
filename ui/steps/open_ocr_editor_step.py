from PyQt6.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot, QThreadPool

from automation.ocr_automation import OcrAutomation
from ui.steps.step import Step


class OpenOcrEditorWorkerSignals(QObject):
    finished = pyqtSignal()


class OpenOcrEditorWorker(QRunnable):
    def __init__(self, path: str, disable_image_editing_settings: bool):
        super(OpenOcrEditorWorker, self).__init__()
        self.signals = OpenOcrEditorWorkerSignals()
        self.path = path
        self.disable_image_editing_settings = disable_image_editing_settings

    @pyqtSlot()
    def run(self) -> None:
        OcrAutomation.open_pdf_in_ocr_editor(
            path_to_pdf=self.path,
            disable_image_editing_settings=self.disable_image_editing_settings,
        )
        self.signals.finished.emit()


class OpenOcrEditorStep(Step):
    finished_signal = pyqtSignal()

    def __init__(
        self,
        *,
        text="Es wird gewartet bis der OCR-Editor vollständig geöffnet wurde",
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
        self.path_to_pdf = ""
        self.worker = None
        self.threadpool = QThreadPool()

    def start(self, path: str, disable_image_editing_settings=False):
        self.worker = OpenOcrEditorWorker(path, disable_image_editing_settings)
        self.worker.signals.finished.connect(self.finished_signal.emit)
        self.threadpool.start(self.worker)
