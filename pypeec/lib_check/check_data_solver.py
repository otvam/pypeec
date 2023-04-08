"""
Combine the voxel and problem data into a new solver data structure.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import numpy as np
from pypeec.lib_utils import datachecker
from pypeec import config

# get config
NP_TYPES = config.NP_TYPES


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


def _get_field(dat_tmp, var_type, idx):
    """
    Cast and check the material and source vectors.
    If the variable is a scalar, cast to an array.
    If the variable is an array, check the length.
    """

    for tag, val in dat_tmp.items():
        # cast
        if var_type == "lumped":
            val = np.full(len(idx), val, dtype=NP_TYPES.FLOAT)
        elif var_type == "distributed":
            val = np.array(val, dtype=NP_TYPES.FLOAT)
        else:
            raise ValueError("invalid material type")

        # check
        cond = len(val) == len(idx)
        datachecker.check_assert(tag, cond, "vector length does not match the number of voxels")

        # update
        dat_tmp[tag] = val

    return dat_tmp


def _get_domain_indices(domain_list, domain_def):
    """
    Get indices from a list of domain names.
    """

    idx_all = np.array([], dtype=NP_TYPES.INT)
    for tag in domain_list:
        idx_tmp = np.array(domain_def[tag], dtype=NP_TYPES.INT)
        idx_all = np.append(idx_all, idx_tmp)

    return idx_all


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
        var_type = dat_tmp["var_type"]
        material_type = dat_tmp["material_type"]
        domain_list = dat_tmp["domain_list"]

        # get indices
        idx = _get_domain_indices(domain_list, domain_def)

        # append domain names
        domain_cm += domain_list

        # assign the indices
        if material_type == "electric":
            idx_c = np.append(idx_c, idx)
        elif material_type == "magnetic":
            idx_m = np.append(idx_m, idx)
        else:
            raise ValueError("invalid material type")

        # assign the material
        material_idx[tag] = {"idx": idx, "material_type": material_type, "var_type": var_type}

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
        var_type = dat_tmp["var_type"]
        source_type = dat_tmp["source_type"]
        domain_list = dat_tmp["domain_list"]

        # get indices
        idx = _get_domain_indices(domain_list, domain_def)

        # append indices
        idx_s = np.append(idx_s, idx)

        # append domain names
        domain_s += domain_list

        # get the source value
        source_idx[tag] = {"idx": idx, "source_type": source_type, "var_type": var_type}

    return domain_s, idx_s, source_idx


def _get_sweep_input(sweep_input, material_idx, source_idx):
    """
    Check the size of the material and source values.
    Convert the values to arrays.
    """

    # extract field
    freq = sweep_input["freq"]
    material_val = sweep_input["material_val"]
    source_val = sweep_input["source_val"]

    # check the material domain name
    for tag in material_idx:
        datachecker.check_choice("material domain name", tag, material_val)
    for tag in source_idx:
        datachecker.check_choice("source domain name", tag, source_val)

    # update values
    for tag, dat_tmp in material_val.items():
        # extract the data
        var_type = material_idx[tag]["var_type"]
        idx = material_idx[tag]["idx"]

        # check type
        material_val[tag] = _get_field(dat_tmp, var_type, idx)

    # update values
    for tag, dat_tmp in source_val.items():
        # extract the data
        var_type = source_idx[tag]["var_type"]
        idx = source_idx[tag]["idx"]

        # check type
        source_val[tag] = _get_field(dat_tmp, var_type, idx)

    # assign results
    sweep_input = {"freq": freq, "material_val": material_val, "source_val": source_val}

    return sweep_input


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
    sweep_config = data_problem["sweep_config"]
    sweep_input = data_problem["sweep_input"]

    # extract field
    domain_def = data_voxel["domain_def"]
    connection_def = data_voxel["connection_def"]

    # get material and source indices
    (domain_cm, idx_c, idx_m, material_idx) = _get_material_idx(material_def, domain_def)
    (domain_s, idx_s, source_idx) = _get_source_idx(source_def, domain_def)

    # check the domain name
    for tag in domain_cm:
        datachecker.check_choice("material domain name", tag, domain_def)
    for tag in domain_s:
        datachecker.check_choice("source domain name", tag, domain_def)

    # get source and material values
    for tag, sweep_input_tmp in sweep_input.items():
        sweep_input[tag] = _get_sweep_input(sweep_input_tmp, material_idx, source_idx)

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
        "material_idx": material_idx,
        "source_idx": source_idx,
        "has_electric": has_electric,
        "has_magnetic": has_magnetic,
        "has_coupling": has_coupling,
    }

    return data_solver, sweep_config, sweep_input
