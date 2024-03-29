import math
import time
from typing import Dict, List, Callable

from automation.procedures.general_procedures import GeneralProcedures
from automation.procedures.procedure_context import ProcedureContext
from automation.procedures.waiting_procedures import WaitingProcedures
from utils.keyboard_util import press_key, write


class OcrProcedures:
    @staticmethod
    def do_pre_optimization() -> None:
        """
        Executes the PDF pre optimization in the OCR editor
        """
        with ProcedureContext("Empfohlene Vorbearbeitung"):
            press_key(key_combination="alt+f", delay_in_seconds=0.5)
            GeneralProcedures.do_select_all_pages()
            press_key(key_combination="alt+f")
            press_key(key_combination="tab", repetitions=2)
            press_key(key_combination="enter", repetitions=2, delay_in_seconds=0.5)

    @staticmethod
    def do_equalize() -> None:
        """
        Executes the PDF equalize in the OCR editor
        """
        with ProcedureContext("Entzerren"):
            press_key(key_combination="alt+z", delay_in_seconds=0.5)
            GeneralProcedures.do_select_all_pages()
            press_key(key_combination="alt+z")
            press_key(key_combination="tab", repetitions=2)
            press_key(key_combination="enter", repetitions=2, delay_in_seconds=0.5)

    @staticmethod
    def do_line_straighten() -> None:
        """
        Executes the PDF line straightening in the OCR editor
        """
        with ProcedureContext("Textzeilen begradigen"):
            press_key(key_combination="alt+x", delay_in_seconds=0.5)
            GeneralProcedures.do_select_all_pages()
            press_key(key_combination="alt+x")
            press_key(key_combination="tab", repetitions=2)
            press_key(key_combination="enter", repetitions=2, delay_in_seconds=0.5)

    @staticmethod
    def do_photo_correction() -> None:
        """
        Executes the PDF photo correction. Currently, only page whiten.
        """
        with ProcedureContext("Hintergund weißen"):
            press_key(key_combination="alt+o", delay_in_seconds=0.5)
            GeneralProcedures.do_select_all_pages()
            press_key(key_combination="alt+ß", delay_in_seconds=0.5)
            press_key(key_combination="enter", delay_in_seconds=1)

    @staticmethod
    def do_eraser() -> None:
        press_key(key_combination="alt+i", delay_in_seconds=0.3)

    @staticmethod
    def do_crop_pdf(
        x: float, y: float, width: float, height: float, should_tab_in: bool = True
    ) -> None:
        """
        Crops the PDF to the given values
        """
        with ProcedureContext("PDF crop"):
            if should_tab_in:
                press_key(key_combination="alt+tab", delay_in_seconds=1)

            press_key(key_combination="alt+c", delay_in_seconds=0.5)
            GeneralProcedures.write_crop_values(1, 1, 0, 0)
            GeneralProcedures.write_crop_values(
                math.floor(width), math.floor(height), math.ceil(x), math.ceil(y)
            )
            press_key(key_combination="alt+shift+.", delay_in_seconds=0.5)
            press_key(key_combination="down", repetitions=3, delay_in_seconds=0.5)
            press_key(key_combination="alt+e", delay_in_seconds=1)
            press_key(key_combination="enter", delay_in_seconds=0.5)

    @staticmethod
    def do_crop_pdf_single_page(
        x: float, y: float, width: float, height: float, should_tab_in: bool = True
    ) -> None:
        if should_tab_in:
            press_key(key_combination="alt+tab", delay_in_seconds=1)

        press_key(key_combination="alt+c", delay_in_seconds=0.5)
        GeneralProcedures.write_crop_values(1, 1, 0, 0)
        GeneralProcedures.write_crop_values(
            math.floor(width), math.floor(height), math.ceil(x), math.ceil(y)
        )
        press_key(key_combination="alt+shift+.", delay_in_seconds=0.5)
        press_key(key_combination="up", repetitions=3, delay_in_seconds=0.5)
        press_key(key_combination="alt+e", delay_in_seconds=1)
        press_key(key_combination="enter", delay_in_seconds=0.5)
        time.sleep(0.5)
        WaitingProcedures.wait_until_cropping_page_is_done()
        # with ProcedureContext("PDF crop"):

    @staticmethod
    def do_binary(should_tab_in: bool = True):
        with ProcedureContext("Binarisierung"):
            if should_tab_in:
                press_key(key_combination="alt+tab", delay_in_seconds=1)
            GeneralProcedures.click_light_bulb()
            press_key(key_combination="shift+s", delay_in_seconds=0.3)
            press_key(key_combination="tab", delay_in_seconds=0.3)
            write("0")
            press_key(key_combination="tab", repetitions=2, delay_in_seconds=0.1)
            write("2")
            press_key(key_combination="tab", delay_in_seconds=0.3, repetitions=4)
            press_key(key_combination="down", repetitions=4, delay_in_seconds=0.3)
            press_key(key_combination="tab", delay_in_seconds=0.3)
            press_key(key_combination="shift+a", delay_in_seconds=0.3)
            press_key(key_combination="enter")

    @staticmethod
    def get_available_procedures() -> Dict[str, Callable]:
        """
        Returns all available procedures and its names.

        :return Mapping of procedure names and corresponding function
        """
        return {
            "Vorverarbeitung": OcrProcedures.do_pre_optimization,
            "Entzerren": OcrProcedures.do_equalize,
            "Linien begradigen": OcrProcedures.do_line_straighten,
            "Hintergrund weißen": OcrProcedures.do_photo_correction,
        }

    @staticmethod
    def get_procedures(names: List[str]) -> List[Callable]:
        """
        Returns all procedures that map to the given names.

        :param names: List of procedure names
        :return All matching procedure functions
        """
        return [
            value
            for key, value in OcrProcedures.get_available_procedures().items()
            if key in names
        ]
