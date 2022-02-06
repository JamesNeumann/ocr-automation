import os
import subprocess
import time
from typing import Callable, List

import pyautogui

from automation.procedures.general_procedures import GeneralProcedures
from automation.procedures.ocr_procedures import OcrProcedures
from automation.procedures.waiting_procedures import WaitingProcedures
from utils.analyze_pdf import get_crop_box
from utils.console import console
from utils.keyboard_util import press_key


class AbbyAutomation:
    ABBY_EXE_PATH = 'D:\\Software\\Abby Finereader 15\\ABBYY FineReader 15\\FineReader.exe'

    @staticmethod
    def open_abby_and_ocr_editor(*, path_to_pdf: str, abby_exe_path: str = ABBY_EXE_PATH) -> None:
        """
        Opens abby and the ocr editor. Waits until both finished opening

        :param path_to_pdf: Path leading to the PDF
        :param abby_exe_path: Path to the Abby executable file
        """
        AbbyAutomation.open_pdf_in_abby(path_to_pdf=path_to_pdf, abby_exe_path=abby_exe_path)
        WaitingProcedures.wait_until_abby_reader_is_opened()
        AbbyAutomation.open_ocr_editor()

    @staticmethod
    def open_pdf_in_abby(*, path_to_pdf: str, abby_exe_path: str = ABBY_EXE_PATH) -> None:
        """
        Opens the given PDF in Abby

        :param path_to_pdf: Path leading to the PDF
        :param abby_exe_path: Path to the abby exe
        """

        subprocess.Popen([abby_exe_path, path_to_pdf])

    @staticmethod
    def open_ocr_editor() -> None:
        """
        Opens the Abby OCR-Editor
        """
        press_key(key_combination='shift+alt+1', repetitions=2)
        press_key(key_combination='alt+e+a')
        press_key(key_combination='shift+f10')
        press_key(key_combination='tab')
        press_key(key_combination='down', repetitions=5)
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
        AbbyAutomation.click_ocr_file_icon()
        press_key(key_combination='alt+e+s')
        press_key(key_combination='ctrl+i')

    @staticmethod
    def click_ocr_file_icon() -> None:
        """
        Clicks the OCR file icon
        """
        x, y = pyautogui.locateCenterOnScreen("ocr_file_icon.png")
        if x is not None and y is not None:
            pyautogui.click(x, y)

    @staticmethod
    def do_optimization(procedures: List[Callable], iterations: int) -> None:
        """
        Executes all the given procedures and crops the pdf afterwards.

        :param procedures: Contains all procedures that should be executed
        :param iterations: How often all procedures should be executed
        """
        AbbyAutomation.open_image_improvement_tools()
        for i in range(iterations):
            for operation in procedures:
                GeneralProcedures.click_light_bulb()
                operation()
        time.sleep(1)
        if WaitingProcedures.is_close_button_visible():
            press_key(key_combination='alt+shift+s')
        time.sleep(1)
        path, file_name = GeneralProcedures.save_temp_pdf()
        press_key(key_combination="alt+tab")
        AbbyAutomation.crop_pdf(path, file_name)

    @staticmethod
    def crop_pdf(path: str, file_name: str) -> None:
        """
        Crops the given PDF file.
        Therefore, analyses the PDF and finds the most suitable crop box.

        :param path: Path to the PDF
        :param file_name: Name of the PDF file
        """

        sanitized_path = os.environ['USERPROFILE'] + "\\AppData\\Local\\Temp"
        rectangle = get_crop_box(path_to_pdf=f"{sanitized_path}\\{file_name}.pdf", offset=0)
        console.log("Crop box: ", rectangle)
        AbbyAutomation.open_abby_and_ocr_editor(path_to_pdf=f"{path}\\{file_name}.pdf")
        AbbyAutomation.open_image_improvement_tools(should_tab_in=False)
        time.sleep(0.5)
        GeneralProcedures.click_light_bulb()
        GeneralProcedures.click_light_bulb()
        OcrProcedures.do_crop_pdf(rectangle.x, rectangle.y, rectangle.width, rectangle.height, should_tab_in=False)
        os.remove(f"{path}\\{file_name}.pdf")
