import math
from typing import Dict, List, Callable

from automation.procedures.general_procedures import GeneralProcedures
from automation.procedures.procedure_context import ProcedureContext
from utils.keyboard_util import press_key


class OcrProcedures:

    @staticmethod
    def do_pre_optimization() -> None:
        """
        Executes the PDF pre optimization in the OCR editor
        """
        with ProcedureContext("pre optimization"):
            press_key(key_combination='alt+f', delay_in_seconds=0.5)
            GeneralProcedures.do_select_all_pages()
            press_key(key_combination='alt+f')
            press_key(key_combination='tab', repetitions=2)
            press_key(key_combination='enter', repetitions=2, delay_in_seconds=0.5)

    @staticmethod
    def do_equalize() -> None:
        """
        Executes the PDF equalize in the OCR editor
        """
        with ProcedureContext("equalize"):
            press_key(key_combination='alt+z', delay_in_seconds=0.5)
            GeneralProcedures.do_select_all_pages()
            press_key(key_combination='alt+z')
            press_key(key_combination='tab', repetitions=2)
            press_key(key_combination='enter', repetitions=2, delay_in_seconds=0.5)

    @staticmethod
    def do_line_straighten() -> None:
        """
        Executes the PDF line straightening in the OCR editor
        """
        with ProcedureContext("line straighten"):
            press_key(key_combination='alt+x', delay_in_seconds=0.5)
            GeneralProcedures.do_select_all_pages()
            press_key(key_combination='alt+x')
            press_key(key_combination='tab', repetitions=2)
            press_key(key_combination='enter', repetitions=2, delay_in_seconds=0.5)

    @staticmethod
    def do_photo_correction() -> None:
        """
        Executes the PDF photo correction. Currently, only page whiten.
        """
        with ProcedureContext("photo correction"):
            press_key(key_combination='alt+o', delay_in_seconds=0.5)
            GeneralProcedures.do_select_all_pages()
            press_key(key_combination='alt+ß', delay_in_seconds=0.5)
            press_key(key_combination='enter', delay_in_seconds=1)

    @staticmethod
    def do_crop_pdf(x: float, y: float, width: float, height: float, should_tab_in: bool = True) -> None:
        """
        Crops the PDF to the given values
        """
        with ProcedureContext("cropping pdf"):
            if should_tab_in:
                press_key(key_combination='alt+tab', delay_in_seconds=1)

            press_key(key_combination='alt+c')
            GeneralProcedures.write_crop_values(1, 1, 0, 0)
            GeneralProcedures.write_crop_values(math.floor(width), math.floor(height), math.ceil(x), math.ceil(y))
            press_key(key_combination='alt+shift+.')
            press_key(key_combination='down', repetitions=3)
            press_key(key_combination='alt+e', delay_in_seconds=1)
            press_key(key_combination='enter')

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
            "Hintergrund weißen": OcrProcedures.do_photo_correction
        }

    @staticmethod
    def get_procedures(names: List[str]) -> List[Callable]:
        """
        Returns all procedures that map to the given names.

        :param names: List of procedure names
        :return All matching procedure functions
        """
        return [value for key, value in OcrProcedures.get_available_procedures().items() if key in names]
