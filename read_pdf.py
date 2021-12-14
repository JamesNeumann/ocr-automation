import os.path
from os import listdir
from os.path import isfile, join
from pathlib import Path
from time import time
from typing import List

import cv2
import numpy
from PIL.Image import Image
from pdf2image import convert_from_path

import tempfile
import multiprocessing

poppler_path = r"D:\Projects\harry\00 Dateien für Programmierung Jannes\Poppler\Library\bin"
pdf_path = '../PDF-Dateien/Fanta, Ein Bericht über die Ansprüche des Königs Alfons auf den deutschen Thron.pdf'
folder_path = '../PDF-Dateien'

RECT_OFFSET = 50


def convert_by_temp(file_path) -> List[Image]:
    start_time = time()
    images_from_path = []
    try:
        with tempfile.TemporaryDirectory() as path:
            images_from_path = convert_from_path(file_path,
                                                 output_folder=path,
                                                 poppler_path=poppler_path,
                                                 thread_count=4)
            print(f"Needed {time() - start_time}s to convert {len(images_from_path)} pages in temporary directory")
    except PermissionError as permissionError:
        print(permissionError)
    except NotADirectoryError as notADirectoryError:
        print(notADirectoryError)
    return images_from_path


def convert_by_mem():
    start_time = time()
    images_from_path = convert_from_path(pdf_path,
                                         poppler_path=poppler_path,
                                         thread_count=multiprocessing.cpu_count())
    print(f"Needed {time() - start_time}s to convert {len(images_from_path)} pages in memory")


def convert_pil_to_c2v(pil_images: List[Image]):
    temp_open_cv_images = []
    for image in pil_images:
        open_cv_image = numpy.array(image)
        open_cv_image = open_cv_image[:, :, ::-1].copy()
        temp_open_cv_images.append(open_cv_image)
    return temp_open_cv_images


if __name__ == '__main__':
    # convert_by_mem()

    pdf_files = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]
    print(pdf_files)
    start_time = time()
    # pdf_files = [pdf_files[0]]
    # pdf_files = ['Fanta, Ein Bericht über die Ansprüche des Königs Alfons auf den deutschen Thron.pdf']
    for index, file in enumerate(pdf_files):
        file_name = os.path.splitext(file)[0]
        images = convert_by_temp(folder_path + '/' + file)
        print(f"Converting {file_name}...")
        open_cv_images = convert_pil_to_c2v(images)
        Path(folder_path + "/" + str(index)).mkdir(parents=True, exist_ok=True)
        # open_cv_images = [open_cv_images[4]]

        global_max_w = 0
        global_min_w = 999999
        global_max_h = 0
        global_min_h = 999999

        for i, image in enumerate(open_cv_images):
            print(f"Detect text image {i} of {len(open_cv_images)}")
            width = images[i].width
            height = images[i].height

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            kernelFactor = 100
            kernelWidth = int(width / kernelFactor)
            kernelHeight = int(height / kernelFactor)

            if kernelWidth % 2 == 0:
                kernelWidth -= 1
            if kernelHeight % 2 == 0:
                kernelHeight -= 1

            blur = cv2.GaussianBlur(gray, (kernelWidth, kernelHeight), 0)

            thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 10)

            # Dilate to combine adjacent text contours
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernelWidth, kernelHeight))
            erosion = cv2.erode(thresh, (100, 100), iterations=12)
            dilate = cv2.dilate(erosion, kernel, iterations=4)
            # dilate = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            # dilate = cv2.erode(thresh, kernel, iterations=4)

            cnts = cv2.findContours(dilate, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[0] if len(cnts) == 2 else cnts[1]

            min_x = width
            max_x = 0
            min_y = height
            max_y = 0

            print(width, height)

            for j, c in enumerate(cnts):
                area = cv2.contourArea(c)
                if area > 2000:
                    x, y, w, h = cv2.boundingRect(c)
                    if x < min_x:
                        min_x = x
                    if x + w > max_x:
                        max_x = x + w
                    if y < min_y:
                        min_y = y
                    if y + h > max_y:
                        max_y = y + h

            if min_x < global_min_w:
                global_min_w = min_x

            if min_y < global_min_w:
                global_min_h = min_y

            if max_x > global_max_w:
                global_max_w = max_x

            if max_y > global_max_h:
                global_max_h = max_y

                # cv2.rectangle(image, (x, y), (x + w, y + h), (36, 255, 12), 3)
            cv2.drawContours(image, cnts, -1, (0, 0, 255), 3)

            cv2.rectangle(image, (min_x, min_y), (max_x, max_y),
                          (36, 255, 12), 3)

            # cv2.imshow('thresh', thresh)
            # cv2.imshow('dilate', dilate)
            # cv2.imshow('erode', erosion)

            # cv2.waitKey()

        print(global_min_w, global_min_h, global_max_w, global_max_h)

        for i, image in enumerate(open_cv_images):
            cv2.rectangle(image, (global_min_w, global_min_h), (global_max_w, global_max_h),
                          (255, 20, 147), 3)
            if not cv2.imwrite("../PDF-Dateien/" + str(index) + "/" + str(i) + ".png", image):
                print("Image " + str(i) + "could not be saved")

    print(f"Needed {time() - start_time}s to convert all PDF-files")

    # with tempfile.TemporaryDirectory() as path:
    #     images_from_path = convert_from_path('../PDF-Dateien/Heinemann, Geschichte BS und Hannover 01.pdf',
    #                                          output_folder=path,
    #                                          poppler_path=poppler_path,
    #                                          thread_count=4)
