from uuid import UUID

from PyQt6.QtWidgets import QWidget, QStackedLayout, QMainWindow

from automation.abby_automation import AbbyAutomation
from ui.steps.crop_amount_step import CropAmountStep
from ui.steps.crop_running_step import CropRunningStep
from ui.steps.file_selection_step import FileSelectionStep
from ui.steps.ocr_language_selection_step import OcrLanguageSelectionStep
from ui.steps.ocr_running_step import OcrRunningStep
from ui.steps.open_abby_step import OpenAbbyStep
from ui.steps.procedure_selection_step import ProcedureSelectionStep
from ui.steps.step import Step


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Abby Automation")
        self.resize(1024, 800)

        self.layout = QStackedLayout()
        self.file_selection_step = FileSelectionStep(text="Wähle eine PDF-Datei aus:",
                                                     next_callback=self.open_abby_and_ocr_editor)

        self.open_abby_step = OpenAbbyStep(
            text="Es wird gewartet, bis Abby und der OCR-Editor vollständig geöffnet wurde",
            detail="Der nächste Schritt öffnet sich automatisch",
            previous_callback=lambda: self.layout.setCurrentIndex(0)
        )
        self.open_abby_step.finished_signal.connect(self.open_procedure_step)

        self.procedures_step = ProcedureSelectionStep(
            text="Welche Optimierungen sollen durchgeführt werden?",
            next_callback=self.do_optimization
        )

        self.procedures_step.finished.connect(lambda file_name: self.open_crop_step(file_name))

        self.crop_amount_step = CropAmountStep(
            text="Wie soll die PDF zugeschnitten werden?",
            next_callback=self.crop_pdf
        )

        self.crop_running_step = CropRunningStep(
            text="Die PDF wird zugeschnitten"
        )
        self.crop_running_step.finished.connect(lambda: self.layout.setCurrentIndex(5))

        self.ocr_language_selection_step = OcrLanguageSelectionStep(
            text="Wähle die OCR-Sprachen für die PDF",
            next_callback=self.do_ocr
        )

        self.ocr_running_step = OcrRunningStep(text="OCR läuft")
        self.ocr_running_step.finished.connect(lambda: (print("finished"), self.layout.setCurrentIndex(7)))

        self.finished_step = Step(text="Alle Schritte abgeschlossen. Die PDF kann nun gespeichert werden.")

        self.layout.addWidget(self.file_selection_step)
        self.layout.addWidget(self.open_abby_step)
        self.layout.addWidget(self.procedures_step)
        self.layout.addWidget(self.crop_amount_step)
        self.layout.addWidget(self.crop_running_step)
        self.layout.addWidget(self.ocr_language_selection_step)
        self.layout.addWidget(self.ocr_running_step)
        self.layout.addWidget(self.finished_step)

        self.layout.setCurrentIndex(0)

        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)
        self.rectangle = None

    def open_abby_and_ocr_editor(self):
        if self.file_selection_step.file_selection.selected_file_name != "":
            self.open_abby_step.set_pdf_path(self.file_selection_step.file_selection.file_path())
            self.layout.setCurrentIndex(1)
            self.open_abby_step.start()

    def open_crop_step(self, file_name: UUID):
        self.layout.setCurrentIndex(3)
        self.crop_amount_step.open_pdf_pages(f"{AbbyAutomation.TEMP_PATH}\\{str(file_name)}.pdf")

    def crop_pdf(self):
        self.crop_running_step.start(self.crop_amount_step.path_to_pdf,
                                     self.crop_amount_step.crop_amount_selection.get_pts_rectangle())
        self.layout.setCurrentIndex(4)

    def open_ocr_editor(self):
        AbbyAutomation.open_ocr_editor()
        self.layout.setCurrentIndex(2)

    def open_image_improvement_tools(self):
        AbbyAutomation.open_image_improvement_tools()
        self.do_optimization()
        self.layout.setCurrentIndex(3)

    def open_procedure_step(self):
        self.layout.setCurrentIndex(2)
        self.window().activateWindow()

    def do_optimization(self):
        self.procedures_step.start()

    def do_ocr(self):
        self.layout.setCurrentIndex(6)
        languages = self.ocr_language_selection_step.get_selected_language()
        self.ocr_running_step.start(languages)
