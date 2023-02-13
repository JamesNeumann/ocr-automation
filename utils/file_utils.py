import os
import re
import time
from time import sleep

import unicodedata

from utils.console import console


def is_file_locked(file_path):
    """
    Checks to see if a file is locked. Performs three checks
        1. Attempts to open the file for reading. This will determine if the file has a write lock.
            Write locks occur when the file is being edited or copied to, e.g. a file copy destination
        2. Attempts to rename the file. If this fails the file is open by some other process for reading. The
            file can be read, but not written to or deleted.
    """
    try:
        f = open(file_path, "r")
        f.close()
    except IOError:
        return True

    lock_file = file_path + ".lckchk"
    if os.path.exists(lock_file):
        os.remove(lock_file)
    try:
        os.rename(file_path, lock_file)
        sleep(1)
        os.rename(lock_file, file_path)
        return False
    except WindowsError:
        return True


def wait_until_file_is_unlocked(file_path) -> None:
    """
    Waits until file is unlocked
    :param file_path: Path to the file to check
    """
    while is_file_locked(file_path):
        console.log("Datei ist gesperrt. Wartet...")
        time.sleep(0.1)


def delete_file(file_path: str) -> None:
    """
    Deletes the given file
    :param file_path:  Path to the file
    """
    wait_until_file_is_unlocked(file_path)
    os.remove(file_path)


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")
