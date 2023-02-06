import os
import time
from sys import exit

from PyQt6.QtWidgets import QWidget, QStackedLayout, QMainWindow, QMessageBox
from rich.panel import Panel

from automation.ocr_automation import OcrAutomation
from automation.procedures.general_procedures import GeneralProcedures
from automation.store import Store
from config import Config
from ui.controller.settings_controller import SettingsController
from ui.steps.check_pdf_orientation_running_step import CheckPdfOrientationRunningStep
from ui.steps.check_pdf_orientation_step import CheckPdfOrientationStep
from ui.steps.clean_up_running_step import CleanUpRunningStep
from ui.steps.crop_amount_step import CropAmountStep
from ui.steps.crop_pdf_question_step import CropPdfQuestionStep
from ui.steps.crop_running_step import CropRunningStep
from ui.steps.file_name_selection_step import FileNameSelectionStep
from ui.steps.file_selection_step import FileSelectionStep
from ui.steps.ocr_clean_up_step import OcrCleanUpStep
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
from utils.dialog import create_dialog
from utils.file_utils import delete_file
from utils.save_config import SaveConfig
from utils.save_pdf import save_pdf


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"OCR Automation v{Config.VERSION}")
        self.resize(1024, 800)

        self.layout = QStackedLayout()

        self.current_index = 0
        self.steps = []

        self.file_selection_step = FileSelectionStep(
            text="Wähle eine PDF-Datei aus",
            previous_text="Einstellungen",
            previous_callback=self.open_settings,
            next_callback=self.open_ocr_editor,
            set_metadata_callback=self.open_save_location_step_for_metadata,
            read_ocr_callback=self.open_crop_ocr_question,
        )

        self.open_ocr_editor_step = OpenOcrEditorStep()
        self.open_ocr_editor_step.finished_signal.connect(self.open_procedure_step)

        self.crop_ocr_pdf_question_step = CropPdfQuestionStep(
            text="Soll die PDF zugeschnitten werden?",
            next_callback=self.open_crop_ocr_pdf_step,
            previous_callback=self.open_ocr_from_file_step,
        )

        self.crop_ocr_pdf_amount_step = CropAmountStep(
            text="Die PDF wird analysiert",
            next_callback=self.crop_ocr_pdf,
            previous_text="Überspringen",
            previous_callback=self.open_ocr_from_file_step,
        )

        self.crop_ocr_pdf_redo_option_step = RedoCropOptionStep(
            next_callback=self.crop_ocr_pdf_redo_skip,
            previous_callback=self.crop_ocr_pdf_redo,
        )

        self.open_cropped_ocr_pdf = OpenOcrEditorStep()
        self.open_cropped_ocr_pdf.finished_signal.connect(self.open_ocr_from_file_step)

        self.crop_ocr_pdf_running_step = CropRunningStep(
            text="Die PDF wird zugeschnitten"
        )
        self.crop_ocr_pdf_running_step.finished.connect(self.crop_ocr_pdf_finished)

        self.select_procedures_step = ProcedureSelectionStep(
            text="Welche Optimierungen sollen durchgeführt werden?",
            next_callback=self.start_procedures,
        )
        self.select_procedures_step.finished.connect(
            lambda: (
                self.open_step(self.crop_pdf_question_step),
                self.window().activateWindow(),
            )
        )

        self.crop_pdf_question_step = CropPdfQuestionStep(
            text="Soll die PDF zugeschnitten werden?",
            next_callback=self.crop_pdf_question_acceptance,
            previous_callback=self.open_ocr_clean_up_step,
        )

        self.ocr_clean_up_step_before_crop = OcrCleanUpStep(
            text="Entferne Artefakte von den Seiten",
            next_text="Fertig",
            next_callback=self.ocr_clean_up_before_crop_finished,
            previous_callback=lambda: self.open_step(self.crop_pdf_question_step),
            previous_text="Zurück",
        )

        self.save_temp_pdf_after_procedures = SaveTempPdfRunningStep(
            text="PDF wird zwischengespeichert"
        )

        self.save_temp_pdf_after_procedures.finished.connect(
            self.save_temp_pdf_after_procedures_finished
        )

        self.check_pdf_orientation_running_step = CheckPdfOrientationRunningStep(
            text="Die PDF wird analyisiert"
        )

        self.check_pdf_orientation_running_step.finished.connect(
            self.open_check_pdf_orientation_step
        )

        self.check_pdf_orientation_step = CheckPdfOrientationStep(
            text="Folgende Seiten müssen überprüft werden",
            next_callback=self.save_pdf_after_orientation_fix,
        )
        self.save_temp_pdf_running_step = SaveTempPdfRunningStep(
            text="PDF wird zwischengespeichert"
        )
        self.save_temp_pdf_running_step.finished.connect(self.open_crop_step)

        self.crop_amount_step = CropAmountStep(
            text="Die PDF wird analysiert",
            next_callback=self.crop_pdf,
            previous_text="Überspringen",
            previous_callback=self.open_ocr_editor_after_crop_skip,
        )

        self.open_ocr_editor_skip_crop = OpenOcrEditorStep()
        self.open_ocr_editor_skip_crop.finished_signal.connect(
            self.open_ocr_editor_after_crop_skip_done
        )

        self.crop_running_step = CropRunningStep(text="Die PDF wird zugeschnitten")
        self.crop_running_step.finished.connect(self.crop_finished)

        self.crop_redo_step = RedoCropOptionStep(
            next_callback=self.open_cropped_pdf, previous_callback=self.crop_redo
        )

        self.open_cropped_pdf_step = OpenOcrEditorStep()

        self.procedures_after_crop = ProcedureSelectionStep(
            text="Welche Optimierungen sollen durchgeführt werden?",
            previous_text="Überspringen",
            previous_callback=self.open_ocr_clean_up_step,
            next_callback=self.start_procedures_after_crop,
        )

        self.open_cropped_pdf_step.finished_signal.connect(
            self.open_cropped_pdf_finished
        )

        self.procedures_after_crop.finished.connect(self.open_ocr_clean_up_step)

        self.ocr_clean_up_step = OcrCleanUpStep(
            text="Entferne Artefakte von den Seiten, um das OCR Ergebnis zu verbessern",
            next_callback=lambda: self.open_ocr_language_selection_step(True),
        )

        self.ocr_language_selection_step = OcrLanguageSelectionStep(
            text="Wähle die OCR-Sprachen für die PDF", next_callback=self.do_ocr
        )

        self.ocr_running_step = OcrRunningStep(
            text="OCR läuft",
            next_text="OCR ist bereits abgeschlossen",
            next_callback=self.ocr_skip_still_running,
        )

        self.ocr_running_step.finished.connect(self.ocr_running_finished)

        self.ocr_from_file_running_step = OcrFromFileRunningStep(
            text="OCR läuft",
            next_text="OCR ist bereits abgeschlossen",
            next_callback=self.ocr_from_file_skip_still_running,
        )
        self.ocr_from_file_running_step.finished.connect(self.ocr_running_finished)

        self.ocr_default_error_replacement_finished_step = Step(
            text="Korrektur der Standardfehler abgeschlossen. Händische Nachkorrektur und dann weiter",
            next_callback=self.open_save_location_step,
            previous_text="OCR wiederholen",
            previous_callback=lambda: self.open_step(self.ocr_language_selection_step),
        )

        self.ocr_finished_step = Step(
            text="OCR abgeschlossen. Sollen die OCR Standardfehler ersetzt werden?",
            previous_text="Nein",
            previous_callback=lambda: self.open_step(
                self.ocr_default_error_replacement_finished_step
            ),
            next_text="Ja",
            next_callback=self.open_ocr_default_error_replacement,
        )

        self.ocr_default_error_replacement_step = OcrDefaultErrorReplacementStep(
            text="Wähle welche Standardfehlerlisten verwendet werden sollen",
            next_callback=self.start_ocr_default_error_replacement,
            previous_callback=self.open_save_location_step,
            previous_text="Überspringen",
        )

        self.ocr_default_error_replacement_running_step = (
            OcrDefaultErrorReplacementRunningStep(
                text="OCR Standardfehler werden korrigiert",
                next_text="Überspringen",
                next_callback=self.skip_ocr_standard_replacement_running,
            )
        )

        self.ocr_default_error_replacement_running_step.finished.connect(
            lambda: self.open_step(self.ocr_default_error_replacement_finished_step)
        )

        self.choose_save_location_step = FileNameSelectionStep(
            text="Wähle Speicherort und Name der PDF",
            previous_text="Ohne Precise Scan speichern",
            previous_callback=None,
            next_callback=self.open_set_metadata,
        )

        self.set_metadata_step = SetMetadataStep(
            text="Setze die Metadaten",
            previous_text="Ohne Precise Scan speichern",
            previous_callback=lambda: self.save_pdf_callback(enable_precise_scan=False),
            next_text="Mit Precise Scan speichern",
            next_callback=lambda: self.save_pdf_callback(enable_precise_scan=True),
        )
        self.set_metadata_step_for_metadata = SetMetadataStep(
            text="Setze die Metadaten",
            next_text="Speichern",
            next_callback=lambda: self.save_pdf_callback(save_without_abby=True),
        )
        self.choose_save_location_for_metadata_step = FileNameSelectionStep(
            text="Wähle Speicherort und Name der PDF",
            next_text="Weiter",
            next_callback=self.open_set_metadata_for_metadata,
        )

        self.save_running_step = SavePDFRunningStep(text="PDF wird gespeichert")
        self.save_running_step.finished.connect(self.open_redo_pdf_save_step)

        self.redo_save_pdf_step = RedoSavePdfStep(
            previous_callback=self.go_back_to_save_pdf_step,
            next_callback=self.clean_up,
        )

        self.redo_save_pdf_for_metadata_step = RedoSavePdfStep(
            previous_callback=self.go_back_to_save_pdf_for_export_step,
            next_callback=self.save_pdf_only_metadata_finished,
        )

        self.clean_up_running_step = CleanUpRunningStep(text="Es wird augeräumt")
        self.clean_up_running_step.finished.connect(self.clean_up_finished)

        self.finished_step = Step(
            text="Fertig!",
            next_callback=lambda: exit(0),
            next_text="Schließen",
            previous_callback=self.reset,
            previous_text="Neue PDF verarbeiten",
        )

        self.settings_controller = SettingsController(
            previous_callback=lambda: self.open_step(self.file_selection_step),
            next_callback=lambda: self.open_step(self.file_selection_step),
        )

        self.steps = [
            self.file_selection_step,
            self.open_ocr_editor_step,
            self.select_procedures_step,
            self.crop_pdf_question_step,
            self.save_temp_pdf_after_procedures,
            self.check_pdf_orientation_running_step,
            self.check_pdf_orientation_step,
            self.ocr_clean_up_step_before_crop,
            self.save_temp_pdf_running_step,
            self.crop_amount_step,
            self.crop_running_step,
            self.crop_redo_step,
            self.open_cropped_pdf_step,
            self.procedures_after_crop,
            self.ocr_clean_up_step,
            self.ocr_language_selection_step,
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

    def open_step(self, step: Step):
        index = self.steps.index(step)
        self.current_index = index
        self.layout.setCurrentIndex(self.current_index)

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
            self.open_crop_step(Store.FILE_PATH_AFTER_PROCEDURES)
        else:
            self.open_next_step()
            self.activateWindow()

    def save_pdf_after_orientation_fix(self):
        self.open_next_step()
        self.save_temp_pdf_running_step.start()

    def open_crop_step(self, path: str):
        self.open_next_step()
        self.window().activateWindow()
        self.crop_amount_step.open_pdf_pages(path)

    def crop_pdf(self):
        self.crop_running_step.start(
            self.crop_amount_step.path_to_pdf,
            self.crop_amount_step.crop_amount_selection_controller.get_max_crop_box_pixel(),
            self.crop_amount_step.crop_amount_selection_controller.get_transformed_crop_boxes_pixel(),
            self.crop_amount_step.crop_amount_selection_controller.analysis_result.images,
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
            self.crop_ocr_pdf_amount_step.open_pdf_pages(Store.SELECTED_FILE_PATH)

    def crop_ocr_pdf(self):
        self.crop_ocr_pdf_running_step.start(
            self.crop_ocr_pdf_amount_step.path_to_pdf,
            self.crop_ocr_pdf_amount_step.crop_amount_selection_controller.get_max_crop_box_pixel(),
            self.crop_ocr_pdf_amount_step.crop_amount_selection_controller.get_transformed_crop_boxes_pixel(),
            self.crop_ocr_pdf_amount_step.crop_amount_selection_controller.analysis_result.images,
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

    def do_ocr(self):
        self.open_next_step()
        languages = self.ocr_language_selection_step.get_selected_language()
        console.log("OCR wird mit folgende Sprachen durchgeführt: ", languages)
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
        self.set_metadata_step.set_title(
            self.choose_save_location_step.file_name_field.text()
        )
        self.open_step(self.set_metadata_step)

    def open_set_metadata_for_metadata(self):
        self.set_metadata_step_for_metadata.set_title(
            self.choose_save_location_for_metadata_step.file_name_field.text()
        )
        self.open_step(self.set_metadata_step_for_metadata)

    def save_pdf_callback(self, enable_precise_scan=False, save_without_abby=False):
        if self.choose_save_location_step.folder_selection.selected_folder != "":
            if save_without_abby:
                folder = (
                    self.choose_save_location_for_metadata_step.folder_selection.selected_folder
                )
                file_name = (
                    self.choose_save_location_for_metadata_step.file_name_field.text()
                )
            else:
                folder = self.choose_save_location_step.folder_selection.selected_folder
                file_name = self.choose_save_location_step.file_name_field.text()
            suffix = "" if ".pdf" in file_name else ".pdf"
            path = os.path.abspath(folder + "\\" + file_name + suffix)
            Store.SAVE_FILE_PATH = path
            if Store.SELECTED_FILE_PATH == Store.SAVE_FILE_PATH:
                dialog = create_dialog(
                    window_title="Achtung",
                    text="Die Originaldatei würde überschrieben werden",
                    buttons=QMessageBox.StandardButton.Abort
                    | QMessageBox.StandardButton.Ok,
                    icon=QMessageBox.Icon.Warning,
                    parent=self,
                )
                button = dialog.exec()
                if button == QMessageBox.StandardButton.Ok:
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
                if button == QMessageBox.StandardButton.Abort:
                    dialog.close()
            elif os.path.exists(Store.SAVE_FILE_PATH):
                dialog = create_dialog(
                    window_title="Achtung",
                    text="Es existiert bereits eine Datei mit diesem Namen",
                    buttons=QMessageBox.StandardButton.Abort
                    | QMessageBox.StandardButton.Ok,
                    icon=QMessageBox.Icon.Warning,
                    parent=self,
                )
                button = dialog.exec()
                if button == QMessageBox.StandardButton.Ok:
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
                if button == QMessageBox.StandardButton.Abort:
                    dialog.close()
            else:
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
