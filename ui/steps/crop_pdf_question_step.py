from ui.steps.step import Step


class CropPdfQuestionStep(Step):
    def __init__(
            self,
            *,
            text: str,
            previous_text="Nein",
            previous_callback,
            next_text="Ja",
            next_callback,
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
