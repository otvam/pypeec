"""
Module for checking the viewer input data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np


class CheckError(Exception):
    """
    Exception used for signaling invalid input data.
    """

    pass


def _check_pts(pts):
    # check size
    if not (len(pts) == 3):
        raise CheckError("pts: invalid point size (should be a tuple with three elements)")

    # check type
    if not all(np.issubdtype(type(x), np.floating) or (x is None) for x in pts):
        raise CheckError("pts: the coordinates of a point should be composed of real floats")


def _check_resampling(use_resampling, n_resampling):
    # check type
    if not isinstance(use_resampling, bool):
        raise CheckError("use_resampling: resampling flag should be a boolean")

    # check size
    if not (len(n_resampling) == 3):
        raise CheckError("n_resampling: invalid voxel resampling (should be a tuple with three elements)")

    # check type
    if not all(np.issubdtype(type(x), np.integer) for x in n_resampling):
        raise CheckError("n_resampling: number of resampling should be composed of integers")

    # check value
    if not all((x >= 1) for x in n_resampling):
        raise CheckError("n_resampling: number of resampling cannot be smaller than one")


def _check_domain_color(domain_color):
    """
    Check that the conductor definition is valid.
    """

    # check type
    if not isinstance(domain_color, dict):
        raise CheckError("domain_color: domain color definition should be a dict")

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


def _check_layer_stack(layer_stack):
    # check type
    if not isinstance(layer_stack, list):
        raise CheckError("layer_stack: layer stack definition should be a list")

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

        # check file
        try:
            fid = open(filename, "rb")
            fid.close()
        except FileNotFoundError:
            raise CheckError("filename: file does not exist")


def _check_domain_stl(domain_stl):
    # check type
    if not isinstance(domain_stl, dict):
        raise CheckError("domain_stl: domain definition should be a dict")

    # check value
    for tag, filename in domain_stl.items():
        # check tag
        if not isinstance(tag, str):
            raise CheckError("tag: conductor name should be a string")

        # check type
        if not isinstance(filename, str):
            raise CheckError("filename: filename should be a string")

        # check file
        try:
            fid = open(filename, "rb")
            fid.close()
        except FileNotFoundError:
            raise CheckError("filename: file does not exist")


def check_mesher_type(mesh_type):
    """
    Check the validity of the dict describing a plot.
    """

    # check type
    if not isinstance(mesh_type, str):
        raise CheckError("mesh_type: mesher type should be a string")

    # check value
    if mesh_type not in ["stl", "png"]:
        raise CheckError("mesh_type: specified mesh type does not exist")


def check_data_mesher_png(data_mesher):
    """
    Check the voxel structure (number and size).
    Check the domain definition (mapping between domain names and indices).
    """

    # check type
    if not isinstance(data_mesher, dict):
        raise CheckError("data_mesher: invalid input data")

    # extract field
    d = data_mesher["d"]
    nx = data_mesher["nx"]
    ny = data_mesher["ny"]
    use_resampling = data_mesher["use_resampling"]
    n_resampling = data_mesher["n_resampling"]
    domain_color = data_mesher["domain_color"]
    layer_stack = data_mesher["layer_stack"]

    # check size
    if not (len(d) == 3):
        raise CheckError("d: invalid voxel size (should be a tuple with three elements)")

    # check type
    if not all(np.issubdtype(type(x), np.floating) for x in d):
        raise CheckError("d: dimension of the voxels should be composed of real floats")
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

    # check resampling
    _check_resampling(use_resampling, n_resampling)

    # check domains and layers
    _check_domain_color(domain_color)
    _check_layer_stack(layer_stack)


def check_data_mesher_stl(data_mesher):
    """
    Check the voxel structure (number and size).
    Check the domain definition (mapping between domain names and indices).
    """

    # check type
    if not isinstance(data_mesher, dict):
        raise CheckError("data_mesher: invalid input data")

    # extract field
    n = data_mesher["n"]
    pts_min = data_mesher["pts_min"]
    pts_max = data_mesher["pts_max"]
    use_resampling = data_mesher["use_resampling"]
    n_resampling = data_mesher["n_resampling"]
    domain_stl = data_mesher["domain_stl"]

    # check size
    if not (len(n) == 3):
        raise CheckError("n: invalid voxel number (should be a tuple with three elements)")

    # check type
    if not all(np.issubdtype(type(x), np.integer) for x in n):
        raise CheckError("n: number of voxels should be composed of integers")

    # check value
    if not all((x >= 1) for x in n):
        raise CheckError("n: number of voxels cannot be smaller than one")

    # check resampling
    _check_resampling(use_resampling, n_resampling)

    # check the points
    _check_pts(pts_min)
    _check_pts(pts_max)

    # check the stl file
    _check_domain_stl(domain_stl)
