import math

from config import DPI

PIXEL_TO_PTS_CONSTANT = 0.352778


def convert_to_pts(pixel: float) -> float:
    """
    Converts the given pixel count to pts

    :param pixel: The amount of pixel
    :return: Pixel in pts
    """
    return pixel * PIXEL_TO_PTS_CONSTANT


def pts_to_pixel(pts: float, pts_per_pixel: float) -> int:
    """
    Convert pts value to amount of pixel
    :param pts: Value in pts
    :param pts_per_pixel: How many pts per pixel
    :return: The pts value in pixel
    """

    return math.floor(pts / PIXEL_TO_PTS_CONSTANT / float(pts_per_pixel))


def pixel_to_pts(pixel: float) -> float:
    return (pixel / DPI) * 72


def pts_to_pixel_dpi(pts: float) -> float:
    return pts * DPI / 72
