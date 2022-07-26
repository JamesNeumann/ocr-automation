import shutil

from utils.set_standard_metadata import set_standard_metadata


def save_pdf(old_path: str, new_path: str) -> None:
    if old_path != new_path:
        shutil.copy(old_path, new_path)
    set_standard_metadata(path_to_pdf=new_path)

