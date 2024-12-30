"""
Generate PNG files from GERBER files (for the different layers).
The PNG files are then used to describe the voxel geometry.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

# base packages
import os
import scilogger

# import plotting libraries
import matplotlib.pyplot as plt
import matplotlib.image as img

# import utils to be demonstrated
from pypeec.utils import gerber

# get a logger
LOGGER = scilogger.get_logger(__name__, "script")

# get the path the folder
PATH_ROOT = os.path.dirname(__file__)


def _plot_stack(folder_png, stack_list):
    """
    Display all the images composing a stack.
    """

    # plot the
    for name in stack_list:
        _plot_image(folder_png, name)

    # show the plots
    plt.show()


def _plot_image(folder_png, name):
    """
    Display an image on the screen.
    """

    # load the images
    data = img.imread(os.path.join(folder_png, name + ".png"))

    # make a plot
    plt.figure()
    plt.imshow(data)
    plt.title(name)


if __name__ == "__main__":
    # ########################################################
    # ### definition of the parameters
    # ########################################################

    # get the folder locations
    folder_gerber = os.path.join(PATH_ROOT, "gerber")
    folder_png = os.path.join(PATH_ROOT, "png")

    # definition of the colors
    color_def = {
        "none": (255, 255, 255),  # color used for the background
        "copper": (255, 0, 0),  # color used for the copper material
        "sink": (0, 0, 255),  # color used for the sink terminal
        "src": (0, 255, 0),  # color used for the source terminal
    }

    # definition of the GERBER files
    gerber_def = {
        "front": "pcb-front_copper.gbr",  # top layer of the PCB
        "back": "pcb-back_copper.gbr",  # bottom layer of the PCB
        "sink": "pcb-sink.gbr",  # layer with the  sink terminal
        "src": "pcb-src.gbr",  # layer with the  source terminal
        "drill": "pcb-PTH.drl",  # layer with the via drilling
        "via": "pcb-VIA.drl",  # layer with the via platting
    }

    # assemble the GERBER data
    data_gerber = {
        "gerber_edge": "pcb-edge.gbr",  # name of the GERBER file with the board edges
        "color_background": (255, 255, 255),  # background color for the images
        "color_edge": (0, 0, 0),  # color of the board edges
        "color_def": color_def,  # dict with the color definition
        "gerber_def": gerber_def,  # dict with the GERBER file definition
    }

    # get the export instructions
    data_export = {
        "margin": 0.1,  # relative margin to be considered around the board
        "oversampling": 1.0,  # oversampling factor for exporting the GERBER files
        "voxel": 17.0e-6,  # size of the voxel
        "folder_gerber": folder_gerber,  # GERBER file location
        "folder_png": folder_png,  # PNG file location
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

    # ########################################################
    # ### convert the GERBER files
    # ########################################################

    # convert the GERBER files
    LOGGER.info("convert the GERBER files")
    gerber.get_convert(data_export, data_gerber, data_stack)

    # plot the generated images
    LOGGER.info("plot the generated images")
    _plot_stack(folder_png, ["front", "back", "terminal", "via"])
