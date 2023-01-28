"""
Module for checking the mesher data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
from PyPEEC.lib_utils.error import CheckError


def _check_voxel_domain_def(n, domain_def):
    """
    Check the domain definition (mapping between domain names and indices).
    """

    # extract the voxel data
    (nx, ny, nz) = n
    n = nx*ny*nz

    # init the domain indices
    idx_domain = np.array([], dtype=np.int64)

    # check type
    if not isinstance(domain_def, dict):
        raise CheckError("domain_def: domain definition should be a dict")
    if not domain_def:
        raise CheckError("domain_def: domain definition cannot be empty")

    # check the different domains
    for tag, idx in domain_def.items():
        # check tag
        if not isinstance(tag, str):
            raise CheckError("tag: domain name should be a string")

        # cast indices
        idx = np.array(idx, dtype=np.int64)
        if not (len(idx.shape) == 1):
            raise CheckError("idx: indices should be a vector")
        if not np.issubdtype(idx.dtype, np.integer):
            raise CheckError("idx: indices should be composed of integers")

        # check for indices range
        if not (np.all(idx >= 0) and np.all(idx < n)):
            raise CheckError("idx: domain indices should belong to the voxel structure")

        # append
        idx_domain = np.append(idx_domain, idx)

    # check for duplicates
    if not (len(np.unique(idx_domain)) == len(idx_domain)):
        raise CheckError("domain indices should be unique")


def _check_voxel_size(n, d, c):
    """
    Check the voxel number, placement, and dimension.
    """

    # check size
    if not (len(n) == 3):
        raise CheckError("n: invalid voxel number (should be a list with three elements)")
    if not (len(d) == 3):
        raise CheckError("d: invalid voxel size (should be a list with three elements)")
    if not (len(c) == 3):
        raise CheckError("c: invalid center coordinate size (should be a list with three elements)")

    # check type
    if not all(np.issubdtype(type(x), np.integer) for x in n):
        raise CheckError("n: number of voxels should be composed of integers")
    if not all(np.issubdtype(type(x), np.floating) for x in d):
        raise CheckError("d: dimension of the voxels should be composed of real floats")
    if not all(np.issubdtype(type(x), np.floating) for x in c):
        raise CheckError("c: center coordinate should be composed of real floats")

    # check value
    if not all((x >= 1) for x in n):
        raise CheckError("n: number of voxels cannot be smaller than one")
    if not all((x > 0) for x in d):
        raise CheckError("d: dimension of the voxels should be positive")


def _check_png_domain_color(domain_color):
    """
    Check that the mapping between the pixel colors and the domains is valid (PNG mesher).
    """

    # check type
    if not isinstance(domain_color, dict):
        raise CheckError("domain_color: domain color definition should be a dict")
    if not domain_color:
        raise CheckError("domain_color: domain color definition cannot be empty")

    # check value
    for tag, color in domain_color.items():
        # check tag
        if not isinstance(tag, str):
            raise CheckError("tag: conductor name should be a string")

        # check size
        if not (len(color) == 4):
            raise CheckError("color: invalid color (should be an array with four elements)")

        # check type
        if not all(np.issubdtype(type(x), np.integer) for x in color):
            raise CheckError("color: color array should be composed of integers")


def _check_png_layer_stack(layer_stack):
    """
    Check the validity of the image layer stack (PNG mesher).
    """

    # check type
    if not isinstance(layer_stack, list):
        raise CheckError("layer_stack: layer stack definition should be a list")
    if not layer_stack:
        raise CheckError("layer_stack: layer stack definition cannot be empty")

    # check value
    for layer_stack_tmp in layer_stack:
        # get the data
        n_layer = layer_stack_tmp["n_layer"]
        filename = layer_stack_tmp["filename"]

        # check type
        if not isinstance(n_layer, int):
            raise CheckError("n_layer: number of layers should be an integer")
        if not isinstance(filename, str):
            raise CheckError("filename: filename should be a string")

        # check value
        if not (n_layer >= 1):
            raise CheckError("n_layer: number of layers cannot be smaller than one")


def _check_stl_pts(pts):
    """
    Check that the points defining the voxel structure bounds are valid (STL mesher).
    """

    # check size
    if not (len(pts) == 3):
        raise CheckError("pts: invalid point size (should be a list with three elements)")

    # check type
    if not all(np.issubdtype(type(x), np.floating) or (x is None) for x in pts):
        raise CheckError("pts: the coordinates of a point should be composed of real floats")


def _check_stl_domain_stl(domain_stl):
    """
    Check the validity of the domain definition (STL mesher).
    """

    # check type
    if not isinstance(domain_stl, dict):
        raise CheckError("domain_stl: domain definition should be a dict")
    if not domain_stl:
        raise CheckError("domain_stl: domain definition cannot be empty")

    # check value
    for tag, filename in domain_stl.items():
        # check tag
        if not isinstance(tag, str):
            raise CheckError("tag: conductor name should be a string")

        # check type
        if not isinstance(filename, str):
            raise CheckError("filename: filename should be a string")


def _check_stl_domain_conflict(domain_conflict):
    """
    Check the validity of the rules to solve conflict between domains (STL mesher).
    """

    # check type
    if not isinstance(domain_conflict, list):
        raise CheckError("domain_conflict: domain conflict should be a list")

    # check value
    for domain_conflict_tmp in domain_conflict:
        # extract data
        domain_keep = domain_conflict_tmp["domain_keep"]
        domain_resolve = domain_conflict_tmp["domain_resolve"]

        # check type
        if not isinstance(domain_keep, str):
            raise CheckError("domain_keep: domain name should be a string")
        if not isinstance(domain_resolve, str):
            raise CheckError("domain_resolve: domain name should be a string")


def _check_stl_domain_name(domain_conflict, domain_name):
    """
    Check the consistency of the domain names.
    """

    for domain_conflict_tmp in domain_conflict:
        # extract data
        domain_resolve = domain_conflict_tmp["domain_resolve"]
        domain_keep = domain_conflict_tmp["domain_keep"]

        # check value
        if domain_resolve not in domain_name:
            raise CheckError("domain_resolve: domain name is invalid")
        if domain_keep not in domain_name:
            raise CheckError("domain_keep: domain name is invalid")


def _check_data_voxelize_png(data_voxelize):
    """
    Check the data used for voxelization (PNG mesher).
    """

    # check type
    if not isinstance(data_voxelize, dict):
        raise CheckError("data_voxelize: mesher data should be a dict")

    # extract field
    d = data_voxelize["d"]
    c = data_voxelize["c"]
    nx = data_voxelize["nx"]
    ny = data_voxelize["ny"]
    domain_color = data_voxelize["domain_color"]
    layer_stack = data_voxelize["layer_stack"]

    # check size
    if not (len(d) == 3):
        raise CheckError("d: invalid voxel size (should be a list with three elements)")
    if not (len(c) == 3):
        raise CheckError("c: invalid center coordinate size (should be a list with three elements)")

    # check type
    if not all(np.issubdtype(type(x), np.floating) for x in d):
        raise CheckError("d: dimension of the voxels should be composed of real floats")
    if not all(np.issubdtype(type(x), np.floating) for x in c):
        raise CheckError("c: center coordinate should be composed of real floats")
    if not np.issubdtype(type(nx), np.integer):
        raise CheckError("nx: number of voxel in x direction should be an integer")
    if not np.issubdtype(type(ny), np.integer):
        raise CheckError("ny: number of voxel in y direction should be an integer")

    # check value
    if not all((x > 0) for x in d):
        raise CheckError("d: dimension of the voxels should be positive")
    if not (nx >= 1):
        raise CheckError("nx: of voxel in x direction cannot be smaller than one")
    if not (ny >= 1):
        raise CheckError("ny: of voxel in y direction cannot be smaller than one")

    # check domains and layers
    _check_png_domain_color(domain_color)
    _check_png_layer_stack(layer_stack)

    # get name
    domain_name = domain_color.keys()

    return domain_name


def _check_data_voxelize_stl(data_voxelize):
    """
    Check the data used for voxelization (STL mesher).
    """

    # check type
    if not isinstance(data_voxelize, dict):
        raise CheckError("data_voxelize: mesher data should be a dict")

    # extract field
    n = data_voxelize["n"]
    pts_min = data_voxelize["pts_min"]
    pts_max = data_voxelize["pts_max"]
    domain_stl = data_voxelize["domain_stl"]
    domain_conflict = data_voxelize["domain_conflict"]

    # check size
    if not (len(n) == 3):
        raise CheckError("n: invalid voxel number (should be a list with three elements)")

    # check type
    if not all(np.issubdtype(type(x), np.integer) for x in n):
        raise CheckError("n: number of voxels should be composed of integers")

    # check value
    if not all((x >= 1) for x in n):
        raise CheckError("n: number of voxels cannot be smaller than one")

    # check the points
    _check_stl_pts(pts_min)
    _check_stl_pts(pts_max)

    # check the stl file
    _check_stl_domain_stl(domain_stl)
    _check_stl_domain_conflict(domain_conflict)

    # get name
    domain_name = domain_stl.keys()

    # check domain name
    _check_stl_domain_name(domain_conflict, domain_name)

    return domain_name


def _check_data_voxelize_voxel(data_voxelize):
    """
    Check the voxel structure (number, placement, and dimension).
    Check the mapping between domain names and indices.
    """

    # check type
    if not isinstance(data_voxelize, dict):
        raise CheckError("data_voxelize: voxel description should be a dict")

    # extract field
    n = data_voxelize["n"]
    d = data_voxelize["d"]
    c = data_voxelize["c"]
    domain_def = data_voxelize["domain_def"]

    # check data
    _check_voxel_size(n, d, c)
    _check_voxel_domain_def(n, domain_def)

    # get name
    domain_name = domain_def.keys()

    return domain_name


def _check_resampling_factor(resampling_factor):
    """
    Check the resampling data.
    This vector is controlling the resampling of a voxel structure.
    """

    # check size
    if not (len(resampling_factor) == 3):
        raise CheckError("resampling_factor: invalid voxel resampling (should be a list with three elements)")

    # check type
    if not all(np.issubdtype(type(x), np.integer) for x in resampling_factor):
        raise CheckError("resampling_factor: number of resampling should be composed of integers")

    # check value
    if not all((x >= 1) for x in resampling_factor):
        raise CheckError("resampling_factor: number of resampling cannot be smaller than one")


def _check_domain_connection(domain_connection, domain_name):
    """
    Check the domain connection data.
    This list is defining the required connection between the domain
    """

    # check type
    if not isinstance(domain_connection, dict):
        raise CheckError("domain_connection: domain connection check should be a dict")

    # check value
    for tag, dat_tmp in domain_connection.items():
        # check type
        if not isinstance(tag, str):
            raise CheckError("domain_connection: domain connection name should be a tring")
        if not isinstance(dat_tmp, dict):
            raise CheckError("domain_connection: domain connection check should be a dict")

        # extract field
        domain_list = dat_tmp["domain_list"]
        connected = dat_tmp["connected"]

        # check type
        if not isinstance(domain_list, list):
            raise CheckError("domain_list: connected domain names should be a list")
        if not domain_list:
            raise CheckError("domain_list: connected domain names should not be empty")
        if not isinstance(connected, bool):
            raise CheckError("connected: domain connection flag should be a boolean")

        # check value
        for tag in domain_list:
            if not isinstance(tag, str):
                raise CheckError("domain_list: domain name should be a string")
            if tag not in domain_name:
                raise CheckError("domain_list: domain name is invalid")


def get_domain_stl_path(domain_stl, path_ref):
    """
    Update the filename of the STL files with respect to the provided path.
    """

    # if none, the specified path are already correct
    if path_ref is None:
        return domain_stl

    # check the path
    if not isinstance(path_ref, str):
        raise CheckError("path_ref: path_ref should be a string or none")

    # init new domain description
    domain_stl_path = dict()

    # check value
    for tag, filename in domain_stl.items():
        # check file
        filename = path_ref + "/" + filename
        try:
            fid = open(filename, "rb")
            fid.close()
        except FileNotFoundError:
            raise CheckError("filename: file does not exist: %s" % filename)

        # add the new item
        domain_stl_path[tag] = filename

    return domain_stl_path


def get_layer_stack_path(layer_stack, path_ref):
    """
    Update the filename of the PNG images with respect to the provided path.
    """

    # if none, the specified path are already correct
    if path_ref is None:
        return layer_stack

    # check the path
    if not isinstance(path_ref, str):
        raise CheckError("path_ref: path_ref should be a string or none")

    # init new layer stack
    layer_stack_path = []

    # update value
    for layer_stack_tmp in layer_stack:
        # get the data
        n_layer = layer_stack_tmp["n_layer"]
        filename = layer_stack_tmp["filename"]

        # check file
        filename = path_ref + "/" + filename
        try:
            fid = open(filename, "rb")
            fid.close()
        except FileNotFoundError:
            raise CheckError("filename: file does not exist: %s" % filename)

        # add the new item
        layer_stack_path.append({"n_layer": n_layer, "filename": filename})

    return layer_stack_path


def check_data_mesher(data_mesher):
    """
    Check the mesher data type and extract the data.
    """

    # check type
    if not isinstance(data_mesher, dict):
        raise CheckError("data_mesher: mesher data should be a dict")

    # extract field
    mesh_type = data_mesher["mesh_type"]
    data_voxelize = data_mesher["data_voxelize"]
    resampling_factor = data_mesher["resampling_factor"]
    domain_connection = data_mesher["domain_connection"]

    # check type
    if not isinstance(mesh_type, str):
        raise CheckError("mesh_type: mesher type should be a string")

    # check value
    if mesh_type not in ["stl", "png", "voxel"]:
        raise CheckError("mesh_type: specified mesh type does not exist")

    # check the mesher
    if mesh_type == "png":
        domain_name = _check_data_voxelize_png(data_voxelize)
    elif mesh_type == "stl":
        domain_name = _check_data_voxelize_stl(data_voxelize)
    elif mesh_type == "voxel":
        domain_name = _check_data_voxelize_voxel(data_voxelize)
    else:
        raise CheckError("invalid mesh type")

    # check the resampling data
    _check_resampling_factor(resampling_factor)

    # check the connection data
    _check_domain_connection(domain_connection, domain_name)
