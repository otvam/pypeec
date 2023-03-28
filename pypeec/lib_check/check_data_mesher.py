"""
Module for checking the mesher data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import os.path
import numpy as np
from pypeec.lib_utils import datachecker
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


def _get_domain_def(n, domain_def):
    """
    Check the domain definition (mapping between domain names and indices).
    """

    # extract the voxel data
    (nx, ny, nz) = n
    nv = nx*ny*nz

    # init new domain indices
    domain_def_array = {}

    # check data
    idx_all = np.array([], dtype=NP_TYPES.INT)
    for tag, idx in domain_def.items():
        # parse the array
        idx_tmp = np.array(idx, dtype=NP_TYPES.INT)
        idx_all = np.append(idx_all, idx_tmp)

        # add the new item
        domain_def_array[tag] = idx_tmp

    # check the indices
    datachecker.check_index_array("domain_def", idx_all, bnd=nv, can_be_empty=False)

    return domain_def_array


def _check_data_voxelize_png(data_voxelize, path_ref):
    """
    Check the data used for voxelization (PNG mesher).
    """

    # extract field
    d = data_voxelize["d"]
    c = data_voxelize["c"]
    nx = data_voxelize["nx"]
    ny = data_voxelize["ny"]
    domain_color = data_voxelize["domain_color"]
    layer_stack = data_voxelize["layer_stack"]

    # update data
    layer_stack = _get_layer_stack(layer_stack, path_ref)

    # assemble data
    data_voxelize = {
        "d": d,
        "c": c,
        "nx": nx,
        "ny": ny,
        "domain_color": domain_color,
        "layer_stack": layer_stack,
    }

    return data_voxelize


def _check_data_voxelize_stl(data_voxelize, path_ref):
    """
    Check the data used for voxelization (STL mesher).
    """

    # check type
    key_list = ["n", "d", "c", "sampling", "pts_min", "pts_max", "domain_stl"]
    datachecker.check_dict("data_voxelize", data_voxelize, key_list=key_list)

    # extract field
    n = data_voxelize["n"]
    d = data_voxelize["d"]
    c = data_voxelize["c"]
    sampling = data_voxelize["sampling"]
    pts_min = data_voxelize["pts_min"]
    pts_max = data_voxelize["pts_max"]
    domain_stl = data_voxelize["domain_stl"]

    # update data
    domain_stl = _get_domain_stl(domain_stl, path_ref)

    # assemble data
    data_voxelize = {
        "d": d,
        "c": c,
        "n": n,
        "sampling": sampling,
        "pts_min": pts_min,
        "pts_max": pts_max,
        "domain_stl": domain_stl,
    }

    return data_voxelize


def _check_data_voxelize_voxel(data_voxelize):
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

    # update data
    domain_def = _get_domain_def(n, domain_def)

    # assemble data
    data_voxelize = {
        "d": d,
        "c": c,
        "n": n,
        "domain_def": domain_def,
    }

    return data_voxelize


def get_data_mesher(data_geometry, path_ref):
    """
    Check the mesher data type and extract the data.
    """

    # extract field
    mesh_type = data_geometry["mesh_type"]
    data_voxelize = data_geometry["data_voxelize"]
    resampling_factor = data_geometry["resampling_factor"]
    domain_conflict = data_geometry["domain_conflict"]
    domain_connection = data_geometry["domain_connection"]

    # check the mesher
    if mesh_type == "png":
        data_voxelize = _check_data_voxelize_png(data_voxelize, path_ref)
    elif mesh_type == "stl":
        data_voxelize = _check_data_voxelize_stl(data_voxelize, path_ref)
    elif mesh_type == "voxel":
        data_voxelize = _check_data_voxelize_voxel(data_voxelize)
    else:
        raise ValueError("invalid mesh type")

    # assemble the results
    data_mesher = {
        "mesh_type": mesh_type,
        "data_voxelize" : data_voxelize,
        "resampling_factor": resampling_factor,
        "domain_conflict": domain_conflict,
        "domain_connection": domain_connection,
    }

    return data_mesher
