"""
Combine the voxel and problem data into a new solver data structure.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
from PyPEEC.lib_utils.error import CheckError


def _get_domain_indices(domain, domain_def):
    """
    Get indices from a list of domain names.
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
            raise CheckError("invalid source type")

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


def get_data_solver(data_voxel, data_problem):
    """
    Combine the voxel data and the problem data.
    The voxel data contains the mapping between domain names and indices.
    The problem data contains domain names used for the conductors and sources.
    The new dict contains the indices used for the conductors and sources.
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
    c = data_voxel["c"]
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
        "c": c,
        "n_green": n_green,
        "freq": freq,
        "solver_options": solver_options,
        "condition_options": condition_options,
        "conductor_idx": conductor_idx,
        "source_idx": source_idx,
    }

    return data_solver
