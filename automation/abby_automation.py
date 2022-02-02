import math
import subprocess
import time
import uuid

import pyautogui
from rich.panel import Panel

from automation.procedures import Procedures
from utils.console import console
from utils.keyboard_util import press_key, write


class AbbyAutomation:
    ABBY_EXE_PATH = 'D:\\Software\\Abby Finereader 15\\ABBYY FineReader 15\\FineReader.exe'

    @staticmethod
    def open_abby_and_ocr_editor(*, path_to_pdf: str, abby_exe_path: str = ABBY_EXE_PATH) -> None:
        AbbyAutomation.open_pdf_in_abby(path_to_pdf=path_to_pdf, abby_exe_path=abby_exe_path)
        AbbyAutomation.wait_until_abby_reader_is_opened()
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

    @staticmethod
    def open_image_improvement_tools() -> None:
        """
        Opens the OCR improvement tools
        """
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
    def crop_pdf(x: float, y: float, width: float, height: float) -> None:
        """
        Crops the PDF to the given values
        """
        press_key(key_combination='alt+tab', delay_in_seconds=1)
        press_key(key_combination='alt+c')
        AbbyAutomation.write_crop_values(1, 1, 0, 0)
        AbbyAutomation.write_crop_values(math.floor(width), math.floor(height), math.ceil(x), math.ceil(y))
        press_key(key_combination='alt+shift+.')
        press_key(key_combination='down', repetitions=3)
        press_key(key_combination='alt+e', delay_in_seconds=1)
        press_key(key_combination='enter')

    @staticmethod
    def crop_pdf_in_ocr_editor(*, path_to_pdf: str, x: float, y: float, width: float,
                               height: float) -> None:
        """
        Opens the given path to the pdf in abby and crops each page by the given rectangle.

        :param path_to_pdf: Path leading to the PDF
        :param x: x position of crop rectangle
        :param y: y position of crop rectangle
        :param height: Height of the crop rectangle
        :param width: Width of the crop rectangle
        """
        abby_exe = 'D:\\Software\\Abby Finereader 15\\ABBYY FineReader 15\\FineReader.exe'

        subprocess.Popen([abby_exe, path_to_pdf])
        time.sleep(5)
        press_key(key_combination='shift+alt+1', repetitions=2)
        press_key(key_combination='alt+e+a', delay_in_seconds=20)
        press_key(key_combination='ctrl+i', delay_in_seconds=10)
        press_key(key_combination='alt+c')

        AbbyAutomation.write_crop_values(1, 1, 0, 0)
        AbbyAutomation.write_crop_values(math.floor(width), math.floor(height), math.ceil(x), math.ceil(y))

        press_key(key_combination='alt+shift+.')
        press_key(key_combination='down', repetitions=3)

        press_key(key_combination='alt+e', delay_in_seconds=1)
        press_key(key_combination='enter')

    @staticmethod
    def write_crop_values(width: int, height: int, x: int, y: int):
        """
        Writes the give crop values into the input fields of the ocr editor

        :param width: Width of the crop rectangle
        :param height: Height of the crop rectangle
        :param x: x-offset of the crop rectangle
        :param y: y-offset of the crop rectangle
        """

        # Width
        press_key(key_combination='alt+ß')
        press_key(key_combination='ctrl+a')
        write(width, 0.1)

        # Height
        press_key(key_combination='enter')
        write(height, 0.1)

        # X
        press_key(key_combination='enter')
        write(x, 0.1)

        # Y
        press_key(key_combination='enter')
        write(y, 0.1)

        press_key(key_combination='enter')

    @staticmethod
    def do_optimization():
        press_key(key_combination='alt+tab', delay_in_seconds=1)

        operations = [
            Procedures.do_pre_optimization,
            Procedures.do_equalize,
            Procedures.do_line_straighten,
            Procedures.do_photo_correction,
        ]

        for i in range(1):
            for operation in operations:
                AbbyAutomation.click_light_bulb()
                operation()
        time.sleep(1)
        press_key(key_combination='alt+shift+s')
        time.sleep(2)
        AbbyAutomation.save_temp_pdf()

    @staticmethod
    def save_temp_pdf():

        temp_path = '%userprofile%\\AppData\\Local\\Temp'

        console.log("Saving temp pdf...")
        arrow_down = pyautogui.locateCenterOnScreen('save_pdf_dropdown.png')
        if arrow_down is None:
            return
        pyautogui.click(arrow_down.x, arrow_down.y)
        press_key(key_combination='down', repetitions=2, delay_in_seconds=0.5)
        press_key(key_combination='enter')
        write(text=temp_path)
        press_key(key_combination='enter')
        time.sleep(0.5)
        temp_uuid = uuid.uuid4()
        write(text=f'{temp_uuid}.pdf')
        press_key(key_combination='enter', delay_in_seconds=0.5)
        press_key(key_combination='tab')
        press_key(key_combination='enter', delay_in_seconds=1)
        press_key(key_combination='tab', repetitions=7)
        press_key(key_combination='enter')
        press_key(key_combination='tab', repetitions=8)
        press_key(key_combination='enter', delay_in_seconds=0.5)
        press_key(key_combination='shift+tab')
        press_key(key_combination='enter', delay_in_seconds=0.5)
        AbbyAutomation.wait_until_saving_pdf_is_finished()
        time.sleep(1)
        AbbyAutomation.wait_until_saving_pdf_is_finished()
        console.log(Panel("PDF saved"))

        AbbyAutomation.open_abby_and_ocr_editor(path_to_pdf=f"{temp_path}\\{temp_uuid}.pdf")


    @staticmethod
    def is_undo_redo_abby_greyed_out_visible() -> bool:
        result_not_greyed_out = pyautogui.locateOnScreen('abby_reader_arrows.png')
        return result_not_greyed_out is not None

    @staticmethod
    def is_undo_redo_ocr_greyed_out_visible() -> bool:
        arrow_is_greyed_out = pyautogui.locateOnScreen('operation_running.png')
        return arrow_is_greyed_out is not None

    @staticmethod
    def click_light_bulb():
        result = pyautogui.locateCenterOnScreen('light_bulb.png')
        if result is not None:
            pyautogui.click(result.x, result.y)

    @staticmethod
    def wait_until_saving_pdf_is_finished() -> None:
        console.log("Waiting for PDF to be saved...")
        finished = AbbyAutomation.is_undo_redo_ocr_greyed_out_visible()
        while not finished:
            console.log("Waiting for PDF to be saved...")
            time.sleep(0.5)
            finished = AbbyAutomation.is_undo_redo_ocr_greyed_out_visible()

    @staticmethod
    def wait_until_abby_reader_is_opened() -> None:
        console.log("Waiting for Abby to open...")
        finished = AbbyAutomation.is_undo_redo_abby_greyed_out_visible()
        while not finished:
            console.log("Waiting for Abby to open...")
            time.sleep(0.5)
            finished = AbbyAutomation.is_undo_redo_abby_greyed_out_visible()
        time.sleep(2)
        console.log("Abby opened")
