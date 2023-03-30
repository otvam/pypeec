"""
Generate PNG files for the example.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

from PIL import Image
from PIL import ImageDraw


def get_image(img_size):
    """
    Get an image.
    """

    img = Image.new("RGBA", (img_size, img_size))
    dr = ImageDraw.Draw(img)

    return img, dr


def get_rectangle(dr, xy_start, xy_end, color):
    """
    Add a circle.
    """

    pos = [xy_start, xy_end]
    dr.rectangle(pos, fill=color)


if __name__ == "__main__":
    # ######################## get the variables
    img_size = 49
    thickness = 10
    via = 3

    # ######################## busbar
    (img, dr) = get_image(img_size)

    xy_start = (0, 0)
    xy_end = (img_size, thickness-1)
    get_rectangle(dr, xy_start, xy_end, (0, 0, 0))

    xy_start = (img_size-thickness, 0)
    xy_end = (img_size, img_size)
    get_rectangle(dr, xy_start, xy_end, (0, 0, 0))

    xy_start = (0, 0)
    xy_end = (0, thickness-1)
    get_rectangle(dr, xy_start, xy_end, (255, 0, 0))

    img.save("busbar.png")

    # ######################## via
    (img, dr) = get_image(img_size)

    xy_start = (img_size-thickness, img_size-via)
    xy_end = (img_size, img_size)
    get_rectangle(dr, xy_start, xy_end, (0, 0, 0))

    img.save("via.png")

    # ######################## plane
    (img, dr) = get_image(img_size)

    xy_start = (0, 0)
    xy_end = (img_size, img_size)
    get_rectangle(dr, xy_start, xy_end, (0, 0, 0))

    xy_start = (0, 0)
    xy_end = (0, thickness-1)
    get_rectangle(dr, xy_start, xy_end, (0, 255, 0))

    img.save("plane.png")
