import json
import os.path
import uuid
from json import JSONDecodeError

from config import Config
from utils.console import console
from utils.ocr_default_error_replacement import default_error_replacement_map
from utils.offset import Offset


class SaveConfig:
    SAVE_CONFIG = {}

    @staticmethod
    def init():
        SaveConfig.SAVE_CONFIG = SaveConfig.load_save_file()

    @staticmethod
    def load_save_file():
        try:
            with open("save.json", "r", encoding="utf-8") as f:
                try:
                    path = json.load(f)
                    return path
                except JSONDecodeError:
                    console.log(
                        "Speicherdatei ist korrupt. Eine neue Datei wird erstellt."
                    )
                    with open("save.json", "w", encoding="utf-8") as wf:
                        wf.write("{}")
        except FileNotFoundError:
            console.log("Speicherdatei nicht gefunden. Überspringe...")

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
            return Config.DEFAULT_CROP_BOX_OFFSET
        offset = SaveConfig.SAVE_CONFIG["offset"]
        return Offset(offset["top"], offset["right"], offset["bottom"], offset["left"])

    @staticmethod
    def update_dpi_value(dpi: int):
        if not SaveConfig.SAVE_CONFIG:
            SaveConfig.SAVE_CONFIG = {"DPI": dpi}
        else:
            SaveConfig.SAVE_CONFIG["DPI"] = dpi
        SaveConfig.save_file()

    @staticmethod
    def update_all(crop_box: Offset, dpi: int, y_axis_threshold: float):

        offset_values = {
            "top": crop_box.top,
            "right": crop_box.right,
            "bottom": crop_box.bottom,
            "left": crop_box.left,
        }
        if not SaveConfig.SAVE_CONFIG:
            SaveConfig.SAVE_CONFIG = {
                "DPI": dpi,
                "offset": offset_values,
                "y_axis_threshold": y_axis_threshold,
            }
        else:
            SaveConfig.SAVE_CONFIG["DPI"] = dpi
            SaveConfig.SAVE_CONFIG["offset"] = offset_values
            SaveConfig.SAVE_CONFIG["y_axis_threshold"] = y_axis_threshold
        SaveConfig.save_file()

    @staticmethod
    def get_dpi_value() -> int:
        if not SaveConfig.SAVE_CONFIG or "DPI" not in SaveConfig.SAVE_CONFIG:
            dpi = Config.DPI
        else:
            dpi = SaveConfig.SAVE_CONFIG["DPI"]
        return dpi

    @staticmethod
    def get_y_axis_threshold() -> float:
        if (
            not SaveConfig.SAVE_CONFIG
            or "y_axis_threshold" not in SaveConfig.SAVE_CONFIG
        ):
            y_axis_threshold = Config.CROP_Y_AXIS_THRESHOLD
        else:
            y_axis_threshold = SaveConfig.SAVE_CONFIG["y_axis_threshold"]
        return y_axis_threshold

    @staticmethod
    def get_default_save_location():
        if not SaveConfig.SAVE_CONFIG or "path" not in SaveConfig.SAVE_CONFIG:
            return "C:"
        return (
            SaveConfig.SAVE_CONFIG["path"] or SaveConfig.read_default_dropbox_folder()
        )

    @staticmethod
    def get_default_error_replacement_maps():
        if (
            not SaveConfig.SAVE_CONFIG
            or "default_error_replacements" not in SaveConfig.SAVE_CONFIG
        ):
            return [default_error_replacement_map]
        return SaveConfig.SAVE_CONFIG["default_error_replacements"]

    @staticmethod
    def save_file():
        with open("save.json", "w+", encoding="utf-8") as f:
            f.write(json.dumps(SaveConfig.SAVE_CONFIG))
        console.log("Einstellungen gespeichert")

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
            console.log("Dropbox-Pfad nicht gefunden. Überspringe...")
            return None
        except FileNotFoundError:
            console.log("Dropbox-Pfad nicht gefunden. Überspringe...")
            return None
