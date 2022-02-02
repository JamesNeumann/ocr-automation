import time

import pyautogui
from rich.panel import Panel

from utils.console import console
from utils.keyboard_util import press_key


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
        finished = Procedures.is_undo_redo_visible()
        while not finished:
            console.log("Operation is running...")
            time.sleep(0.5)
            finished = Procedures.is_undo_redo_visible()

    @staticmethod
    def do_select_all_pages():
        press_key(key_combination='tab')
        press_key(key_combination='down', repetitions=3)

    @staticmethod
    def is_undo_redo_visible() -> bool:
        result_greyed_out = pyautogui.locateOnScreen('operation_finished.png')
        return result_greyed_out is not None
