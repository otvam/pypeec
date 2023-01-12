"""
User script for solving a problem with the FFT-PEEC solver.
Contain the program entry point.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import os
import sys
from PyPEEC import solver
from PyPEEC import fileio


def run(file_voxel, file_problem, file_res):
    """
    Load the voxel structure, solve the problem and write the solver results.
    """

    # load voxel file
    data_voxel = fileio.load_pickle(file_voxel)

    # load mesher file
    data_problem = fileio.load_json(file_problem)

    # call solver
    (status, data_solution) = solver.run(data_voxel, data_problem)

    # save results
    fileio.write_pickle(status, file_res, data_solution)

    # exit
    exit_code = int(not status)

    return exit_code


if __name__ == "__main__":
    # name of the simulation
    name = "test_slab"
    # name = "png_inductor"
    # name = "stl_inductor"

    # get the filename
    file_problem = os.path.join("data_input_solver", "%s.json" % name)
    file_voxel = os.path.join("data_output_voxel",  name + ".pck")
    file_res = os.path.join("data_output_solution",  name + ".pck")

    # run
    exit_code = run(file_voxel, file_problem, file_res)
    sys.exit(exit_code)
