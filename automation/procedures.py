import math
import time
from typing import Dict, List

import pyautogui
from rich.panel import Panel

from utils.console import console
from utils.keyboard_util import press_key, write


class ProcedureContext:
    def __init__(self, context_name: str):
        self.context_name = context_name
        pass

    def __enter__(self):
        self.start = time.time()
        console.log(f"Doing {self.context_name}...")

    def __exit__(self, exc_type, exc_val, exc_tb):
        Procedures.wait_until_operation_finished()
        time.sleep(1)
        Procedures.wait_until_operation_finished()
        press_key(key_combination='alt+shift+s')
        self.end = time.time()
        console.log(
            Panel(f"[green]Finished [white]{self.context_name} [green]in [cyan]{self.end - self.start} seconds"))


class Procedures:

    @staticmethod
    def do_pre_optimization():
        with ProcedureContext("pre optimization"):
            press_key(key_combination='alt+f', delay_in_seconds=0.5)
            Procedures.do_select_all_pages()
            press_key(key_combination='alt+f')
            press_key(key_combination='tab', repetitions=2)
            press_key(key_combination='enter', repetitions=2, delay_in_seconds=0.5)

    @staticmethod
    def do_equalize():
        with ProcedureContext("equalize"):
            press_key(key_combination='alt+z', delay_in_seconds=0.5)
            Procedures.do_select_all_pages()
            press_key(key_combination='alt+z')
            press_key(key_combination='tab', repetitions=2)
            press_key(key_combination='enter', repetitions=2, delay_in_seconds=0.5)

    @staticmethod
    def do_line_straighten():
        with ProcedureContext("line straighten"):
            press_key(key_combination='alt+x', delay_in_seconds=0.5)
            Procedures.do_select_all_pages()
            press_key(key_combination='alt+x')
            press_key(key_combination='tab', repetitions=2)
            press_key(key_combination='enter', repetitions=2, delay_in_seconds=0.5)

    @staticmethod
    def do_photo_correction():
        with ProcedureContext("photo correction"):
            press_key(key_combination='alt+o', delay_in_seconds=0.5)
            Procedures.do_select_all_pages()
            press_key(key_combination='alt+ß', delay_in_seconds=0.5)
            press_key(key_combination='enter', delay_in_seconds=1)

    @staticmethod
    def wait_until_operation_finished():
        console.log("Operation is running...")
        finished = Procedures.is_undo_redo_visible() or Procedures.is_close_button_visible()
        while not finished:
            console.log("Operation is running...")
            time.sleep(0.5)
            finished = Procedures.is_undo_redo_visible()

    @staticmethod
    def is_close_button_visible() -> bool:
        visible = pyautogui.locateOnScreen('close_dialog_button.png')
        return visible is not None

    @staticmethod
    def do_crop_pdf(x: float, y: float, width: float, height: float, should_tab_in: bool = True) -> None:
        """
        Crops the PDF to the given values
        """
        with ProcedureContext("cropping pdf"):
            if should_tab_in:
                press_key(key_combination='alt+tab', delay_in_seconds=1)

            press_key(key_combination='alt+c')
            Procedures.write_crop_values(1, 1, 0, 0)
            Procedures.write_crop_values(math.floor(width), math.floor(height), math.ceil(x), math.ceil(y))
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
    def do_select_all_pages():
        press_key(key_combination='tab')
        press_key(key_combination='down', repetitions=3)

    @staticmethod
    def is_undo_redo_visible() -> bool:
        result_greyed_out = pyautogui.locateOnScreen('operation_finished.png')
        return result_greyed_out is not None

    @staticmethod
    def get_available_procedures() -> Dict:
        return {
            "Vorverarbeitung": Procedures.do_pre_optimization,
            "Entzerren": Procedures.do_equalize,
            "Linien begradigen": Procedures.do_line_straighten,
            "Hintergrund weißen": Procedures.do_photo_correction
        }

    @staticmethod
    def get_procedures(names: List[str]) -> List:
        return [value for key, value in Procedures.get_available_procedures().items() if key in names]
