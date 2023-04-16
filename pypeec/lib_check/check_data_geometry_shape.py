"""
Module for checking the shape mesher data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

from pypeec.lib_check import datachecker


def check_data_voxelize(data_voxelize):
    """
    Check the data used for voxelization (PNG mesher).
    """

    domain_name = data_voxelize["geometry_shape"].keys()

    return domain_name
