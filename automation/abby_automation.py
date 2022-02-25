import os
import shutil
import time
from typing import Callable, List
from uuid import UUID

import pyautogui

from automation.procedures.general_procedures import GeneralProcedures
from automation.procedures.ocr_procedures import OcrProcedures
from automation.procedures.waiting_procedures import WaitingProcedures
from config import ABBY_LNK_PATH, ABBY_WORKING_DIR
from utils.keyboard_util import press_key, write
from utils.rectangle import Rectangle
from utils.screen import Screen


class AbbyAutomation:

    @staticmethod
    def open_pdf_in_abby_ocr_editor(*, path_to_pdf: str):
        """
        Opens the given PDF in Abby OCR editor

        :param path_to_pdf: Path leading to the PDF
        """
        os.startfile(os.path.abspath(ABBY_LNK_PATH))
        WaitingProcedures.wait_until_open_pdf_is_visible()
        x, y = Screen.locate_center_on_screen('open_ocr_editor.png')
        pyautogui.click(x, y)
        time.sleep(0.5)
        write(os.path.abspath(path_to_pdf))
        press_key(key_combination='enter')
        WaitingProcedures.wait_until_close_button_visible()
        press_key(key_combination='alt+shift+s')

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
        GeneralProcedures.click_ocr_file_icon()
        AbbyAutomation.close_image_improvement_tools()
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
        AbbyAutomation.open_image_improvement_tools()
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
        time.sleep(0.5)
        path, file_name = GeneralProcedures.save_temp_pdf()
        progress_callback(100)
        return path, file_name

    @staticmethod
    def save_pdf(path: str):
        GeneralProcedures.open_save_pdf_dialog()
        write(path)
        press_key(key_combination="enter")
        WaitingProcedures.wait_until_saving_pdf_is_finished(path)

    @staticmethod
    def crop_pdf(path_to_pdf: str, crop_rectangle: Rectangle):
        AbbyAutomation.open_pdf_in_abby_ocr_editor(path_to_pdf=path_to_pdf)
        AbbyAutomation.open_image_improvement_tools(should_tab_in=False)
        time.sleep(0.5)
        GeneralProcedures.click_light_bulb()
        GeneralProcedures.click_light_bulb()
        OcrProcedures.do_crop_pdf(crop_rectangle.x, crop_rectangle.y, crop_rectangle.width, crop_rectangle.height,
                                  should_tab_in=False)

    @staticmethod
    def clean_up():
        os.system("taskkill /f /im FineReader.exe")
        os.system("taskkill /f /im FineReaderOCR.exe")
        time.sleep(2)
        folder = ABBY_WORKING_DIR
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    # @staticmethod
    # def open_abby_and_ocr_editor(*, path_to_pdf: str, abby_exe_path: str = ABBY_EXE_PATH) -> None:
    #     """
    #     Opens abby and the ocr editor. Waits until both finished opening
    #
    #     :param path_to_pdf: Path leading to the PDF
    #     :param abby_exe_path: Path to the Abby executable file
    #     """
    #     # AbbyAutomation.open_pdf_in_abby(path_to_pdf=path_to_pdf, abby_exe_path=abby_exe_path)
    #     # WaitingProcedures.wait_until_abby_reader_is_opened()
    #     # AbbyAutomation.open_ocr_editor()
    #     AbbyAutomation.open_pdf_in_abby_ocr_editor(path_to_pdf=path_to_pdf)
    #
    # @staticmethod
    # def open_pdf_in_abby(*, path_to_pdf: str, abby_exe_path: str = ABBY_EXE_PATH) -> None:
    #     """
    #     Opens the given PDF in Abby
    #
    #     :param path_to_pdf: Path leading to the PDF
    #     :param abby_exe_path: Path to the abby exe
    #     """
    #
    #     # p_open = subprocess.Popen([abby_exe_path, path_to_pdf])
    #     # AbbyAutomation.OPEN_INSTANCES.append(p_open)
    #     # AbbyAutomation.CURR_INSTANCE = p_open
    #
    #     os.startfile(os.path.abspath(ABBY_LNK_PATH))
    #     WaitingProcedures.wait_until_open_pdf_is_visible()
    #     x, y = Screen.locate_center_on_screen('open_pdf.png')
    #     pyautogui.click(x, y)
    #     time.sleep(0.5)
    #     write(os.path.abspath(path_to_pdf))
    #     press_key(key_combination='enter')

    # @staticmethod
    # def open_ocr_editor() -> None:
    #     """
    #     Opens the Abby OCR-Editor
    #     """
    #     press_key(key_combination='shift+alt+1', repetitions=2)
    #     press_key(key_combination='alt+e+a')
    #     press_key(key_combination='shift+f10')
    #     press_key(key_combination='tab')
    #     press_key(key_combination='down', repetitions=5)
    #     press_key(key_combination='enter')
    #     WaitingProcedures.wait_until_close_button_visible()
    #     press_key(key_combination='alt+shift+s')
