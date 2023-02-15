"""
Module for checking the point data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import numpy as np
from PyPEEC.lib_utils.error import CheckError


def check_data_point(data_point):
    """
    Check the point structure (defining the point cloud).
    The point cloud is used for magnetic field evaluation.
    """

    # check type
    if not isinstance(data_point, list):
        raise CheckError("data_point: point description should be a list")

    # check the points (if any)
    if data_point:
        data_point = np.array(data_point)
        if not (len(data_point.shape) == 2):
            raise CheckError("data_point: coordinates should be a 2D array")
        if not (data_point.shape[0] > 0):
            raise CheckError("coord: coordinates cannot be empty")
        if not (data_point.shape[1] == 3):
            raise CheckError("data_point: coordinates should have three dimensions")
        if not np.issubdtype(data_point.dtype, np.floating):
            raise CheckError("data_point: coordinates should be composed of floats")
