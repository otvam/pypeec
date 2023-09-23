"""
User script for solving a problem with the PEEC solver.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import sys
import os.path
from pypeec import main
import examples_config

# get config
PATH_ROOT = examples_config.PATH_ROOT
FOLDER_CONFIG = examples_config.FOLDER_CONFIG
FOLDER_EXAMPLE = examples_config.FOLDER_EXAMPLE


if __name__ == "__main__":
    # get the filenames
    file_problem = os.path.join(PATH_ROOT, FOLDER_EXAMPLE, "problem.yaml")
    file_voxel = os.path.join(PATH_ROOT, FOLDER_EXAMPLE, "voxel.pck")
    file_solution = os.path.join(PATH_ROOT, FOLDER_EXAMPLE, "solution.pck")
    file_tolerance = os.path.join(PATH_ROOT, FOLDER_CONFIG, "tolerance.yaml")

    # run
    (status, ex) = main.run_solver_file(file_voxel, file_problem, file_tolerance, file_solution)
    sys.exit(int(not status))
