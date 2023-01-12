"""
User script for meshing a voxel structure.
Contain the program entry point.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import sys
import pickle
import importlib
from PyPEEC import mesher


def run(name, mesh_type, data_mesher, data_resampling):
    """
    Solve the problem and write the mesher results.
    """

    # call solver
    (status, data_voxel) = mesher.run(mesh_type, data_mesher, data_resampling)

    # save results
    if status:
        filename = "data_output/mesher_%s.pck" % name
        with open(filename, "wb") as fid:
            pickle.dump(data_voxel, fid)

    # exit
    exit_code = int(not status)

    return exit_code


if __name__ == "__main__":
    # name of the simulation
    # name = "png_inductor"
    # name = "stl_inductor"
    name = "test_slab"

    # get the data
    data = importlib.import_module("data_input_mesher.%s" % name)
    (mesh_type, data_mesher, data_resampling) = data.get_data()

    # run
    exit_code = run(name, mesh_type, data_mesher, data_resampling)
    sys.exit(exit_code)
