from typing import Dict

from ui.components.ocr_default_error_replacement.ocr_default_error_replacement_settings import (
    OcrDefaultErrorReplacementSettings,
)
from utils.console import console
from utils.ocr_default_error_replacement import create_new_default_error_replacement_map
from utils.save_config import SaveConfig


class OcrDefaultErrorReplacementSettingsController:
    def __init__(self):
        self.settings = OcrDefaultErrorReplacementSettings(
            edit_callback=self.edit_button_clicked,
            delete_callback=self.delete_button_clicked,
            edit_back_callback=self.edit_back_button_clicked,
            edit_save_callback=self.edit_save_button_clicked,
            delete_entry_callback=self.delete_entry_callback,
            create_new_callback=self.create_new_callback,
        )

    def edit_button_clicked(self, replacement_map: Dict):
        self.settings.edit.set_replacement_map(replacement_map)
        self.settings.layout.setCurrentIndex(1)

    def delete_button_clicked(self, replacement_map: Dict):
        console.log(replacement_map)

    def edit_back_button_clicked(self):
        self.settings.layout.setCurrentIndex(0)

    def edit_save_button_clicked(self, updated_replacement_map: Dict):
        SaveConfig.update_replacement_map(updated_replacement_map)
        self.settings.list.reload()
        self.settings.layout.setCurrentIndex(0)

    def delete_entry_callback(self, index):
        console.log(index)

    def create_new_callback(self):
        replacement_map = create_new_default_error_replacement_map()
        self.settings.edit.set_replacement_map(replacement_map)
        self.settings.layout.setCurrentIndex(1)
