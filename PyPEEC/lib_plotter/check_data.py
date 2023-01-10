"""
Module for checking the plotter input data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np


class CheckError(Exception):
    """
    Exception used for signaling invalid input data.
    """

    pass


def check_data_plotter(data_plotter):
    """
    Check the type of the input data.
    """

    if not isinstance(data_plotter, list):
        raise CheckError("invalid input data")


def check_plot(data_plotter):
    """
    Check the voxel structure (number and size) and the Green function parameter.
    """

    pass