import sys
from enum import Enum

import pyautogui


class FolderType(Enum):
    ABBY = 1
    WIN = 2


class Screen:
    SCREEN_RESOLUTION_STRING = "1920x1080"

    @staticmethod
    def set_screen_resolution_string():
        width, height = pyautogui.size()
        Screen.SCREEN_RESOLUTION_STRING = f"{width}x{height}"

    @staticmethod
    def is_win_11():
        if sys.getwindowsversion().build > 20000:
            return True
        else:
            return False

    @staticmethod
    def locate_center_on_screen(file_name: str, folder: FolderType = FolderType.ABBY):
        return pyautogui.locateCenterOnScreen(Screen.get_image_path(file_name, folder))

    @staticmethod
    def locate_on_screen(file_name: str, folder: FolderType = FolderType.ABBY):
        return pyautogui.locateOnScreen(Screen.get_image_path(file_name, folder))

    @staticmethod
    def get_image_path(file_name: str, folder: FolderType = FolderType.ABBY):
        return f"./images/{Screen.get_folder(folder)}/{Screen.SCREEN_RESOLUTION_STRING}/{file_name}"

    @staticmethod
    def get_folder(folder: FolderType) -> str:
        if folder == FolderType.ABBY:
            return 'FineReader'
        if folder == FolderType.WIN:
            if Screen.is_win_11():
                return 'Win11'
            else:
                return 'Win10'
