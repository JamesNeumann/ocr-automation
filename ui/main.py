import os
import time

from PyQt6.QtWidgets import QWidget, QStackedLayout, QMainWindow

from automation.abby_automation import AbbyAutomation
from automation.procedures.ocr_procedures import OcrProcedures
from ui.steps.procedure_selection_step import ProcedureSelectionStep
from ui.steps.file_selection_step import FileSelectionStep


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Abby Automation")
        self.resize(600, 400)

        self.layout = QStackedLayout()
        self.file_selection_step = FileSelectionStep(text="Wähle eine PDF-Datei aus:",
                                                     next_callback=self.open_abby_and_ocr_editor)

        self.procedures_step = ProcedureSelectionStep(
            text="Welche Optimierungen sollen durchgeführt werden?",
            previous_callback=lambda: self.layout.setCurrentIndex(0),
            next_callback=self.do_optimization
        )

        # self.abby_opened_step = Step(
        #     text="Ist die Datei in Abby geöffnet?",
        #     previous_callback=lambda: self.layout.setCurrentIndex(0),
        #     next_text="Ja",
        #     next_callback=self.open_ocr_editor
        # )
        #
        # self.ocr_editor_opened_step = Step(
        #     text="Dateiverarbeitung starten",
        #     previous_callback=lambda: self.layout.setCurrentIndex(1),
        #     next_callback=self.open_image_improvement_tools,
        #     detail="<h2>Bitte alle (Fehler-)dialoge entfernen und die erste Seite auswählen.</h2>"
        #            "<h2>Dann erst auf Weiter</h2>"
        # )
        #
        # self.cut_pdf_step = Step(
        #     text="PDF-Zuschneiden",
        #     previous_callback=lambda: self.layout.setCurrentIndex(2),
        #     next_text="Zuschneiden",
        #     next_callback=self.crop_pdf
        # )
        self.layout.addWidget(self.file_selection_step)
        self.layout.addWidget(self.procedures_step)
        # self.layout.addWidget(self.abby_opened_step)
        # self.layout.addWidget(self.ocr_editor_opened_step)
        # self.layout.addWidget(self.cut_pdf_step)

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
            # abs_path = os.path.abspath("C:\\Users\\janne\\Downloads\\tmpl=s_t.pdf")

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
