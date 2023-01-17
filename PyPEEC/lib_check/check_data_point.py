"""
Module for checking the point data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
from PyPEEC.lib_utils.error import CheckError


def check_data_point(data_point):
    """
    Check the point structure (defining the cloud of points).
    """

    # check type
    if not isinstance(data_point, dict):
        raise CheckError("data_point: point description should be a dict")

    # check the different domains
    for tag, coord in data_point.items():
        # check tag
        if not isinstance(tag, str):
            raise CheckError("tag: conductor name should be a string")

        # cast indices
        coord = np.array(coord)
        if not (len(coord.shape) == 2):
            raise CheckError("coord: coordinates should be a 2D array")
        if not (coord.shape[0] > 0):
            raise CheckError("coord: coordinates cannot be empty")
        if not (coord.shape[1] == 3):
            raise CheckError("coord: coordinates should have three dimensions")
        if not np.issubdtype(coord.dtype, np.floating):
            raise CheckError("coord: coordinates should be composed of floats")
