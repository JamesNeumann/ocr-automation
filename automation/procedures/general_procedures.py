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
        press_key(key_combination='alt+ß', delay_in_seconds=0.3)
        press_key(key_combination='ctrl+a', delay_in_seconds=0.1)
        write(width, 0.1)

        # Height
        press_key(key_combination='tab', delay_in_seconds=0.3)
        press_key(key_combination='ctrl+a', delay_in_seconds=0.1)
        write(height, 0.1)

        # X
        press_key(key_combination='tab', delay_in_seconds=0.3)
        press_key(key_combination='ctrl+a', delay_in_seconds=0.1)
        write(x, 0.1)

        # Y
        press_key(key_combination='tab', delay_in_seconds=0.3)
        press_key(key_combination='ctrl+a', delay_in_seconds=0.1)
        write(y, 0.1)

        press_key(key_combination='tab', delay_in_seconds=0.3)

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
    def open_save_pdf_dialog():
        """
        Opens the save PDF dialog for saving a searchable PDF
        """
        arrow_down = pyautogui.locateCenterOnScreen('save_pdf_dropdown.png')
        if arrow_down is None:
            return
        pyautogui.click(arrow_down.x, arrow_down.y)
        press_key(key_combination='down', repetitions=1)
        press_key(key_combination='enter')

    @staticmethod
    def click_light_bulb(attempts: int = 5) -> None:
        """
        Clicks the light bulb in the OCR image improvement tools
        """
        i = 0
        while i < attempts:
            result = pyautogui.locateCenterOnScreen('light_bulb.png')
            if result is not None:
                pyautogui.click(result.x, result.y)
                return
            i += 1

    @staticmethod
    def click_ocr_file_icon(attempts: int = 5) -> None:
        """
        Clicks the OCR file icon
        """
        i = 0
        while i < attempts:
            x, y = pyautogui.locateCenterOnScreen("ocr_file_icon.png")
            if x is not None and y is not None:
                pyautogui.click(x, y)
                return
            i += 1

    @staticmethod
    def click_ocr_pages_header(attempts: int = 5) -> None:
        """
        Clicks the OCR pages header
        """
        i = 0
        while i < attempts:
            result = pyautogui.locateOnScreen("ocr_pages_header.png")
            if result is not None:
                pyautogui.click(result.left + 10, result.top + 10)
                return
            i += 1

    @staticmethod
    def click_ocr_language_selection(attempts: int = 5) -> None:
        """
        Clicks the OCR option icon in the options menu
        :return:
        """
        i = 0
        while i < attempts:
            result = pyautogui.locateCenterOnScreen('ocr_language_selection.png')
            result_selected = pyautogui.locateCenterOnScreen('ocr_language_selection_selected.png')
            if result is not None:
                pyautogui.click(result.x, result.y)
                return
            if result_selected is not None:
                pyautogui.click(result_selected.x, result_selected.y)
                return
            i += 1

    @staticmethod
    def click_ocr_page_recognition_icon(attempts: int = 5):
        """
        Clicks the OCR page recognition icon
        """
        i = 0
        while i < attempts:
            result = pyautogui.locateCenterOnScreen('ocr_page_recognition.png')
            if result is not None:
                pyautogui.click(result.x, result.y)
                return
            i += 1
