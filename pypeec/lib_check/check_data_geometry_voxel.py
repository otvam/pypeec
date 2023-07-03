"""
Module for checking the voxel mesher data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

from pypeec.lib_check import datachecker


def _check_domain_index(domain_index):
    """
    Check the domain definition (mapping between domain names and indices).
    """

    # check type
    datachecker.check_dict("domain_index", domain_index, can_be_empty=False)

    # check data
    for idx in domain_index.values():
        datachecker.check_integer_array("domain_index", idx, is_positive=True, can_be_zero=True)


def _check_param(param):
    """
    Check the voxel structure parameters.
    """

    # check type
    key_list = ["n", "d", "c"]
    datachecker.check_dict("param", param, key_list=key_list)

    # check data
    datachecker.check_integer_array("n", param["n"], size=3, is_positive=True, can_be_zero=False)
    datachecker.check_float_array("d", param["d"], size=3, is_positive=True, can_be_zero=False)
    datachecker.check_float_array("c", param["c"], size=3)


def check_data_voxelize(data_voxelize):
    """
    Check the data used for voxelization.
    """

    # check type
    key_list = ["param", "domain_index"]
    datachecker.check_dict("data_voxelize", data_voxelize, key_list=key_list)

    # extract field
    param = data_voxelize["param"]
    domain_index = data_voxelize["domain_index"]

    # check voxel structure parameters
    _check_param(param)

    # check domain definition
    _check_domain_index(domain_index)

    # get the domain name
    domain_list = domain_index.keys()

    return domain_list
