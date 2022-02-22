import os

TEMP_PATH = os.environ['USERPROFILE'] + "\\AppData\\Local\\Temp"
ABBY_AUTOMATION_TEMP_FOLDER = "AbbyAutomation"
ABBY_WORKING_DIR = os.path.join(TEMP_PATH, ABBY_AUTOMATION_TEMP_FOLDER)

ABBY_EXE_PATH = 'D:\\Software\\Abby Finereader 15\\ABBYY FineReader 15\\FineReader.exe'
ABBY_LNK_PATH = 'C:\\ProgramData\\Microsoft\Windows\\Start Menu\\Programs\\ABBYY FineReader PDF 15\\ABBYY FineReader PDF 15.lnk'
OPEN_INSTANCES = []
CURR_INSTANCE = None


def initialize_directories() -> None:
    if not os.path.exists(ABBY_WORKING_DIR):
        os.makedirs(ABBY_WORKING_DIR)
