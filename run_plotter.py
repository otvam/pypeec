"""
User script for plotting the solution of a FFT-PEEC problem.
Contain the program entry point.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import sys
import pickle

from main import plotter


def run(name, data_plotter):
    """
    Load the result file and plot the results.
    """

    # load data_output
    filename = "data_output/%s.pck" % name
    with open(filename, "rb") as fid:
        data_res = pickle.load(fid)

    # call plotter
    exit_code = plotter.run(data_res, data_plotter)

    return exit_code


if __name__ == "__main__":
    # get the data
    name = "data_pcb_trf"

    # get the data
    from data_input import data_plotter
    data_plotter = data_plotter.get_data()

    # run
    exit_code = run(name, data_plotter)
    sys.exit(exit_code)
