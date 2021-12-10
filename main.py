import glob

from rich.traceback import install

from cut_pdf import cut_pdf

from convert_pdf import convert_pdfs_to_images
from utils.console import console

if __name__ == '__main__':
    install(show_locals=True)
    for file_path in glob.glob("./files/*.pdf"):
        cut_pdf(file_path)
