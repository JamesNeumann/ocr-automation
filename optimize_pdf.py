import math
import os
import subprocess
import time

import keyboard

from utils.console import console


def optimize_pdf_in_abby(path_to_pdf: str, iterations: int, x: float, y: float, width: float, height: float) -> None:
    """
    Opens the given PDF in abby and runs multiple different optimizations on them.

    :param path_to_pdf: Path leading to the PDF
    :param iterations: How often the optimizations should be applied
    :param x: x position of crop rectangle
    :param y: y position of crop rectangle
    :param height: Height of the crop rectangle
    :param width: Width of the crop rectangle
    """
    abby_exe = 'D:\\Software\\Abby Finereader 15\\ABBYY FineReader 15\\FineReader.exe'
    # abby_exe = "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\ABBYY FineReader PDF 15\\ABBYY FineReader 15 OCR-Editor.lnk"
    pid = subprocess.Popen([abby_exe, path_to_pdf]).pid
    console.log(pid)
    # os.startfile(abby_exe)
    time.sleep(5)
    keyboard.press_and_release('shift+alt+1')
    keyboard.press_and_release('shift+alt+1')

    keyboard.press_and_release('alt+e+a')
    time.sleep(10)
    keyboard.press_and_release('ctrl+i')
    time.sleep(5)

    keyboard.press_and_release('alt+c')

    write_crop_values(1, 1, 0, 0)
    write_crop_values(math.floor(width), math.floor(height), math.ceil(x), math.ceil(y))

    keyboard.press_and_release('alt+shift+.')
    keyboard.press_and_release('down')
    keyboard.press_and_release('down')
    keyboard.press_and_release('down')
    keyboard.press_and_release('alt+e')
    time.sleep(1)
    keyboard.press_and_release('enter')


def write_crop_values(width: int, height: int, x: int, y: int):
    # Width
    keyboard.press_and_release('alt+ß')
    keyboard.press_and_release('ctrl+a')
    keyboard.write(str(width))
    time.sleep(0.1)

    # Height
    keyboard.press_and_release('enter')
    keyboard.write(str(height))
    time.sleep(0.1)

    # X
    keyboard.press_and_release('enter')
    keyboard.write(str(x))
    time.sleep(0.1)
    # Y
    keyboard.press_and_release('enter')
    keyboard.write(str(y))
    time.sleep(0.1)
    keyboard.press_and_release('enter')
