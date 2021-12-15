import glob
import os.path

from rich.traceback import install

from automation.analyze_pdf import get_crop_box

from utils.console import console

if __name__ == '__main__':
    install(show_locals=True)

    for file_path in glob.glob("./files/*.pdf"):
        rectangle = get_crop_box(file_path, offset=80)
        console.print("Calculated bounding box: ", rectangle)
        abs_path = os.path.abspath(file_path)
        # crop_pdf_in_ocr_editor(path_to_pdf=abs_path, x=rectangle.x, y=rectangle.y, width=rectangle.width,
        #                       height=rectangle.height)
