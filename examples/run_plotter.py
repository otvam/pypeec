"""
User script for plotting the solution of a PEEC problem.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import sys
import os.path
from pypeec import main
from examples import examples_config

# get config
PATH_ROOT = examples_config.PATH_ROOT
EXAMPLE_NAME = examples_config.EXAMPLE_NAME


if __name__ == "__main__":
    # get the filenames
    file_solution = os.path.join(PATH_ROOT, EXAMPLE_NAME, "solution.pck")
    file_point = os.path.join(PATH_ROOT, EXAMPLE_NAME, "point.yaml")
    file_plotter = os.path.join(PATH_ROOT, "config", "plotter.json")

    # run
    (status, ex) = main.run_plotter(file_solution, file_point, file_plotter)
    sys.exit(int(not status))
