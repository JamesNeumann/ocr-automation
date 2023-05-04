from ui.steps.step import Step


class GrayscaleInfo(Step):
    def __init__(
        self,
        *,
        text: str = "Das Bild enthält Graustufen?",
        previous_text="Nicht umwandeln",
        previous_callback=None,
        next_text="In Schwarzweiß umwandeln",
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
