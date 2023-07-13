"""
Module for checking the geometry data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

from pypeec.lib_check import datachecker
from pypeec.lib_check import check_data_geometry_png
from pypeec.lib_check import check_data_geometry_stl
from pypeec.lib_check import check_data_geometry_shape
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


def _check_domain_conflict(domain_list, domain_conflict):
    """
    Check the validity of the rules to solve conflict between domains (STL mesher).
    """

    # check type
    datachecker.check_list("domain_conflict", domain_conflict, can_be_empty=True)

    # check value
    for domain_conflict_tmp in domain_conflict:
        # check type
        key_list = ["domain_keep", "domain_resolve"]
        datachecker.check_dict("domain_conflict", domain_conflict_tmp, key_list=key_list)

        # extract the data
        domain_keep = domain_conflict_tmp["domain_keep"]
        domain_resolve = domain_conflict_tmp["domain_resolve"]

        # check type
        datachecker.check_list("domain_keep", domain_keep, sub_type=str, can_be_empty=False)
        datachecker.check_list("domain_resolve", domain_resolve, sub_type=str, can_be_empty=False)

        # check data
        for tag in domain_keep:
            datachecker.check_choice("domain_keep", tag, domain_list)
        for tag in domain_resolve:
            datachecker.check_choice("domain_resolve", tag, domain_list)


def _check_domain_connection(domain_list, domain_connection):
    """
    Check the domain connection data.
    This list is defining the required connection between the domain
    """

    # check type
    datachecker.check_dict("domain_connection", domain_connection)

    # check value
    for domain_connection_tmp in domain_connection.values():
        # check type
        key_list = ["connected", "domain_group"]
        datachecker.check_dict("domain_connection", domain_connection_tmp, key_list=key_list)

        # extract field
        domain_group = domain_connection_tmp["domain_group"]
        connected = domain_connection_tmp["connected"]

        # check type
        datachecker.check_boolean("connected", connected)
        datachecker.check_list("domain_group", domain_group, can_be_empty=False)

        # check value
        for domain_group_tmp in domain_group:
            datachecker.check_list("domain_group", domain_group_tmp, sub_type=str, can_be_empty=False)
            for tag in domain_group_tmp:
                datachecker.check_choice("domain_group", tag, domain_list)


def check_data_geometry(data_geometry):
    """
    Check the mesher data type and extract the data.
    """

    # check type
    key_list = [
        "mesh_type",
        "data_voxelize",
        "resampling",
        "check_conflict",
        "check_connection",
        "domain_conflict",
        "domain_connection",
    ]
    datachecker.check_dict("data_geometry", data_geometry, key_list=key_list)

    # extract field
    mesh_type = data_geometry["mesh_type"]
    data_voxelize = data_geometry["data_voxelize"]
    resampling = data_geometry["resampling"]
    check_conflict = data_geometry["check_conflict"]
    check_connection = data_geometry["check_connection"]
    domain_conflict = data_geometry["domain_conflict"]
    domain_connection = data_geometry["domain_connection"]

    # check type
    datachecker.check_choice("mesh_type", mesh_type, ["stl", "png", "shape", "voxel"])
    datachecker.check_boolean("check_conflict", check_conflict)
    datachecker.check_boolean("check_connection", check_connection)

    # check the mesher
    if mesh_type == "png":
        domain_list = check_data_geometry_png.check_data_voxelize(data_voxelize)
    elif mesh_type == "stl":
        domain_list = check_data_geometry_stl.check_data_voxelize(data_voxelize)
    elif mesh_type == "shape":
        domain_list = check_data_geometry_shape.check_data_voxelize(data_voxelize)
    elif mesh_type == "voxel":
        domain_list = check_data_geometry_voxel.check_data_voxelize(data_voxelize)
    else:
        raise ValueError("invalid mesh type")

    # check the resampling data
    _check_resampling(resampling)

    # check the conflict data
    _check_domain_conflict(domain_list, domain_conflict)

    # check the connection data
    _check_domain_connection(domain_list, domain_connection)
