"""
Combine the voxel and problem data into a new solver data structure.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import numpy as np
from pypeec.lib_utils import datachecker
from pypeec.lib_utils import config

# get config
NP_TYPES = config.NP_TYPES


def _get_domain_indices(domain_list, domain_def):
    """
    Get indices from a list of domain names.
    """

    idx = np.array([], dtype=NP_TYPES.INT)
    for tag in domain_list:
        idx = np.append(idx, domain_def[tag])

    return idx


def _get_material_idx(material_def, domain_def):
    """
    Get the indices of the material.
    Create a new dict with the indices in place of the domain names.
    Split the electric and magnetic materials.
    """

    # init
    material_idx = {}
    idx_c = np.array([], dtype=NP_TYPES.INT)
    idx_m = np.array([], dtype=NP_TYPES.INT)
    domain_cm = []

    for tag, dat_tmp in material_def.items():
        # extract the data
        material_type = dat_tmp["material_type"]
        domain_list = dat_tmp["domain_list"]

        # get indices
        idx = _get_domain_indices(domain_list, domain_def)

        # append domain names
        domain_cm += domain_list

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
            raise ValueError("invalid material type")

    return domain_cm, idx_c, idx_m, material_idx


def _get_source_idx(source_def, domain_def):
    """
    Get the indices of the sources.
    Create a new dict with the indices in place of the domain names.
    """

    # init
    source_idx = {}
    idx_s = np.array([], dtype=NP_TYPES.INT)
    domain_s = []

    for tag, dat_tmp in source_def.items():
        # extract the data
        source_type = dat_tmp["source_type"]
        domain_list = dat_tmp["domain_list"]

        # get indices
        idx = _get_domain_indices(domain_list, domain_def)

        # append indices
        idx_s = np.append(idx_s, idx)

        # append domain names
        domain_s += domain_list

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
            raise ValueError("invalid source type")

    return domain_s, idx_s, source_idx


def _check_names(domain_cm, domain_s, domain_def):
    """
    Check the validity of the domain names.
    """

    # check the material domain name
    for tag in domain_cm:
        datachecker.check_choice("material domain name", tag, domain_def)

    # check the source domain name
    for tag in domain_s:
        datachecker.check_choice("source domain name", tag, domain_def)


def _check_indices(n, idx_c, idx_m, idx_s):
    """
    Check that the material and source indices are valid.
    The indices should be unique and compatible with the voxel size.
    The source indices should be included in the electric indices.
    """

    # extract the voxel data
    (nx, ny, nz) = n
    nv = nx*ny*nz

    # check the indices
    datachecker.check_index_array("index electric", idx_c, bnd=nv, can_be_empty=False)
    datachecker.check_index_array("index magnetic", idx_m, bnd=nv, can_be_empty=True)
    datachecker.check_index_array("index source", idx_s, bnd=nv, can_be_empty=False)

    # check for invalid material
    cond = len(np.intersect1d(idx_c, idx_m)) == 0
    datachecker.check_assert("index overlap", cond, "magnetic and electric indices should not overlap")

    # check that the terminal indices are electric indices
    cond = np.all(np.in1d(idx_s, idx_c))
    datachecker.check_assert("index overlap", cond, "source indices should overlap with electric indices")

    # check that the terminal indices are electric indices
    cond = np.all(np.logical_not(np.in1d(idx_s, idx_m)))
    datachecker.check_assert("index overlap", cond, "source indices should not overlap with magnetic indices")


def _check_source_graph(idx_c, idx_m, idx_s, connection_def):
    """
    Check that there is at least one source per connected component.
    A connected components without a source would lead to a singular problem.
    """

    for idx_graph in connection_def:
        has_magnetic = len(np.intersect1d(idx_graph, idx_m)) > 0
        has_electric = len(np.intersect1d(idx_graph, idx_c)) > 0
        has_source = len(np.intersect1d(idx_graph, idx_s)) > 0

        cond = (not has_electric) or has_source
        datachecker.check_assert("index overlap", cond, "electric components should include at least one source")

        cond = (not has_magnetic) or (not has_source)
        datachecker.check_assert("index overlap", cond, "magnetic components should not include sources")


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
    n = data_voxel["n"]
    domain_def = data_voxel["domain_def"]
    connection_def = data_voxel["connection_def"]

    # get material and source indices
    (domain_cm, idx_c, idx_m, material_idx) = _get_material_idx(material_def, domain_def)
    (domain_s, idx_s, source_idx) = _get_source_idx(source_def, domain_def)

    # check the domain name
    _check_names(domain_cm, domain_s, domain_def)

    # check indices
    _check_indices(n, idx_c, idx_m, idx_s)

    # check graph
    _check_source_graph(idx_c, idx_m, idx_s, connection_def)

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
        "factorization_options": data_tolerance["factorization_options"],
        "freq": data_problem["freq"],
        "material_idx": material_idx,
        "source_idx": source_idx,
        "has_electric": has_electric,
        "has_magnetic": has_magnetic,
        "has_coupling": has_coupling,
    }

    return data_solver
