from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel

from ui.components.navigation_button import NavigationButton


class Step(QWidget):
    def __init__(
        self,
        *,
        text: str,
        previous_text="Zurück",
        previous_callback=None,
        next_text="Weiter",
        next_callback=None,
        detail: str = "",
        optional_button_text="",
        optional_button_callback=None,
    ):
        super().__init__()
        self.text = text
        self.layout = QGridLayout()
        self.header = f"<h1 >{self.text}</h1>"
        self.label = QLabel(self.header)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(
            self.label, 1, 0, 1, 4, alignment=Qt.AlignmentFlag.AlignCenter
        )
        detail = f"<p>{detail}</p>"
        self.layout.addWidget(
            QLabel(detail), 2, 0, 1, 4, alignment=Qt.AlignmentFlag.AlignCenter
        )
        if optional_button_callback:
            self.optional_button = NavigationButton(
                optional_button_text, 0, 0, 100, 100
            )
            self.optional_button.clicked.connect(optional_button_callback)
            self.layout.addWidget(self.optional_button, 6, 1)

        if previous_callback:
            self.previous_callback = previous_callback
            self.previous_button = NavigationButton(previous_text, 10, 10, 100, 100)
            self.previous_button.clicked.connect(self._previous_callback)
            self.layout.addWidget(self.previous_button, 6, 2)

        if next_callback:
            self.next_button = NavigationButton(next_text, 150, 150, 100, 100)
            self.next_button.clicked.connect(next_callback)
            self.layout.addWidget(self.next_button, 6, 3)

        self.setLayout(self.layout)

    def _previous_callback(self):
        self.previous_callback()
        self.close()

    def reset(self):
        pass

    def close(self):
        pass
