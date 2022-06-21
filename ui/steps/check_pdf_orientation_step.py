from typing import List

from ui.steps.step import Step


class CheckPdfOrientationStep(Step):
    def __init__(
        self,
        *,
        text: str,
        previous_text="Zurück",
        previous_callback=None,
        next_text="Weiter",
        next_callback=None,
        detail: str = "",
    ):
        super().__init__(
            text=text,
            previous_text=previous_text,
            previous_callback=previous_callback,
            next_text=next_text,
            next_callback=next_callback,
            detail=detail,
        )

        self.indices = []

    def set_indices(self, indices: List[int]):
        self.indices = indices
        string_indices = [str(index + 1) for index in self.indices]
        self.label.setText(
            f'<h1>Folgende Seiten müssen gedreht werden: {", ".join(string_indices)}</h1>'
        )

    def reset(self):
        self.label.setText(f"Es müssen keine Seiten gedreht werden")
