import math
import subprocess
import time

from utils.keyboard_util import press_key, write


def crop_pdf_in_ocr_editor(*, path_to_pdf: str, x: float, y: float, width: float,
                           height: float) -> None:
    """
    Opens the given path to the pdf in abby and crops each page by the given rectangle.

    :param path_to_pdf: Path leading to the PDF
    :param x: x position of crop rectangle
    :param y: y position of crop rectangle
    :param height: Height of the crop rectangle
    :param width: Width of the crop rectangle
    """
    abby_exe = 'D:\\Software\\Abby Finereader 15\\ABBYY FineReader 15\\FineReader.exe'

    subprocess.Popen([abby_exe, path_to_pdf])
    time.sleep(5)
    press_key(key_combination='shift+alt+1', repetitions=2)

    press_key(key_combination='alt+e+a', delay=10)

    press_key(key_combination='ctrl+i', delay=5)

    press_key(key_combination='alt+c')

    write_crop_values(1, 1, 0, 0)
    write_crop_values(math.floor(width), math.floor(height), math.ceil(x), math.ceil(y))

    press_key(key_combination='alt+shift+.')
    press_key(key_combination='down', repetitions=3)

    press_key(key_combination='alt+e', delay=1)
    press_key(key_combination='enter')


def write_crop_values(width: int, height: int, x: int, y: int):
    """
    Writes the give crop values into the input fields of the ocr editor

    :param width: Width of the crop rectangle
    :param height: Height of the crop rectangle
    :param x: x-offset of the crop rectangle
    :param y: y-offset of the crop rectangle
    """

    # Width
    press_key(key_combination='alt+ß')
    press_key(key_combination='ctrl+a')
    write(width, 0.1)

    # Height
    press_key(key_combination='enter')
    write(height, 0.1)

    # X
    press_key(key_combination='enter')
    write(x, 0.1)

    # Y
    press_key(key_combination='enter')
    write(y, 0.1)

    press_key(key_combination='enter')
