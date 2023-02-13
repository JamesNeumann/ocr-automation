import json
import os
import uuid
import glob
from typing import Dict

from utils.console import console
from utils.file_utils import slugify

OCR_DEFAULT_ERROR_REPLACEMENTS_KEY = "ocr_default_error_replacements"


def create_new_default_error_replacement_map():
    return {"id": str(uuid.uuid4()), "name": "Standard", "map": []}


standard_ocr_default_error_replacement_map = {
    "id": "1",
    "name": "Standard",
    "map": [
        ["-^l", "¬^l"],
        ["§", "ę"],
        ["$", "ę"],
        ["%", ""],
        ["&", ""],
        ["^", "ę"],
        ["?", "ę"],
        ["{", "("],
        ["0.", "O."],
        ["» ", ", "],
        ["»", "„"],
        ["<", ""],
        ["«", "."],
        ["IL", "II."],
        ["IH", "III"],
        ["HI", "III"],
        ["VH", "VII"],
        ["XH", "XII"],
        ["XL", "XI."],
        ["XU", "XII"],
        ["H.", "II."],
        ["H,", "II."],
        ["UI", "III"],
        ["IU", "III"],
        ["8.", "S."],
        ["à", "d"],
        ["Bibi", "Bibl"],
        ["vergi", "vergl"],
        ["vergL", "vergl."],
        ["vgL", "vgl."],
        ["sdi", "sch"],
        ["Mise.", "Misc."],
        ["stör.", "stor."],
        ["stör,", "stor."],
        ["tarnen", "tamen"],
    ],
}


def load_all_ocr_default_error_replacement_maps():
    files = glob.glob("ocr_default_error_replacement/*.json")
    maps = []
    for file in files:
        with open(file) as f:
            maps.append(json.load(f))
    maps.sort(key=lambda x: len(x["id"]))
    return maps


def save_ocr_default_error_replacement_map(replacement_map: Dict):
    file_name = slugify("save-" + replacement_map["name"]) + ".json"
    with open("ocr_default_error_replacement/" + file_name, "w") as f:
        json.dump(replacement_map, f)


def delete_ocr_default_error_replacement_map(replacement_map: Dict):
    file_name = slugify(replacement_map["name"])
    file_path = f"ocr_default_error_replacement/save-{file_name}.json"
    if os.path.exists(file_path):
        os.remove(file_path)


def ocr_default_error_replacement_map_exists(replacement_map: Dict):
    file_name = slugify(replacement_map["name"])
    file_path = f"ocr_default_error_replacement/save-{file_name}.json"
    return os.path.exists(file_path)


def upsert_ocr_default_error_replacement_map(replacement_map: Dict):
    maps = load_all_ocr_default_error_replacement_maps()
    for saved_map in maps:
        if (
            saved_map["name"] == replacement_map["name"]
            and saved_map["id"] != replacement_map["id"]
        ):
            return False
        if saved_map["id"] == replacement_map["id"]:
            delete_ocr_default_error_replacement_map(saved_map)
            break
    save_ocr_default_error_replacement_map(replacement_map)
    return True
