"""
User script for solving a problem with the FFT-PEEC solver.
Contain the program entry point.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import os
import sys
from PyPEEC import script
from examples import config_examples

# get config
PATH_ROOT = config_examples.PATH_ROOT
EXAMPLE_NAME = config_examples.EXAMPLE_NAME


if __name__ == "__main__":
    # get the filename
    file_problem = os.path.join(PATH_ROOT, "data_solver", EXAMPLE_NAME + ".json")
    file_voxel = os.path.join(PATH_ROOT, "data_voxel", EXAMPLE_NAME + ".pck")
    file_solution = os.path.join(PATH_ROOT, "data_solution", EXAMPLE_NAME + ".pck")

    # run
    exit_code = script.run_solver(file_voxel, file_problem, file_solution)
    sys.exit(exit_code)
