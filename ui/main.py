import os
from sys import exit
from typing import List
from uuid import UUID

from PyQt6.QtWidgets import QWidget, QStackedLayout, QMainWindow
from rich.panel import Panel

from automation.finereader_automation import FineReaderAutomation
from config import FINEREADER_WORKING_DIR, VERSION
from ui.steps.SaveTempPdfRunningStep import SaveTempPdfRunningStep
from ui.steps.check_pdf_orientation_running_step import CheckPdfOrientationRunningStep
from ui.steps.check_pdf_orientation_step import CheckPdfOrientationStep
from ui.steps.clean_up_running_step import CleanUpRunningStep
from ui.steps.crop_amount_step import CropAmountStep
from ui.steps.crop_running_step import CropRunningStep
from ui.steps.file_name_selection_step import FileNameSelectionStep
from ui.steps.file_selection_step import FileSelectionStep
from ui.steps.ocr_language_selection_step import OcrLanguageSelectionStep
from ui.steps.ocr_running_step import OcrRunningStep
from ui.steps.open_finereader import OpenFineReaderStep
from ui.steps.procedure_selection_step import ProcedureSelectionStep
from ui.steps.save_pdf_running_step import SavePDFRunningStep
from ui.steps.step import Step
from utils.console import console
from utils.save_config import SaveConfig


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"FineReader Automation v{VERSION}")
        self.resize(1024, 800)

        self.layout = QStackedLayout()

        self.current_index = 0

        self.file_selection_step = FileSelectionStep(
            text="Wähle eine PDF-Datei aus",
            next_callback=self.open_finereader_and_ocr_editor
        )

        self.open_finereader_step = OpenFineReaderStep(
            text="Es wird gewartet bis der OCR-Editor vollständig geöffnet wurde",
        )
        self.open_finereader_step.finished_signal.connect(self.open_procedure_step)

        self.procedures_step = ProcedureSelectionStep(
            text="Welche Optimierungen sollen durchgeführt werden?",
            next_callback=self.do_optimization
        )
        self.procedures_step.finished.connect(lambda file_name: self.open_check_pdf_orientation_running_step(file_name))

        self.check_pdf_orientation_running_step = CheckPdfOrientationRunningStep(
            text="Die PDF wird analyisiert"
        )
        self.check_pdf_orientation_running_step.finished.connect(
            lambda indices, path: self.open_check_pdf_orientation_step(indices, path))

        self.save_temp_pdf_running_step = SaveTempPdfRunningStep(
            text="PDF wird zwischengespeichert"
        )
        self.save_temp_pdf_running_step.finished.connect(lambda path: self.open_crop_step(path))

        self.check_pdf_orientation_step = CheckPdfOrientationStep(
            text="Folgende Seiten müssen überprüft werden",
            next_callback=self.open_crop_step_after_rotation
        )

        self.crop_amount_step = CropAmountStep(
            text="Die PDF wird analysiert",
            next_callback=self.crop_pdf
        )

        self.crop_running_step = CropRunningStep(
            text="Die PDF wird zugeschnitten"
        )
        self.crop_running_step.finished.connect(self.crop_finished)

        self.ocr_language_selection_step = OcrLanguageSelectionStep(
            text="Wähle die OCR-Sprachen für die PDF",
            next_callback=self.do_ocr
        )

        self.ocr_running_step = OcrRunningStep(text="OCR läuft")
        self.ocr_running_step.finished.connect(self.ocr_running_finished)
        self.ocr_finished_step = Step(
            text="OCR abgeschlossen. Bitte überprüfen und dann auf weiter.",
            next_callback=self.open_save_location_step
        )

        self.choose_save_location_step = FileNameSelectionStep(
            text="Wähle Speicherort und Name der PDF",
            next_callback=self.save_pdf
        )

        self.save_running_step = SavePDFRunningStep(
            text="PDF wird gespeichert"
        )
        self.save_running_step.finished.connect(self.clean_up)

        self.clean_up_running_step = CleanUpRunningStep(
            text="Es wird augeräumt"
        )
        self.clean_up_running_step.finished.connect(self.clean_up_finished)

        self.finished_step = Step(
            text="Fertig!",
            next_callback=lambda: exit(0),
            next_text="Schließen",
            previous_callback=self.reset,
            previous_text="Neue PDF verarbeiten"
        )

        self.steps = [
            self.file_selection_step,
            self.open_finereader_step,
            self.procedures_step,
            self.check_pdf_orientation_running_step,
            self.check_pdf_orientation_step,
            self.save_temp_pdf_running_step,
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

        self.layout.setCurrentIndex(self.current_index)

        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)
        self.rectangle = None

    def open_next_step(self):
        self.current_index += 1
        self.layout.setCurrentIndex(self.current_index)

    def open_finereader_and_ocr_editor(self):
        if self.file_selection_step.file_selection.selected_file_name != "":
            self.open_finereader_step.set_pdf_path(self.file_selection_step.file_selection.file_path())
            self.open_next_step()
            self.open_finereader_step.start()

    def open_crop_step(self, path: str):
        self.open_next_step()
        self.window().activateWindow()
        self.crop_amount_step.open_pdf_pages(path)

    def open_crop_step_after_rotation(self):
        self.open_next_step()
        self.save_temp_pdf_running_step.start()

    def crop_finished(self):
        self.open_next_step()
        self.window().activateWindow()

    def crop_pdf(self):
        self.crop_running_step.start(
            self.crop_amount_step.path_to_pdf,
            self.crop_amount_step.crop_amount_selection.get_pts_rectangle()
        )
        self.open_next_step()

    def open_image_improvement_tools(self):
        FineReaderAutomation.open_image_improvement_tools()
        self.do_optimization()
        self.open_next_step()

    def open_check_pdf_orientation_running_step(self, file_name: UUID):
        self.open_next_step()
        path = os.path.abspath(f"{FINEREADER_WORKING_DIR}\\{str(file_name)}.pdf")
        self.check_pdf_orientation_running_step.start(path)

    def open_check_pdf_orientation_step(self, indices: List[int], path: str):
        self.check_pdf_orientation_step.set_indices(indices)
        self.check_pdf_orientation_step.set_path(path)
        if len(indices) == 0:
            self.open_next_step()
            self.open_next_step()
            self.open_crop_step(path)
        else:
            self.open_next_step()
            self.activateWindow()

    def open_procedure_step(self):
        self.open_next_step()
        self.window().activateWindow()

    def do_optimization(self):
        self.procedures_step.start()

    def do_ocr(self):
        self.open_next_step()
        languages = self.ocr_language_selection_step.get_selected_language()
        self.ocr_running_step.start(languages)

    def ocr_running_finished(self):
        console.log(Panel("[green]OCR Finished"))
        self.open_next_step()
        self.window().activateWindow()

    def open_save_location_step(self):
        self.open_next_step()
        self.choose_save_location_step.folder_selection.set_folder(SaveConfig.STANDARD_SAVE_LOCATION)
        self.choose_save_location_step.set_previous_name(self.file_selection_step.file_selection.selected_file_name)

    def save_pdf(self):
        if self.choose_save_location_step.folder_selection.selected_folder != "":
            self.open_next_step()
            folder = self.choose_save_location_step.folder_selection.selected_folder
            file_name = self.choose_save_location_step.file_name_field.text()
            suffix = "" if ".pdf" in file_name else ".pdf"
            path = os.path.abspath(folder + "\\" + file_name + suffix)
            self.save_running_step.start(path)

    def reset(self):
        for step in self.steps:
            step.reset()
        self.layout.setCurrentIndex(0)
        self.current_index = 0

    def clean_up_finished(self):
        self.open_next_step()
        self.window().activateWindow()

    def clean_up(self):
        self.window().activateWindow()
        self.open_next_step()
        self.clean_up_running_step.start()
