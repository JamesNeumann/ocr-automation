import os
import shutil
import subprocess
import time
from typing import Callable, List, Dict
from uuid import UUID

import psutil
import pyautogui
from psutil import NoSuchProcess

from automation.procedures.general_procedures import GeneralProcedures
from automation.procedures.ocr_procedures import OcrProcedures
from automation.procedures.waiting_procedures import WaitingProcedures
from automation.store import Store
from config import Config
from utils.console import console
from utils.keyboard_util import press_key, write
from utils.rectangle import Rectangle


class OcrAutomation:
    @staticmethod
    def open_pdf_in_ocr_editor(
        path_to_pdf: str, disble_image_editing_settings=False
    ) -> None:
        """
        Opens the given PDF in the OCR editor

        :param disble_image_editing_settings: If the image editing settings should be disabled
        :param path_to_pdf: path to the PDF that should be opened
        """
        os.startfile(Config.OCR_EDITOR_LNK_PATH)
        WaitingProcedures.wait_util_ocr_open_pdf_is_visible()
        time.sleep(1)
        press_key(key_combination="alt+n")
        time.sleep(1)
        # OcrAutomation.disable_initial_ocr()
        if disble_image_editing_settings:
            OcrAutomation.disable_image_editing_settings()
        else:
            OcrAutomation.enable_image_editing_settings()
        GeneralProcedures.click_ocr_open_pdf_icon()
        time.sleep(0.5)
        write(path_to_pdf)
        press_key(key_combination="enter", delay_in_seconds=0.3)
        WaitingProcedures.wait_until_ocr_page_recognition_icon_is_visible()

    @staticmethod
    def open_eraser():
        if not Store.IMAGE_EDIT_TOOL_OPEN:
            OcrAutomation.open_image_improvement_tools(should_tab_in=True)
        GeneralProcedures.click_light_bulb()
        OcrProcedures.do_eraser()
        OcrAutomation.adjust_pdf_pages_to_width()
        OcrAutomation.select_first_page()

    @staticmethod
    def adjust_pdf_pages_to_width():
        width, height = pyautogui.size()
        pyautogui.click(width / 2, height / 2)
        press_key(key_combination="alt+a+r", delay_in_seconds=0.5)

    @staticmethod
    def replace_default_ocr_errors(selected_replacement_maps: List[Dict]):
        OcrAutomation.open_replace_dialog()
        press_key(key_combination="tab", repetitions=5, delay_in_seconds=0.1)
        press_key(key_combination="+")
        OcrAutomation.close_replace_dialog()
        for replacement_map in selected_replacement_maps:
            for replacement in replacement_map["map"]:
                OcrAutomation.open_replace_dialog()
                press_key(key_combination="ctrl+a")
                write(replacement[0])
                press_key(key_combination="tab", repetitions=2, delay_in_seconds=0.1)
                press_key(key_combination="ctrl+a")
                write(replacement[1])
                press_key(key_combination="alt+t", delay_in_seconds=0.1)
                WaitingProcedures.wait_until_warning_symbol_is_visible(-1)
                press_key(key_combination="enter", delay_in_seconds=0.1)
                OcrAutomation.close_replace_dialog()
                OcrAutomation.select_first_page()

    @staticmethod
    def open_replace_dialog():
        GeneralProcedures.click_ocr_pages_header()
        press_key(key_combination="ctrl+h", delay_in_seconds=0.5)

    @staticmethod
    def close_replace_dialog():
        press_key(key_combination="esc", delay_in_seconds=0.5)

    @staticmethod
    def select_first_page():
        press_key(key_combination="ctrl+pos1", delay_in_seconds=1)

    @staticmethod
    def open_image_improvement_tools(should_tab_in: bool = True) -> None:
        """
        Opens the OCR improvement tools
        """
        if should_tab_in:
            press_key(key_combination="alt+tab", delay_in_seconds=1)
        GeneralProcedures.click_ocr_pages_header()
        press_key(key_combination="ctrl+a")
        press_key(key_combination="ctrl+i")
        Store.IMAGE_EDIT_TOOL_OPEN = True

    @staticmethod
    def close_image_improvement_tools() -> None:
        """
        Closes the OCR improvement tools
        """
        if Store.IMAGE_EDIT_TOOL_OPEN:
            press_key(key_combination="ctrl+i")
            Store.IMAGE_EDIT_TOOL_OPEN = False

    @staticmethod
    def run_ocr(languages: str) -> None:
        """
        Runs ocr detection
        :param languages: Languages which should be used for ocr
        """
        OcrAutomation.open_ocr_editor_options()
        OcrAutomation.set_ocr_mode()
        OcrAutomation.set_ocr_languages(languages)
        OcrAutomation.start_ocr()

    @staticmethod
    def start_ocr():
        GeneralProcedures.click_ocr_pages_header()
        press_key(key_combination="ctrl+a")
        GeneralProcedures.click_ocr_page_recognition_icon()
        WaitingProcedures.wait_until_ocr_is_finished()
        press_key(key_combination="alt+shift+s", delay_in_seconds=0.3)

    @staticmethod
    def run_ocr_with_ocr_from_text():
        """
        Runs OCR detection by only using the text provided in the OCR of the file
        """
        OcrAutomation.open_ocr_editor_options()
        OcrAutomation.set_ocr_mode(ocr_from_text=True, close=True)
        OcrAutomation.start_ocr()

    @staticmethod
    def open_ocr_editor_options():
        """
        Opens the OCR editor options
        """
        GeneralProcedures.click_ocr_file_icon()
        time.sleep(0.5)
        press_key(key_combination="alt+k")
        press_key(key_combination="i")
        time.sleep(0.5)

    @staticmethod
    def set_ocr_mode(ocr_from_text=False, close=False):
        """
        Sets the OCR mode
        :param ocr_from_text: If the OCR should be selected from the file
        :param close: If the OCR should be closed afterwards
        """
        GeneralProcedures.click_ocr_option_icon()
        press_key(key_combination="tab")
        press_key(key_combination="up", repetitions=2)
        if ocr_from_text:
            press_key(key_combination="down", repetitions=2)
        else:
            press_key(key_combination="down", repetitions=1)

        if close:
            press_key(key_combination="tab", repetitions=15)
            press_key(key_combination="enter", delay_in_seconds=0.3)

    @staticmethod
    def set_ocr_languages(languages: str):
        """
        Sets the languages to be used for OCR
        :param languages: String of combined OCR languages
        """
        GeneralProcedures.click_ocr_language_selection()
        press_key(key_combination="alt+s", delay_in_seconds=0.3)
        press_key(key_combination="shift+tab", delay_in_seconds=0.3)
        write(text=languages)
        press_key(key_combination="enter", repetitions=2, delay_in_seconds=0.3)
        press_key(key_combination="tab", repetitions=7, delay_in_seconds=0.1)
        press_key(key_combination="enter")

    @staticmethod
    def do_optimization(
        procedures: List[Callable],
        iterations: int,
        progress_callback: Callable[[int], None],
    ) -> [str, UUID]:
        """
        Executes all the given procedures and crops the pdf afterwards.

        :param progress_callback: Callback function for progress
        :param procedures: Contains all procedures that should be executed
        :param iterations: How often all procedures should be executed
        """
        OcrAutomation.open_image_improvement_tools()
        progress_step = 100 / (iterations * len(procedures) + 1)
        curr_step = 0
        for i in range(iterations):
            for index, operation in enumerate(procedures):
                GeneralProcedures.click_light_bulb()
                operation()
                curr_step += progress_step
                progress_callback(curr_step)
        time.sleep(1)
        if WaitingProcedures.is_close_button_visible():
            press_key(key_combination="alt+shift+s")
        time.sleep(0.3)
        # path, file_name = GeneralProcedures.save_temp_pdf()
        # OcrAutomation.close_ocr_project()
        progress_callback(100)
        # return path, file_name

    @staticmethod
    def save_pdf(path: str, enable_precise_scan: bool) -> None:
        """
        Saves the pdf in the given folder

        :param path: Path where the PDF should be saved
        :param enable_precise_scan: If Abby Precise Scan should be enabled

        """
        GeneralProcedures.click_ocr_pages_header()
        if enable_precise_scan:
            OcrAutomation.enable_abby_precise_scan()
        else:
            OcrAutomation.disable_abby_precise_scan()
        GeneralProcedures.open_save_pdf_dialog()
        write(path)
        press_key(key_combination="enter")
        WaitingProcedures.wait_until_saving_pdf_is_finished(path)

    @staticmethod
    def open_pdf_in_default_program(path: str):
        Store.PDF_APPLICATION_PROCESS = subprocess.Popen(
            [path], shell=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )

    @staticmethod
    def close_pdf_in_default_program():
        if Store.PDF_APPLICATION_PROCESS is not None:
            try:
                pobj = psutil.Process(Store.PDF_APPLICATION_PROCESS.pid)
                for c in pobj.children(recursive=True):
                    c.kill()
                pobj.kill()
            except NoSuchProcess:
                pass

    @staticmethod
    def crop_pdf(path_to_pdf: str, crop_rectangle: Rectangle) -> None:
        """
        Crops the given pdf

        :param path_to_pdf: Path to the pdf that should be cropped
        :param crop_rectangle: The crop rectangle
        """
        OcrAutomation.open_pdf_in_ocr_editor(path_to_pdf)
        OcrAutomation.open_image_improvement_tools(should_tab_in=False)
        time.sleep(0.5)
        GeneralProcedures.click_light_bulb()
        GeneralProcedures.click_light_bulb()
        OcrProcedures.do_crop_pdf(
            crop_rectangle.x,
            crop_rectangle.y,
            crop_rectangle.width,
            crop_rectangle.height,
            should_tab_in=False,
        )

    @staticmethod
    def crop_pdf_single_pages(path_to_pdf: str, crop_rectangles: List[Rectangle]):
        OcrAutomation.open_pdf_in_ocr_editor(path_to_pdf)
        OcrAutomation.open_image_improvement_tools(should_tab_in=False)
        time.sleep(0.5)
        GeneralProcedures.click_light_bulb()
        press_key(key_combination="ä")
        press_key(key_combination="+")
        for rectangle in crop_rectangles:
            OcrProcedures.do_crop_pdf_single_page(
                rectangle.x,
                rectangle.y,
                rectangle.width,
                rectangle.height,
                should_tab_in=False,
            )

    @staticmethod
    def disable_initial_ocr() -> None:
        """
        Disables the initial OCR when opening a PDF
        """
        console.log("Initiale OCR Überprüfung wird deaktiviert...")
        GeneralProcedures.open_options()
        GeneralProcedures.click_ocr_image_processing_icon()
        press_key(key_combination="tab", repetitions=3, delay_in_seconds=0.1)
        press_key(key_combination="-", delay_in_seconds=0.3)
        press_key(key_combination="tab", repetitions=5, delay_in_seconds=0.1)
        press_key(key_combination="enter", delay_in_seconds=0.3)

    @staticmethod
    def enable_abby_precise_scan():
        GeneralProcedures.open_options()
        GeneralProcedures.click_format_settings_icon()
        press_key(key_combination="tab", repetitions=8, delay_in_seconds=0.3)
        press_key(key_combination="+", delay_in_seconds=0.3)
        press_key(key_combination="tab", delay_in_seconds=0.3)
        press_key(key_combination="+", delay_in_seconds=0.3)
        press_key(key_combination="tab", repetitions=5, delay_in_seconds=0.3)
        press_key(key_combination="-", delay_in_seconds=0.3)
        press_key(key_combination="tab")
        press_key(key_combination="enter", delay_in_seconds=0.3)

    @staticmethod
    def disable_image_editing_settings():
        GeneralProcedures.open_options()
        GeneralProcedures.click_ocr_image_processing_icon()
        press_key(key_combination="tab", delay_in_seconds=0.1)
        press_key(key_combination="-", delay_in_seconds=0.3)
        press_key(key_combination="tab", repetitions=2, delay_in_seconds=0.1)
        press_key(key_combination="-", delay_in_seconds=0.3)
        press_key(key_combination="tab", delay_in_seconds=0.1)
        press_key(key_combination="-", delay_in_seconds=0.3)
        press_key(key_combination="tab", delay_in_seconds=0.1)
        press_key(key_combination="-", delay_in_seconds=0.3)
        press_key(key_combination="tab", delay_in_seconds=0.1)
        press_key(key_combination="enter", delay_in_seconds=0.3)
        press_key(key_combination="tab", repetitions=2, delay_in_seconds=0.1)
        press_key(key_combination="enter", delay_in_seconds=0.3)

    @staticmethod
    def enable_image_editing_settings():
        GeneralProcedures.open_options()
        GeneralProcedures.click_ocr_image_processing_icon()
        press_key(key_combination="tab", delay_in_seconds=0.1)
        press_key(key_combination="+", delay_in_seconds=0.3)
        press_key(key_combination="tab", repetitions=3, delay_in_seconds=0.1)
        press_key(key_combination="+", delay_in_seconds=0.3)
        press_key(key_combination="tab", delay_in_seconds=0.1)
        press_key(key_combination="+", delay_in_seconds=0.3)
        press_key(key_combination="tab", repetitions=2, delay_in_seconds=0.1)
        press_key(key_combination="enter", delay_in_seconds=0.3)
        press_key(key_combination="shift+tab", repetitions=4, delay_in_seconds=0.1)
        press_key(key_combination="+", delay_in_seconds=0.3)
        press_key(key_combination="shift+tab", delay_in_seconds=0.1)
        press_key(key_combination="+", delay_in_seconds=0.3)
        press_key(key_combination="shift+tab", delay_in_seconds=0.1)
        press_key(key_combination="+", delay_in_seconds=0.3)
        press_key(key_combination="shift+tab", repetitions=3, delay_in_seconds=0.1)
        press_key(key_combination="+", delay_in_seconds=0.3)
        press_key(key_combination="shift+tab", repetitions=2, delay_in_seconds=0.1)
        press_key(key_combination="+", delay_in_seconds=0.3)
        press_key(key_combination="shift+tab", delay_in_seconds=0.1)
        press_key(key_combination="+", delay_in_seconds=0.3)
        press_key(key_combination="shift+tab", delay_in_seconds=0.1)
        press_key(key_combination="+", delay_in_seconds=0.3)
        press_key(key_combination="tab", repetitions=13, delay_in_seconds=0.1)
        press_key(key_combination="enter", delay_in_seconds=0.3)
        press_key(key_combination="tab", delay_in_seconds=0.1)
        press_key(key_combination="enter", delay_in_seconds=0.3)

    @staticmethod
    def disable_abby_precise_scan():
        GeneralProcedures.open_options()
        GeneralProcedures.click_format_settings_icon()
        press_key(key_combination="tab", repetitions=8, delay_in_seconds=0.3)
        press_key(key_combination="-", delay_in_seconds=0.3)
        press_key(key_combination="tab", delay_in_seconds=0.3)
        press_key(key_combination="-", delay_in_seconds=0.3)
        press_key(key_combination="tab", repetitions=5, delay_in_seconds=0.3)
        press_key(key_combination="-", delay_in_seconds=0.3)
        press_key(key_combination="tab")
        press_key(key_combination="enter", delay_in_seconds=0.3)

    @staticmethod
    def close_ocr_project() -> None:
        """
        Closes the OCR instance
        """
        GeneralProcedures.click_ocr_pages_header()
        Store.IMAGE_EDIT_TOOL_OPEN = False
        press_key(key_combination="alt+f4", delay_in_seconds=0.3)
        press_key(key_combination="alt+n")

    @staticmethod
    def clean_up() -> None:
        """
        Clean up all temporary files and instances
        """
        console.log("Es wird aufgeräumt")
        OcrAutomation.close_pdf_in_default_program()
        OcrAutomation.close_ocr_project()
        time.sleep(2)
        folder = Config.OCR_WORKING_DIR
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print("Failed to delete %s. Reason: %s" % (file_path, e))
