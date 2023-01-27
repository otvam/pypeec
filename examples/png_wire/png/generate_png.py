"""
Generate PNG files for the example.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

from PIL import Image
from PIL import ImageDraw


def get_image(img_size):
    """
    Get an image.
    """

    img = Image.new("RGBA", (img_size, img_size))
    dr = ImageDraw.Draw(img)

    return (img, dr)


def get_circle(dr, radius, xy, color):
    """
    Add a circle.
    """

    (x, y) = xy
    pos = (x-radius, y-radius, x+radius, y+radius)
    dr.ellipse(pos, fill=color)


if __name__ == "__main__":
    # ######################## get the variables
    img_size = 49
    radius = 24

    # ######################## get the position
    mid = (img_size-1)/2
    xy = (mid, mid)

    # ######################## wire
    (img, dr) = get_image(img_size)
    get_circle(dr, radius, xy, (0, 0, 0))
    img.save("wire.png")

    # ######################## source
    (img, dr) = get_image(img_size)
    get_circle(dr, radius, xy, (255, 0, 0))
    img.save("src.png")

    # ######################## sink
    (img, dr) = get_image(img_size)
    get_circle(dr, radius, xy, (0, 255, 0))
    img.save("sink.png")
