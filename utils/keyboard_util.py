import time
from typing import Any

import keyboard


def write(text: Any, delay: float = 0.0):
    """
    Writes given text via keyboard presses
    :param text: Text to be written
    :param delay: Time to wait after text was written
    """
    keyboard.write(str(text))
    if delay > 0.0:
        time.sleep(delay)


def press_key(*, key_combination: str, repetitions: int = 1, delay_in_seconds: float = 0):
    """
    Presses the given key combination. To press multiple key simultaneous combine them with `+`.

    :param key_combination: The keys to be pressed
    :param repetitions: How often they should be pressed
    :param delay_in_seconds: Time to wait after each key press
        """
    for i in range(repetitions):
        keyboard.press_and_release(key_combination)
        if delay_in_seconds > 0.0:
            time.sleep(delay_in_seconds)
