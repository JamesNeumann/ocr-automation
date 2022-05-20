import math
import os
from uuid import UUID

from PyQt6.QtCore import QObject, pyqtSignal, QRunnable, pyqtSlot, QThreadPool

from automation.ocr_automation import OcrAutomation
from automation.procedures.ocr_procedures import OcrProcedures
from automation.store import Store
from config import OCR_WORKING_DIR
from ui.components.procedures_selection import ProcedureSelection
from ui.components.progress_bar import ProgressBar
from ui.steps.step import Step


class ProcedureWorkerSignals(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(float)


class ProcedureWorker(QRunnable):
    def __init__(self, procedures, iterations):
        super(ProcedureWorker, self).__init__()
        self.signals = ProcedureWorkerSignals()
        self.iterations = iterations
        self.procedures = procedures

    @pyqtSlot()
    def run(self):
        OcrAutomation.do_optimization(
            self.procedures,
            self.iterations,
            self.signals.progress.emit,
        )

        # Store.FILE_PATH_AFTER_PROCEDURES = os.path.abspath(f"{OCR_WORKING_DIR}\\{str(filename)}.pdf")
        self.signals.finished.emit()


class ProcedureSelectionStep(Step):
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
        self.procedure_selection = ProcedureSelection()
        self.layout.addWidget(self.procedure_selection, 2, 0, 2, 4)
        self.progressbar = ProgressBar()
        self.progressbar.hide()
        self.layout.addWidget(self.progressbar, 4, 0, 2, 4)
        self.threadpool = QThreadPool()
        self.worker = None

    def start(self):
        self.progressbar.show()
        procedure_names = self.procedure_selection.get_selected_procedures()
        procedures = OcrProcedures.get_procedures(procedure_names)
        self.worker = ProcedureWorker(
            procedures, self.procedure_selection.get_iteration_amount()
        )
        self.worker.signals.progress.connect(
            lambda value: self.progressbar.setValue(math.floor(value))
        )
        self.worker.signals.finished.connect(self.finished.emit)
        self.threadpool.start(self.worker)

    def reset(self):
        self.procedure_selection.reset()
        self.progressbar.hide()
        self.progressbar.setValue(0)
