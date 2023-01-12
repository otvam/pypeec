"""
User script for visualizing a 3D voxel structure.
Contain the program entry point.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import sys
import pickle
from PyPEEC import viewer
from data_input_plotter_viewer import data_viewer


def run(name, data_viewer):
    """
    Load the voxel structure and plot the results.
    """

    # load data
    filename = "data_output/mesher_%s.pck" % name
    with open(filename, "rb") as fid:
        data_voxel = pickle.load(fid)

    # call lib_plotter
    exit_code = viewer.run(data_voxel, data_viewer)

    return exit_code


if __name__ == "__main__":
    # name of the simulation
    # name = "png_inductor"
    # name = "stl_inductor"
    name = "test_slab"

    # get the data
    data_viewer = data_viewer.get_data()

    # run viewer
    exit_code = run(name, data_viewer)
    sys.exit(exit_code)
