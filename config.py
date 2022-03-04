import os

TEMP_PATH = os.environ['USERPROFILE'] + "\\AppData\\Local\\Temp"
FINEREADER_AUTOMATION_TEMP_FOLDER = "FineReaderAutomation"
FINEREADER_WORKING_DIR = os.path.join(TEMP_PATH, FINEREADER_AUTOMATION_TEMP_FOLDER)

FINEREADER_LNK_PATH = 'C:\\ProgramData\\Microsoft\Windows\\Start Menu\\Programs\\ABBYY FineReader PDF 15\\ABBYY FineReader PDF 15.lnk'
OCR_EDITOR_LNK_PATH = '"C:\\ProgramData\\Microsoft\Windows\\Start Menu\\Programs\\ABBYY FineReader PDF 15\\ABBYY FineReader 15 OCR-Editor.lnk"'

VERSION = "1.0.2"


def initialize_directories() -> None:
    """
    Initializes needed directories
    """
    if not os.path.exists(FINEREADER_WORKING_DIR):
        os.makedirs(FINEREADER_WORKING_DIR)
