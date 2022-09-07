import uuid


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
