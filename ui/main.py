import os
from uuid import UUID

from PyQt6.QtWidgets import QWidget, QStackedLayout, QMainWindow
from rich.panel import Panel

from automation.abby_automation import AbbyAutomation
from config import ABBY_WORKING_DIR
from ui.steps.clean_up_running_step import CleanUpRunningStep
from ui.steps.crop_amount_step import CropAmountStep
from ui.steps.crop_running_step import CropRunningStep
from ui.steps.file_name_selection_step import FileNameSelectionStep
from ui.steps.file_selection_step import FileSelectionStep
from ui.steps.ocr_language_selection_step import OcrLanguageSelectionStep
from ui.steps.ocr_running_step import OcrRunningStep
from ui.steps.open_abby_step import OpenAbbyStep
from ui.steps.procedure_selection_step import ProcedureSelectionStep
from ui.steps.save_pdf_running_step import SavePDFRunningStep
from ui.steps.step import Step
from utils.console import console


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Abby Automation")
        self.resize(1024, 800)

        self.layout = QStackedLayout()
        self.file_selection_step = FileSelectionStep(text="Wähle eine PDF-Datei aus",
                                                     next_callback=self.open_abby_and_ocr_editor)

        self.open_abby_step = OpenAbbyStep(
            text="Es wird gewartet, bis Abby und der OCR-Editor vollständig geöffnet wurde",
        )
        self.open_abby_step.finished_signal.connect(self.open_procedure_step)

        self.procedures_step = ProcedureSelectionStep(
            text="Welche Optimierungen sollen durchgeführt werden?",
            next_callback=self.do_optimization
        )

        self.procedures_step.finished.connect(lambda file_name: self.open_crop_step(file_name))

        self.crop_amount_step = CropAmountStep(
            text="Die PDF wird analysiert",
            next_callback=self.crop_pdf
        )

        self.crop_running_step = CropRunningStep(
            text="Die PDF wird zugeschnitten"
        )

        self.crop_running_step.finished.connect(
            lambda: (self.layout.setCurrentIndex(5), self.window().activateWindow()))

        self.ocr_language_selection_step = OcrLanguageSelectionStep(
            text="Wähle die OCR-Sprachen für die PDF",
            next_callback=self.do_ocr
        )

        self.ocr_running_step = OcrRunningStep(text="OCR läuft")

        self.ocr_running_step.finished.connect(
            lambda: (
                console.log(Panel("[green]OCR Finished")), self.layout.setCurrentIndex(7),
                self.window().activateWindow()))

        self.ocr_finished_step = Step(text="OCR abgeschlossen. Bitte überprüfen und dann auf weiter.",
                                      next_callback=self.open_save_location_step)

        self.choose_save_location_step = FileNameSelectionStep(
            text="Wähle Speicherort und Name der PDF",
            next_callback=self.save_pdf
        )

        self.save_running_step = SavePDFRunningStep(
            text="PDF wird gespeichert"
        )
        self.save_running_step.finished.connect(lambda: self.clean_up())

        self.clean_up_running_step = CleanUpRunningStep(
            text="Es wird augeräumt"
        )
        self.clean_up_running_step.finished.connect(
            lambda: (self.layout.setCurrentIndex(11), self.window().activateWindow()))

        self.finished_step = Step(
            text="Fertig!",
            next_callback=lambda: exit(0),
            next_text="Schließen",
            previous_callback=lambda: self.reset(),
            previous_text="Neue PDF verarbeiten"
        )

        self.steps = [
            self.file_selection_step,
            self.open_abby_step,
            self.procedures_step,
            self.crop_amount_step,
            self.crop_running_step,
            self.ocr_language_selection_step,
            self.ocr_running_step,
            self.ocr_finished_step,
            self.choose_save_location_step,
            self.save_running_step,
            self.clean_up_running_step,
            self.finished_step
        ]

        for step in self.steps:
            self.layout.addWidget(step)

        self.layout.setCurrentIndex(0)

        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)
        self.rectangle = None

    def open_abby_and_ocr_editor(self):
        if self.file_selection_step.file_selection.selected_file_name != "":
            self.open_abby_step.set_pdf_path(self.file_selection_step.file_selection.file_path())
            self.layout.setCurrentIndex(1)
            self.open_abby_step.start()

    def open_crop_step(self, file_name: UUID):
        self.layout.setCurrentIndex(3)
        self.window().activateWindow()
        path = os.path.abspath(f"{ABBY_WORKING_DIR}\\{str(file_name)}.pdf")
        console.log(path)
        self.crop_amount_step.open_pdf_pages(path)

    def crop_pdf(self):
        self.crop_running_step.start(self.crop_amount_step.path_to_pdf,
                                     self.crop_amount_step.crop_amount_selection.get_pts_rectangle())
        self.layout.setCurrentIndex(4)

    def open_image_improvement_tools(self):
        AbbyAutomation.open_image_improvement_tools()
        self.do_optimization()
        self.layout.setCurrentIndex(3)

    def open_procedure_step(self):
        self.layout.setCurrentIndex(2)
        self.window().activateWindow()

    def do_optimization(self):
        self.procedures_step.start()

    def do_ocr(self):
        self.layout.setCurrentIndex(6)
        languages = self.ocr_language_selection_step.get_selected_language()
        self.ocr_running_step.start(languages)

    def open_save_location_step(self):
        self.layout.setCurrentIndex(8),
        self.choose_save_location_step.set_previous_name(self.file_selection_step.file_selection.selected_file_name)

    def save_pdf(self):
        if self.choose_save_location_step.folder_selection.selected_folder != "":
            self.layout.setCurrentIndex(9)
            folder = self.choose_save_location_step.folder_selection.selected_folder
            file_name = self.choose_save_location_step.file_name_field.text()
            suffix = "" if ".pdf" in file_name else ".pdf"
            path = os.path.abspath(folder + "\\" + file_name + suffix)
            self.save_running_step.start(path)

    def reset(self):
        for step in self.steps:
            step.reset()
        self.layout.setCurrentIndex(0)

    def clean_up(self):
        self.window().activateWindow()
        self.layout.setCurrentIndex(10)
        self.clean_up_running_step.start()
