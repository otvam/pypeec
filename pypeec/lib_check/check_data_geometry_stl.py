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


def _check_voxel_structure(d, bounds):
    """
    Check the voxel structure parameters.
    """

    datachecker.check_float_array("d", d, size=3, is_positive=True, can_be_zero=False)
    if bounds is not None:
        key_list = ["xyz_min", "xyz_max"]
        datachecker.check_dict("bounds", bounds, key_list=key_list)
        datachecker.check_float_array("xyz_min", bounds["xyz_min"], size=3)
        datachecker.check_float_array("xyz_max", bounds["xyz_max"], size=3)


def check_data_voxelize(data_voxelize):
    """
    Check the data used for voxelization (STL mesher).
    """

    # check type
    key_list = ["d", "bounds", "domain_stl"]
    datachecker.check_dict("data_voxelize", data_voxelize, key_list=key_list)

    # extract field
    d = data_voxelize["d"]
    bounds = data_voxelize["bounds"]
    domain_stl = data_voxelize["domain_stl"]

    # check voxel structure parameters
    _check_voxel_structure(d, bounds)

    # check the stl file
    _check_domain_stl(domain_stl)

    # get the domain name
    domain_name = domain_stl.keys()

    return domain_name
