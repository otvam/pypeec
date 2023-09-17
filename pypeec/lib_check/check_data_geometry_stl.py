"""
Module for checking the STL mesher data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

from pypeec.lib_check import datachecker


def _check_domain_stl(domain_stl):
    """
    Check the validity of the domain definition.
    """

    # check type
    datachecker.check_dict("domain_stl", domain_stl, can_be_empty=False)

    # check content
    for tag, domain_stl_tmp in domain_stl.items():
        datachecker.check_list("domain_stl", domain_stl_tmp, can_be_empty=False)
        for domain_stl_tmp_tmp in domain_stl_tmp:
            # check type
            key_list = ["scale", "offset", "filename"]
            datachecker.check_dict("domain_stl", domain_stl_tmp_tmp, key_list=key_list)

            # extract the data
            scale = domain_stl_tmp_tmp["scale"]
            offset = domain_stl_tmp_tmp["offset"]
            filename = domain_stl_tmp_tmp["filename"]

            # check data
            datachecker.check_float("scale", scale, is_positive=True, can_be_zero=False)
            datachecker.check_float_array("offset", offset, size=3)
            datachecker.check_filename("filename", filename)


def _check_param(param):
    """
    Check the voxel structure parameters.
    """

    # check type
    key_list = ["d", "xyz_min", "xyz_max"]
    datachecker.check_dict("param", param, key_list=key_list)

    # check data
    datachecker.check_float_array("d", param["d"], size=3, is_positive=True, can_be_zero=False)
    datachecker.check_float_array("xyz_min", param["xyz_min"], size=3, is_positive=False, can_be_zero=True, can_be_none=True)
    datachecker.check_float_array("xyz_max", param["xyz_max"], size=3, is_positive=False, can_be_zero=True, can_be_none=True)


def check_data_voxelize(data_voxelize):
    """
    Check the data used for voxelization.
    """

    # check type
    key_list = ["param", "domain_stl"]
    datachecker.check_dict("data_voxelize", data_voxelize, key_list=key_list)

    # extract field
    param = data_voxelize["param"]
    domain_stl = data_voxelize["domain_stl"]

    # check voxel structure parameters
    _check_param(param)

    # check the STL file
    _check_domain_stl(domain_stl)

    # get the domain name
    domain_list = domain_stl.keys()

    return domain_list
