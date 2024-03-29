import json
import os.path
from json import JSONDecodeError
from typing import Dict

import deprecation

from config import Config
from utils.console import console
from utils.ocr_default_error_replacement import (
    standard_ocr_default_error_replacement_map,
)
from utils.offset import Offset


class SaveConfig:
    SAVE_CONFIG = {}

    PATH_KEY = "path"

    OFFSET_KEY = "offset"
    OFFSET_TOP_KEY = "top"
    OFFSET_RIGHT_KEY = "right"
    OFFSET_BOTTOM_KEY = "bottom"
    OFFSET_LEFT_KEY = "left"

    DPI_KEY = "DPI"

    Y_AXIS_OFFSET_KEY = "y_axis_threshold"

    AUTHOR_DB_PATH = "author_db_path"

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
            SaveConfig.SAVE_CONFIG = {SaveConfig.PATH_KEY: path_to_folder}
        else:
            SaveConfig.SAVE_CONFIG[SaveConfig.PATH_KEY] = path_to_folder
        SaveConfig.save_file()

    @staticmethod
    def update_default_crop_box_offset(top: int, right: int, bottom: int, left: int):
        offset_values = {
            SaveConfig.OFFSET_TOP_KEY: top,
            SaveConfig.OFFSET_RIGHT_KEY: right,
            SaveConfig.OFFSET_BOTTOM_KEY: bottom,
            SaveConfig.OFFSET_LEFT_KEY: left,
        }
        if not SaveConfig.SAVE_CONFIG:
            SaveConfig.SAVE_CONFIG = {SaveConfig.OFFSET_KEY: offset_values}
        else:
            SaveConfig.SAVE_CONFIG[SaveConfig.OFFSET_KEY] = offset_values
        SaveConfig.save_file()

    @staticmethod
    def get_default_crop_box_offset() -> Offset:
        if (
            not SaveConfig.SAVE_CONFIG
            or SaveConfig.OFFSET_KEY not in SaveConfig.SAVE_CONFIG
        ):
            return Config.DEFAULT_CROP_BOX_OFFSET
        offset = SaveConfig.SAVE_CONFIG[SaveConfig.OFFSET_KEY]
        return Offset(
            offset[SaveConfig.OFFSET_TOP_KEY],
            offset[SaveConfig.OFFSET_RIGHT_KEY],
            offset[SaveConfig.OFFSET_BOTTOM_KEY],
            offset[SaveConfig.OFFSET_LEFT_KEY],
        )

    @staticmethod
    def update_dpi_value(dpi: int):
        if not SaveConfig.SAVE_CONFIG:
            SaveConfig.SAVE_CONFIG = {SaveConfig.DPI_KEY: dpi}
        else:
            SaveConfig.SAVE_CONFIG[SaveConfig.DPI_KEY] = dpi
        SaveConfig.save_file()

    @staticmethod
    def update_all(
        crop_box: Offset, dpi: int, y_axis_threshold: float, author_db_path: str
    ):
        offset_values = {
            SaveConfig.OFFSET_TOP_KEY: crop_box.top,
            SaveConfig.OFFSET_RIGHT_KEY: crop_box.right,
            SaveConfig.OFFSET_BOTTOM_KEY: crop_box.bottom,
            SaveConfig.OFFSET_LEFT_KEY: crop_box.left,
        }
        if not SaveConfig.SAVE_CONFIG:
            SaveConfig.SAVE_CONFIG = {
                SaveConfig.DPI_KEY: dpi,
                SaveConfig.OFFSET_KEY: offset_values,
                SaveConfig.Y_AXIS_OFFSET_KEY: y_axis_threshold,
                SaveConfig.AUTHOR_DB_PATH: author_db_path,
            }
        else:
            SaveConfig.SAVE_CONFIG[SaveConfig.DPI_KEY] = dpi
            SaveConfig.SAVE_CONFIG[SaveConfig.OFFSET_KEY] = offset_values
            SaveConfig.SAVE_CONFIG[SaveConfig.Y_AXIS_OFFSET_KEY] = y_axis_threshold
            SaveConfig.SAVE_CONFIG[SaveConfig.AUTHOR_DB_PATH] = author_db_path
        SaveConfig.save_file()

    @staticmethod
    def get_dpi_value() -> int:
        if (
            not SaveConfig.SAVE_CONFIG
            or SaveConfig.DPI_KEY not in SaveConfig.SAVE_CONFIG
        ):
            dpi = Config.DPI
        else:
            dpi = SaveConfig.SAVE_CONFIG[SaveConfig.DPI_KEY]
        return dpi

    @staticmethod
    def get_y_axis_threshold() -> float:
        if (
            not SaveConfig.SAVE_CONFIG
            or SaveConfig.Y_AXIS_OFFSET_KEY not in SaveConfig.SAVE_CONFIG
        ):
            y_axis_threshold = Config.CROP_Y_AXIS_THRESHOLD
        else:
            y_axis_threshold = SaveConfig.SAVE_CONFIG[SaveConfig.Y_AXIS_OFFSET_KEY]
        return y_axis_threshold

    @staticmethod
    def get_default_save_location():
        if (
            not SaveConfig.SAVE_CONFIG
            or SaveConfig.PATH_KEY not in SaveConfig.SAVE_CONFIG
        ):
            return "C:"
        return (
            SaveConfig.SAVE_CONFIG[SaveConfig.PATH_KEY]
            or SaveConfig.read_default_dropbox_folder()
        )

    @staticmethod
    def get_author_db_path():
        if (
            not SaveConfig.SAVE_CONFIG
            or SaveConfig.AUTHOR_DB_PATH not in SaveConfig.SAVE_CONFIG
        ):
            return ""
        return SaveConfig.SAVE_CONFIG[SaveConfig.AUTHOR_DB_PATH]

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
