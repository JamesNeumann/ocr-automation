import time

from rich.panel import Panel

from automation.procedures.waiting_procedures import WaitingProcedures
from utils.console import console
from utils.keyboard_util import press_key


class ProcedureContext:
    """
    Context class which does informative logging and tracks operation duration.
    """

    def __init__(self, context_name: str):
        self.context_name = context_name
        pass

    def __enter__(self):
        self.start = time.time()
        console.log(f"Doing {self.context_name}...")

    def __exit__(self, exc_type, exc_val, exc_tb):
        WaitingProcedures.wait_until_procedure_finished()
        time.sleep(0.5)
        WaitingProcedures.wait_until_procedure_finished()
        press_key(key_combination='alt+shift+s')
        self.end = time.time()
        console.log(
            Panel(f"[green]Finished [white]{self.context_name} [green]in [cyan]{self.end - self.start} seconds"))
