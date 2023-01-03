"""
Module for checking and extracting the solver input data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np


class CheckError(Exception):
    """
    Exception used for signaling invalid input data.
    """

    pass


def __check_conductor(idx_v, conductor):
    """
    Check that the conductors are valid.
    Append the conductor indices to an array.
    """

    for dat_tmp in conductor:
        # extract the data
        idx = dat_tmp["idx"]
        rho = dat_tmp["rho"]

        # check the resistivity
        if not np.isscalar(rho):
            raise CheckError("conductor resistivity should be a scalar")
        if not np.isreal(rho):
            raise CheckError("conductor resistivity should be real")
        if not (rho > 0):
            raise CheckError("conductor resistivity should be greater than zero")

        # append the indices
        idx_v = np.append(idx_v, np.array(idx))

    return idx_v


def __check_src(idx_src, tag_src, src):
    """
    Check that the sources (voltage or current) are valid.
    Append the source tag to a list.
    Append the source indices to an array.
    """

    for dat_tmp in src:
        # extract the data
        tag = dat_tmp["tag"]
        idx = dat_tmp["idx"]
        value = dat_tmp["value"]

        # check the source value and tag
        if not np.isscalar(value):
            raise CheckError("source value should be a scalar")
        if not isinstance(tag, str):
            raise CheckError("source name should be a string")

        # append the tag and indices
        tag_src.append(tag)
        idx_src = np.append(idx_src, np.array(idx))

    return idx_src, tag_src


def check_voxel(data_solver):
    """
    Check and extract the voxel structure (number and size) and the Green function parameter.
    """

    # extract field
    n = data_solver["n"]
    d = data_solver["d"]
    n_green_simplify = data_solver["n_green_simplify"]

    # check size
    if not (len(n) == 3):
        raise CheckError("invalid voxel number (should be three)")
    if not (len(d) == 3):
        raise CheckError("invalid voxel size (should be three)")

    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d

    # check value
    if not ((nx >= 1) and (ny >= 1) and (nz >= 1)):
        raise CheckError("number of voxels cannot be smaller than one")
    if not ((dx > 0) and (dy > 0) and (dz > 0)):
        raise CheckError("voxel dimension cannot be zero or smaller")
    if not (n_green_simplify > 0):
        raise CheckError("voxel distance to simplify the green function cannot be zero of smaller")

    return n, d, n_green_simplify


def check_problem(data_solver):
    """
    Check and extract the conductors and sources.
    More particularly, check that the indices of the voxels are valid.
    """

    # extract field
    conductor = data_solver["conductor"]
    src_current = data_solver["src_current"]
    src_voltage = data_solver["src_voltage"]
    n = data_solver["n"]

    # extract the voxel data
    (nx, ny, nz) = n
    n = nx*ny*nz

    # check type
    if not isinstance(conductor, list):
        raise CheckError("solver options should be a dict")
    if not isinstance(src_current, list):
        raise CheckError("solver options should be a dict")
    if not isinstance(src_voltage, list):
        raise CheckError("solver options should be a dict")

    # check the conductor
    idx_v = np.array([], dtype=np.int64)
    idx_src = np.array([], dtype=np.int64)
    tag_src = []

    # find the indices and tags
    idx_v = __check_conductor(idx_v, conductor)
    (idx_src, tag_src) = __check_src(idx_src, tag_src, src_current)
    (idx_src, tag_src) = __check_src(idx_src, tag_src, src_voltage)

    # check for unicity
    if not (len(np.unique(idx_v)) == len(idx_v)):
        raise CheckError("conductor indices should be unique")
    if not (len(np.unique(idx_src)) == len(idx_src)):
        raise CheckError("source indices should be unique")
    if not (len(np.unique(tag_src)) == len(tag_src)):
        raise CheckError("source tag should be unique")

    # check for indices range
    if not (np.all(idx_v >= 0) and np.all(idx_v < n)):
        raise CheckError("conductor indices should belong to the voxel structure")
    if not (np.all(idx_src >= 0) and np.all(idx_src < n)):
        raise CheckError("source indices should belong to the voxel structure")

    # check that the terminal indices are conductor indices
    if not np.all(np.isin(idx_src, idx_v)):
        "source indices are not included in conductor indices"

    return conductor, src_current, src_voltage


def check_solver(data_solver):
    """
    Check and extract the frequency and the solver options.
    """

    # extract field
    freq = data_solver["freq"]
    solver_options = data_solver["solver_options"]

    # check frequency
    if not(freq >= 0):
        raise CheckError("frequency cannot be negative")

    # check solver options
    if not isinstance(solver_options, dict):
        raise CheckError("solver options should be a dict")
    if not (solver_options["tol"] > 0):
        raise CheckError("solver relative tolerance should be greater than zero")
    if not (solver_options["atol"] > 0):
        raise CheckError("solver absolute tolerance should be greater than zero")
    if not (solver_options["restart"] >= 1):
        raise CheckError("number of iterations between restarts should be greater than zero")
    if not (solver_options["maxiter"] >= 1):
        raise CheckError("number of restart cycles should be greater than zero")
    if not (solver_options["condmax"] > 0):
        raise CheckError("maximum condition number should be greater than zero")

    return freq, solver_options
