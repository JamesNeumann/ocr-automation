from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel

from ui.file_selection import FileSelection
from ui.navigation_button import NavigationButton
from ui.procedures_selection import ProcedureSelection
from ui.progress_bar import ProgressBar


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


class FileSelectionStep(Step):
    def __init__(self, *, text: str, previous_text="Zurück", previous_callback=None, next_text="Weiter",
                 next_callback=None, detail: str = ""):
        super().__init__(text=text,
                         previous_text=previous_text,
                         previous_callback=previous_callback,
                         next_text=next_text,
                         next_callback=next_callback, detail=detail)

        self.file_selection = FileSelection()
        self.layout.addWidget(self.file_selection, 2, 0, 2, 4)
        self.progress_bar = ProgressBar()
        self.progress_bar.hide()
        self.layout.addWidget(self.progress_bar, 3, 0, 3, 4)


class ProcedureSelectionStep(Step):
    def __init__(self, *, text: str, previous_text="Zurück", previous_callback=None, next_text="Weiter",
                 next_callback=None, detail: str = ""):
        super().__init__(
            text=text,
            previous_text=previous_text,
            previous_callback=previous_callback,
            next_text=next_text,
            next_callback=next_callback, detail=detail
        )
        self.procedure_selection = ProcedureSelection()
        self.layout.addWidget(self.procedure_selection, 2, 0, 2, 4)
