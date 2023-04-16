"""
Module for checking the STL mesher data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

from pypeec.lib_check import datachecker


def _check_domain_stl(domain_stl):
    """
    Check the validity of the domain definition (STL mesher).
    """

    # check type
    datachecker.check_dict("domain_stl", domain_stl, can_be_empty=False, sub_type=dict)

    # check content
    for domain_stl_tmp in domain_stl.values():
        # check type
        key_list = ["offset", "filename_list"]
        datachecker.check_dict("domain_stl", domain_stl_tmp, key_list=key_list)

        # check data
        datachecker.check_float_array("domain_color", domain_stl_tmp["offset"], size=3)
        datachecker.check_list("filename_list", domain_stl_tmp["filename_list"], can_be_empty=False, sub_type=str)


def _check_voxel_structure(c, xyz_min, xyz_max):
    """
    Check the voxel structure parameters.
    """

    if c is not None:
        datachecker.check_float_array("c", c, size=3)
    if xyz_min is not None:
        datachecker.check_float_array("xyz_min", xyz_min, size=3)
    if xyz_max is not None:
        datachecker.check_float_array("xyz_max", xyz_max, size=3)


def check_data_voxelize(data_voxelize):
    """
    Check the data used for voxelization (STL mesher).
    """

    # check type
    key_list = ["n", "d", "c", "sampling", "xyz_min", "xyz_max", "domain_stl"]
    datachecker.check_dict("data_voxelize", data_voxelize, key_list=key_list)

    # extract field
    n = data_voxelize["n"]
    d = data_voxelize["d"]
    c = data_voxelize["c"]
    sampling = data_voxelize["sampling"]
    xyz_min = data_voxelize["xyz_min"]
    xyz_max = data_voxelize["xyz_max"]
    domain_stl = data_voxelize["domain_stl"]

    # check data
    datachecker.check_choice("sampling", sampling, ["number", "dimension"])
    if sampling == "number":
        datachecker.check_integer_array("n", n, size=3, is_positive=True, can_be_zero=False)
        datachecker.check_assert("d", d is None, "d should be None")
    elif sampling == "dimension":
        datachecker.check_float_array("d", d, size=3, is_positive=True, can_be_zero=False)
        datachecker.check_assert("n", n is None, "n should be None")
    else:
        raise ValueError("inconsistent definition of the voxel number/size")

    # check voxel structure parameters
    _check_voxel_structure(c, xyz_min, xyz_max)

    # check the stl file
    _check_domain_stl(domain_stl)

    # get the domain name
    domain_name = domain_stl.keys()

    return domain_name
