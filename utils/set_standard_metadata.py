from datetime import datetime
from pathlib import Path

import pytz
from PyPDF2 import PdfReader, PdfWriter

from utils.console import console


def set_standard_metadata(path_to_pdf: str) -> None:
    """
    Sets the standard PDF metadata. Removes all existing data

    :param path_to_pdf: Path to the PDF
    """

    pdf_reader = PdfReader(path_to_pdf)
    pdf_reader.getXmpMetadata()
    writer = PdfWriter()
    writer.appendPagesFromReader(pdf_reader)

    curr_date = datetime.utcnow()
    timezone = pytz.timezone("Europe/Berlin")
    timezone_date = timezone.localize(curr_date)
    utc_offset = timezone_date.utcoffset()
    utc_offset = utc_offset.seconds // 3600
    metadata_time_string = f"D:{curr_date.strftime('%Y%m%d%H%M%S')}+0{utc_offset}'00'"

    file_name = Path(path_to_pdf).stem

    new_metadata = {
        "/Creator": "BE4-BDLK2-V2",
        "/Title": file_name,
        "/ModDate": "",
        "/CreationDate": metadata_time_string,
        "/Producer": "ABBYY FineReader PDF 15 and OCR Automation by Jannes Neemann",
    }
    writer.addMetadata(new_metadata)

    writer.write(path_to_pdf)

    console.log(f"Metadaten wurden für '{file_name}' gesetzt")
