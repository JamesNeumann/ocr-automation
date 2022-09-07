from typing import Dict, List

from PyQt6.QtCore import QThreadPool, QRunnable, QObject, pyqtSignal, pyqtSlot

from automation.ocr_automation import OcrAutomation
from ui.steps.step import Step


class Signals(QObject):
    finished = pyqtSignal()


class ReplaceOcrDefaultErrorWorker(QRunnable):
    def __init__(self, selected_replacement_maps: List[Dict]):
        super(ReplaceOcrDefaultErrorWorker, self).__init__()
        self.signals = Signals()
        self.selected_replacement_maps = selected_replacement_maps

    @pyqtSlot()
    def run(self) -> None:
        OcrAutomation.replace_default_ocr_errors(self.selected_replacement_maps)
        self.signals.finished.emit()


class OcrDefaultErrorReplacementRunningStep(Step):
    finished = pyqtSignal()

    def __init__(
        self,
        *,
        text: str,
        previous_text="Zurück",
        previous_callback=None,
        next_text="Weiter",
        next_callback=None,
        detail: str = "Folge den Anweisungen in Abby"
    ):
        super().__init__(
            text=text,
            previous_text=previous_text,
            previous_callback=previous_callback,
            next_text=next_text,
            next_callback=next_callback,
            detail=detail,
        )
        self.threadpool = QThreadPool()
        self.worker = None

    def start(self, selected_replacement_maps: List[Dict]):
        self.worker = ReplaceOcrDefaultErrorWorker(selected_replacement_maps)
        self.threadpool.start(self.worker)
        self.worker.signals.finished.connect(self.finished.emit)
