"""
Module for checking the point data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

from pypeec.lib_utils import datachecker


def check_data_point(data_point):
    """
    Check the point structure (defining the point cloud).
    The point cloud is used for magnetic field evaluation.
    """

    # check type
    datachecker.check_list("data_point", data_point, sub_type=list)

    # check the points (if any)
    for dat_tmp in data_point:
        datachecker.check_float_array("data_point", dat_tmp, size=3)
