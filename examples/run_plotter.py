"""
User script for plotting the solution of a PEEC problem.
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
CFG_PLOT = examples_config.CFG_PLOT
FOLDER_NAME = examples_config.FOLDER_NAME
EXAMPLE_NAME = examples_config.EXAMPLE_NAME


if __name__ == "__main__":
    # get the filenames
    file_solution = os.path.join(PATH_ROOT, FOLDER_NAME, EXAMPLE_NAME, "solution.pck")
    file_point = os.path.join(PATH_ROOT, FOLDER_NAME, EXAMPLE_NAME, "point.yaml")
    file_config = os.path.join(PATH_ROOT, CFG_PYPEEC, "config.yaml")
    file_plotter = os.path.join(PATH_ROOT, CFG_PLOT, "plotter.json")

    # set config
    status = config.set_config(file_config)
    assert status, "invalid configuration"

    # run
    (status, ex) = main.run_plotter_file(file_solution, file_point, file_plotter)
    sys.exit(int(not status))
