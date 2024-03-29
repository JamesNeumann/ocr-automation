import os

from utils.offset import Offset


class Config:
    TEMP_PATH = os.environ["USERPROFILE"] + "\\AppData\\Local\\Temp"
    OCR_AUTOMATION_TEMP_FOLDER = "OcrAutomation"
    OCR_WORKING_DIR = os.path.join(TEMP_PATH, OCR_AUTOMATION_TEMP_FOLDER)

    OCR_EDITOR_LNK_PATH = (
        '"C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\'
        'ABBYY FineReader PDF 15\\ABBYY FineReader 15 OCR-Editor.lnk"'
    )

    DPI = 600

    CROP_Y_AXIS_THRESHOLD = 0.95

    MIN_DPI = 72
    MAX_DPI = 900

    VERSION = "1.3.5"

    STOP_STUCK_RUNNING = False

    MIN_PEN_WIDTH = 3
    MAX_PEN_WIDTH = 50

    DEFAULT_CROP_BOX_OFFSET = Offset(top=5, right=5, bottom=10, left=5)

    IMAGE_SETTINGS_ENABLED = None
    METADATA_IS_ENABLED = False
    PREVIOUS_RUN_WAS_COMPLETE_PROCEDURE = None

    AUTHOR_DB_NAME = "authors.sqlite"

    @staticmethod
    def initialize_directories() -> None:
        """
        Initializes needed directories
        """
        if not os.path.exists(Config.OCR_WORKING_DIR):
            os.makedirs(Config.OCR_WORKING_DIR)

    @staticmethod
    def map_dpi_to_pen_width(dpi_value: int):
        return round(
            Config.MIN_PEN_WIDTH
            + (dpi_value - Config.MIN_DPI)
            * (Config.MAX_PEN_WIDTH - Config.MIN_PEN_WIDTH)
            / (Config.MAX_DPI - Config.MIN_DPI)
        )
