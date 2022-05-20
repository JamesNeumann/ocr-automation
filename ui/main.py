import os
import time
from sys import exit
from typing import List
from uuid import UUID

from PyQt6.QtWidgets import QWidget, QStackedLayout, QMainWindow
from rich.panel import Panel

from automation.ocr_automation import OcrAutomation
from automation.procedures.general_procedures import GeneralProcedures
from automation.store import Store
from config import OCR_WORKING_DIR, VERSION
from ui.steps.check_pdf_orientation_running_step import CheckPdfOrientationRunningStep
from ui.steps.check_pdf_orientation_step import CheckPdfOrientationStep
from ui.steps.clean_up_running_step import CleanUpRunningStep
from ui.steps.crop_amount_step import CropAmountStep
from ui.steps.crop_pdf_question_step import CropPdfQuestionStep
from ui.steps.crop_running_step import CropRunningStep
from ui.steps.file_name_selection_step import FileNameSelectionStep
from ui.steps.file_selection_step import FileSelectionStep
from ui.steps.ocr_language_selection_step import OcrLanguageSelectionStep
from ui.steps.ocr_running_step import OcrRunningStep
from ui.steps.open_ocr_editor_step import OpenOcrEditorStep
from ui.steps.procedure_selection_step import ProcedureSelectionStep
from ui.steps.save_pdf_running_step import SavePDFRunningStep
from ui.steps.save_temp_pdf_running import SaveTempPdfRunningStep
from ui.steps.settings_step import SettingsStep
from ui.steps.step import Step
from utils.console import console
from utils.keyboard_util import press_key
from utils.save_config import SaveConfig


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"OCR Automation v{VERSION}")
        self.resize(1024, 800)

        self.layout = QStackedLayout()

        self.current_index = 0

        self.file_selection_step = FileSelectionStep(
            text="Wähle eine PDF-Datei aus",
            previous_text="Einstellungen",
            previous_callback=self.open_settings,
            next_callback=self.open_ocr_editor
        )

        self.open_ocr_editor_step = OpenOcrEditorStep(
            text="Es wird gewartet bis der OCR-Editor vollständig geöffnet wurde",
        )
        self.open_ocr_editor_step.finished_signal.connect(self.open_procedure_step)

        self.procedures_step = ProcedureSelectionStep(
            text="Welche Optimierungen sollen durchgeführt werden?",
            next_callback=self.start_procedures
        )
        self.procedures_step.finished.connect(
            lambda: (self.open_step(self.crop_pdf_question_step), self.window().activateWindow()))

        self.crop_pdf_question_step = CropPdfQuestionStep(text="Soll die PDF zugeschnitten werden?",
                                                          next_callback=self.crop_pdf_question_acceptance,
                                                          previous_callback=self.open_ocr_language_selection_step)

        self.save_temp_pdf_after_procedures = SaveTempPdfRunningStep(
            text="PDF wird zwischengespeichert"
        )

        self.save_temp_pdf_after_procedures.finished.connect(
            lambda file: self.save_temp_pdf_after_procedures_finished(file)
        )

        self.check_pdf_orientation_running_step = CheckPdfOrientationRunningStep(
            text="Die PDF wird analyisiert"
        )
        self.check_pdf_orientation_running_step.finished.connect(self.open_check_pdf_orientation_step)

        self.check_pdf_orientation_step = CheckPdfOrientationStep(
            text="Folgende Seiten müssen überprüft werden",
            next_callback=self.save_pdf_after_orientation_fix
        )
        self.save_temp_pdf_running_step = SaveTempPdfRunningStep(
            text="PDF wird zwischengespeichert"
        )
        self.save_temp_pdf_running_step.finished.connect(
            lambda file: self.open_crop_step(file)
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
            next_callback=self.open_save_location_step,
            previous_text="OCR wiederholen",
            previous_callback=lambda: self.open_step(self.ocr_language_selection_step)
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

        self.settings_step = SettingsStep(text="Einstellungen",
                                          previous_callback=lambda: self.open_step(self.file_selection_step),
                                          next_callback=self.save_settings_callback)

        self.steps = [
            self.file_selection_step,
            self.open_ocr_editor_step,
            self.procedures_step,
            self.crop_pdf_question_step,
            self.save_temp_pdf_after_procedures,
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
            self.finished_step,
            self.settings_step,
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

    def open_step(self, step: Step):
        index = self.steps.index(step)
        self.current_index = index
        self.layout.setCurrentIndex(self.current_index)

    def open_settings(self):
        self.settings_step.update_values()
        self.open_step(self.settings_step)

    def save_settings_callback(self):
        top, right, bottom, left = self.settings_step.get_crop_box()
        SaveConfig.update_default_crop_box_offset(top, right, bottom, left)
        self.open_step(self.file_selection_step)

    def open_ocr_editor(self):
        if Store.SELECTED_FILE_PATH != "":
            self.open_step(self.open_ocr_editor_step)
            self.open_ocr_editor_step.start()

    def start_procedures(self):
        self.procedures_step.start()

    def crop_pdf_question_acceptance(self):
        self.open_step(self.save_temp_pdf_after_procedures)
        self.save_temp_pdf_after_procedures.start()

    def save_temp_pdf_after_procedures_finished(self, file):
        Store.FILE_PATH_AFTER_PROCEDURES = file
        self.open_step(self.check_pdf_orientation_running_step)
        self.check_pdf_orientation_running_step.start()

    def open_check_pdf_orientation_running_step(self):
        self.open_step(self.check_pdf_orientation_running_step)
        self.check_pdf_orientation_running_step.start()

    def open_check_pdf_orientation_step(self):
        self.check_pdf_orientation_step.set_indices(Store.INDICES_TO_ROTATE)
        console.log(Store.INDICES_TO_ROTATE)
        if len(Store.INDICES_TO_ROTATE) == 0:
            self.open_step(self.save_temp_pdf_running_step)
            self.open_crop_step(Store.FILE_PATH_AFTER_PROCEDURES)
        else:
            self.open_next_step()
            self.activateWindow()

    def open_crop_step(self, path: str):
        self.open_next_step()
        self.window().activateWindow()
        self.crop_amount_step.open_pdf_pages(path)

    def save_pdf_after_orientation_fix(self):
        self.open_next_step()
        self.save_temp_pdf_running_step.start()

    def crop_finished(self):
        self.open_next_step()
        self.window().activateWindow()

    def crop_pdf(self):
        self.crop_running_step.start(
            self.crop_amount_step.path_to_pdf,
            self.crop_amount_step.crop_amount_selection.get_pts_rectangle(),
            self.crop_amount_step.crop_amount_selection.get_pts_rectangles()
        )
        self.open_next_step()

    def open_image_improvement_tools(self):
        OcrAutomation.open_image_improvement_tools()
        self.start_procedures()
        self.open_next_step()

    def open_procedure_step(self):
        self.open_step(self.procedures_step)
        self.window().activateWindow()

    def do_ocr(self):
        self.open_next_step()
        languages = self.ocr_language_selection_step.get_selected_language()
        console.log(languages)
        self.ocr_running_step.start(languages)

    def ocr_running_finished(self):
        console.log(Panel("[green]OCR Finished"))
        self.open_next_step()
        self.window().activateWindow()

    def open_save_location_step(self):
        self.open_next_step()
        self.choose_save_location_step.folder_selection.set_folder(SaveConfig.STANDARD_SAVE_LOCATION)
        self.choose_save_location_step.set_previous_name(self.file_selection_step.file_selection.selected_file_name)

    def open_ocr_language_selection_step(self):
        GeneralProcedures.click_ocr_pages_header()
        time.sleep(0.3)
        OcrAutomation.close_image_improvement_tools()
        time.sleep(0.3)
        self.activateWindow()
        self.open_step(self.ocr_language_selection_step)

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
        Store.reset()
