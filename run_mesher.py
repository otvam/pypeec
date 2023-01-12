"""
User script for meshing a voxel structure.
Contain the program entry point.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import os
import sys
from PyPEEC import mesher
from PyPEEC import fileio


def run(file_mesher, file_voxel):
    """
    Solve the problem and write the mesher results.
    """

    # load mesher file
    data_mesher = fileio.load_json(file_mesher)

    # call solver
    (status, data_voxel) = mesher.run(data_mesher)

    # save results
    fileio.write_pickle(status, file_voxel, data_voxel)

    return status


if __name__ == "__main__":
    # name of the simulation
    name = "png_inductor"
    # name = "stl_inductor"
    # name = "test_slab"

    # get the filename
    file_mesher = os.path.join("data_input_mesher", name + ".json")
    file_voxel = os.path.join("data_output_voxel",  name + ".pck")

    # run
    status = run(file_mesher, file_voxel)
    sys.exit(int(not status))
