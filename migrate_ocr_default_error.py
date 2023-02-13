import glob
import json
import os

from utils.console import console
from utils.file_utils import slugify
from utils.ocr_default_error_replacement import (
    save_ocr_default_error_replacement_map,
    OCR_DEFAULT_ERROR_REPLACEMENTS_KEY,
)


def migrate():
    save_files = [
        os.path.basename(x) for x in glob.glob("ocr_default_error_replacement/*.json")
    ]
    if not os.path.exists("save.json"):
        console.log("Speicherdatei existiert nicht. Überspringe migration...")
        return False
    with open("save.json") as f:
        save_data = json.load(f)
        if not OCR_DEFAULT_ERROR_REPLACEMENTS_KEY in save_data:
            console.log("Keine Standardfehlerlisten gefunden. Überspringe migration...")
            return False
        ocr_error_maps = save_data[OCR_DEFAULT_ERROR_REPLACEMENTS_KEY]
        for error_map in ocr_error_maps:
            error_map_name = error_map["name"]
            slugged_name = slugify("save-" + error_map_name)
            if slugged_name + ".json" not in save_files:
                for i in range(len(error_map["map"])):
                    if "Löschen" in error_map["map"][i]:
                        error_map["map"][i].remove("Löschen")
                save_ocr_default_error_replacement_map(error_map)
                console.log("Gespeichert: ", slugged_name)
            else:
                console.log("Existiert bereits:", slugged_name)
    return True

if __name__ == "__main__":
    migrate()
