import os
import shutil
import time
from typing import Callable, List
from uuid import UUID

from automation.procedures.general_procedures import GeneralProcedures
from automation.procedures.ocr_procedures import OcrProcedures
from automation.procedures.waiting_procedures import WaitingProcedures
from config import OCR_WORKING_DIR, OCR_EDITOR_LNK_PATH
from utils.console import console
from utils.keyboard_util import press_key, write
from utils.rectangle import Rectangle


class OcrAutomation:

    @staticmethod
    def open_pdf_in_ocr_editor(path_to_pdf: str):
        os.startfile(OCR_EDITOR_LNK_PATH)
        WaitingProcedures.wait_util_ocr_open_pdf_is_visible()
        time.sleep(1)
        press_key(key_combination='alt+n')
        time.sleep(1)
        OcrAutomation.disable_initial_ocr()
        GeneralProcedures.click_ocr_open_pdf_icon()
        time.sleep(0.5)
        write(path_to_pdf)
        press_key(key_combination='enter', delay_in_seconds=0.3)
        WaitingProcedures.wait_until_ocr_page_recognition_icon_is_visible()

    @staticmethod
    def open_image_improvement_tools(should_tab_in: bool = True) -> None:
        """
        Opens the OCR improvement tools
        """
        if should_tab_in:
            press_key(key_combination='alt+tab', delay_in_seconds=1)
        GeneralProcedures.click_ocr_pages_header()
        press_key(key_combination='ctrl+a')
        press_key(key_combination='ctrl+i')

    @staticmethod
    def close_image_improvement_tools() -> None:
        """
        Closes the OCR improvement tools
        """
        press_key(key_combination='ctrl+i')

    @staticmethod
    def run_ocr(languages: str) -> None:
        """
        Runs ocr detection

        :param languages: Languages which should be used for ocr
        """
        GeneralProcedures.click_ocr_file_icon()
        OcrAutomation.close_image_improvement_tools()
        time.sleep(0.5)
        press_key(key_combination='alt+k')
        press_key(key_combination='i')
        time.sleep(0.5)
        GeneralProcedures.click_ocr_language_selection()
        press_key(key_combination='alt+s', delay_in_seconds=0.3)
        press_key(key_combination='shift+tab', delay_in_seconds=0.3)
        write(text=languages)
        press_key(key_combination='enter', repetitions=2, delay_in_seconds=0.3)
        press_key(key_combination='tab', repetitions=7, delay_in_seconds=0.1)
        press_key(key_combination='enter')
        GeneralProcedures.click_ocr_pages_header()
        press_key(key_combination='ctrl+a')
        GeneralProcedures.click_ocr_page_recognition_icon()
        WaitingProcedures.wait_until_ocr_is_finished()
        press_key(key_combination='alt+shift+s', delay_in_seconds=0.3)

    @staticmethod
    def do_optimization(procedures: List[Callable], iterations: int, progress_callback: Callable[[int], None]) \
            -> [str, UUID]:
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
            press_key(key_combination='alt+shift+s')
        time.sleep(0.3)
        path, file_name = GeneralProcedures.save_temp_pdf()
        OcrAutomation.close_ocr_project()
        progress_callback(100)
        return path, file_name

    @staticmethod
    def save_pdf(path: str) -> None:
        """
        Saves the pdf in the given folder

        :param path: Path where the PDF should be saved
        """
        GeneralProcedures.open_save_pdf_dialog()
        write(path)
        press_key(key_combination="enter")
        WaitingProcedures.wait_until_saving_pdf_is_finished(path)

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
        OcrProcedures.do_crop_pdf(crop_rectangle.x, crop_rectangle.y, crop_rectangle.width, crop_rectangle.height,
                                  should_tab_in=False)

    @staticmethod
    def disable_initial_ocr() -> None:
        console.log("Disabling initial ocr...")
        press_key(key_combination='alt+k', delay_in_seconds=0.2)
        press_key(key_combination='i', delay_in_seconds=0.3)
        GeneralProcedures.click_ocr_image_processing_icon()
        press_key(key_combination='tab', repetitions=3, delay_in_seconds=0.1)
        press_key(key_combination='-', delay_in_seconds=0.3)
        press_key(key_combination='tab', repetitions=5, delay_in_seconds=0.1)
        press_key(key_combination='enter', delay_in_seconds=0.3)

    @staticmethod
    def close_ocr_project():
        GeneralProcedures.click_ocr_pages_header()
        press_key(key_combination='alt+f4', delay_in_seconds=0.3)
        press_key(key_combination='alt+n')

    @staticmethod
    def clean_up() -> None:
        """
        Clean up all temporary files and instances
        """
        OcrAutomation.close_ocr_project()
        time.sleep(2)
        folder = OCR_WORKING_DIR
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
