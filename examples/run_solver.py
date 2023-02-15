"""
User script for solving a problem with the PEEC solver.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import os
import sys
from PyPEEC import script
from examples import examples_config

# get config
PATH_ROOT = examples_config.PATH_ROOT
EXAMPLE_NAME = examples_config.EXAMPLE_NAME


if __name__ == "__main__":
    # get the filename
    file_problem = os.path.join(PATH_ROOT, EXAMPLE_NAME, "problem.yaml")
    file_voxel = os.path.join(PATH_ROOT, EXAMPLE_NAME, "voxel.pck")
    file_solution = os.path.join(PATH_ROOT, EXAMPLE_NAME, "solution.pck")
    file_tolerance = os.path.join(PATH_ROOT, "config", "data_tolerance.json")

    # run
    (status, ex) = script.run_solver(file_voxel, file_problem, file_tolerance, file_solution)
    sys.exit(int(not status))
