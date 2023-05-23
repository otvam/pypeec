"""
User script for solving a problem with the PEEC solver.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import sys
import os.path
from pypeec import main
from pypeec import config
from examples import examples_config

# get config
PATH_ROOT = examples_config.PATH_ROOT
CFG_PYPEEC = examples_config.CFG_PYPEEC
FOLDER_NAME = examples_config.FOLDER_NAME
EXAMPLE_NAME = examples_config.EXAMPLE_NAME


if __name__ == "__main__":
    # get the filenames
    file_problem = os.path.join(PATH_ROOT, FOLDER_NAME, EXAMPLE_NAME, "problem.yaml")
    file_voxel = os.path.join(PATH_ROOT, FOLDER_NAME, EXAMPLE_NAME, "voxel.pck")
    file_solution = os.path.join(PATH_ROOT, FOLDER_NAME, EXAMPLE_NAME, "solution.pck")
    file_config = os.path.join(PATH_ROOT, CFG_PYPEEC, "configuration.yaml")
    file_tolerance = os.path.join(PATH_ROOT, CFG_PYPEEC, "tolerance.yaml")

    # set config
    status = config.set_config(file_config)
    assert status, "invalid configuration"

    # run
    (status, ex) = main.run_solver_file(file_voxel, file_problem, file_tolerance, file_solution)
    sys.exit(int(not status))
