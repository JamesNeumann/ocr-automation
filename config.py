import os

TEMP_PATH = os.environ["USERPROFILE"] + "\\AppData\\Local\\Temp"
OCR_AUTOMATION_TEMP_FOLDER = "OcrAutomation"
OCR_WORKING_DIR = os.path.join(TEMP_PATH, OCR_AUTOMATION_TEMP_FOLDER)

OCR_EDITOR_LNK_PATH = (
    '"C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\'
    'ABBYY FineReader PDF 15\\ABBYY FineReader 15 OCR-Editor.lnk"'
)

DPI = 600

VERSION = "1.0.0"


def initialize_directories() -> None:
    """
    Initializes needed directories
    """
    if not os.path.exists(OCR_WORKING_DIR):
        os.makedirs(OCR_WORKING_DIR)
