import os
import time

from PyQt6.QtWidgets import QWidget, QStackedLayout, QMainWindow

from automation.abby_automation import AbbyAutomation
from automation.procedures.ocr_procedures import OcrProcedures
from ui.steps.crop_amount_step import CropAmountStep
from ui.steps.file_selection_step import FileSelectionStep
from ui.steps.procedure_selection_step import ProcedureSelectionStep


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Abby Automation")
        self.resize(1024, 800)

        self.layout = QStackedLayout()
        self.file_selection_step = FileSelectionStep(text="Wähle eine PDF-Datei aus:",
                                                     next_callback=self.open_crop_step)

        self.procedures_step = ProcedureSelectionStep(
            text="Welche Optimierungen sollen durchgeführt werden?",
            previous_callback=lambda: self.layout.setCurrentIndex(0),
            next_callback=self.do_optimization
        )

        self.crop_amount_step = CropAmountStep(
            text="Wähle dein Beschneidungsrahmen?",
            previous_callback=lambda: self.layout.setCurrentIndex(0),
            next_callback=self.do_optimization
        )

        self.layout.addWidget(self.file_selection_step)
        self.layout.addWidget(self.crop_amount_step)
        self.layout.addWidget(self.procedures_step)

        self.layout.setCurrentIndex(0)

        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)
        self.rectangle = None

    def open_abby_and_ocr_editor(self):
        if self.file_selection_step.file_selection.selected_file_name != "":
            abs_path = os.path.abspath(self.file_selection_step.file_selection.file_path())
            AbbyAutomation.open_abby_and_ocr_editor(path_to_pdf=abs_path)
            time.sleep(0.5)
            self.layout.setCurrentIndex(1)
            self.window().activateWindow()

    def open_abby(self):
        if self.file_selection_step.file_selection.selected_file_name != "":
            abs_path = os.path.abspath(self.file_selection_step.file_selection.file_path())
            abs_path = os.path.abspath("C:\\Users\\janne\\Downloads\\tmpl=s_t.pdf")

            AbbyAutomation.open_abby_and_ocr_editor(path_to_pdf=abs_path)
            # AbbyAutomation.open_pdf_in_abby(path_to_pdf=abs_path)
            self.layout.setCurrentIndex(2)

            # if self.file_selection_step.file_selection.selected_file_name != "":
        #     self.file_selection_step.progress_bar.show()
        #     self.file_selection_step.progress_bar.setValue(0)
        #
        #     self.rectangle = get_crop_box(self.file_selection_step.file_selection.file_path(),
        #                                   self.file_selection_step.progress_bar, offset=80)
        #     abs_path = os.path.abspath(self.file_selection_step.file_selection.file_path())
        #     self.layout.setCurrentIndex(1)

    def open_crop_step(self):
        path = self.file_selection_step.file_selection.file_path()
        # path = os.path.abspath(
        #     r"D:\Projects\harry\00 Dateien für Programmierung Jannes\PDF-Dateien\Fanta, Ein Bericht über die Ansprüche des Königs Alfons auf den deutschen Thron.pdf")
        self.layout.setCurrentIndex(1)
        self.crop_amount_step.open_pdf_pages(path)

    def open_ocr_editor(self):
        AbbyAutomation.open_ocr_editor()
        self.layout.setCurrentIndex(2)

    def open_image_improvement_tools(self):
        AbbyAutomation.open_image_improvement_tools()
        self.do_optimization()
        self.layout.setCurrentIndex(3)

    def do_optimization(self):
        names = self.procedures_step.procedure_selection.get_selected_procedures()
        procedures = OcrProcedures.get_procedures(names)
        iterations = self.procedures_step.procedure_selection.get_iteration_amount()
        AbbyAutomation.do_optimization(procedures, iterations)
