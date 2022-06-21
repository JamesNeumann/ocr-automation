from ui.steps.settings_step import SettingsStep
from utils.save_config import SaveConfig


class SettingsController:

    def __init__(self,
                 next_callback=None,
                 previous_callback=None
                 ):
        self.next_callback = next_callback
        self.previous_callback = previous_callback

        self.settings_step = SettingsStep(
            text="Einstellungen",
            next_callback=self.save_settings,
            previous_callback=self.previous_callback
        )

        self.update_values()

    def update_values(self):
        offset = SaveConfig.get_default_crop_box_offset()
        dpi = SaveConfig.get_dpi_value()
        y_axis_threshold = SaveConfig.get_y_axis_threshold()
        self.settings_step.update_crop_box(offset)
        self.settings_step.update_dpi(dpi)
        self.settings_step.update_y_axis_threshold(int(y_axis_threshold * 100))

    def save_settings(self):
        SaveConfig.update_all(self.settings_step.get_crop_box(), self.settings_step.get_dpi_value(),
                              self.settings_step.get_y_axis_threshold() / 100)
        self.next_callback()
