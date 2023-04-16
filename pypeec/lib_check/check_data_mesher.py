"""
Module for checking the mesher data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import os.path
import numpy as np
from pypeec.lib_check import datachecker
from pypeec import config

# get config
NP_TYPES = config.NP_TYPES


def _get_filename(path_ref, filename):
    """
    Form a file path from a file name.
    Check if a filename is valid.
    """

    # form the complete path
    if (path_ref is not None) and (not os.path.isabs(filename)):
        datachecker.check_string("path_ref", path_ref)
        datachecker.check_string("filename", filename)
        filename = os.path.join(path_ref, filename)

    # check that the file exist
    datachecker.check_filename("filename", filename)

    return filename


def _get_domain_stl(domain_stl, path_ref):
    """
    Update the filename of the STL files with respect to the provided path.
    """

    # init new domain description
    domain_stl_path = {}

    # check value
    for tag, domain_stl_tmp in domain_stl.items():
        # get the data
        offset = domain_stl_tmp["offset"]
        filename_list = domain_stl_tmp["filename_list"]

        # check file
        filename_list_path = []
        for filename in filename_list:
            filename = _get_filename(path_ref, filename)
            filename_list_path.append(filename)

        # add the new item
        domain_stl_path[tag] = {"offset": offset, "filename_list": filename_list_path}

    return domain_stl_path


def _get_layer_stack(layer_stack, path_ref):
    """
    Update the filename of the PNG images with respect to the provided path.
    """

    # init new layer stack
    layer_stack_path = []

    # update value
    for layer_stack_tmp in layer_stack:
        # get the data
        n_layer = layer_stack_tmp["n_layer"]
        filename_list = layer_stack_tmp["filename_list"]

        # check file
        filename_list_path = []
        for filename in filename_list:
            filename = _get_filename(path_ref, filename)
            filename_list_path.append(filename)

        # add the new item
        layer_stack_path.append({"n_layer": n_layer, "filename_list": filename_list_path})

    return layer_stack_path


def _check_data_voxelize_png(data_voxelize, path_ref):
    """
    Check the data used for voxelization (PNG mesher).
    """

    # extract field
    d = data_voxelize["d"]
    c = data_voxelize["c"]
    size = data_voxelize["size"]
    domain_color = data_voxelize["domain_color"]
    layer_stack = data_voxelize["layer_stack"]

    # update data
    layer_stack = _get_layer_stack(layer_stack, path_ref)

    # assemble data
    data_voxelize = {
        "d": d,
        "c": c,
        "size": size,
        "domain_color": domain_color,
        "layer_stack": layer_stack,
    }

    return data_voxelize


def _check_data_voxelize_stl(data_voxelize, path_ref):
    """
    Check the data used for voxelization (STL mesher).
    """

    # extract field
    n = data_voxelize["n"]
    d = data_voxelize["d"]
    c = data_voxelize["c"]
    sampling = data_voxelize["sampling"]
    xyz_min = data_voxelize["xyz_min"]
    xyz_max = data_voxelize["xyz_max"]
    domain_stl = data_voxelize["domain_stl"]

    # update data
    domain_stl = _get_domain_stl(domain_stl, path_ref)

    # assemble data
    data_voxelize = {
        "d": d,
        "c": c,
        "n": n,
        "sampling": sampling,
        "xyz_min": xyz_min,
        "xyz_max": xyz_max,
        "domain_stl": domain_stl,
    }

    return data_voxelize


def get_data_mesher(data_geometry, path_ref):
    """
    Check the mesher data type and extract the data.
    """

    # extract field
    mesh_type = data_geometry["mesh_type"]
    data_voxelize = data_geometry["data_voxelize"]
    resampling = data_geometry["resampling"]
    domain_conflict = data_geometry["domain_conflict"]
    domain_connection = data_geometry["domain_connection"]

    # check the mesher
    if mesh_type == "png":
        data_voxelize = _check_data_voxelize_png(data_voxelize, path_ref)
    elif mesh_type == "stl":
        data_voxelize = _check_data_voxelize_stl(data_voxelize, path_ref)
    elif mesh_type == "voxel":
        pass
    else:
        raise ValueError("invalid mesh type")

    # assemble the results
    data_mesher = {
        "mesh_type": mesh_type,
        "data_voxelize": data_voxelize,
        "resampling": resampling,
        "domain_conflict": domain_conflict,
        "domain_connection": domain_connection,
    }

    return data_mesher
