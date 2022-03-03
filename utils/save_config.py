import json
import os.path

from utils.console import console


class SaveConfig:
    STANDARD_SAVE_LOCATION = ''

    @staticmethod
    def init():
        SaveConfig.STANDARD_SAVE_LOCATION = SaveConfig.read_default_dropbox_folder() \
                                            or SaveConfig.read_saved_folder_path() \
                                            or os.path.abspath("C:")

    @staticmethod
    def save_folder_path(path_to_folder: str):
        console.log("Saving path...")
        with open('path.save', 'w+', encoding='utf-8') as f:
            f.write(path_to_folder)

    @staticmethod
    def read_saved_folder_path():
        try:
            with open('path.save', 'r', encoding='utf-8') as f:
                path = os.path.abspath(f.read())
                console.log("Save file found. Path:", path)
                return path
        except FileNotFoundError:
            console.log("Did not find save file. Skipping...")
            return None

    @staticmethod
    def read_default_dropbox_folder():
        app_data = os.getenv('APPDATA')
        path = os.path.join(app_data, "Dropbox\\info.json")
        try:
            with open(path, 'r') as f:
                dropbox_info = json.load(f)
                if 'personal' in dropbox_info:
                    if 'path' in dropbox_info['personal']:
                        return os.path.abspath(
                            os.path.join(dropbox_info['personal']['path'], '00 Petersen\\00 Digitalisierung MGH'))
                if 'business' in dropbox_info:
                    if 'path' in dropbox_info['business']:
                        return os.path.abspath(
                            os.path.join(dropbox_info['business']['path'], '00 Petersen\\00 Digitalisierung MGH'))
            console.log("Dropbox path not found. Skipping...")
            return None
        except FileNotFoundError:
            console.log("Dropbox path not found. Skipping...")
            return None
