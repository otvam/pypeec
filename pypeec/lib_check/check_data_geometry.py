"""
Module for checking the geometry data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

from pypeec.lib_check import datachecker
from pypeec.lib_check import check_data_geometry_png
from pypeec.lib_check import check_data_geometry_stl
from pypeec.lib_check import check_data_geometry_voxel


def _check_resampling(resampling):
    """
    Check the validity of resampling parameters.
    """

    # check type
    key_list = [
        "use_reduce",
        "use_resample",
        "resampling_factor",
    ]
    datachecker.check_dict("resampling", resampling, key_list=key_list)

    # check data
    datachecker.check_boolean("use_reduce", resampling["use_reduce"])
    datachecker.check_boolean("use_resample", resampling["use_resample"])
    datachecker.check_integer_array("resampling_factor", resampling["resampling_factor"], size=3, is_positive=True, can_be_zero=False)


def _check_domain_conflict(domain_name, domain_conflict):
    """
    Check the validity of the rules to solve conflict between domains (STL mesher).
    """

    # check type
    datachecker.check_list("domain_conflict", domain_conflict, sub_type=dict)

    # check value
    for domain_conflict_tmp in domain_conflict:
        # check type
        key_list = ["domain_keep", "domain_resolve"]
        datachecker.check_dict("domain_conflict", domain_conflict_tmp, key_list=key_list)

        # extract data
        domain_keep = domain_conflict_tmp["domain_keep"]
        domain_resolve = domain_conflict_tmp["domain_resolve"]

        # check type
        datachecker.check_string("domain_keep", domain_keep)
        datachecker.check_string("domain_resolve", domain_resolve)

        # check data
        datachecker.check_choice("domain_resolve", domain_resolve, domain_name)
        datachecker.check_choice("domain_keep", domain_keep, domain_name)


def _check_domain_connection(domain_name, domain_connection):
    """
    Check the domain connection data.
    This list is defining the required connection between the domain
    """

    # check type
    datachecker.check_dict("domain_connection", domain_connection, sub_type=dict)

    # check value
    for dat_tmp in domain_connection.values():
        # check type
        key_list = ["connected", "domain_list"]
        datachecker.check_dict("domain_connection", dat_tmp, key_list=key_list)

        # extract field
        domain_list = dat_tmp["domain_list"]
        connected = dat_tmp["connected"]

        # check data
        datachecker.check_boolean("connected", connected)
        datachecker.check_list("domain_list", domain_list, can_be_empty=False, sub_type=str)

        # check value
        for tag in domain_list:
            datachecker.check_choice("source_type", tag, domain_name)


def check_data_geometry(data_geometry):
    """
    Check the mesher data type and extract the data.
    """

    # check type
    key_list = [
        "mesh_type",
        "data_voxelize",
        "resampling",
        "domain_conflict",
        "domain_connection",
    ]
    datachecker.check_dict("data_geometry", data_geometry, key_list=key_list)

    # extract field
    mesh_type = data_geometry["mesh_type"]
    data_voxelize = data_geometry["data_voxelize"]
    resampling = data_geometry["resampling"]
    domain_conflict = data_geometry["domain_conflict"]
    domain_connection = data_geometry["domain_connection"]

    # check type
    datachecker.check_choice("mesh_type", mesh_type, ["stl", "png", "voxel"])

    # check the mesher
    if mesh_type == "png":
        domain_name = check_data_geometry_png.check_data_voxelize(data_voxelize)
    elif mesh_type == "stl":
        domain_name = check_data_geometry_stl.check_data_voxelize(data_voxelize)
    elif mesh_type == "voxel":
        domain_name = check_data_geometry_voxel.check_data_voxelize(data_voxelize)
    else:
        raise ValueError("invalid mesh type")

    # check the resampling data
    _check_resampling(resampling)

    # check the conflict data
    _check_domain_conflict(domain_name, domain_conflict)

    # check the connection data
    _check_domain_connection(domain_name, domain_connection)
