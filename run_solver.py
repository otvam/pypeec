"""
User script for solving a problem with the FFT-PEEC solver.
Contain the program entry point.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import sys
import pickle
import importlib
from PyPEEC import solver


def run(name, data_voxel, data_problem):
    """
    Solve the problem and write the result file.
    """

    # load data
    if data_voxel is None:
        filename = "data_output/mesher_%s.pck" % name
        with open(filename, "rb") as fid:
            data_voxel = pickle.load(fid)

    # call solver
    (status, data_res) = solver.run(data_voxel, data_problem)

    # save results
    if status:
        filename = "data_output/solver_%s.pck" % name
        with open(filename, "wb") as fid:
            pickle.dump(data_res, fid)

    # exit
    exit_code = int(not status)

    return exit_code


if __name__ == "__main__":
    # name of the simulation
    name = "test_slab"

    # get the data
    data = importlib.import_module("data_input_solver.%s" % name)
    (data_voxel, data_problem) = data.get_data()

    # run
    exit_code = run(name, data_voxel, data_problem)
    sys.exit(exit_code)
