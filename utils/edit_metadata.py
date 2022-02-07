from datetime import datetime
from pathlib import Path

import pytz
from PyPDF2 import PdfFileReader, PdfFileWriter

from utils.console import console


def set_standard_metadata(path_to_pdf: str) -> None:
    """
    Sets the standard PDF metadata. Removes all existing data.
    :param path_to_pdf: Path to the PDF
    """
    console.log(path_to_pdf)

    file_in = open(path_to_pdf, 'rb')
    pdf_reader = PdfFileReader(file_in)
    pdf_reader.getXmpMetadata()
    writer = PdfFileWriter()
    writer.appendPagesFromReader(pdf_reader)
    metadata = pdf_reader.getDocumentInfo()
    console.log(metadata)

    curr_date = datetime.utcnow()
    timezone = pytz.timezone("Europe/Berlin")
    timezone_date = timezone.localize(curr_date)
    utc_offset = timezone_date.utcoffset()
    utc_offset = utc_offset.seconds // 3600

    writer.addMetadata({
        '/Creator': "BE4-BDLK2-V2",
        '/Title': Path(path_to_pdf).stem,
        '/ModDate': "",
        '/CreationDate': "D:" + curr_date.strftime("%Y%m%d%H%M%S") + f"+0{utc_offset}'00'",
        '/Producer': "libimg Image Output V6.92G (c) Image Access"
    })

    file_out = open(path_to_pdf, 'ab')
    writer.write(file_out)
    file_in.close()
    file_out.close()
