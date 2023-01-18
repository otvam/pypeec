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
from examples import examples_visualization
from examples import examples_config

# get config
PATH_ROOT = examples_config.PATH_ROOT
EXAMPLE_NAME = examples_config.EXAMPLE_NAME


if __name__ == "__main__":
    # get the filename
    file_solution = os.path.join(PATH_ROOT, EXAMPLE_NAME, "solution.pck")
    file_point = os.path.join(PATH_ROOT, EXAMPLE_NAME, "point.json")
    file_plotter = os.path.join(PATH_ROOT, "data_visualization", "data_plotter.json")

    # get viewer data
    data_plotter = examples_visualization.get_data_plotter()

    # create file
    with open(file_plotter, "w") as fid:
        json.dump(data_plotter, fid, indent=4)

    # run
    status = script.run_plotter(file_solution, file_point, file_plotter, True)
    sys.exit(int(not status))
