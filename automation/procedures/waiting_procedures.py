import time

import pyautogui

from utils.console import console


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
    def wait_until_saving_pdf_is_finished() -> None:
        """
        Wait until saving PDF is finished
        """
        console.log("Waiting for PDF to be saved...")
        finished = WaitingProcedures.is_undo_redo_ocr_greyed_out_visible()
        while not finished:
            console.log("Waiting for PDF to be saved...")
            time.sleep(0.5)
            finished = WaitingProcedures.is_undo_redo_ocr_greyed_out_visible()

    @staticmethod
    def is_undo_redo_abby_greyed_out_visible() -> bool:
        """
        Checks if the undo redo button in the abby reader is visible and greyed out

        :return Is visible or not
        """
        result_not_greyed_out = pyautogui.locateOnScreen('abby_reader_arrows.png')
        return result_not_greyed_out is not None

    @staticmethod
    def is_undo_redo_ocr_greyed_out_visible() -> bool:
        """
        Checks if the undo redo buttons in the OCR editor are visible and greyed out

        :return Is visible or not
        """
        arrow_is_greyed_out = pyautogui.locateOnScreen('operation_running.png')
        return arrow_is_greyed_out is not None

    @staticmethod
    def is_close_button_visible() -> bool:
        """
        Checks whether the close button of the dialog is visible

        :return Is visible or not
        """
        focused_closed_button_visible = pyautogui.locateOnScreen('close_dialog_button.png')
        if focused_closed_button_visible is not None:
            return True

        close_button_visible = pyautogui.locateOnScreen('close_dialog_button_not_focused.png')
        if close_button_visible is not None:
            return True

        highlighted_button_visible = pyautogui.locateOnScreen('close_dialog_button_highlighted.png')
        if highlighted_button_visible is not None:
            return True
        return False

    @staticmethod
    def is_undo_redo_visible() -> bool:
        """
        Checks if undo redo button is visible. The undo button is not greyed out.

        :return Is visible or not
        """
        result_greyed_out = pyautogui.locateOnScreen('operation_finished.png')
        return result_greyed_out is not None
