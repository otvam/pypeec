"""
User script for plotting the solution of a FFT-PEEC problem.
Contain the program entry point.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import os
import sys
from PyPEEC import script
from examples import examples_visualization
from examples import examples_utils
from examples import examples_config

# get config
PATH_ROOT = examples_config.PATH_ROOT
EXAMPLE_NAME = examples_config.EXAMPLE_NAME


if __name__ == "__main__":
    # get the filename
    file_solution = os.path.join(PATH_ROOT, "data_solution", EXAMPLE_NAME + ".pck")
    file_point = os.path.join(PATH_ROOT, "data_point", EXAMPLE_NAME + ".json")
    file_plotter = os.path.join(PATH_ROOT, "data_visualization", "data_plotter.json")

    # get viewer data
    data_plotter = examples_visualization.get_data_plotter()

    # create folder and file
    examples_utils.create_folder(file_plotter)
    examples_utils.write_json(file_plotter, data_plotter)

    # run
    status = script.run_plotter(file_solution, file_point, file_plotter, True)
    sys.exit(int(not status))
