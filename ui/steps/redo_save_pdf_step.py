from ui.steps.step import Step


class RedoSavePdfStep(Step):
    def __init__(
        self,
        *,
        text="Soll die PDF nochmal gespeichert werden?",
        previous_text="PDF erneut speichern",
        previous_callback=None,
        next_text="Überspringen",
        next_callback=None,
        detail: str = ""
    ):
        super().__init__(
            text=text,
            previous_text=previous_text,
            previous_callback=previous_callback,
            next_text=next_text,
            next_callback=next_callback,
            detail=detail,
        )
