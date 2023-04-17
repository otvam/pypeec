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
    for tag, domain_stl_tmp in domain_stl.items():
        # check type
        key_list = ["offset", "filename_list"]
        datachecker.check_dict("domain_stl", domain_stl_tmp, key_list=key_list)

        # get the data
        offset = domain_stl_tmp["offset"]
        filename_list = domain_stl_tmp["filename_list"]

        # check data
        datachecker.check_float_array("domain_color", offset, size=3)
        datachecker.check_list("filename_list", filename_list, can_be_empty=False, sub_type=str)

        # check files
        for filename in filename_list:
            datachecker.check_filename("filename_list", filename)


def _check_param(param):
    """
    Check the voxel structure parameters.
    """

    # check type
    key_list = ["d", "xyz_min", "xyz_max"]
    datachecker.check_dict("param", param, key_list=key_list)

    # check data
    datachecker.check_float_array("d", param["d"], size=3, is_positive=True, can_be_zero=False)
    if param["xyz_min"] is not None:
        datachecker.check_float_array("xyz_min", param["xyz_min"], size=3)
    if param["xyz_max"] is not None:
        datachecker.check_float_array("xyz_max", param["xyz_max"], size=3)


def check_data_voxelize(data_voxelize):
    """
    Check the data used for voxelization (STL mesher).
    """

    # check type
    key_list = ["param", "domain_stl"]
    datachecker.check_dict("data_voxelize", data_voxelize, key_list=key_list)

    # extract field
    param = data_voxelize["param"]
    domain_stl = data_voxelize["domain_stl"]

    # check voxel structure parameters
    _check_param(param)

    # check the stl file
    _check_domain_stl(domain_stl)

    # get the domain name
    domain_name = domain_stl.keys()

    return domain_name
