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
    keyboard.press_and_release('alt+ß')
    keyboard.write(str("1"))
    keyboard.press_and_release('tab')
    keyboard.write(str("1"))
    keyboard.press_and_release('alt+a')
    keyboard.write(str("0"))
    keyboard.press_and_release('tab')
    keyboard.write(str("0"))

    keyboard.press_and_release('alt+ß')
    keyboard.press_and_release('ctrl+a')
    keyboard.write(str(math.floor(width)))
    keyboard.press_and_release('tab')
    keyboard.press_and_release('ctrl+a')
    keyboard.write(str(math.floor(height)))
    keyboard.press_and_release('alt+a')
    keyboard.press_and_release('ctrl+a')
    keyboard.write(str(math.ceil(x)))
    keyboard.press_and_release('tab')
    keyboard.press_and_release('ctrl+a')

    keyboard.write(str(math.ceil(y)))
    keyboard.press_and_release('alt+shift+.')
    keyboard.press_and_release('down')
    keyboard.press_and_release('down')
    keyboard.press_and_release('down')
    keyboard.press_and_release('alt+e')
