import glob
import os.path

from rich.traceback import install

from crop_pdf import get_crop_box

from optimize_pdf import optimize_pdf_in_abby
from utils.console import console

if __name__ == '__main__':
    install(show_locals=True)

    for file_path in glob.glob("./files/*.pdf"):
        min_x, min_y, max_x, max_y = get_crop_box(file_path)
        console.log("Calculated bounding box: ", min_x, min_y, max_x, max_y)
        abs_path = os.path.abspath(file_path)
        optimize_pdf_in_abby(abs_path, 10, min_x, min_y, max_x, max_y)
