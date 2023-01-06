"""
Module for checking the solver input data_output.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np


class CheckError(Exception):
    """
    Exception used for signaling invalid input data_output.
    """

    pass


def _check_conductor(idx_v, conductor):
    """
    Check that the conductors are valid.
    Append the conductor indices to an array.
    """

    for tag, dat_tmp in conductor.items():
        # extract the data_output
        idx = dat_tmp["idx"]
        rho = dat_tmp["rho"]

        # check the resistivity and tag
        if not isinstance(tag, str):
            raise CheckError("conductor name should be a string")
        if not np.isscalar(rho):
            raise CheckError("conductor resistivity should be a scalar")
        if not np.isreal(rho):
            raise CheckError("conductor resistivity should be real")
        if not (rho > 0):
            raise CheckError("conductor resistivity should be greater than zero")

        # append the indices
        idx_v = np.append(idx_v, np.array(idx))

    return idx_v


def _check_source(idx_src, tag_src, source):
    """
    Check that the sources (voltage or current) are valid.
    Append the source tag to a list.
    Append the source indices to an array.
    """

    for tag, dat_tmp in source.items():
        # extract the data_output
        source_type = dat_tmp["source_type"]
        idx = dat_tmp["idx"]
        value = dat_tmp["value"]

        # check the source value and tag
        if not isinstance(tag, str):
            raise CheckError("source name should be a string")
        if not np.isscalar(value):
            raise CheckError("source value should be a scalar")
        if not isinstance(source_type, str):
            raise CheckError("source type should be a string")
        if not ((source_type == "current") or (source_type == "voltage")):
            raise CheckError("source type should be voltage or current")

        # append the tag and indices
        tag_src.append(tag)
        idx_src = np.append(idx_src, np.array(idx))

    return idx_src, tag_src


def check_data_solver(data_solver):
    """
    Check the type of the input data_output.
    """

    if not isinstance(data_solver, dict):
        raise CheckError("invalid input data_output")


def check_voxel(data_solver):
    """
    Check the voxel structure (number and size) and the Green function parameter.
    """

    # extract field
    n = data_solver["n"]
    r = data_solver["r"]
    d = data_solver["d"]
    ori = data_solver["ori"]
    d_green = data_solver["d_green"]

    # check size
    if not (len(n) == 3):
        raise CheckError("invalid voxel number (should be a tuple with three elements)")
    if not (len(r) == 3):
        raise CheckError("invalid voxel resampling factor (should be a tuple with three elements)")
    if not (len(d) == 3):
        raise CheckError("invalid voxel size (should be a tuple with three elements)")
    if not (len(ori) == 3):
        raise CheckError("invalid voxel origin (should be a tuple with three elements)")

    # extract the voxel data_output
    (nx, ny, nz) = n
    (rx, ry, rz) = r
    (dx, dy, dz) = d

    # check value
    if not ((nx >= 1) and (ny >= 1) and (nz >= 1)):
        raise CheckError("number of voxels cannot be smaller than one")
    if not ((rx >= 1) and (ry >= 1) and (rz >= 1)):
        raise CheckError("number of resampling cannot be smaller than one")
    if not ((dx > 0) and (dy > 0) and (dz > 0)):
        raise CheckError("dimension of the voxels cannot be zero or smaller")
    if not (d_green > 0):
        raise CheckError("voxel distance to simplify the green function cannot be zero of smaller")


def check_problem(data_solver):
    """
    Check the conductors and sources.
    More particularly, check that the indices of the voxels are valid.
    """

    # extract field
    conductor = data_solver["conductor"]
    source = data_solver["source"]
    n = data_solver["n"]

    # extract the voxel data_output
    (nx, ny, nz) = n
    n = nx*ny*nz

    # check type
    if not isinstance(conductor, dict):
        raise CheckError("the conductor description should be a dict")
    if not isinstance(source, dict):
        raise CheckError("the source description should be a dict")

    # check the conductor
    idx_v = np.array([], dtype=np.int64)
    idx_src = np.array([], dtype=np.int64)
    tag_src = []

    # find the indices and tags
    idx_v = _check_conductor(idx_v, conductor)
    (idx_src, tag_src) = _check_source(idx_src, tag_src, source)

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


def check_solver(data_solver):
    """
    Check the frequency and the solver options.
    """

    # extract field
    freq = data_solver["freq"]
    solver_options = data_solver["solver_options"]
    condition_options = data_solver["condition_options"]

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

    # check condition options
    if not isinstance(condition_options, dict):
        raise CheckError("solver options should be a dict")
    if not isinstance(condition_options["check"], bool):
        raise CheckError("the flag for checking the condition should be a boolean")
    if not (condition_options["tolerance"] > 0):
        raise CheckError("maximum condition number tolerance should be greater than zero")
    if not (condition_options["accuracy"] > 0):
        raise CheckError("condition number accuracy should be greater than zero")
