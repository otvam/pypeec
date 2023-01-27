"""
Generate PNG files for the example.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import math
from PIL import Image
from PIL import ImageDraw


def get_image(img_size):
    """
    Get an image.
    """

    img = Image.new("RGBA", (img_size, img_size))
    dr = ImageDraw.Draw(img)

    return (img, dr)


def get_circle(dr, thickness, xy, color):
    """
    Add a circle.
    """

    (x, y) = xy
    radius = (thickness-1)/2
    pos = (x-radius, y-radius, x+radius, y+radius)
    dr.ellipse(pos, fill=color)


def get_line(dr, thickness, xy_start, xy_end, color):
    """
    Add a line.
    """

    pos = [xy_start, xy_end]
    dr.line(pos, width=thickness, fill=color, joint="curve")


if __name__ == "__main__":
    # ######################## get the variables
    img_size = 121
    margin = 10
    thickness = 9

    # ######################## get the position
    mid = (img_size-1)/2
    diag = (img_size-2*margin)/math.sqrt(2)

    # ######################## insulation layer (empty)
    (img, _) = get_image(img_size)
    img.save("insulation.png")

    # ######################## top layer (straight trace)
    (img, dr) = get_image(img_size)

    xy_start = (margin, mid)
    xy_end = (img_size-margin, mid)

    get_line(dr, thickness, xy_start, xy_end, (0, 0, 0))
    get_circle(dr, thickness, xy_start, (255, 0, 0))
    get_circle(dr, thickness, xy_end, (0, 0, 255))
    img.save("top.png")

    # ######################## bottom layer (diagonal trace)
    (img, dr) = get_image(img_size)

    tmp_start = mid-(diag/2)
    tmp_end = mid+(diag/2)
    xy_start = (tmp_start, tmp_start)
    xy_end = (tmp_end, tmp_end)

    get_line(dr, thickness, xy_start, xy_end, (0, 0, 0))
    get_circle(dr, thickness, xy_start, (0, 255, 0))
    get_circle(dr, thickness, xy_end, (0, 0, 255))
    img.save("bottom.png")
