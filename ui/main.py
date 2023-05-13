import os
import time
from sys import exit

from PyQt6.QtWidgets import QWidget, QStackedLayout, QMainWindow, QMessageBox
from rich.panel import Panel
from automation.check_pdf_save_location import check_pdf_save_location

from automation.ocr_automation import OcrAutomation
from automation.procedures.general_procedures import GeneralProcedures
from automation.procedures.ocr_procedures import OcrProcedures
from automation.store import Store
from config import Config
from ui.controller.settings_controller import SettingsController
from ui.steps.convert_pdf_step import ConvertPdfStep
from ui.steps.author_administration_step import AuthorAdministrationStep
from ui.steps.check_pdf_orientation_running_step import CheckPdfOrientationRunningStep
from ui.steps.check_pdf_orientation_step import CheckPdfOrientationStep
from ui.steps.clean_up_running_step import CleanUpRunningStep
from ui.steps.crop_amount_step import CropAmountStep
from ui.steps.crop_pdf_question_step import CropPdfQuestionStep
from ui.steps.crop_running_step import CropRunningStep
from ui.steps.file_name_selection_step import FileNameSelectionStep
from ui.steps.grayscale_running_step import GrayscaleRunning
from ui.steps.start_step import StartStep
from ui.steps.ocr_clean_up_step import OcrCleanUpStep
from ui.steps.ocr_custom_ocr_file_step import OcrCustomOcrFileStep
from ui.steps.ocr_default_error_replacement_running_step import (
    OcrDefaultErrorReplacementRunningStep,
)
from ui.steps.ocr_default_error_replacement_step import OcrDefaultErrorReplacementStep
from ui.steps.ocr_from_file_running_step import OcrFromFileRunningStep
from ui.steps.ocr_language_selection_step import OcrLanguageSelectionStep
from ui.steps.ocr_running_step import OcrRunningStep
from ui.steps.open_ocr_editor_step import OpenOcrEditorStep
from ui.steps.procedure_selection_step import ProcedureSelectionStep
from ui.steps.redo_crop_option_step import RedoCropOptionStep
from ui.steps.redo_save_pdf_step import RedoSavePdfStep
from ui.steps.save_pdf_running_step import SavePDFRunningStep
from ui.steps.save_temp_pdf_running import SaveTempPdfRunningStep
from ui.steps.set_metadata_step import SetMetadataStep
from ui.steps.step import Step
from utils.console import console
from utils.convert_pdf_result import ConvertPdfResult
from utils.dialog import create_dialog
from utils.file_utils import delete_file
from utils.keyboard_util import press_key
from utils.ocr_languages import german_old
from utils.save_config import SaveConfig
from utils.save_pdf import save_pdf


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"OCR Automation v{Config.VERSION}")
        self.resize(1024, 800)

        self.layout = QStackedLayout()

        # self.current_index = 26
        self.current_index = 0
        self.steps = []

        self.file_selection_step: Step = None
        self.open_ocr_editor_step = None
        self.crop_ocr_pdf_question_step = None
        self.convert_pdf_step = None
        self.crop_ocr_pdf_amount_step = None
        self.gray_scale_check_step = None
        self.open_cropped_ocr_pdf = None
        self.crop_ocr_pdf_running_step = None
        self.crop_ocr_pdf_redo_option_step = None
        self.select_procedures_step = None
        self.crop_pdf_question_step = None
        self.ocr_clean_up_step_before_crop = None
        self.save_temp_pdf_after_procedures = None
        self.check_pdf_orientation_running_step = None
        self.check_pdf_orientation_step = None
        self.save_temp_pdf_running_step = None
        self.crop_amount_step = None
        self.open_ocr_editor_skip_crop = None
        self.crop_running_step = None
        self.open_cropped_pdf_step = None
        self.procedures_after_crop = None
        self.ocr_clean_up_step = None
        self.ocr_language_selection_step = None
        self.select_custom_ocr_file = None
        self.ocr_running_step = None
        self.ocr_from_file_running_step = None
        self.ocr_default_error_replacement_finished_step = None
        self.ocr_finished_step = None
        self.ocr_default_error_replacement_step = None
        self.ocr_default_error_replacement_running_step = None
        self.choose_save_location_step = None
        self.set_metadata_step = None
        self.set_metadata_step_for_metadata = None
        self.choose_save_location_for_metadata_step = None
        self.save_running_step = None
        self.redo_save_pdf_step = None
        self.redo_save_pdf_for_metadata_step = None
        self.clean_up_running_step = None
        self.finished_step = None
        self.settings_controller = None
        self.author_administration_step = None
        self.crop_redo_step = None
        self.gray_scale_running_step = None

        # region Steps

        # region READ OCR FROM FILE OPTION: Crop PDF question
        self.crop_ocr_pdf_question_step = CropPdfQuestionStep(
            text="Soll die PDF zugeschnitten werden?",
            next_callback=lambda: self.open_convert_pdf_step(Store.SELECTED_FILE_PATH),
            previous_callback=self.open_ocr_from_file_step,
        )
        # endregion

        # region READ OCR FROM FILE OPTION: OCR from file running
        self.ocr_from_file_running_step = OcrFromFileRunningStep(
            text="OCR läuft",
            next_text="OCR ist bereits abgeschlossen",
            next_callback=self.ocr_from_file_skip_still_running,
        )
        self.ocr_from_file_running_step.finished.connect(self.ocr_running_finished)
        # endregion

        # region READ OCR FROM FILE OPTION: Crop redo question
        self.crop_ocr_pdf_redo_option_step = RedoCropOptionStep(
            next_callback=self.crop_ocr_pdf_redo_skip,
            previous_callback=self.crop_ocr_pdf_redo,
        )
        # endregion

        # region READ OCR FROM FILE OPTION: Open OCR editor
        self.open_cropped_ocr_pdf = OpenOcrEditorStep()
        self.open_cropped_ocr_pdf.finished_signal.connect(self.open_ocr_from_file_step)
        # endregion

        # region READ OCR FROM FILE OPTION: Crop PDF running
        self.crop_ocr_pdf_running_step = CropRunningStep(
            text="Die PDF wird zugeschnitten"
        )
        self.crop_ocr_pdf_running_step.finished.connect(self.crop_ocr_pdf_finished)
        # endregion

        # region Start Step
        self.file_selection_step = StartStep(
            text="Wähle eine PDF-Datei aus",
            previous_text="Einstellungen",
            previous_callback=self.open_settings,
            next_callback=self.open_ocr_editor,
            set_metadata_callback=self.open_save_location_step_for_metadata,
            read_ocr_callback=lambda: self.open_step(self.crop_ocr_pdf_question_step),
            author_administration_callback=self.open_author_administration,
        )
        # endregion

        # region Author administration
        self.author_administration_step = AuthorAdministrationStep(
            text="Autoren",
            previous_callback=lambda: self.open_step(self.file_selection_step),
        )
        # endregion

        # region Open OCR Editor
        self.open_ocr_editor_step = OpenOcrEditorStep()
        self.open_ocr_editor_step.finished_signal.connect(self.open_procedure_step)
        # endregion Open OCR Editor

        # region Select procedures
        self.select_procedures_step = ProcedureSelectionStep(
            text="Welche Optimierungen sollen durchgeführt werden?",
            next_callback=self.start_procedures,
        )
        self.select_procedures_step.finished.connect(
            lambda: (
                self.open_grayscale_check(),
                self.window().activateWindow(),
            )
        )
        # endregion

        # region Save temp PDF after procedures
        self.save_temp_pdf_after_procedures = SaveTempPdfRunningStep(
            text="PDF wird zwischengespeichert"
        )
        self.save_temp_pdf_after_procedures.finished.connect(
            self.save_temp_pdf_after_procedures_finished
        )
        # endregion

        # region Grayscale Check
        self.gray_scale_check_step = Step(
            text="Soll das Bild in schwarzweiß umgewandelt werden?",
            next_text="Ja",
            next_callback=self.convert_image_to_binary,
            previous_text="Nein",
            previous_callback=lambda: (
                self.open_step(self.crop_pdf_question_step),
                self.activateWindow(),
            ),
        )
        # endregion

        # region Grayscale running
        self.gray_scale_running_step = GrayscaleRunning(
            text="PDF wird zu schwarzweiß konvertiert"
        )
        self.gray_scale_running_step.finished.connect(
            lambda: (self.open_step(self.crop_pdf_question_step), self.activateWindow())
        )

        # endregion

        # region Convert PDF to images
        self.convert_pdf_step = ConvertPdfStep(
            text="Die PDF wird analysiert",
            next_callback=self.crop_ocr_pdf,
            previous_text="Überspringen",
            previous_callback=self.open_ocr_from_file_step,
        )
        self.convert_pdf_step.finished.connect(self.open_crop_step)
        # endregion

        # region Generate initial crop boxes
        self.crop_ocr_pdf_amount_step = CropAmountStep(
            text="Die PDF wird analysiert",
            next_callback=self.crop_ocr_pdf,
            previous_text="Überspringen",
            previous_callback=self.open_ocr_from_file_step,
        )
        # endregion

        # region Crop PDF question
        self.crop_pdf_question_step = CropPdfQuestionStep(
            text="Soll die PDF zugeschnitten werden?",
            next_callback=self.crop_pdf_question_acceptance,
            previous_callback=self.open_ocr_clean_up_step,
        )
        # endregion

        # region OCR clean up step before crop
        self.ocr_clean_up_step_before_crop = OcrCleanUpStep(
            text="Entferne Artefakte von den Seiten",
            next_text="Fertig",
            next_callback=self.ocr_clean_up_before_crop_finished,
            previous_callback=lambda: self.open_step(self.crop_pdf_question_step),
            previous_text="Zurück",
        )
        # endregion

        # region Check PDF orientation running
        self.check_pdf_orientation_running_step = CheckPdfOrientationRunningStep(
            text="Die PDF wird analyisiert"
        )

        self.check_pdf_orientation_running_step.finished.connect(
            self.open_check_pdf_orientation_step
        )
        # endregion

        # region Check PDF orientation
        self.check_pdf_orientation_step = CheckPdfOrientationStep(
            text="Folgende Seiten müssen überprüft werden",
            next_callback=self.save_pdf_after_orientation_fix,
        )
        # endregion

        # region Save temp PDF running
        self.save_temp_pdf_running_step = SaveTempPdfRunningStep(
            text="PDF wird zwischengespeichert"
        )
        self.save_temp_pdf_running_step.finished.connect(self.open_convert_pdf_step)
        # endregion

        # region Crop amount step
        self.crop_amount_step = CropAmountStep(
            text="Die PDF wird analysiert",
            next_callback=self.crop_pdf,
            previous_text="Überspringen",
            previous_callback=self.open_ocr_editor_after_crop_skip,
        )
        # endregion

        # region Open OCR editor skip crop
        self.open_ocr_editor_skip_crop = OpenOcrEditorStep()
        self.open_ocr_editor_skip_crop.finished_signal.connect(
            self.open_ocr_editor_after_crop_skip_done
        )
        # endregion

        # region Crop running
        self.crop_running_step = CropRunningStep(text="Die PDF wird zugeschnitten")
        self.crop_running_step.finished.connect(self.crop_finished)
        # endregion

        # region Crop redo step
        self.crop_redo_step = RedoCropOptionStep(
            next_callback=self.open_cropped_pdf, previous_callback=self.crop_redo
        )
        # endregion

        # region Open cropped PDF in OCR editor
        self.open_cropped_pdf_step = OpenOcrEditorStep()
        self.open_cropped_pdf_step.finished_signal.connect(
            self.open_cropped_pdf_finished
        )
        # endregion

        # region Procedures after crop
        self.procedures_after_crop = ProcedureSelectionStep(
            text="Welche Optimierungen sollen durchgeführt werden?",
            previous_text="Überspringen",
            previous_callback=self.open_ocr_clean_up_step,
            next_callback=self.start_procedures_after_crop,
        )
        self.procedures_after_crop.finished.connect(self.open_ocr_clean_up_step)
        # endregion

        # region OCR clean up
        self.ocr_clean_up_step = OcrCleanUpStep(
            text="Entferne Artefakte von den Seiten, um das OCR Ergebnis zu verbessern",
            next_callback=lambda: (self.open_ocr_language_selection_step(True)),
        )
        # endregion

        # region OCR language selection
        self.ocr_language_selection_step = OcrLanguageSelectionStep(
            text="Wähle die OCR-Sprachen für die PDF",
            next_callback=self.check_ocr_languages,
        )
        # endregion

        # region select custom OCR file (Fraktur)
        self.select_custom_ocr_file = OcrCustomOcrFileStep(next_callback=self.start_ocr)
        # endregion

        # region OCR running
        self.ocr_running_step = OcrRunningStep(
            text="OCR läuft",
            next_text="OCR ist bereits abgeschlossen",
            next_callback=self.ocr_skip_still_running,
        )

        self.ocr_running_step.finished.connect(self.ocr_running_finished)
        # endregion

        # region OCR default error replacement finished
        self.ocr_default_error_replacement_finished_step = Step(
            text="Korrektur der Standardfehler abgeschlossen. Händische Nachkorrektur und dann weiter",
            next_callback=self.open_save_location_step,
            previous_text="OCR wiederholen",
            previous_callback=lambda: self.open_step(self.ocr_language_selection_step),
        )
        # endregion

        # region OCR finished
        self.ocr_finished_step = Step(
            text="OCR abgeschlossen. Sollen die OCR Standardfehler ersetzt werden?",
            previous_text="Nein",
            previous_callback=lambda: self.open_step(
                self.ocr_default_error_replacement_finished_step
            ),
            next_text="Ja",
            next_callback=self.open_ocr_default_error_replacement,
        )
        # endregion

        # region OCR default error replacement
        self.ocr_default_error_replacement_step = OcrDefaultErrorReplacementStep(
            text="Wähle welche Standardfehlerlisten verwendet werden sollen",
            next_callback=self.start_ocr_default_error_replacement,
            next_text="Weiter",
            previous_callback=self.open_save_location_step,
            previous_text="Überspringen",
        )
        # endregion

        # region OCR default error replacement running
        self.ocr_default_error_replacement_running_step = (
            OcrDefaultErrorReplacementRunningStep(
                text="OCR Standardfehler werden korrigiert",
                next_text="Überspringen",
                next_callback=self.skip_ocr_standard_replacement_running,
            )
        )

        self.ocr_default_error_replacement_running_step.finished.connect(
            lambda: self.open_step(
                self.ocr_default_error_replacement_finished_step, focus_window=True
            )
        )
        # endregion

        # region Choose save location
        self.choose_save_location_step = FileNameSelectionStep(
            text="Wähle Speicherort und Name der PDF",
            previous_text="Ohne Precise Scan speichern",
            previous_callback=None,
            next_callback=self.open_set_metadata,
        )
        # endregion

        # region Set metadata
        self.set_metadata_step = SetMetadataStep(
            text="Setze die Metadaten",
            previous_text="Ohne Precise Scan speichern",
            previous_callback=lambda: self.save_pdf_callback(enable_precise_scan=False),
            next_text="Mit Precise Scan speichern",
            next_callback=lambda: self.save_pdf_callback(enable_precise_scan=True),
        )
        # endregion

        # region Save running
        self.save_running_step = SavePDFRunningStep(text="PDF wird gespeichert")
        self.save_running_step.finished.connect(self.open_redo_pdf_save_step)
        # endregion

        # region Redo save
        self.redo_save_pdf_step = RedoSavePdfStep(
            previous_callback=self.go_back_to_save_pdf_step,
            next_callback=self.clean_up,
        )
        # endregion

        # region Clean up running
        self.clean_up_running_step = CleanUpRunningStep(text="Es wird augeräumt")
        self.clean_up_running_step.finished.connect(self.clean_up_finished)
        # endregion

        # region Finished
        self.finished_step = Step(
            text="Fertig!",
            next_callback=lambda: exit(0),
            next_text="Schließen",
            previous_callback=self.reset,
            previous_text="Neue PDF verarbeiten",
        )
        # endregion

        # region Settings controller
        self.settings_controller = SettingsController(
            previous_callback=lambda: self.open_step(self.file_selection_step),
            next_callback=lambda: self.open_step(self.file_selection_step),
        )
        # endregion

        # region SET METADATA OPTION: Set metadata
        self.set_metadata_step_for_metadata = SetMetadataStep(
            text="Setze die Metadaten",
            next_text="Speichern",
            next_callback=lambda: self.save_pdf_callback(save_without_abby=True),
        )
        # endregion

        # region SET METADATA OPTION: Choose save location
        self.choose_save_location_for_metadata_step = FileNameSelectionStep(
            text="Wähle Speicherort und Name der PDF",
            next_text="Weiter",
            next_callback=self.open_set_metadata_for_metadata,
        )
        # endregion

        # region SET METADATA OPTION: Redo save PDF
        self.redo_save_pdf_for_metadata_step = RedoSavePdfStep(
            previous_callback=self.go_back_to_save_pdf_for_export_step,
            next_callback=self.save_pdf_only_metadata_finished,
        )
        # endregion

        # endregion Steps

        self.steps = [
            self.file_selection_step,
            self.author_administration_step,
            self.open_ocr_editor_step,
            self.select_procedures_step,
            self.crop_pdf_question_step,
            self.save_temp_pdf_after_procedures,
            self.check_pdf_orientation_running_step,
            self.check_pdf_orientation_step,
            self.ocr_clean_up_step_before_crop,
            self.save_temp_pdf_running_step,
            self.convert_pdf_step,
            self.gray_scale_check_step,
            self.gray_scale_running_step,
            self.crop_amount_step,
            self.crop_running_step,
            self.crop_redo_step,
            self.open_cropped_pdf_step,
            self.procedures_after_crop,
            self.ocr_clean_up_step,
            self.ocr_language_selection_step,
            self.select_custom_ocr_file,
            self.ocr_running_step,
            self.ocr_from_file_running_step,
            self.ocr_finished_step,
            self.ocr_default_error_replacement_step,
            self.ocr_default_error_replacement_running_step,
            self.ocr_default_error_replacement_finished_step,
            self.choose_save_location_step,
            self.choose_save_location_for_metadata_step,
            self.set_metadata_step,
            self.save_running_step,
            self.redo_save_pdf_step,
            self.redo_save_pdf_for_metadata_step,
            self.clean_up_running_step,
            self.finished_step,
            self.settings_controller.settings_step,
            self.open_ocr_editor_skip_crop,
            self.crop_ocr_pdf_question_step,
            self.crop_ocr_pdf_amount_step,
            self.crop_ocr_pdf_running_step,
            self.crop_ocr_pdf_redo_option_step,
            self.set_metadata_step_for_metadata,
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

    def open_step(self, step: Step, focus_window=False):
        index = self.steps.index(step)
        self.current_index = index
        self.layout.setCurrentIndex(self.current_index)
        if focus_window:
            self.window().activateWindow()

    def open_settings(self):
        self.settings_controller.update_values()
        self.open_step(self.settings_controller.settings_step)

    def open_ocr_editor(self):
        if Store.SELECTED_FILE_PATH != "":
            self.open_step(self.open_ocr_editor_step)
            self.open_ocr_editor_step.start(Store.SELECTED_FILE_PATH)

    def open_ocr_editor_after_crop_skip(self):
        OcrAutomation.close_pdf_in_default_program()
        self.open_step(self.open_ocr_editor_skip_crop)
        self.open_ocr_editor_skip_crop.start(self.crop_amount_step.path_to_pdf)

    def open_ocr_editor_after_crop_skip_done(self):
        self.open_step(self.ocr_language_selection_step)
        self.window().activateWindow()

    def start_procedures(self):
        self.select_procedures_step.start()

    def start_procedures_after_crop(self):
        self.procedures_after_crop.start()

    def crop_pdf_question_acceptance(self):
        self.open_step(self.ocr_clean_up_step_before_crop)
        self.ocr_clean_up_step_before_crop.start()

    def ocr_clean_up_before_crop_finished(self):
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
        if len(Store.INDICES_TO_ROTATE) == 0:
            self.open_step(self.save_temp_pdf_running_step)
            self.open_convert_pdf_step(Store.FILE_PATH_AFTER_PROCEDURES)
        else:
            self.open_next_step()
            self.activateWindow()

    def save_pdf_after_orientation_fix(self):
        self.open_next_step()
        self.save_temp_pdf_running_step.start()

    def open_convert_pdf_step(self, pdf_path: str):
        self.open_step(self.convert_pdf_step)
        self.convert_pdf_step.convert_pdf_pages(pdf_path)

    def open_grayscale_check(self):
        self.open_step(self.gray_scale_check_step)

    def convert_image_to_binary(self):
        self.open_step(self.gray_scale_running_step)
        self.gray_scale_running_step.start()
        # Store.CONVERT_PDF_RESULT.should_convert_to_greyscale = True

    def open_crop_step(self):
        self.open_step(self.crop_amount_step)
        self.window().activateWindow()
        self.crop_amount_step.open_pdf_pages()

    def crop_pdf(self):
        self.crop_running_step.start(
            Store.CONVERT_PDF_RESULT.path_to_pdf,
            self.crop_amount_step.crop_amount_selection_controller.get_max_crop_box_pixel(),
            self.crop_amount_step.crop_amount_selection_controller.get_transformed_crop_boxes_pixel(),
            Store.CONVERT_PDF_RESULT.images,
            self.crop_amount_step.crop_amount_selection_controller.get_transformed_crop_boxes_pts(),
            False,
        )
        self.open_next_step()

    def crop_finished(self):
        self.open_step(self.crop_redo_step)
        self.window().activateWindow()

    def crop_redo(self):
        OcrAutomation.close_pdf_in_default_program()
        self.open_step(self.crop_amount_step)

    def open_crop_ocr_question(self):
        self.open_step(self.crop_ocr_pdf_question_step)

    def open_crop_ocr_pdf_step(self):
        if Store.SELECTED_FILE_PATH != "":
            self.open_step(self.crop_ocr_pdf_amount_step)
            self.crop_ocr_pdf_amount_step.open_pdf_pages()

    def crop_ocr_pdf(self):
        self.crop_ocr_pdf_running_step.start(
            self.crop_ocr_pdf_amount_step.convert_pdf_result.path_to_pdf,
            self.crop_ocr_pdf_amount_step.crop_amount_selection_controller.get_max_crop_box_pixel(),
            self.crop_ocr_pdf_amount_step.crop_amount_selection_controller.get_transformed_crop_boxes_pixel(),
            Store.CONVERT_PDF_RESULT.images,
            self.crop_ocr_pdf_amount_step.crop_amount_selection_controller.get_transformed_crop_boxes_pts(),
            True,
        )
        self.open_step(self.crop_ocr_pdf_running_step)

    def crop_ocr_pdf_finished(self):
        self.open_step(self.crop_ocr_pdf_redo_option_step)
        self.activateWindow()

    def open_cropped_pdf(self):
        OcrAutomation.close_pdf_in_default_program()
        self.open_cropped_pdf_step.start(Store.CROPPED_PDF_PATH)

    def open_cropped_pdf_finished(self):
        self.activateWindow()
        self.open_step(self.procedures_after_crop)

    def crop_ocr_pdf_redo(self):
        OcrAutomation.close_pdf_in_default_program()
        self.open_step(self.crop_ocr_pdf_amount_step)

    def crop_ocr_pdf_redo_skip(self):
        OcrAutomation.close_pdf_in_default_program()
        self.open_cropped_ocr_pdf.start(Store.CROPPED_PDF_PATH, True)

    def open_image_improvement_tools(self):
        OcrAutomation.open_image_improvement_tools()
        self.start_procedures()
        self.open_next_step()

    def open_procedure_step(self):
        Config.PREVIOUS_RUN_WAS_COMPLETE_PROCEDURE = True
        self.open_step(self.select_procedures_step)
        self.window().activateWindow()

    def check_ocr_languages(self):
        languages = self.ocr_language_selection_step.get_selected_language()
        if german_old in languages:
            self.open_step(self.select_custom_ocr_file)
        else:
            self.start_ocr()

        console.log("OCR wird mit folgende Sprachen durchgeführt: ", languages)

    def start_ocr(self):
        languages = self.ocr_language_selection_step.get_selected_language()
        self.open_step(self.ocr_running_step)
        self.ocr_running_step.start(languages)

    def ocr_running_finished(self):
        console.log(Panel("[green]OCR fertig"))
        self.open_step(self.ocr_finished_step)
        self.window().activateWindow()

    def ocr_skip_still_running(self):
        self.ocr_running_step.stop()

    def ocr_from_file_skip_still_running(self):
        self.ocr_from_file_running_step.stop()

    def open_save_location_step(self):
        self.open_step(self.choose_save_location_step)
        self.choose_save_location_step.folder_selection.set_folder(
            SaveConfig.get_default_save_location()
        )
        self.choose_save_location_step.set_previous_name(
            self.file_selection_step.file_selection.selected_file_name
        )
        self.window().activateWindow()

    def open_ocr_clean_up_step(self):
        self.open_step(self.ocr_clean_up_step)
        self.ocr_clean_up_step.start()

    def open_ocr_language_selection_step(self, should_close=True):
        press_key(key_combination="alt+tab", delay_in_seconds=0.3)
        if should_close and Store.IMAGE_EDIT_TOOL_OPEN:
            GeneralProcedures.click_ocr_pages_header()
            time.sleep(0.3)
            OcrAutomation.close_image_improvement_tools()
        self.activateWindow()
        self.open_step(self.ocr_language_selection_step)

    def open_ocr_default_error_replacement(self):
        self.ocr_default_error_replacement_step.add_replacement_maps_check_boxes()
        self.open_step(self.ocr_default_error_replacement_step)

    def start_ocr_default_error_replacement(self):
        self.open_step(self.ocr_default_error_replacement_running_step)
        selected_maps = (
            self.ocr_default_error_replacement_step.get_selected_replacement_maps()
        )
        self.ocr_default_error_replacement_running_step.start(selected_maps)

    def skip_ocr_standard_replacement_running(self):
        self.ocr_default_error_replacement_running_step.stop()

    def open_ocr_from_file_step(self):
        self.open_step(self.ocr_from_file_running_step)
        self.ocr_from_file_running_step.start()

    def open_set_metadata(self):
        folder = self.choose_save_location_step.folder_selection.selected_folder
        file_name = self.choose_save_location_step.file_name_field.text()
        suffix = "" if ".pdf" in file_name else ".pdf"
        path = os.path.abspath(folder + "\\" + file_name + suffix)
        if self.handle_pdf_save_location(path):
            self.set_metadata_step.set_title(
                self.choose_save_location_step.file_name_field.text()
            )
            self.set_metadata_step.init()
            self.open_step(self.set_metadata_step)

    def open_set_metadata_for_metadata(self):
        folder = (
            self.choose_save_location_for_metadata_step.folder_selection.selected_folder
        )
        file_name = self.choose_save_location_for_metadata_step.file_name_field.text()
        suffix = "" if file_name.endswith(".pdf") else ".pdf"
        path = os.path.abspath(folder + "\\" + file_name + suffix)
        if self.handle_pdf_save_location(path):
            self.set_metadata_step_for_metadata.set_title(
                self.choose_save_location_for_metadata_step.file_name_field.text()
            )
            self.set_metadata_step_for_metadata.init()
            self.open_step(self.set_metadata_step_for_metadata)

    def handle_pdf_save_location(self, pdf_save_path: str):
        Store.SAVE_FILE_PATH = pdf_save_path
        return check_pdf_save_location(self)

    def save_pdf_callback(self, enable_precise_scan=False, save_without_abby=False):
        if save_without_abby:
            save_pdf(
                Store.SELECTED_FILE_PATH,
                Store.SAVE_FILE_PATH,
                self.set_metadata_step_for_metadata.get_metadata(),
            )
            self.open_step(self.redo_save_pdf_for_metadata_step)
        else:
            self.open_step(self.save_running_step)
            self.save_running_step.start(
                Store.SAVE_FILE_PATH,
                enable_precise_scan,
                self.set_metadata_step.get_metadata(),
            )

    def open_save_location_step_for_metadata(self):
        if Store.SELECTED_FILE_PATH != "":
            self.choose_save_location_for_metadata_step.folder_selection.set_folder(
                SaveConfig.get_default_save_location()
            )
            self.choose_save_location_for_metadata_step.set_previous_name(
                self.file_selection_step.file_selection.selected_file_name
            )

            self.open_step(self.choose_save_location_for_metadata_step)

    def open_author_administration(self):
        self.open_step(self.author_administration_step)
        self.author_administration_step.init()

    def go_back_to_save_pdf_step(self):
        OcrAutomation.close_pdf_in_default_program()
        delete_file(Store.SAVE_FILE_PATH)
        Store.SAVE_FILE_PATH = None
        self.open_save_location_step()

    def go_back_to_save_pdf_for_export_step(self):
        OcrAutomation.close_pdf_in_default_program()
        delete_file(Store.SAVE_FILE_PATH)
        Store.SAVE_FILE_PATH = None
        self.open_save_location_step_for_metadata()

    def open_redo_pdf_save_step(self):
        self.window().activateWindow()
        self.open_step(self.redo_save_pdf_step)

    def reset(self):
        for step in self.steps:
            step.reset()
        self.layout.setCurrentIndex(0)
        self.current_index = 0

    def clean_up_finished(self):
        self.open_step(self.finished_step)
        self.window().activateWindow()
        console.log(Panel("[green]Fertig"))

    def save_pdf_only_metadata_finished(self):
        self.open_step(self.finished_step)
        self.window().activateWindow()

    def clean_up(self):
        self.window().activateWindow()
        self.open_step(self.clean_up_running_step)
        self.clean_up_running_step.start()
