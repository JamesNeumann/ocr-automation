from ui.procedures_selection import ProcedureSelection
from ui.steps.step import Step


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
