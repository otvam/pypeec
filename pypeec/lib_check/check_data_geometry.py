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


def _check_data_point(data_point):
    """
    Check the validity of cloud point parameters.
    """

    # check type
    key_list = [
        "check_cloud",
        "full_cloud",
        "pts_cloud",
    ]
    datachecker.check_dict("data_point", data_point, key_list=key_list)

    # check data
    datachecker.check_boolean("check_cloud", data_point["check_cloud"])
    datachecker.check_boolean("full_cloud", data_point["full_cloud"])
    datachecker.check_float_pts("pts_cloud", data_point["pts_cloud"], size=3, can_be_empty=True)


def _check_data_resampling(data_resampling):
    """
    Check the validity of resampling parameters.
    """

    # check type
    key_list = [
        "use_reduce",
        "use_resample",
        "resampling_factor",
    ]
    datachecker.check_dict("data_resampling", data_resampling, key_list=key_list)

    # check data
    datachecker.check_boolean("use_reduce", data_resampling["use_reduce"])
    datachecker.check_boolean("use_resample", data_resampling["use_resample"])
    datachecker.check_integer_array("resampling_factor", data_resampling["resampling_factor"], size=3, is_positive=True, can_be_zero=False)


def _check_conflict_rules(domain_list, conflict_rules):
    """
    Check the conflict resolution rules.
    """

    for conflict_rules_tmp in conflict_rules:
        # check type
        key_list = ["domain_keep", "domain_resolve"]
        datachecker.check_dict("conflict_rules", conflict_rules_tmp, key_list=key_list)

        # extract the data
        domain_keep = conflict_rules_tmp["domain_keep"]
        domain_resolve = conflict_rules_tmp["domain_resolve"]

        # check type
        datachecker.check_list("domain_keep", domain_keep, sub_type=str, can_be_empty=False)
        datachecker.check_list("domain_resolve", domain_resolve, sub_type=str, can_be_empty=False)

        # check data
        for tag in domain_keep:
            datachecker.check_choice("domain_keep", tag, domain_list)
        for tag in domain_resolve:
            datachecker.check_choice("domain_resolve", tag, domain_list)


def _check_data_conflict(domain_list, data_conflict):
    """
    Check the validity of the rules to solve conflict between domains.
    """

    # check type
    key_list = [
        "resolve_rules",
        "resolve_random",
        "conflict_rules",
    ]
    datachecker.check_dict("data_conflict", data_conflict, key_list=key_list)

    # check type
    datachecker.check_boolean("resolve_rules", data_conflict["resolve_rules"])
    datachecker.check_boolean("resolve_random", data_conflict["resolve_random"])
    datachecker.check_list("conflict_rules", data_conflict["conflict_rules"], can_be_empty=True)
    _check_conflict_rules(domain_list, data_conflict["conflict_rules"])


def _check_domain_integrity(domain_list, domain_integrity):
    """
    Check the domain integrity rules.
    """

    # check type
    datachecker.check_dict("domain_integrity", domain_integrity)

    # check value
    for domain_tmp in domain_integrity.values():
        # check type
        key_list = ["connected", "domain_group"]
        datachecker.check_dict("domain_integrity", domain_tmp, key_list=key_list)

        # extract field
        domain_group = domain_tmp["domain_group"]
        connected = domain_tmp["connected"]

        # check type
        datachecker.check_boolean("connected", connected)
        datachecker.check_list("domain_group", domain_group, can_be_empty=False)

        # check value
        for domain_group_tmp in domain_group:
            datachecker.check_list("domain_group", domain_group_tmp, sub_type=str, can_be_empty=False)
            for tag in domain_group_tmp:
                datachecker.check_choice("domain_group", tag, domain_list)


def _check_data_integrity(domain_list, data_integrity):
    """
    Check the validity of the rules to check the mesh integrity.
    """

    # check type
    key_list = [
        "domain_connected",
        "domain_adjacent",
    ]
    datachecker.check_dict("data_integrity", data_integrity, key_list=key_list)

    # check type
    datachecker.check_dict("domain_connected", data_integrity["domain_connected"], can_be_empty=True)
    datachecker.check_dict("domain_adjacent", data_integrity["domain_adjacent"], can_be_empty=True)
    _check_domain_integrity(domain_list, data_integrity["domain_connected"])
    _check_domain_integrity(domain_list, data_integrity["domain_adjacent"])


def check_data_geometry(data_geometry):
    """
    Check the mesher data type and extract the data.
    """

    # check type
    key_list = [
        "mesh_type",
        "data_voxelize",
        "data_point",
        "data_resampling",
        "data_conflict",
        "data_integrity",
    ]
    datachecker.check_dict("data_geometry", data_geometry, key_list=key_list)

    # extract field
    mesh_type = data_geometry["mesh_type"]
    data_voxelize = data_geometry["data_voxelize"]
    data_point = data_geometry["data_point"]
    data_resampling = data_geometry["data_resampling"]
    data_conflict = data_geometry["data_conflict"]
    data_integrity = data_geometry["data_integrity"]

    # check type
    datachecker.check_choice("mesh_type", mesh_type, ["stl", "png", "shape", "voxel"])

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
    _check_data_resampling(data_resampling)

    # check the resampling data
    _check_data_point(data_point)

    # check the conflict data
    _check_data_conflict(domain_list, data_conflict)

    # check the integrity data
    _check_data_integrity(domain_list, data_integrity)
