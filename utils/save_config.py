import json
import os.path

from utils.offset import Offset
from utils.console import console


class SaveConfig:
    SAVE_CONFIG = {}
    STANDARD_SAVE_LOCATION = ""

    @staticmethod
    def init():
        SaveConfig.SAVE_CONFIG = SaveConfig.load_save_file()
        SaveConfig.STANDARD_SAVE_LOCATION = SaveConfig.get_default_save_location()

    @staticmethod
    def load_save_file():
        try:
            with open("save.json", "r", encoding="utf-8") as f:
                path = json.load(f)
                return path
        except FileNotFoundError:
            console.log("Save file not found. Skipping...")

    @staticmethod
    def update_default_save_location(path_to_folder: str):
        if not SaveConfig.SAVE_CONFIG:
            SaveConfig.SAVE_CONFIG = {"path": path_to_folder}
        else:
            SaveConfig.SAVE_CONFIG["path"] = path_to_folder
        SaveConfig.save_file()

    @staticmethod
    def update_default_crop_box_offset(top: int, right: int, bottom: int, left: int):
        offset_values = {"top": top, "right": right, "bottom": bottom, "left": left}
        if not SaveConfig.SAVE_CONFIG:
            SaveConfig.SAVE_CONFIG = {"offset": offset_values}
        else:
            SaveConfig.SAVE_CONFIG["offset"] = offset_values
        SaveConfig.save_file()

    @staticmethod
    def get_default_crop_box_offset() -> Offset:
        if not SaveConfig.SAVE_CONFIG or "offset" not in SaveConfig.SAVE_CONFIG:
            offset = {"top": 7, "right": 7, "bottom": 10, "left": 7}
        else:
            offset = SaveConfig.SAVE_CONFIG["offset"]
        return Offset(offset["top"], offset["right"], offset["bottom"], offset["left"])

    @staticmethod
    def get_default_save_location():
        if not SaveConfig.SAVE_CONFIG:
            return "C:"
        return (
            SaveConfig.SAVE_CONFIG["path"] or SaveConfig.read_default_dropbox_folder()
        )

    @staticmethod
    def save_file():
        console.log("Saving settings...")
        with open("save.json", "w+", encoding="utf-8") as f:
            f.write(json.dumps(SaveConfig.SAVE_CONFIG))

    @staticmethod
    def read_default_dropbox_folder():
        app_data = os.getenv("APPDATA")
        path = os.path.join(app_data, "Dropbox\\info.json")
        try:
            with open(path, "r") as f:
                dropbox_info = json.load(f)
                if "personal" in dropbox_info:
                    if "path" in dropbox_info["personal"]:
                        return os.path.abspath(
                            os.path.join(
                                dropbox_info["personal"]["path"],
                                "00 Petersen\\00 Digitalisierung MGH",
                            )
                        )
                if "business" in dropbox_info:
                    if "path" in dropbox_info["business"]:
                        return os.path.abspath(
                            os.path.join(
                                dropbox_info["business"]["path"],
                                "00 Petersen\\00 Digitalisierung MGH",
                            )
                        )
            console.log("Dropbox path not found. Skipping...")
            return None
        except FileNotFoundError:
            console.log("Dropbox path not found. Skipping...")
            return None
