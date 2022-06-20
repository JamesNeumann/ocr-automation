import os.path
import time

from config import Config
from utils.console import console
from utils.file_utils import is_file_locked
from utils.screen import Screen, FolderType


class WaitingProcedures:
    @staticmethod
    def wait_until_procedure_finished() -> None:
        """
        Waits until one procedure is finished
        """
        console.log("Operation is running...")
        finished = (
            WaitingProcedures.is_undo_redo_visible()
            or WaitingProcedures.is_close_button_visible()
        )
        while not finished:
            console.log("Operation is running...")
            time.sleep(0.5)
            finished = (
                WaitingProcedures.is_undo_redo_visible()
                or WaitingProcedures.is_close_button_visible()
            )

    @staticmethod
    def wait_until_ocr_is_finished() -> None:
        """
        Waits until ocr is finished
        """
        WaitingProcedures.wait_until_ocr_not_done_is_visible()

        if not Config.STOP_STUCK_RUNNING:
            time.sleep(1)
            WaitingProcedures.wait_until_ocr_not_done_is_not_visible()

    @staticmethod
    def wait_until_ocr_not_done_is_visible() -> None:
        """
        Waits until OCR not done banner is visible
        """
        console.log("Waiting until OCR is finished...")
        ocr_not_finished = Screen.locate_on_screen("ocr_not_done.png")
        while ocr_not_finished is None and not Config.STOP_STUCK_RUNNING:
            console.log("Waiting until OCR is finished...")
            time.sleep(0.5)
            ocr_not_finished = Screen.locate_on_screen("ocr_not_done.png")

    @staticmethod
    def wait_until_ocr_not_done_is_not_visible() -> None:
        """
        Waits until ocr not done banner is visible
        """
        console.log("Waiting until OCR is finished...")
        ocr_not_finished = Screen.locate_on_screen("ocr_not_done.png")
        while ocr_not_finished is not None and not Config.STOP_STUCK_RUNNING:
            console.log("Waiting until OCR is finished...")
            time.sleep(0.5)
            ocr_not_finished = Screen.locate_on_screen("ocr_not_done.png")

    @staticmethod
    def wait_until_cropping_page_is_done() -> None:
        console.log("Waiting until cropping page is done")
        cropping_done = Screen.locate_on_screen(
            "ocr_cropping_not_done.png", FolderType.WIN
        )
        while cropping_done is not None:
            console.log("Waiting until cropping page is done")
            time.sleep(0.5)
            cropping_done = Screen.locate_on_screen(
                "ocr_cropping_not_done.png", FolderType.WIN
            )

    @staticmethod
    def wait_until_close_button_visible(max_time: int = 3) -> None:
        """
        Waits until the close button of a dialog is visible
        """
        console.log("Waiting for close button to be visible...")
        visible = WaitingProcedures.is_close_button_visible()
        iteration = 0
        while not visible:
            if iteration > max_time:
                return
            console.log("Waiting for close button to be visible...")
            time.sleep(0.5)
            visible = WaitingProcedures.is_close_button_visible()
            iteration += 1
        console.log("Close button is visible")

    @staticmethod
    def wait_until_saving_pdf_is_finished(pdf_path: str) -> None:
        """
        Wait until saving PDF is finished
        """
        console.log("Waiting for PDF to be saved...")
        # finished = WaitingProcedures.is_undo_redo_ocr_greyed_out_visible()
        file_exists = os.path.isfile(pdf_path)
        file_locked = is_file_locked(pdf_path)
        while file_locked or not file_exists:
            console.log("Waiting for PDF to be saved...")
            time.sleep(0.5)
            # finished = WaitingProcedures.is_undo_redo_ocr_greyed_out_visible()
            file_exists = os.path.isfile(pdf_path)
            file_locked = is_file_locked(pdf_path)

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
    def wait_until_ocr_page_recognition_icon_is_visible() -> None:
        """
        Waits until the OCR page recognition icon is visible
        """
        console.log("Waiting for open ocr page recognition icon to be visible")
        visible = WaitingProcedures.is_ocr_page_recognition_icon_visible()
        while not visible:
            console.log("Waiting for open ocr page recognition icon to be visible")
            time.sleep(0.5)
            visible = WaitingProcedures.is_ocr_page_recognition_icon_visible()

    @staticmethod
    def wait_util_ocr_open_pdf_is_visible() -> None:
        """
        Waits until open PDF in OCR editor is visible

        """
        console.log("Waiting for ocr open pdf icon to be visible...")
        visible = WaitingProcedures.is_ocr_open_odf_visible()
        while not visible:
            console.log("Waiting for ocr open pdf icon to be visible...")
            time.sleep(0.5)
            visible = WaitingProcedures.is_ocr_open_odf_visible()

    @staticmethod
    def is_ocr_open_odf_visible() -> bool:
        """
        Checks if open PDF in the OCR editor is visible

        :return: Is visible or not
        """
        result = Screen.locate_on_screen("ocr_open_pdf.png")
        if result is None:
            return False
        return True

    @staticmethod
    def is_ocr_page_recognition_icon_visible() -> bool:
        """
        Checks if the OCR page recognition icon is visible

        :return: Is visible or not
        """
        result = Screen.locate_on_screen("ocr_page_recognition.png")
        if result is None:
            return False
        return True

    @staticmethod
    def is_undo_redo_ocr_greyed_out_visible() -> bool:
        """
        Checks if the undo redo buttons in the OCR editor are visible and greyed out

        :return Is visible or not
        """
        arrow_is_greyed_out = Screen.locate_on_screen("operation_running.png")
        return arrow_is_greyed_out is not None

    @staticmethod
    def is_open_pdf_visible() -> bool:
        """
        Checks if the open PDF button is visible

        :return: Is visible or not
        """
        result = Screen.locate_center_on_screen("open_ocr_editor.png")
        if result is not None:
            return True
        return False

    @staticmethod
    def is_close_button_visible() -> bool:
        """
        Checks whether the close button of the dialog is visible

        :return Is visible or not
        """
        focused_closed_button_visible = Screen.locate_on_screen(
            "close_dialog_button.png", FolderType.WIN
        )
        if focused_closed_button_visible is not None:
            return True

        focused_closed_button_not_highlighted = Screen.locate_on_screen(
            "close_dialog_button_not_highlighted.png", FolderType.WIN
        )
        if focused_closed_button_not_highlighted is not None:
            return True

        close_button_visible = Screen.locate_on_screen(
            "close_dialog_button_not_focused.png", FolderType.WIN
        )
        if close_button_visible is not None:
            return True

        highlighted_button_visible = Screen.locate_on_screen(
            "close_dialog_button_highlighted.png", FolderType.WIN
        )
        if highlighted_button_visible is not None:
            return True
        return False

    @staticmethod
    def is_undo_redo_visible() -> bool:
        """
        Checks if undo redo button is visible. The undo button is not greyed out.

        :return Is visible or not
        """
        result_greyed_out = Screen.locate_on_screen("operation_finished.png")
        return result_greyed_out is not None

    @staticmethod
    def is_warning_symbol_visible(attempts: int = 5) -> bool:
        """
        Checks if warning symbol is visible
        """
        for i in range(attempts):
            result = Screen.locate_on_screen("warning_symbol.png")
            if result is not None:
                return True
        return False
