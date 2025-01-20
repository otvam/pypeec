"""
User script for solving a problem with the PEEC solver.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import os.path
import pypeec
import examples_config

# get the path of the root of the code
PATH_ROOT = os.path.dirname(__file__)

# get config
FOLDER_CONFIG = examples_config.FOLDER_CONFIG
FOLDER_EXAMPLE = examples_config.FOLDER_EXAMPLE


if __name__ == "__main__":
    # get the filenames
    file_problem = os.path.join(PATH_ROOT, FOLDER_EXAMPLE, "problem.yaml")
    file_voxel = os.path.join(PATH_ROOT, FOLDER_EXAMPLE, "voxel.json.gz")
    file_solution = os.path.join(PATH_ROOT, FOLDER_EXAMPLE, "solution.json.gz")
    file_tolerance = os.path.join(PATH_ROOT, FOLDER_CONFIG, "tolerance.yaml")

    # run
    pypeec.run_solver_file(
        file_voxel=file_voxel,
        file_problem=file_problem,
        file_tolerance=file_tolerance,
        file_solution=file_solution,
    )
