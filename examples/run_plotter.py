"""
User script for plotting the solution of a PEEC problem.
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
FOLDER_NAME = examples_config.FOLDER_NAME
EXAMPLE_NAME = examples_config.EXAMPLE_NAME


if __name__ == "__main__":
    # get the filenames
    file_solution = os.path.join(PATH_ROOT, FOLDER_NAME, EXAMPLE_NAME, "solution.pck")
    file_point = os.path.join(PATH_ROOT, FOLDER_NAME, EXAMPLE_NAME, "point.yaml")
    file_plotter = os.path.join(PATH_ROOT, FOLDER_CONFIG, "plotter.yaml")

    # run
    (status, ex) = main.run_plotter_file(file_solution, file_point, file_plotter, plot_mode="qt")
    sys.exit(int(not status))
