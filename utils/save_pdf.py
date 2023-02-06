import shutil

from utils.set_metadata import set_standard_metadata, Metadata


def save_pdf(old_path: str, new_path: str, metadata: Metadata) -> None:
    if old_path != new_path:
        shutil.copy(old_path, new_path)
    print(metadata.creator)
    set_standard_metadata(path_to_pdf=new_path, metadata=metadata)
