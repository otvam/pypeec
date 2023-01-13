"""
User script for solving a problem with the FFT-PEEC solver.
Contain the program entry point.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import os
import sys
from PyPEEC import script


if __name__ == "__main__":
    # name of the simulation
    # name = "png_inductor"
    # name = "stl_inductor"
    # name = "voxel_slab"
    name = "voxel_transformer"

    # get the filename
    file_problem = os.path.join("data_input_solver", "%s.json" % name)
    file_voxel = os.path.join("data_output_voxel",  name + ".pck")
    file_solution = os.path.join("data_output_solution",  name + ".pck")

    # run
    exit_code = script.run_solver(file_voxel, file_problem, file_solution)
    sys.exit(exit_code)
