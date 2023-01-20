"""
User script for plotting the solution of a FFT-PEEC problem.
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
    file_solution = os.path.join(PATH_ROOT, EXAMPLE_NAME, "solution.pck")
    file_point = os.path.join(PATH_ROOT, EXAMPLE_NAME, "point.json")
    file_plotter = os.path.join(PATH_ROOT, "visualization", "data_plotter.json")

    # run
    status = script.run_plotter(file_solution, file_point, file_plotter, True)
    sys.exit(int(not status))
