import glob
import os.path

from rich.traceback import install

from cut_pdf import cut_pdf

from convert_pdf import convert_pdfs_to_images
from optimize_pdf import optimize_pdf_in_abby
from utils.console import console

if __name__ == '__main__':
    install(show_locals=True)

    for file_path in glob.glob("./files/*.pdf"):

        min_x, min_y, max_x, max_y = cut_pdf(file_path)

        print(min_x, min_y, max_x, max_y)
        print(file_path)
        abs_path = os.path.abspath(file_path)
        print(abs_path)
        optimize_pdf_in_abby(abs_path, 10, min_x, min_y, max_x, max_y)

