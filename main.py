import ctypes
import sys

from PyQt6 import QtCore
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from cv2 import cv2
from rich.traceback import install

from config import initialize_directories, VERSION
from ui.main import MainWindow
from utils.analyze_pdf import get_pdf_pages_as_images, get_crop_boxes
from utils.console import console
from utils.save_config import SaveConfig
from utils.screen import Screen


def test():
    images, width, height, index = get_pdf_pages_as_images(
        "./files/Lorem ipsum dolor sit amet OCR.pdf", lambda value: None
    )

    rectangles, max_rectangle = get_crop_boxes(images, lambda value: None)

    for i, image in enumerate(images):
        centered_rectangle = rectangles[i].move_to_center(max_rectangle)

        centered_rectangle.x = int(centered_rectangle.x)
        centered_rectangle.y = int(centered_rectangle.y)
        # cv2.rectangle(image, (max_rectangle.x, max_rectangle.y),
        #               (max_rectangle.x + max_rectangle.width,
        #                max_rectangle.y + max_rectangle.height), (0, 200, 200),
        #               3)
        # cv2.rectangle(image, (centered_rectangle.x, centered_rectangle.y),
        #               (centered_rectangle.x + centered_rectangle.width,
        #                centered_rectangle.y + centered_rectangle.height), (0, 0, 200),
        #               3)

        cv2.imwrite(f"converted_files/temp_{i}.png", image)


def main():
    install(show_locals=True)

    app_id = "jamesneumann.OcrAutomation.v" + VERSION
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    SaveConfig.init()

    Screen.set_screen_resolution_string()
    initialize_directories()
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("./images/icon.ico"))
    window = MainWindow()
    MainWindow.setWindowFlags(
        window,
        QtCore.Qt.WindowType.WindowCloseButtonHint
        | QtCore.Qt.WindowType.WindowMinimizeButtonHint,
    )

    window.show()

    app.exec()


if __name__ == "__main__":
    main()
    # test()
