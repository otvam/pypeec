"""
Generate PNG files from the GERBER files for the example.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import os
import sys
import matplotlib.pyplot as plt
import matplotlib.image as img
from pypeec.utils import gerber


def _plot_image(folder, name):
    """
    Display an image on the screen.
    """

    # load the images
    data = img.imread(os.path.join(folder, name + ".png"))

    # make a plot
    plt.figure()
    plt.imshow(data)
    plt.title(name)


if __name__ == "__main__":
    # ########################################################
    # ### definition of the parameters
    # ########################################################

    # definition of the colors
    color_def = {
        "none":  (255, 255, 255),
        "copper": (255, 0, 0),
        "sink":  (0, 0, 255),
        "src": (0, 255, 0),
    }

    # definition of the GERBER files
    gerber_def = {
        "front": "pcb-front_copper.gbr",
        "back": "pcb-back_copper.gbr",
        "src": "pcb-src.gbr",
        "sink": "pcb-sink.gbr",
        "drill": "pcb-PTH.drl",
        "via":  "pcb-VIA.drl",
    }

    # assemble the GERBER data
    data_gerber = {
        "gerber_edge": "pcb-edge.gbr",           # name of the GERBER file with the board edges
        "color_background": (255, 255, 255),     # background color for the images
        "color_edge": (0, 0, 0),                 # color of the board edges
        "color_def": color_def,                  # dict with the color definition
        "gerber_def": gerber_def                 # dict with the GERBER file definition
    }

    # get the layer stack (combination between GERBER files and colors)
    data_stack = {
        "front": [
            {"gerber": "drill", "color": "none"},
            {"gerber": "front", "color": "copper"},
        ],
        "back": [
            {"gerber": "drill", "color": "none"},
            {"gerber": "back", "color": "copper"},
        ],
        "terminal": [
            {"gerber": "drill", "color": "none"},
            {"gerber": "sink", "color": "sink"},
            {"gerber": "src", "color": "src"},
        ],
        "via": [
            {"gerber": "drill", "color": "none"},
            {"gerber": "via", "color": "copper"},
        ],
    }

    # get the export instructions
    data_export = {
        "margin": 0.1,                    # relative margin to be considered around the board
        "oversampling": 1.0,              # oversampling factor for exporting the GERBER files
        "voxel": 17.0e-6,                 # size of the voxel
        "folder_gerber": "gerber",        # GERBER file location
        "folder_png": "png",              # PNG file location
    }

    # ########################################################
    # ### convert the GERBER files
    # ########################################################

    # convert the GERBER files to PNG files
    gerber.get_convert(data_export, data_gerber, data_stack)

    # show the images
    _plot_image("png", "front")
    _plot_image("png", "back")
    _plot_image("png", "terminal")
    _plot_image("png", "via")
    plt.show()

    # exit
    sys.exit(0)
