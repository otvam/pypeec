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
    name = "test_slab"
    # name = "png_inductor"
    # name = "stl_inductor"

    # get the filename
    file_res = os.path.join("data_output_solution",  name + ".pck")
    file_plotter = os.path.join("data_input_plotter_viewer", "data_plotter.json")

    # run
    status = script.run_plotter(file_res, file_plotter)
    sys.exit(int(not status))
