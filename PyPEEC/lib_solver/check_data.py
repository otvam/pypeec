"""
Module for checking the solver input data.
Check the voxel and problem data.
Combine the voxel and problem data into solver data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np


class CheckError(Exception):
    """
    Exception used for signaling invalid input data.
    """

    pass


def _get_domain_indices(domain, domain_def):
    """
    Get indices from list of domain names.
    """

    # init array
    idx = np.array([], dtype=np.int64)

    # find the indices
    for tag_domain in domain:
        # check that the domain exist
        if tag_domain not in domain_def:
            raise CheckError("domain: domain name should be list in the voxel definition")

        # append indices
        idx = np.append(idx, domain_def[tag_domain])

    return idx


def _check_domain_def(n, domain_def):
    """
    Check that the domain definition is valid.
    """

    # extract the voxel data
    (nx, ny, nz) = n
    n = nx * ny * nz

    # init the domain indices
    idx_domain = np.array([], dtype=np.int64)

    # check type
    if not isinstance(domain_def, dict):
        raise CheckError("domain_def: domain definition should be a dict")

    # check the different domains
    for tag, idx in domain_def.items():
        # check tag
        if not isinstance(tag, str):
            raise CheckError("tag: conductor name should be a string")

        # cast indices
        idx = np.array(idx)
        if not (len(idx.shape) == 1):
            raise CheckError("idx: indices should be a vector")
        if not np.issubdtype(idx.dtype, np.integer):
            raise CheckError("idx: indices should be composed of integers")

        # check for indices range
        if not (np.all(idx >= 0) and np.all(idx < n)):
            raise CheckError("idx: conductor indices should belong to the voxel structure")

        # append
        idx_domain = np.append(idx_domain, idx)

    # check for duplicates
    if not (len(np.unique(idx_domain)) == len(idx_domain)):
        raise CheckError("domain indices should be unique")


def _check_conductor_def(conductor_def):
    """
    Check that the conductor definition is valid.
    """

    # check type
    if not isinstance(conductor_def, dict):
        raise CheckError("conductor_def: conductor definition should be a dict")

    # check value
    for tag, dat_tmp in conductor_def.items():
        # extract the data
        domain = dat_tmp["domain"]
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
        if not all(np.issubdtype(type(x), str) for x in domain):
            raise CheckError("domain: domain name should be composed of strings")


def _check_source_def(source_def):
    """
    Check that the source definition is valid.
    """

    # check type
    if not isinstance(source_def, dict):
        raise CheckError("source_def: source definition should be a dict")

    # check value
    for tag, dat_tmp in source_def.items():
        # extract the data
        source_type = dat_tmp["source_type"]
        domain = dat_tmp["domain"]

        # check type
        if not isinstance(tag, str):
            raise CheckError("tag: source name should be a string")
        if not isinstance(source_type, str):
            raise CheckError("source_type: source type should be a string")

        # check value
        if not (source_type in ["current", "voltage"]):
            raise CheckError("source_type: source type should be voltage or current")
        if not all(np.issubdtype(type(x), str) for x in domain):
            raise CheckError("domain: domain name should be composed of strings")

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


def _get_conductor_idx(conductor_def, domain_def):
    """
    Get the indices of the conductors.
    Create a new dict with the indices in place of the domain names.
    """

    # init
    conductor_idx = dict()
    idx_conductor = np.array([], dtype=np.int64)

    for tag, dat_tmp in conductor_def.items():
        # extract the data
        domain = dat_tmp["domain"]
        rho = dat_tmp["rho"]

        # get indices
        idx = _get_domain_indices(domain, domain_def)

        # append indices
        idx_conductor = np.append(idx_conductor, idx)

        # assign data
        conductor_idx[tag] = {"idx": idx, "rho": rho}

    return idx_conductor, conductor_idx


def _get_source_idx(source_def, domain_def):
    """
    Get the indices of the sources.
    Create a new dict with the indices in place of the domain names.
    """

    # init
    source_idx = dict()
    idx_source = np.array([], dtype=np.int64)

    for tag, dat_tmp in source_def.items():
        # extract the data
        source_type = dat_tmp["source_type"]
        domain = dat_tmp["domain"]

        # get indices
        idx = _get_domain_indices(domain, domain_def)

        # append indices
        idx_source = np.append(idx_source, idx)

        # get the source value
        if source_type == "current":
            I = dat_tmp["I"]
            G = dat_tmp["G"]
            source_idx[tag] = {"idx": idx, "source_type": source_type, "I": I, "G": G}
        elif source_type == "voltage":
            V = dat_tmp["V"]
            R = dat_tmp["R"]
            source_idx[tag] = {"idx": idx, "source_type": source_type, "V": V, "R": R}
        else:
            raise ValueError("invalid source type")

    return idx_source, source_idx


def _check_indices(idx_conductor, idx_source):
    """
    Check that the conductor and source indices are valid.
    The indices should be unique and compatible with the voxel size.
    The source indices should be included in the conductor indices.
    """

    # check for unicity
    if not (len(np.unique(idx_conductor)) == len(idx_conductor)):
        raise CheckError("conductor indices should be unique")
    if not (len(np.unique(idx_source)) == len(idx_source)):
        raise CheckError("source indices should be unique")

    # check that the terminal indices are conductor indices
    if not np.all(np.isin(idx_source, idx_conductor)):
        raise CheckError("source indices are not included in conductor indices")


def check_data_voxel(data_voxel):
    """
    Check the voxel structure (number and size).
    Check the domain definition (mapping between domain names and indices).
    """

    # check type
    if not isinstance(data_voxel, dict):
        raise CheckError("data_voxel: voxel description should be a dict")

    # extract field
    n = data_voxel["n"]
    d = data_voxel["d"]
    domain_def = data_voxel["domain_def"]

    # check size
    if not (len(n) == 3):
        raise CheckError("n: invalid voxel number (should be a tuple with three elements)")
    if not (len(d) == 3):
        raise CheckError("d: invalid voxel size (should be a tuple with three elements)")

    # check type
    if not all(np.issubdtype(type(x), np.integer) for x in n):
        raise CheckError("n: number of voxels should be composed of integers")
    if not all(np.issubdtype(type(x), np.floating) for x in d):
        raise CheckError("d: dimension of the voxels should be composed of real floats")

    # check value
    if not all((x >= 1) for x in n):
        raise CheckError("n: number of voxels cannot be smaller than one")
    if not all((x > 0) for x in d):
        raise CheckError("d: dimension of the voxels should be positive")

    # check domain
    _check_domain_def(n, domain_def)


def check_data_problem(data_problem):
    """
    Check the problem data (Green function, frequency, solver options, matrix condition options).
    Check the conductor and source definition.
    """

    # check type
    if not isinstance(data_problem, dict):
        raise CheckError("data_problem: problem description should be a dict")

    # extract field
    n_green = data_problem["n_green"]
    freq = data_problem["freq"]
    solver_options = data_problem["solver_options"]
    condition_options = data_problem["condition_options"]
    conductor_def = data_problem["conductor_def"]
    source_def = data_problem["source_def"]

    # check type
    if not np.issubdtype(type(freq), np.floating):
        raise CheckError("freq: frequency should be a float")
    if not np.issubdtype(type(n_green), np.floating):
        raise CheckError("n_green: voxel distance to simplify the green function should be a float")

    # check value
    if not(freq >= 0):
        raise CheckError("freq: frequency should be positive")
    if not (n_green > 0):
        raise CheckError("n_green: voxel distance to simplify the green function should be positive")

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

    # check conductor and source
    _check_conductor_def(conductor_def)
    _check_source_def(source_def)


def get_data_solver(data_voxel, data_problem):
    """
    Combine the voxel data and the problem data.
    The voxel data contains the mapping between domain names and indices.
    The problem data contains domain names used for the sourced.
    The new dict contains the indices used for the sources.
    """

    # extract field
    n_green = data_problem["n_green"]
    freq = data_problem["freq"]
    solver_options = data_problem["solver_options"]
    condition_options = data_problem["condition_options"]
    conductor_def = data_problem["conductor_def"]
    source_def = data_problem["source_def"]

    # extract field
    n = data_voxel["n"]
    d = data_voxel["d"]
    domain_def = data_voxel["domain_def"]

    # get conductor indices
    (idx_conductor, conductor_idx) = _get_conductor_idx(conductor_def, domain_def)
    (idx_source, source_idx) = _get_source_idx(source_def, domain_def)

    # check indices
    _check_indices(idx_conductor, idx_source)

    # assign combined data
    data_solver = {
        "n": n,
        "d": d,
        "n_green": n_green,
        "freq": freq,
        "solver_options": solver_options,
        "condition_options": condition_options,
        "conductor_idx": conductor_idx,
        "source_idx": source_idx,
    }

    return data_solver