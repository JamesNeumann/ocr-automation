import time
import uuid

import pyautogui
from rich.panel import Panel

from automation.procedures.waiting_procedures import WaitingProcedures
from utils.console import console
from utils.keyboard_util import press_key, write


class GeneralProcedures:

    @staticmethod
    def do_select_all_pages() -> None:
        """
        Selects the "all pages" option in the dropdown to apply one procedure to all pages.
        """
        press_key(key_combination='tab')
        press_key(key_combination='down', repetitions=3)

    @staticmethod
    def write_crop_values(width: int, height: int, x: int, y: int) -> None:
        """
        Writes the give crop values into the input fields of the ocr editor

        :param width: Width of the crop rectangle
        :param height: Height of the crop rectangle
        :param x: x-offset of the crop rectangle
        :param y: y-offset of the crop rectangle
        """

        # Width
        press_key(key_combination='alt+ß')
        press_key(key_combination='ctrl+a', delay_in_seconds=0.3)
        write(width, 0.5)

        # Height
        press_key(key_combination='enter', delay_in_seconds=0.3)
        write(height, 0.5)

        # X
        press_key(key_combination='enter', delay_in_seconds=0.3)
        write(x, 0.5)

        # Y
        press_key(key_combination='enter', delay_in_seconds=0.3)
        write(y, 0.5)

        press_key(key_combination='enter', delay_in_seconds=0.3)

    @staticmethod
    def save_temp_pdf() -> (str, str):
        """
        Saves the currently open PDF file in the temporary directory

        :returns The path to file and the file name
        """
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
        WaitingProcedures.wait_until_saving_pdf_is_finished()
        time.sleep(1)
        WaitingProcedures.wait_until_saving_pdf_is_finished()
        console.log(Panel("[green]PDF saved"))
        return temp_path, temp_uuid

    @staticmethod
    def click_light_bulb() -> None:
        """
        Clicks the light bulb in the OCR image improvement tools
        """
        result = pyautogui.locateCenterOnScreen('light_bulb.png')
        if result is not None:
            pyautogui.click(result.x, result.y)
