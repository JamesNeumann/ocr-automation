import glob
import json
import os

from utils.console import console
from utils.file_utils import slugify
from utils.ocr_default_error_replacement import (
    save_ocr_default_error_replacement_map,
    OCR_DEFAULT_ERROR_REPLACEMENTS_KEY,
)
from utils.save_config import SaveConfig

def migrate():
    save_files = [
        os.path.basename(x) for x in glob.glob("ocr_default_error_replacement/*.json")
    ]
    with open("save.json") as f:
        save_data = json.load(f)
        ocr_error_maps = save_data[OCR_DEFAULT_ERROR_REPLACEMENTS_KEY]
        for error_map in ocr_error_maps:
            error_map_name = error_map["name"]
            slugged_name = slugify("save-" + error_map_name)
            if slugged_name + ".json" not in save_files:
                for i in range(len(error_map["map"])):
                    if "Löschen" in error_map["map"][i]:
                        error_map["map"][i].remove("Löschen")
                save_ocr_default_error_replacement_map(error_map)
                console.log("Saved: ", slugged_name)
            else:
                console.log("Already exists:", slugged_name)

if __name__ == "__main__":
    migrate()
