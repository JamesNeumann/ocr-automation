from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel

from ui.navigation_button import NavigationButton


class Step(QWidget):
    def __init__(self, *, text: str, previous_text="Zurück", previous_callback=None, next_text="Weiter",
                 next_callback=None, detail: str = ""):
        super().__init__()

        self.layout = QGridLayout()
        header = f'<h1 >{text}</h1>'
        label = QLabel(header)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(label, 1, 0, 1, 4)
        detail = f'<p>{detail}</p>'
        self.layout.addWidget(QLabel(detail), 2, 2)

        if previous_callback:
            self.previous_button = NavigationButton(previous_text, 10, 10, 100, 100)
            self.previous_button.clicked.connect(previous_callback)
            self.layout.addWidget(self.previous_button, 5, 2)

        if next_callback:
            self.next_button = NavigationButton(next_text, 150, 150, 100, 100)
            self.next_button.clicked.connect(next_callback)
            self.layout.addWidget(self.next_button, 5, 3)

        self.setLayout(self.layout)


