class Store:
    SELECTED_FILE_PATH = ""
    FILE_PATH_AFTER_PROCEDURES = ""
    FILE_PATH_AFTER_ORIENTATION_SAVE = ""
    INDICES_TO_ROTATE = []
    PDF_APPLICATION_PROCESS = None
    SAVE_FILE_PATH = ""
    IMAGE_EDIT_TOOL_OPEN = False
    CROPPED_PDF_PATH = ""
    FBT_FILE_PATH = ""

    @staticmethod
    def reset():
        Store.SELECTED_FILE_PATH = ""
        Store.FILE_PATH_AFTER_PROCEDURES = None
        Store.INDICES_TO_ROTATE = []
        Store.FILE_PATH_AFTER_ORIENTATION_SAVE = ""
        Store.PDF_APPLICATION_PROCESS = None
        Store.SAVE_FILE_PATH = ""
        Store.IMAGE_EDIT_TOOL_OPEN = False
        Store.CROPPED_PDF_PATH = ""
        Store.FBT_FILE_PATH = ""