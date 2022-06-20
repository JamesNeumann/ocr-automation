import os


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

    VERSION = "1.0.0"

    STOP_STUCK_RUNNING = False

    @staticmethod
    def initialize_directories() -> None:
        """
        Initializes needed directories
        """
        if not os.path.exists(Config.OCR_WORKING_DIR):
            os.makedirs(Config.OCR_WORKING_DIR)
