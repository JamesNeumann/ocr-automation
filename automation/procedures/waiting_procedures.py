import os.path
import time

from utils.console import console
from utils.screen import Screen, FolderType


class WaitingProcedures:
    @staticmethod
    def wait_until_procedure_finished() -> None:
        """
        Waits until one procedure is finished
        """
        console.log("Operation is running...")
        finished = WaitingProcedures.is_undo_redo_visible() or WaitingProcedures.is_close_button_visible()
        while not finished:
            console.log("Operation is running...")
            time.sleep(0.5)
            finished = WaitingProcedures.is_undo_redo_visible() or WaitingProcedures.is_close_button_visible()

    @staticmethod
    def wait_until_abby_reader_is_opened() -> None:
        """
        Waits until Abby Reader has opened
        """
        console.log("Waiting for Abby to open...")
        finished = WaitingProcedures.is_undo_redo_abby_greyed_out_visible()
        while not finished:
            console.log("Waiting for Abby to open...")
            time.sleep(0.5)
            finished = WaitingProcedures.is_undo_redo_abby_greyed_out_visible()
        time.sleep(2)
        console.log("Abby opened")

    @staticmethod
    def wait_until_ocr_is_finished() -> None:
        WaitingProcedures.wait_until_ocr_not_done_is_visible()
        time.sleep(1)
        WaitingProcedures.wait_until_ocr_not_done_is_not_visible()

    @staticmethod
    def wait_until_ocr_not_done_is_visible() -> None:
        """
        Waits until OCR not done banner is visible
        """
        console.log("Waiting until OCR is finished...")
        ocr_not_finished = Screen.locate_on_screen('ocr_not_done.png')
        while ocr_not_finished is None:
            console.log("Waiting until OCR is finished...")
            ocr_not_finished = Screen.locate_on_screen('ocr_not_done.png')

    @staticmethod
    def wait_until_ocr_not_done_is_not_visible() -> None:
        console.log("Waiting until OCR is finished...")
        ocr_not_finished = Screen.locate_on_screen('ocr_not_done.png')
        while ocr_not_finished is not None:
            console.log("Waiting until OCR is finished...")
            ocr_not_finished = Screen.locate_on_screen('ocr_not_done.png')

    @staticmethod
    def wait_until_close_button_visible() -> None:
        """
        Waits until the close button of a dialog is visible
        """
        console.log("Waiting for close button to be visible...")
        visible = WaitingProcedures.is_close_button_visible()
        while not visible:
            console.log("Waiting for close button to be visible...")
            time.sleep(0.5)
            visible = WaitingProcedures.is_close_button_visible()
        console.log("Close button is visible")

    @staticmethod
    def wait_until_saving_pdf_is_finished(pdf_path: str) -> None:
        """
        Wait until saving PDF is finished
        """
        console.log("Waiting for PDF to be saved...")
        finished = WaitingProcedures.is_undo_redo_ocr_greyed_out_visible()
        file_exists = os.path.isfile(pdf_path)
        while not finished and not file_exists:
            console.log("Waiting for PDF to be saved...")
            time.sleep(0.5)
            finished = WaitingProcedures.is_undo_redo_ocr_greyed_out_visible()
            file_exists = os.path.isfile(pdf_path)

    @staticmethod
    def wait_until_open_pdf_is_visible():
        """
        Waits until open PDF button is visible
        """
        console.log("Waiting for open PDF button to be visible")
        visible = WaitingProcedures.is_open_pdf_visible()
        while not visible:
            console.log("Waiting for open PDF button to be visible")
            time.sleep(0.5)
            visible = WaitingProcedures.is_open_pdf_visible()

    @staticmethod
    def is_undo_redo_abby_greyed_out_visible() -> bool:
        """
        Checks if the undo redo button in the abby reader is visible and greyed out

        :return Is visible or not
        """
        result_not_greyed_out = Screen.locate_on_screen('abby_reader_arrows.png')
        return result_not_greyed_out is not None

    @staticmethod
    def is_undo_redo_ocr_greyed_out_visible() -> bool:
        """
        Checks if the undo redo buttons in the OCR editor are visible and greyed out

        :return Is visible or not
        """
        arrow_is_greyed_out = Screen.locate_on_screen('operation_running.png')
        return arrow_is_greyed_out is not None

    @staticmethod
    def is_open_pdf_visible() -> bool:
        """
        Checks if the open PDF button in Abby is visible
        :return: Is visible or not
        """
        result = Screen.locate_center_on_screen('open_pdf.png')
        if result is not None:
            return True
        return False

    @staticmethod
    def is_close_button_visible() -> bool:
        """
        Checks whether the close button of the dialog is visible

        :return Is visible or not
        """
        focused_closed_button_visible = Screen.locate_on_screen('close_dialog_button.png', FolderType.WIN)
        if focused_closed_button_visible is not None:
            return True

        focused_closed_button_not_highlighted = Screen.locate_on_screen('close_dialog_button_not_highlighted.png',
                                                                        FolderType.WIN)
        if focused_closed_button_not_highlighted is not None:
            return True

        close_button_visible = Screen.locate_on_screen('close_dialog_button_not_focused.png', FolderType.WIN)
        if close_button_visible is not None:
            return True

        highlighted_button_visible = Screen.locate_on_screen('close_dialog_button_highlighted.png', FolderType.WIN)
        if highlighted_button_visible is not None:
            return True
        return False

    @staticmethod
    def is_undo_redo_visible() -> bool:
        """
        Checks if undo redo button is visible. The undo button is not greyed out.

        :return Is visible or not
        """
        result_greyed_out = Screen.locate_on_screen('operation_finished.png')
        return result_greyed_out is not None
