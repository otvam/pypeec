"""
Module for checking the solver input data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np


class CheckError(Exception):
    """
    Exception used for signaling invalid input data.
    """

    pass


def _check_idx(idx):
    """
    Check if the indices are correct and cast to numpy array.
    """

    # cast to numpy array
    idx = np.array(idx)

    # check if vector
    if not (len(idx.shape) == 1):
        raise CheckError("idx: indices should be a vector")

    if not np.issubdtype(idx.dtype, np.integer):
        raise CheckError("idx: indices should be composed of integers")

    return idx


def _check_conductor(idx_v, conductor):
    """
    Check that the conductors are valid.
    Append the conductor indices to an array.
    """

    for tag, dat_tmp in conductor.items():
        # extract the data
        idx = dat_tmp["idx"]
        rho = dat_tmp["rho"]

        # check type
        if not isinstance(tag, str):
            raise CheckError("tag: conductor name should be a string")
        if not np.issubdtype(type(rho), np.floating):
            raise CheckError("rho: conductor resistivity should be a float")

        # check value
        if not np.isscalar(rho):
            raise CheckError("rho: conductor resistivity should be a real scalar")
        if not (rho > 0):
            raise CheckError("rho: conductor resistivity should be greater than zero")

        # check indices
        idx = _check_idx(idx)

        # append the indices
        idx_v = np.append(idx_v, idx)

    return idx_v


def _check_source(idx_src, tag_src, source):
    """
    Check that the sources (voltage or current) are valid.
    Append the source tag to a list.
    Append the source indices to an array.
    """

    for tag, dat_tmp in source.items():
        # extract the data
        source_type = dat_tmp["source_type"]
        idx = dat_tmp["idx"]

        # check type
        if not isinstance(tag, str):
            raise CheckError("tag: source name should be a string")
        if not isinstance(source_type, str):
            raise CheckError("source_type: source type should be a string")

        # check value
        if not ((source_type == "current") or (source_type == "voltage")):
            raise CheckError("source_type: source type should be voltage or current")

        # get the source value
        if source_type == "current":
            value = dat_tmp["I"]
            element = dat_tmp["G"]
        elif source_type == "voltage":
            value = dat_tmp["V"]
            element = dat_tmp["R"]
        else:
            raise ValueError("invalid source type")

        # check the source type
        if not np.issubdtype(type(value), np.number):
            raise CheckError("I/V: current/voltage source value should be a complex number")
        if not np.issubdtype(type(element), np.floating):
            raise CheckError("G/R: source internal conductance/resistance should be a float")

        # check the source value
        if not np.isscalar(value):
            raise CheckError("I/V: current/voltage source value should be a scalar")
        if not np.isscalar(element):
            raise CheckError("G/R: source internal conductance/resistance should be a real scalar")

        # check indices
        idx = _check_idx(idx)

        # append the tag and indices
        tag_src.append(tag)
        idx_src = np.append(idx_src, idx)

    return idx_src, tag_src


def check_data_solver(data_solver):
    """
    Check the type of the input data.
    """

    if not isinstance(data_solver, dict):
        raise CheckError("invalid input data")


def check_voxel(data_solver):
    """
    Check the voxel structure (number and size) and the Green function parameter.
    """

    # extract field
    n = data_solver["n"]
    r = data_solver["r"]
    d = data_solver["d"]
    ori = data_solver["ori"]
    n_green = data_solver["n_green"]

    # check size
    if not (len(n) == 3):
        raise CheckError("n: invalid voxel number (should be a tuple with three elements)")
    if not (len(r) == 3):
        raise CheckError("r: invalid voxel resampling factor (should be a tuple with three elements)")
    if not (len(d) == 3):
        raise CheckError("d: invalid voxel size (should be a tuple with three elements)")
    if not (len(ori) == 3):
        raise CheckError("ori: invalid voxel origin (should be a tuple with three elements)")

    # check type
    if not all(np.issubdtype(type(x), np.integer) for x in n):
        raise CheckError("n: number of voxels should be composed of integers")
    if not all(np.issubdtype(type(x), np.integer) for x in r):
        raise CheckError("r: number of resampling be composed of integers")
    if not all(np.issubdtype(type(x), np.floating) for x in d):
        raise CheckError("d: dimension of the voxels should be composed of real floats")
    if not all(np.issubdtype(type(x), np.floating) for x in ori):
        raise CheckError("ori: voxel origin should be composed of real floats")
    if not np.issubdtype(type(n_green), np.floating):
        raise CheckError("n_green: voxel distance to simplify the green function should be a float")

    # check value
    if not all((x >= 1) for x in n):
        raise CheckError("n: number of voxels cannot be smaller than one")
    if not all((x >= 1) for x in r):
        raise CheckError("r: number of resampling cannot be smaller than one")
    if not all((x > 0) for x in d):
        raise CheckError("d: dimension of the voxels should be positive")
    if not (n_green > 0):
        raise CheckError("n_green: voxel distance to simplify the green function should be positive")


def check_problem(data_solver):
    """
    Check the conductors and sources.
    More particularly, check that the indices of the voxels are valid.
    """

    # extract field
    conductor = data_solver["conductor"]
    source = data_solver["source"]
    n = data_solver["n"]

    # extract the voxel data
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
    Check the frequency, the condition number options, and the solver options.
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
        raise CheckError("solver_options: solver options should be a dict")
    if not (solver_options["tol"] > 0):
        raise CheckError("tol: solver relative tolerance should be greater than zero")
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
