"""
Combine the voxel and problem data into a new solver data structure.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import numpy as np
from PyPEEC.lib_utils.error import CheckError


def _get_domain_indices(domain_list, domain_def):
    """
    Get indices from a list of domain names.
    """

    # init array
    idx = np.array([], dtype=np.int64)

    # find the indices
    for tag in domain_list:
        # check that the domain exist
        if tag not in domain_def:
            raise CheckError("domain: domain name should be list in the voxel definition")

        # append indices
        idx = np.append(idx, domain_def[tag])

    return idx


def _get_material_idx(material_def, domain_def):
    """
    Get the indices of the material.
    Create a new dict with the indices in place of the domain names.
    Split the electric and magnetic materials.
    """

    # init
    material_idx = dict()
    idx_c = np.array([], dtype=np.int64)
    idx_m = np.array([], dtype=np.int64)

    for tag, dat_tmp in material_def.items():
        # extract the data
        material_type = dat_tmp["material_type"]
        domain_list = dat_tmp["domain_list"]

        # get indices
        idx = _get_domain_indices(domain_list, domain_def)

        # assign the indices
        if material_type == "electric":
            rho = dat_tmp["rho"]
            idx_c = np.append(idx_c, idx)
            material_idx[tag] = {"idx": idx, "material_type": material_type, "rho": rho}
        elif material_type == "magnetic":
            chi = dat_tmp["chi_re"]-1j*dat_tmp["chi_im"]
            idx_m = np.append(idx_m, idx)
            material_idx[tag] = {"idx": idx, "material_type": material_type, "chi": chi}
        else:
            raise CheckError("invalid material type")

    return idx_c, idx_m, material_idx


def _get_source_idx(source_def, domain_def):
    """
    Get the indices of the sources.
    Create a new dict with the indices in place of the domain names.
    """

    # init
    source_idx = dict()
    idx_s = np.array([], dtype=np.int64)

    for tag, dat_tmp in source_def.items():
        # extract the data
        source_type = dat_tmp["source_type"]
        domain_list = dat_tmp["domain_list"]

        # get indices
        idx = _get_domain_indices(domain_list, domain_def)

        # append indices
        idx_s = np.append(idx_s, idx)

        # get the source value
        if source_type == "current":
            I = dat_tmp["I_re"]+1j*dat_tmp["I_im"]
            Y = dat_tmp["Y_re"]+1j*dat_tmp["Y_im"]
            source_idx[tag] = {"idx": idx, "source_type": source_type, "I": I, "Y": Y}
        elif source_type == "voltage":
            V = dat_tmp["V_re"]+1j*dat_tmp["V_im"]
            Z = dat_tmp["Z_re"]+1j*dat_tmp["Z_im"]
            source_idx[tag] = {"idx": idx, "source_type": source_type, "V": V, "Z": Z}
        else:
            raise CheckError("invalid source type")

    return idx_s, source_idx


def _check_indices(idx_c, idx_m, idx_s):
    """
    Check that the material and source indices are valid.
    The indices should be unique and compatible with the voxel size.
    The source indices should be included in the electric indices.
    """

    # check for unicity
    if not (len(np.unique(idx_c)) == len(idx_c)):
        raise CheckError("electric indices should be unique")
    if not (len(np.unique(idx_m)) == len(idx_m)):
        raise CheckError("magnetic indices should be unique")
    if not (len(np.unique(idx_s)) == len(idx_s)):
        raise CheckError("source indices should be unique")

    # check for invalid material
    if len(np.intersect1d(idx_c, idx_m)) != 0:
        raise CheckError("magnetic and electric indices should be unique")

    # check that the problem is not empty
    if len(idx_c) == 0:
        raise CheckError("electric indices should not be empty")
    if len(idx_s) == 0:
        raise CheckError("sources indices should not be empty")

    # check that the terminal indices are electric indices
    if not np.all(np.in1d(idx_s, idx_c)):
        raise CheckError("source indices are not included in electric indices")


def _check_source_graph(idx_c, idx_s, connection_def):
    """
    Check that there is at least one source per connected component.
    A connected components without a source would lead to a singular problem.
    """

    for idx_graph in connection_def:
        if len(np.intersect1d(idx_graph, idx_c)) > 0:
            if len(np.intersect1d(idx_graph, idx_s)) == 0:
                raise CheckError("a connected component does not include at least one source")


def get_data_solver(data_voxel, data_problem, data_tolerance):
    """
    Combine the voxel data, the problem data, and the tolerance data.
    The voxel data contains the mapping between domain names and indices.
    The problem data contains domain names used for the materials and sources.
    The tolerance data contains numerical options.
    The new dict contains the indices used for the materials and sources.
    """

    # extract field
    material_def = data_problem["material_def"]
    source_def = data_problem["source_def"]

    # extract field
    domain_def = data_voxel["domain_def"]
    connection_def = data_voxel["connection_def"]

    # get material and source indices
    (idx_c, idx_m, material_idx) = _get_material_idx(material_def, domain_def)
    (idx_s, source_idx) = _get_source_idx(source_def, domain_def)

    # check indices
    _check_indices(idx_c, idx_m, idx_s)

    # check graph
    _check_source_graph(idx_c, idx_s, connection_def)

    # check the existence of magnetic domains
    has_electric = len(idx_c) > 0
    has_magnetic = len(idx_m) > 0
    has_coupling = has_electric and has_magnetic

    # assign combined data
    data_solver = {
        "n": data_voxel["n"],
        "d": data_voxel["d"],
        "c": data_voxel["c"],
        "green_simplify": data_tolerance["green_simplify"],
        "coupling_simplify": data_tolerance["coupling_simplify"],
        "solver_options": data_tolerance["solver_options"],
        "condition_options": data_tolerance["condition_options"],
        "freq": data_problem["freq"],
        "material_idx": material_idx,
        "source_idx": source_idx,
        "has_electric": has_electric,
        "has_magnetic": has_magnetic,
        "has_coupling": has_coupling,
    }

    return data_solver
