import sys
from enum import Enum
from typing import Any

import pyautogui


class FolderType(Enum):
    OCR = 1
    WIN = 2


class Screen:
    SCREEN_RESOLUTION_STRING = "1920x1080"

    @staticmethod
    def set_screen_resolution_string() -> None:
        """
        Sets the screen resolution screen. Which can be used to select the correct images
        """
        width, height = pyautogui.size()
        Screen.SCREEN_RESOLUTION_STRING = f"{width}x{height}"

    @staticmethod
    def is_win_11() -> bool:
        """
        Checks if current operating system is Windows 11

        :return: Is Windows 11 or not
        """
        return sys.getwindowsversion().build > 20000

    @staticmethod
    def locate_center_on_screen(
        image_name: str, folder: FolderType = FolderType.OCR
    ) -> Any:
        """
        Locates the given image on screen. Then returns the center position of that image relative to its screen position

        :param image_name: Image name of the image to locate on screen
        :param folder: In which folder the image is saved
        :return: Any
        """
        return pyautogui.locateCenterOnScreen(
            Screen.get_image_path(image_name, folder), confidence=0.90
        )

    @staticmethod
    def locate_on_screen(image_name: str, folder: FolderType = FolderType.OCR) -> Any:
        """
        Locates the given image on screen. Then returns the position of that image  relative to its screen position

        :param image_name: Image name of the image to locate on screen
        :param folder: In which folder the image is saved
        :return: Any
        """
        return pyautogui.locateOnScreen(
            Screen.get_image_path(image_name, folder), confidence=0.90
        )

    @staticmethod
    def get_image_path(image_name: str, folder: FolderType = FolderType.OCR) -> str:
        """
        Returns the full path to the given image

        :param image_name: Name of the image
        :param folder: Folder where the image is located
        :return: The full path to the image
        """
        return f"./images/{Screen.get_folder(folder)}/{Screen.SCREEN_RESOLUTION_STRING}/{image_name}"

    @staticmethod
    def get_folder(folder: FolderType) -> str:
        """
        Returns the string of the given FolderType

        :param folder: Type of the
        :return: The name of the FolderType
        """
        if folder == FolderType.OCR:
            return "OCR"
        if folder == FolderType.WIN:
            if Screen.is_win_11():
                return "Win11"
            return "Win10"
