"""
User script for plotting the solution of a FFT-PEEC problem.
Contain the program entry point.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import os
import sys
from PyPEEC import script


if __name__ == "__main__":
    # get the data
    # name = "png_inductor"
    # name = "stl_inductor"
    # name = "voxel_slab"
    name = "voxel_transformer"

    # get the filename
    file_solution = os.path.join("data_output_solution",  name + ".pck")
    file_plotter = os.path.join("data_input_plotter_viewer", "data_plotter.json")

    # run
    status = script.run_plotter(file_solution, file_plotter, True)
    sys.exit(int(not status))
