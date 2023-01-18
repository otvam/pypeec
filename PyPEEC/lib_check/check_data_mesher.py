"""
Module for checking the mesher data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
from PyPEEC.lib_utils.error import CheckError


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
    for dat_tmp in layer_stack:
        # get the data
        n_add = dat_tmp["n_add"]
        filename = dat_tmp["filename"]

        # check type
        if not isinstance(n_add, int):
            raise CheckError("n_add: number of layers should be an integer")
        if not isinstance(filename, str):
            raise CheckError("filename: filename should be a string")

        # check value
        if not (n_add >= 1):
            raise CheckError("n_add: number of layers cannot be smaller than one")


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
    Check the validity of the rules to solve conflict between domains (STL mesher).
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
    Check the validity of the domain definition (STL mesher).
    Check the validity of the rules to solve conflict between domains (STL mesher).
    """

    # check type
    if not isinstance(domain_conflict, list):
        raise CheckError("domain_conflict: domain conflict should be a list")

    # check value
    for dat_tmp in domain_conflict:
        # extract data
        domain_ref = dat_tmp["domain_ref"]
        domain_fix = dat_tmp["domain_fix"]

        # check type
        if not isinstance(domain_ref, str):
            raise CheckError("domain_ref: domain name should be a string")
        if not isinstance(domain_fix, str):
            raise CheckError("domain_fix: domain name should be a string")


def _check_stl_domain_name(domain_stl, domain_conflict):
    """
    Check the consistency of the domain names.
    """

    for dat_tmp in domain_conflict:
        # extract data
        domain_ref = dat_tmp["domain_ref"]
        domain_fix = dat_tmp["domain_fix"]

        # check value
        if domain_ref not in domain_stl:
            raise CheckError("domain_ref: domain name should be a valid domain name")
        if domain_fix not in domain_stl:
            raise CheckError("domain_fix: domain name should be a valid domain name")


def check_data_mesher(data_mesher):
    """
    Check the validity of the mesh type.
    """

    # check type
    if not isinstance(data_mesher, dict):
        raise CheckError("data_mesher: mesher data should be a dict")

    # extract field
    mesh_type = data_mesher["mesh_type"]
    data_voxelize = data_mesher["data_voxelize"]
    data_resampling = data_mesher["data_resampling"]

    return mesh_type, data_voxelize, data_resampling


def check_mesh_type(mesh_type):
    """
    Check the validity of the mesh type.
    """

    # check type
    if not isinstance(mesh_type, str):
        raise CheckError("mesh_type: mesher type should be a string")

    # check value
    if mesh_type not in ["stl", "png", "voxel"]:
        raise CheckError("mesh_type: specified mesh type does not exist")


def check_data_voxelize_png(data_voxelize):
    """
    Check the mesher structure (PNG mesher).
    """

    # check type
    if not isinstance(data_voxelize, dict):
        raise CheckError("data_mesher: mesher data should be a dict")

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


def check_data_voxelize_stl(data_voxelize):
    """
    Check the mesher structure (STL mesher).
    """

    # check type
    if not isinstance(data_voxelize, dict):
        raise CheckError("data_mesher: mesher data should be a dict")

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
    _check_stl_domain_name(domain_stl, domain_conflict)


def check_data_resampling(data_resampling):
    """
    Check the resampling data.
    These data are controlling the resampling of a voxel structure.
    """

    # check type
    if not isinstance(data_resampling, dict):
        raise CheckError("data_resampling: resampling data should be a dict")

    # extract field
    use_resampling = data_resampling["use_resampling"]
    n_resampling = data_resampling["n_resampling"]

    # check type
    if not isinstance(use_resampling, bool):
        raise CheckError("use_resampling: resampling flag should be a boolean")

    # check size
    if not (len(n_resampling) == 3):
        raise CheckError("n_resampling: invalid voxel resampling (should be a list with three elements)")

    # check type
    if not all(np.issubdtype(type(x), np.integer) for x in n_resampling):
        raise CheckError("n_resampling: number of resampling should be composed of integers")

    # check value
    if not all((x >= 1) for x in n_resampling):
        raise CheckError("n_resampling: number of resampling cannot be smaller than one")


def get_domain_stl_path(domain_stl, path_ref):
    """
    Update the filename of the STL files with respect to the provided path.
    """

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

    # init new layer stack
    layer_stack_path = []

    # update value
    for dat_tmp in layer_stack:
        # get the data
        n_add = dat_tmp["n_add"]
        filename = dat_tmp["filename"]

        # check file
        filename = path_ref + "/" + filename
        try:
            fid = open(filename, "rb")
            fid.close()
        except FileNotFoundError:
            raise CheckError("filename: file does not exist: %s" % filename)

        # add the new item
        layer_stack_path.append({"n_add": n_add, "filename": filename})

    return layer_stack_path
