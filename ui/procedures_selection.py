from typing import List

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QGroupBox, QCheckBox, QVBoxLayout, QHBoxLayout, QLabel, QSlider

from automation.procedures import Procedures


class ProcedureSelection(QWidget):

    def __init__(self):
        super().__init__()

        self.procedures_group_box = QGroupBox()
        self.iterations_group_box = QGroupBox()

        self.vbox_layout = QVBoxLayout()

        for name, procedure in Procedures.get_available_procedures().items():
            checkbox = QCheckBox(name)
            self.vbox_layout.addWidget(checkbox)

        self.vbox_layout.addStretch(1)
        self.procedures_group_box.setLayout(self.vbox_layout)

        self.parent_vbox = QVBoxLayout()
        self.parent_vbox.addSpacing(15)
        self.parent_vbox.addWidget(self.procedures_group_box)

        self.iterations_vbox = QVBoxLayout()

        self.iteration_label = QLabel("Wie viele Iterationen sollen durchgeführt werden?")
        self.iterations_vbox.addWidget(self.iteration_label)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(20)
        self.slider.setTickInterval(1)
        self.slider.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.slider.valueChanged.connect(self.update_label)

        self.slider_hbox = QHBoxLayout()
        self.slider_hbox.addWidget(self.slider)
        self.slider_hbox.addStretch()
        self.slider_label = QLabel("1")
        self.slider_hbox.addWidget(self.slider_label)
        self.iterations_vbox.addLayout(self.slider_hbox)

        self.iterations_group_box.setLayout(self.iterations_vbox)

        self.parent_vbox.addWidget(self.iterations_group_box)
        self.setLayout(self.parent_vbox)

    def update_label(self, value):
        self.slider_label.setText(str(value))

    def get_selected_procedures(self) -> List[str]:
        checked_procedures = []
        for checkbox in self.procedures_group_box.findChildren(QCheckBox):
            if checkbox.isChecked():
                checked_procedures.append(checkbox.text())
        return checked_procedures

    def get_iteration_amount(self) -> int:
        return self.slider.value()
