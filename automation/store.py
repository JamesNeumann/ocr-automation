class Store:
    SELECTED_FILE_PATH = ''
    FILE_PATH_AFTER_PROCEDURES = ''
    FILE_PATH_AFTER_ORIENTATION_SAVE = ''
    INDICES_TO_ROTATE = []

    @staticmethod
    def reset():
        Store.SELECTED_FILE_PATH = ''
        Store.FILE_PATH_AFTER_PROCEDURES = None
        Store.INDICES_TO_ROTATE = []
        Store.FILE_PATH_AFTER_ORIENTATION_SAVE = ''
