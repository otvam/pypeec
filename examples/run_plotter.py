"""
User script for plotting the solution of a FFT-PEEC problem.
Contain the program entry point.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import os
import sys
import json
from PyPEEC import script
from examples import config_viewer_plotter
from examples import config_examples

# get config
PATH_ROOT = config_examples.PATH_ROOT
EXAMPLE_NAME = config_examples.EXAMPLE_NAME


if __name__ == "__main__":
    # get the filename
    file_solution = os.path.join(PATH_ROOT, "data_solution", EXAMPLE_NAME + ".pck")
    file_plotter = os.path.join(PATH_ROOT, "data_viewer_plotter", "data_plotter.json")

    # get viewer data
    data_plotter = config_viewer_plotter.get_data_plotter()

    # write file
    with open(file_plotter, "w") as fid:
        json.dump(data_plotter, fid, indent=4)

    # run
    status = script.run_plotter(file_solution, file_plotter, True)
    sys.exit(int(not status))
