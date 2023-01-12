"""
User script for visualizing a 3D voxel structure.
Contain the program entry point.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import os
import sys
from PyPEEC import viewer
from PyPEEC import fileio


def run(file_voxel, file_viewer):
    """
    Load the voxel structure and plot the results.
    """

    # load voxel file
    data_voxel = fileio.load_pickle(file_voxel)

    # load viewer file
    data_viewer = fileio.load_json(file_viewer)

    # call lib_plotter
    status = viewer.run(data_voxel, data_viewer)

    return status


if __name__ == "__main__":
    # name of the simulation
    # name = "png_inductor"
    # name = "stl_inductor"
    name = "test_slab"

    # get the filename
    file_voxel = os.path.join("data_output_voxel",  name + ".pck")
    file_viewer = os.path.join("data_input_plotter_viewer", "data_viewer.json")

    # run viewer
    status = run(file_voxel, file_viewer)
    sys.exit(int(not status))
