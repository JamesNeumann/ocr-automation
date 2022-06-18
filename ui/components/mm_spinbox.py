from PyQt6.QtWidgets import QSpinBox


def create_mm_spinbox(*, default_value=0.0) -> QSpinBox:
    spinbox = QSpinBox()
    spinbox.setSuffix(" mm")
    spinbox.setMinimum(-9999)
    spinbox.setMaximum(9999)
    spinbox.setValue(default_value)
    return spinbox
