"""
Module for checking the voxel mesher data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

from pypeec.lib_check import datachecker


def _check_domain_def(domain_def):
    """
    Check the domain definition (mapping between domain names and indices).
    """

    # check type
    datachecker.check_dict("domain_def", domain_def, can_be_empty=False, sub_type=list)

    # check data
    for idx in domain_def.values():
        datachecker.check_integer_array("domain_def", idx, is_positive=True)


def _check_voxel_structure(n, d, c):
    """
    Check the voxel structure parameters.
    """

    datachecker.check_integer_array("n", n, size=3, is_positive=True, can_be_zero=False)
    datachecker.check_float_array("d", d, size=3, is_positive=True, can_be_zero=False)
    datachecker.check_float_array("c", c, size=3)


def check_data_voxelize(data_voxelize):
    """
    Check the voxel structure (number, placement, and dimension).
    Check the mapping between domain names and indices.
    """

    # check type
    key_list = ["n", "d", "c", "domain_def"]
    datachecker.check_dict("data_voxelize", data_voxelize, key_list=key_list)

    # extract field
    n = data_voxelize["n"]
    d = data_voxelize["d"]
    c = data_voxelize["c"]
    domain_def = data_voxelize["domain_def"]

    # check voxel structure parameters
    _check_voxel_structure(n, d, c)

    # check domain definition
    _check_domain_def(domain_def)

    # get the domain name
    domain_name = domain_def.keys()

    return domain_name
